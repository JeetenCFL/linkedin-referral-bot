import json
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    StaleElementReferenceException
)
from selenium.webdriver.support.ui import WebDriverWait
import hashlib
import time
from datetime import datetime
import os
from typing import Optional, Dict, Any

from config.config import (
    LINKEDIN_LOGIN_URL,
    LINKEDIN_JOBS_URL,
    LINKEDIN_EMAIL,
    LINKEDIN_PASSWORD,
    SELECTORS,
    LOGIN_TIMEOUT
)
from config.logging_config import log_manager
from .browser_manager import BrowserManager
from .ai_matcher import JobMatcher

class LinkedInBotError(Exception):
    """Base exception class for LinkedInBot errors"""
    pass

class LinkedInBot:
    def __init__(self):
        self._setup_directories()
        self.logger = log_manager.get_logger(__name__)
        self.browser = BrowserManager()
        self.driver = None
        self.settings = self._load_settings()
        self.job_matcher = JobMatcher()
        # Use the timestamp from log manager
        self.run_timestamp = log_manager.timestamp

    def _setup_directories(self):
        """Create necessary directories for logs and data"""
        # Create data directory for job descriptions and scores
        os.makedirs('data', exist_ok=True)

    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from Settings.json file."""
        try:
            with open('config/Settings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning("Settings.json not found. Using default settings.")
            return {
                "job_keywords": [],
                "locations": [],
                "universities": [],
                "custom_message": "",
                "my_needs": ""
            }
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing Settings.json: {str(e)}")
            raise LinkedInBotError("Invalid Settings.json format")

    def _format_search_query(self, keywords):
        """Format keywords with AND operator for LinkedIn search."""
        return " AND ".join(f'{keyword}' for keyword in keywords)

    def start(self) -> bool:
        """Initialize the browser and start the bot."""
        try:
            self.driver = self.browser.initialize_browser()
            if not self.driver:
                self.logger.error("Failed to initialize browser")
                return False
            return True
        except WebDriverException as e:
            self.logger.error(f"Browser initialization failed: {str(e)}")
            return False

    def login(self) -> bool:
        """Log in to LinkedIn."""
        try:
            # Navigate to login page
            self.driver.get(LINKEDIN_LOGIN_URL)
            
            # Wait for and fill in email
            email_field = self.browser.wait_for_element(
                (By.ID, SELECTORS["login"]["email_field"]),
                LOGIN_TIMEOUT
            )
            if not email_field:
                self.logger.error("Email field not found")
                return False
            email_field.send_keys(LINKEDIN_EMAIL)
            
            # Wait for and fill in password
            password_field = self.browser.wait_for_element(
                (By.ID, SELECTORS["login"]["password_field"]),
                LOGIN_TIMEOUT
            )
            if not password_field:
                self.logger.error("Password field not found")
                return False
            password_field.send_keys(LINKEDIN_PASSWORD)
            
            # Click submit button
            submit_button = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["login"]["submit_button"]),
                LOGIN_TIMEOUT
            )
            if not submit_button:
                self.logger.error("Submit button not found")
                return False
            submit_button.click()
            
            # Wait for feed to load (indicating successful login)
            feed_button = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["login"]["feed_button"]),
                LOGIN_TIMEOUT
            )
            
            if not feed_button:
                self.logger.error("Feed button not found after login attempt")
                return False
                
            self.logger.info("Successfully logged in to LinkedIn")
            return True
            
        except TimeoutException as e:
            self.logger.error(f"Login timeout: {str(e)}")
            return False
        except WebDriverException as e:
            self.logger.error(f"Browser error during login: {str(e)}")
            return False
        except Exception as e:
            self.logger.exception("Unexpected error during login")
            return False

    def _apply_date_filter(self):
        """Apply the date posted filter based on settings."""
        try:
            # Step 1: Open the date filter dropdown
            if not self._open_date_filter_dropdown():
                raise Exception("Failed to open date filter dropdown")

            # Step 2: Select the date filter option
            if not self._select_date_filter_option():
                raise Exception("Failed to select date filter option")

            # Step 3: Apply the filter
            if not self._click_apply_filter_button():
                raise Exception("Failed to click apply filter button")

            return True

        except TimeoutException as e:
            print(f"Timeout while applying date filter: {str(e)}")
            return False
        except Exception as e:
            print(f"Failed to apply date filter: {str(e)}")
            return False

    def _open_date_filter_dropdown(self):
        """Open the date filter dropdown menu."""
        print("\n[Date Filter] Opening dropdown...")
        date_filter_button = self.browser.wait_for_clickable(
            (By.XPATH, SELECTORS["jobs"]["date_posted_button"])
        )
        
        if not date_filter_button:
            print("[Date Filter] ❌ Date filter button not found")
            return False

        self.browser.ensure_element_in_viewport(date_filter_button)
        date_filter_button.click()
        time.sleep(1)  # Wait for dropdown animation
        print("[Date Filter] ✅ Dropdown opened")
        return True

    def _select_date_filter_option(self):
        """Select the date filter option from the dropdown."""
        date_filter = self.settings.get("date_posted_filter", "any_time")
        print(f"\n[Date Filter] Selecting option: {date_filter}")
        
        # Find the radio input
        option_xpath = SELECTORS["jobs"]["date_posted_options"].get(date_filter)
        if not option_xpath:
            print(f"[Date Filter] ❌ Invalid date filter option: {date_filter}")
            return False

        radio_input = self.browser.wait_for_element((By.XPATH, option_xpath))
        if not radio_input:
            print(f"[Date Filter] ❌ Radio input not found for {date_filter}")
            return False

        # Get the associated label and click it
        radio_id = radio_input.get_attribute('id')
        label_xpath = f"//label[@for='{radio_id}']"
        label = self.browser.wait_for_clickable((By.XPATH, label_xpath))
        
        if not label:
            print(f"[Date Filter] ❌ Label not found for radio input {radio_id}")
            return False

        self.browser.ensure_element_in_viewport(label)
        label.click()
        time.sleep(1)  # Wait for selection to register
        print(f"[Date Filter] ✅ Selected {date_filter}")
        return True

    def _click_apply_filter_button(self):
        """Click the apply filter button to update results."""
        print("\n[Date Filter] Applying filter...")
        apply_button = self.browser.wait_for_clickable(
            (By.XPATH, SELECTORS["jobs"]["apply_filter_button"])
        )
        
        if not apply_button:
            print("[Date Filter] ❌ Apply button not found")
            return False

        self.browser.ensure_element_in_viewport(apply_button)
        apply_button.click()
        print("[Date Filter] ✅ Filter applied")
        return True

    def search_jobs(self, job_title: Optional[str] = None, location: Optional[str] = None) -> bool:
        """Search for jobs with given criteria."""
        try:
            # Navigate to jobs page
            self.driver.get(LINKEDIN_JOBS_URL)
            
            # Use provided job title or combine keywords from settings
            search_query = job_title if job_title else self._format_search_query(self.settings["job_keywords"])
            
            # Wait for and fill in job title
            search_input = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["jobs"]["search_input"])
            )
            if not search_input:
                self.logger.error("Search input field not found")
                return False
                
            search_input.clear()
            search_input.send_keys(search_query)
            
            # Use provided location or first location from settings
            location_to_use = location if location else self.settings["locations"][0] if self.settings["locations"] else "Worldwide"
            self.logger.info(f"Using location: {location_to_use}")
            
            # Wait for and fill in location
            location_input = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["jobs"]["location_input"])
            )
            if not location_input:
                self.logger.error("Location input field not found")
                return False
                
            time.sleep(1)  # Allow default to populate
            location_input.clear()
            location_input.send_keys(location_to_use)
            time.sleep(1)  # Allow suggestions to appear
            location_input.send_keys(Keys.RETURN)
            
            # Apply date filter if specified
            if "date_posted_filter" in self.settings:
                try:
                    if not self._apply_date_filter():
                        self.logger.warning("Failed to apply date filter, continuing with unfiltered results")
                except Exception as e:
                    self.logger.error(f"Error during date filter application: {str(e)}")
                    self.logger.info("Continuing with unfiltered results")
            
            time.sleep(2)  # Wait for page to stabilize
            
            # Wait for job results to load
            job_cards = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["jobs"]["job_cards"])
            )
            
            if not job_cards:
                self.logger.error("No job cards found after search")
                return False
                
            self.logger.info("Successfully found job listings")
            return True
            
        except TimeoutException as e:
            self.logger.error(f"Search timeout: {str(e)}")
            return False
        except WebDriverException as e:
            self.logger.error(f"Browser error during search: {str(e)}")
            return False
        except Exception as e:
            self.logger.exception("Unexpected error during job search")
            return False

    def quit(self):
        """Close the browser and clean up."""
        try:
            self.browser.quit()
            self.logger.info("Browser closed successfully")
        except Exception as e:
            self.logger.error(f"Error while closing browser: {str(e)}")

    def _load_all_job_cards(self):
        """Scroll through the jobs container to load all available job cards."""
        self.logger.info("Loading all job cards...")
        
        # 1) Wait for the scroll sentinel to appear
        scroll_sentinel = self.browser.wait_for_element(
            (By.XPATH, SELECTORS["jobs"]["scroll_sentinel"])
        )
        if not scroll_sentinel:
            self.logger.error("Could not find scroll sentinel")
            return
            
        # 2) Find the container (parent of the sentinel)
        jobs_container = scroll_sentinel.find_element(By.XPATH, "./..")
        if not jobs_container:
            self.logger.error("Could not find jobs container")
            return
            
        self.logger.info("Found jobs container, starting to scroll...")
        
        # 3) Count how many cards are currently in that container
        last_card_count = len(
            jobs_container.find_elements(By.XPATH, SELECTORS["jobs"]["job_cards"])
        )
        self.logger.info(f"Initial number of job cards: {last_card_count}")
        
        scroll_attempt = 0
        max_scroll_attempts = 50  # Prevent infinite scrolling
        
        while scroll_attempt < max_scroll_attempts:
            scroll_attempt += 1
            
            # 4) Measure viewport height and choose an overlap (20%)
            viewport_height = int(self.driver.execute_script(
                "return Math.round(arguments[0].clientHeight);", jobs_container
            ))
            overlap = int(viewport_height * 0.20)
            scroll_amount = viewport_height - overlap

            # 5) Find current scroll and container height
            current_scroll = int(self.driver.execute_script(
                "return Math.round(arguments[0].scrollTop);", jobs_container
            ))
            container_height = int(self.driver.execute_script(
                "return Math.round(arguments[0].scrollHeight);", jobs_container
            ))

            # 6) Compute next scroll target (don't exceed bottom)
            target_scroll = min(current_scroll + scroll_amount, container_height)
            self.driver.execute_script(
                "arguments[0].scrollTo(0, arguments[1]);", 
                jobs_container, target_scroll
            )

            # 7) Wait up to 2 s for at least one new card, then wait for another 2 for rest of them to load
            try:
                WebDriverWait(self.driver, 2).until(
                    lambda drv: len(
                        jobs_container.find_elements(By.XPATH, SELECTORS["jobs"]["job_cards"])
                    ) > last_card_count
                )
                # At least one new card arrived; now enter a "stability wait" so we let the rest of the batch load
                while True:
                    time.sleep(2)
                    current_count = len(
                        jobs_container.find_elements(By.XPATH, SELECTORS["jobs"]["job_cards"])
                    )
                    if current_count > last_card_count:
                        # More cards keep coming—update last_card_count and keep waiting
                        last_card_count = current_count
                        continue
                    # If we slept 2s and saw no increase, assume batch is done
                    break

                self.logger.info(f"Loaded batch; total cards now: {last_card_count}")
                continue  # Go to the next scroll iteration

            except TimeoutException:
                # 8) If no card appeared in 2 s, check if we're truly at the bottom
                new_scroll = int(self.driver.execute_script(
                    "return Math.round(arguments[0].scrollTop);", jobs_container
                ))
                new_height = int(self.driver.execute_script(
                    "return Math.round(arguments[0].scrollHeight);", jobs_container
                ))

                # If scroll + viewport ≥ height − 5px, we're at the bottom
                if new_scroll + viewport_height >= new_height - 5:
                    self.logger.info("No additional cards detected; bottom reached.")
                    break

                # Otherwise, we're not at the bottom yet—loop again to scroll further
                continue

        # 9) Pagination check (still expect 25 on non‐last pages)
        has_next = self._has_next_page()
        
        if has_next and last_card_count != 25:
            self.logger.warning(f"Expected 25 cards on a page with next button, but found {last_card_count} cards")
        elif not has_next:
            self.logger.info(f"Last page contains {last_card_count} cards")
        else:
            self.logger.info(f"Verified: Found expected 25 cards on page")
            
        # 10) Scroll back to top for cleanliness
        self.driver.execute_script("arguments[0].scrollTo(0, 0);", jobs_container)
        time.sleep(1)
        
        final_cards = len(
            jobs_container.find_elements(By.XPATH, SELECTORS["jobs"]["job_cards"])
        )
        self.logger.info(f"Final number of job cards after scrolling: {final_cards}")

    def _get_job_cards_on_current_page(self):
        """Get all job cards on the current page."""
        # First load all job cards by scrolling
        self._load_all_job_cards()
        
        # Then find all job cards
        job_cards = self.driver.find_elements(
            By.XPATH, SELECTORS["jobs"]["job_cards"]
        )
        
        print(f"Found {len(job_cards)} job cards on current page")
        return job_cards if job_cards else []

    def _has_next_page(self) -> bool:
        """Check if there is a next page of results."""
        try:
            next_button = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["jobs"]["next_page_button"]),
                timeout=2  # Short timeout since we expect this to fail at the end
            )
            return bool(next_button and next_button.is_enabled())
        except TimeoutException:
            # This is expected when we reach the last page
            self.logger.info("Reached last page of results")
            return False
        except Exception as e:
            self.logger.error(f"Error checking for next page: {str(e)}")
            return False

    def _go_to_next_page(self):
        """Navigate to the next page of results."""
        next_button = self.browser.wait_for_clickable(
            (By.XPATH, SELECTORS["jobs"]["next_page_button"])
        )
        if next_button:
            self.browser.ensure_element_in_viewport(next_button)
            next_button.click()
            time.sleep(2)  # Wait for page to load
            return True
        return False

    def _extract_company_info(self):
        """Extract company name and LinkedIn URL from the job details."""
        try:
            company_div = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["jobs"]["company_name"])
            )
            if company_div:
                company_name = company_div.text.strip()
                company_url = company_div.get_attribute('href')
                return {"name": company_name, "url": company_url}
            return None
        except TimeoutException:
            return None

    def _extract_job_url_and_title(self):
        """Extract job title and LinkedIn URL from the job details."""
        try:
            job_title_div = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["jobs"]["job_title"])
            )
            if job_title_div:
                job_title = job_title_div.text.strip()
                job_url = job_title_div.get_attribute('href')
                return {"title": job_title, "url": job_url}
            return None
        except TimeoutException:
            return None

    def _generate_job_id(self, company_name, company_url, job_title, job_url, job_description):
        """Generate a unique job ID by hashing the job details."""
        # Combine all fields into a single string
        combined_string = f"{company_name}|{company_url}|{job_title}|{job_url}|{job_description}"
        # Create SHA-256 hash
        return hashlib.sha256(combined_string.encode()).hexdigest()

    def _extract_job_description(self):
        """Extract the job description from the current job posting."""
        try:
            job_description = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["jobs"]["job_description"])
            )
            return job_description.text if job_description else None
        except TimeoutException:
            return None

    def _get_total_job_count(self):
        """Get the total number of jobs from the results subtitle."""
        try:
            subtitle = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["jobs"]["results_count"])
            )
            if subtitle:
                # Extract number from text like "1,229 results"
                count_text = subtitle.text.strip()
                count_str = count_text.split()[0].replace(',', '')
                count = int(count_str)
                print(f"Total jobs available: {count}")
                return count
            return None
        except Exception as e:
            print(f"Error getting total job count: {str(e)}")
            return None

    def process_job_listings(self) -> bool:
        """Process all job listings and score them in real-time."""
        try:
            # Initialize tracking variables
            job_descriptions = {}
            scored_jobs = {}
            total_jobs = self._get_total_job_count()
            processed_count = 0
            failed_count = 0
            
            # Handle case where total jobs count is not available
            if total_jobs is None or total_jobs == 0:
                self.logger.warning("Could not determine total number of jobs. Will process all available jobs.")
                total_jobs = "unknown"
            
            # Use the run timestamp for all files
            jobs_file = f"data/job_descriptions_{self.run_timestamp}.json"
            scored_file = f"data/job_descriptions_scored_{self.run_timestamp}.json"
            
            self.logger.info(f"Starting job processing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info(f"Total jobs to process: {total_jobs}")
            self.logger.info(f"Raw jobs will be saved to: {jobs_file}")
            self.logger.info(f"Scored jobs will be saved to: {scored_file}")
            
            # Process jobs page by page
            page_number = 1
            while True:
                self.logger.info(f"Processing page {page_number}...")
                
                # Get all job cards on current page
                job_cards = self._get_job_cards_on_current_page()
                
                if not job_cards:
                    self.logger.info("No job cards found on current page. Ending processing.")
                    break
                
                for card in job_cards:
                    try:
                        # Click the job card to load details
                        self.browser.ensure_element_in_viewport(card)
                        card.click()
                        time.sleep(2)  # Wait for job details to load
                        
                        # Extract job information
                        company_info = self._extract_company_info()
                        job_info = self._extract_job_url_and_title()
                        job_description = self._extract_job_description()
                        
                        if not all([company_info, job_info, job_description]):
                            self.logger.warning("Skipping job - missing required information")
                            failed_count += 1
                            continue
                        
                        # Generate unique job ID
                        job_id = self._generate_job_id(
                            company_info["name"],
                            company_info["url"],
                            job_info["title"],
                            job_info["url"],
                            job_description
                        )
                        
                        # Create job data
                        job_data = {
                            "company_name": company_info["name"],
                            "company_url": company_info["url"],
                            "job_title": job_info["title"],
                            "job_url": job_info["url"],
                            "job_description": job_description,
                            "scraped_at": datetime.now().isoformat()
                        }
                        
                        # Add to job descriptions
                        job_descriptions[job_id] = job_data
                        
                        # Save raw job data
                        with open(jobs_file, 'w') as f:
                            json.dump(job_descriptions, f, indent=2)
                        
                        # Score the job immediately
                        self.logger.info(f"Scoring job: {job_info['title']} at {company_info['name']}")
                        match_score = self.job_matcher.get_match_score(job_description)
                        
                        # Create scored job data
                        scored_job = {
                            **job_data,
                            'match_score': match_score,
                            'scored_at': datetime.now().isoformat()
                        }
                        
                        # Add to scored jobs
                        scored_jobs[job_id] = scored_job
                        
                        # Save scored job data
                        with open(scored_file, 'w') as f:
                            json.dump(scored_jobs, f, indent=2)
                        
                        self.logger.info(f"Score: {match_score}/10")
                        
                        processed_count += 1
                        if total_jobs != "unknown":
                            self.logger.info(f"Processed {processed_count}/{total_jobs} jobs")
                        else:
                            self.logger.info(f"Processed {processed_count} jobs")
                    
                    except Exception as e:
                        self.logger.error(f"Error processing job card: {str(e)}")
                        failed_count += 1
                        continue
                
                # Check if there's a next page
                if not self._has_next_page():
                    break
                    
                # Go to next page
                if not self._go_to_next_page():
                    self.logger.error("Failed to navigate to next page")
                    break
                
                page_number += 1
            
            # Print final statistics
            self.logger.info(f"\nJob processing completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info(f"Total jobs processed: {processed_count}")
            self.logger.info(f"Failed jobs: {failed_count}")
            self.logger.info(f"Raw jobs saved to: {jobs_file}")
            self.logger.info(f"Scored jobs saved to: {scored_file}")
            
            return True
            
        except Exception as e:
            self.logger.exception("Fatal error during job processing")
            return False 