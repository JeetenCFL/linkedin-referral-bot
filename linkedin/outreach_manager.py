import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

from config.config import (
    LINKEDIN_SEARCH_URL,
    SELECTORS,
    DEFAULT_TIMEOUT
)
from config.logging_config import log_manager
from .browser_manager import BrowserManager
from .session_manager import SessionManager

class OutreachManager:
    def __init__(self):
        self.logger = log_manager.get_logger(__name__)
        self.browser = BrowserManager()
        self.driver = None
        self.settings = self._load_settings()
        self.scored_jobs = self._load_latest_scored_jobs()
        self.session_manager = SessionManager()

    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from Settings.json file."""
        try:
            with open('config/Settings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning("Settings.json not found. Using default settings.")
            return {
                "custom_message": "",
                "universities": []
            }

    def _load_latest_scored_jobs(self) -> Dict[str, Any]:
        """Load the most recent scored jobs file."""
        job_files = [f for f in os.listdir('data') if f.startswith('job_descriptions_scored_') and f.endswith('.json')]
        if not job_files:
            raise FileNotFoundError("No scored jobs file found in data directory")
        
        latest_file = max(job_files)  # Gets the most recent file based on timestamp
        file_path = os.path.join('data', latest_file)
        
        with open(file_path, 'r') as f:
            return json.load(f)

    def start(self) -> bool:
        """Initialize the browser and start the outreach manager."""
        try:
            self.driver = self.browser.initialize_browser()
            if not self.driver:
                self.logger.error("Failed to initialize browser")
                return False

            # Try to restore session from cookies
            if self._restore_session():
                self.logger.info("Successfully restored session from cookies")
                return True

            # If session restoration fails, we'll need to login
            self.logger.info("No valid session found, login required")
            return True

        except Exception as e:
            self.logger.error(f"Browser initialization failed: {str(e)}")
            return False

    def _restore_session(self) -> bool:
        """Try to restore session using saved cookies."""
        try:
            cookies = self.session_manager.load_cookies()
            if not cookies:
                return False

            # First navigate to LinkedIn domain
            self.driver.get("https://www.linkedin.com/feed")
            time.sleep(2)

            # Add cookies
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    self.logger.warning(f"Failed to add cookie: {str(e)}")

            # Refresh page to apply cookies
            self.driver.refresh()
            time.sleep(2)

            # Check if we're logged in by looking for feed button
            feed_button = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["login"]["feed_button"]),
                timeout=10
            )

            return bool(feed_button)

        except Exception as e:
            self.logger.error(f"Error restoring session: {str(e)}")
            return False

    def save_session(self) -> bool:
        """Save current session cookies."""
        try:
            cookies = self.driver.get_cookies()
            return self.session_manager.save_cookies(cookies)
        except Exception as e:
            self.logger.error(f"Error saving session: {str(e)}")
            return False

    def _search_people(self, job_title: str, company_name: str) -> bool:
        """Search for people based on job title and company name."""
        try:
            # Navigate to people search page
            self.driver.get(LINKEDIN_SEARCH_URL)
            time.sleep(2)  # Wait for page load

            # Enter job title in keywords search
            keyword_input = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["search"]["keyword_input"])
            )
            if not keyword_input:
                self.logger.error("Keyword input field not found")
                return False
            
            keyword_input.clear()
            keyword_input.send_keys(job_title)
            time.sleep(1)
            keyword_input.send_keys(Keys.RETURN)
            time.sleep(2)  # Wait for initial results

            # Click company filter button
            company_filter_button = self.browser.wait_for_clickable(
                (By.XPATH, SELECTORS["search"]["company_filter_button"])
            )
            if not company_filter_button:
                self.logger.error("Company filter button not found")
                return False
            
            company_filter_button.click()
            time.sleep(1)  # Wait for filter dropdown

            # Enter company name
            company_input = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["search"]["company_input"])
            )
            if not company_input:
                self.logger.error("Company input field not found")
                return False
            
            company_input.clear()
            company_input.send_keys(company_name)
            time.sleep(2)  # Wait for suggestions

            # Select first company suggestion
            company_suggestion = self.browser.wait_for_clickable(
                (By.XPATH, SELECTORS["search"]["company_suggestion"])
            )
            if not company_suggestion:
                self.logger.error("Company suggestion not found")
                return False
            
            company_suggestion.click()
            time.sleep(1)

            # Click apply filter button
            apply_button = self.browser.wait_for_clickable(
                (By.XPATH, SELECTORS["search"]["apply_company_filter"])
            )
            if not apply_button:
                self.logger.error("Apply filter button not found")
                return False
            
            apply_button.click()
            time.sleep(2)  # Wait for filtered results
            
            return True

        except Exception as e:
            self.logger.error(f"Error during people search: {str(e)}")
            return False

    def _get_search_results(self) -> List[Dict[str, str]]:
        """Get the list of people from search results."""
        try:
            # Wait for results container to load
            results_container = self.browser.wait_for_element(
                (By.XPATH, "//div[@class='search-results-container']")
            )
            if not results_container:
                self.logger.error("Results container not found")
                return []

            self.logger.info("Found results container, starting to scroll...")
            
            # Initialize tracking variables
            last_person_count = 0
            scroll_attempt = 0
            max_scroll_attempts = 50  # Prevent infinite scrolling
            
            while scroll_attempt < max_scroll_attempts:
                scroll_attempt += 1
                
                # Measure viewport height and choose an overlap (20%)
                viewport_height = int(self.driver.execute_script(
                    "return Math.round(arguments[0].clientHeight);", results_container
                ))
                overlap = int(viewport_height * 0.20)
                scroll_amount = viewport_height - overlap

                # Find current scroll and container height
                current_scroll = int(self.driver.execute_script(
                    "return Math.round(arguments[0].scrollTop);", results_container
                ))
                container_height = int(self.driver.execute_script(
                    "return Math.round(arguments[0].scrollHeight);", results_container
                ))

                # Compute next scroll target (don't exceed bottom)
                target_scroll = min(current_scroll + scroll_amount, container_height)
                self.driver.execute_script(
                    "arguments[0].scrollTo(0, arguments[1]);", 
                    results_container, target_scroll
                )

                # Wait for new content to load
                time.sleep(2)  # Wait for initial load
                
                # Count current people
                current_people = results_container.find_elements(
                    By.XPATH, ".//a[.//img[contains(@class, 'EntityPhoto-circle')]]"
                )
                current_count = len(current_people)
                
                if current_count > last_person_count:
                    self.logger.info(f"Loaded batch; total people now: {current_count}")
                    last_person_count = current_count
                    continue
                
                # Check if we've reached the bottom
                new_scroll = int(self.driver.execute_script(
                    "return Math.round(arguments[0].scrollTop);", results_container
                ))
                new_height = int(self.driver.execute_script(
                    "return Math.round(arguments[0].scrollHeight);", results_container
                ))

                # If scroll + viewport ≥ height − 5px, we're at the bottom
                if new_scroll + viewport_height >= new_height - 5:
                    self.logger.info("No additional people detected; bottom reached.")
                    break

            # Extract people information
            people = []
            person_elements = results_container.find_elements(
                By.XPATH, ".//a[.//img[contains(@class, 'EntityPhoto-circle')]]"
            )
            
            for element in person_elements:
                try:
                    # Get profile URL
                    profile_url = element.get_attribute("href")
                    if not profile_url:
                        continue
                        
                    # Get name using the profile URL
                    name_xpath = f"//a[@href='{profile_url}']/span/span"
                    name_element = self.driver.find_element(By.XPATH, name_xpath)
                    if name_element:
                        name = name_element.text.strip()
                        people.append({
                            'name': name,
                            'profile_url': profile_url
                        })
                except NoSuchElementException:
                    continue
                except Exception as e:
                    self.logger.warning(f"Error extracting person info: {str(e)}")
                    continue

            self.logger.info(f"Found {len(people)} people in search results")
            return people

        except Exception as e:
            self.logger.error(f"Error getting search results: {str(e)}")
            return []

    def _send_connection_request(self, person: Dict[str, str], job_data: Dict[str, Any]) -> bool:
        """Send a connection request with personalized message."""
        try:
            # Navigate to person's profile
            self.driver.get(person['profile_url'])
            time.sleep(2)

            # Click connect button
            connect_button = self.browser.wait_for_clickable(
                (By.XPATH, f"//button[contains(@aria-label, 'Invite {person['name']} to connect')]")
            )
            if not connect_button:
                self.logger.error("Connect button not found")
                return False
            
            connect_button.click()
            time.sleep(1)

            # Click "Add a note" button
            add_note_button = self.browser.wait_for_clickable(
                (By.XPATH, SELECTORS["profile"]["add_note_button"])
            )
            if not add_note_button:
                self.logger.error("Add note button not found")
                return False
            
            add_note_button.click()
            time.sleep(1)

            # Fill in personalized message
            message_input = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["profile"]["message_input"])
            )
            if not message_input:
                self.logger.error("Message input field not found")
                return False

            # Create personalized message
            message = self.settings["custom_message"].format(
                name=person['name'],
                company=job_data['company_name'],
                role=job_data['job_title']
            )
            
            message_input.send_keys(message)
            time.sleep(1)

            # Click send button
            send_button = self.browser.wait_for_clickable(
                (By.XPATH, SELECTORS["profile"]["send_button"])
            )
            if not send_button:
                self.logger.error("Send button not found")
                return False
            
            send_button.click()
            time.sleep(2)
            return True

        except Exception as e:
            self.logger.error(f"Error sending connection request: {str(e)}")
            return False

    def process_job_outreach(self, job_id: str) -> bool:
        """Process outreach for a single job."""
        try:
            job_data = self.scored_jobs.get(job_id)
            if not job_data:
                self.logger.error(f"Job data not found for ID: {job_id}")
                return False

            # Search for people
            if not self._search_people(job_data['job_title'], job_data['company_name']):
                return False

            # Get search results
            people = self._get_search_results()
            if not people:
                self.logger.warning(f"No people found for job: {job_data['job_title']}")
                return False

            # Send connection requests
            for person in people:
                print("person:", person)
                if self._send_connection_request(person, job_data):
                    self.logger.info(f"Successfully sent connection request to {person['name']}")
                else:
                    self.logger.error(f"Failed to send connection request to {person['name']}")
                time.sleep(2)  # Rate limiting

            return True

        except Exception as e:
            self.logger.error(f"Error processing job outreach: {str(e)}")
            return False

    def quit(self):
        """Close the browser and clean up."""
        if self.browser:
            # Save session before quitting
            self.save_session()
            self.browser.quit() 