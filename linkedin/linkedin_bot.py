import json
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import hashlib

from config.config import (
    LINKEDIN_LOGIN_URL,
    LINKEDIN_JOBS_URL,
    LINKEDIN_EMAIL,
    LINKEDIN_PASSWORD,
    SELECTORS,
    LOGIN_TIMEOUT
)
from .browser_manager import BrowserManager
import time

class LinkedInBot:
    def __init__(self):
        self.browser = BrowserManager()
        self.driver = None
        self.settings = self._load_settings()

    def _load_settings(self):
        """Load settings from Settings.json file."""
        try:
            with open('config/Settings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: Settings.json not found. Using default settings.")
            return {
                "job_keywords": [],
                "locations": [],
                "universities": [],
                "custom_message": "",
                "prompt": ""
            }

    def _format_search_query(self, keywords):
        """Format keywords with AND operator for LinkedIn search."""
        return " AND ".join(f'{keyword}' for keyword in keywords)

    def start(self):
        """Initialize the browser and start the bot."""
        self.driver = self.browser.initialize_browser()
        return self

    def login(self):
        """Log in to LinkedIn."""
        try:
            # Navigate to login page
            self.driver.get(LINKEDIN_LOGIN_URL)
            
            # Wait for and fill in email
            email_field = self.browser.wait_for_element(
                (By.ID, SELECTORS["login"]["email_field"]),
                LOGIN_TIMEOUT
            )
            if email_field:
                email_field.send_keys(LINKEDIN_EMAIL)
            
            # Wait for and fill in password
            password_field = self.browser.wait_for_element(
                (By.ID, SELECTORS["login"]["password_field"]),
                LOGIN_TIMEOUT
            )
            if password_field:
                password_field.send_keys(LINKEDIN_PASSWORD)
            
            # Click submit button
            submit_button = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["login"]["submit_button"]),
                LOGIN_TIMEOUT
            )
            if submit_button:
                submit_button.click()
            
            # Wait for feed to load (indicating successful login)
            feed_button = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["login"]["feed_button"]),
                LOGIN_TIMEOUT
            )
            
            return bool(feed_button)
            
        except TimeoutException as e:
            print(f"Login failed: {str(e)}")
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
        time.sleep(2)  # Wait for results to update
        print("[Date Filter] ✅ Filter applied")
        return True

    def search_jobs(self, job_title=None, location=None):
        """Search for jobs with given criteria.
        
        Args:
            job_title (str, optional): Override job title from settings
            location (str, optional): Override location from settings
        """
        try:
            # Navigate to jobs page
            self.driver.get(LINKEDIN_JOBS_URL)
            
            # Use provided job title or combine keywords from settings
            search_query = job_title if job_title else self._format_search_query(self.settings["job_keywords"])
            
            # Wait for and fill in job title
            search_input = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["jobs"]["search_input"])
            )
            if search_input:
                search_input.clear()
                search_input.send_keys(search_query)
            
            # Use provided location or first location from settings
            location_to_use = location if location else self.settings["locations"][0] if self.settings["locations"] else "Worldwide"
            print(f"Location to use: {location_to_use}")
            
            # Wait for and fill in location
            location_input = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["jobs"]["location_input"])
            )
            if location_input and location_to_use:
                location_input.clear()
                location_input.send_keys(location_to_use)
                # Add a small delay to allow suggestions to appear
                time.sleep(1)
                location_input.send_keys(Keys.RETURN)
            
            # Apply date filter if specified in settings
            if "date_posted_filter" in self.settings:
                try:
                    if not self._apply_date_filter():
                        print("Warning: Failed to apply date filter, continuing with unfiltered results")
                except Exception as e:
                    print(f"Error during date filter application: {str(e)}")
                    print("Continuing with unfiltered results")
            
            # Wait for job results to load
            job_cards = self.browser.wait_for_element(
                (By.XPATH, SELECTORS["jobs"]["job_cards"])
            )
            
            return bool(job_cards)
            
        except TimeoutException as e:
            print(f"Job search failed: {str(e)}")
            return False

    def quit(self):
        """Close the browser and clean up."""
        self.browser.quit()

    def _load_all_job_cards(self):
        """Scroll through the jobs container to load all available job cards."""
        print("\nLoading all job cards...")
        
        # 1) Wait for the scroll sentinel to appear
        scroll_sentinel = self.browser.wait_for_element(
            (By.XPATH, SELECTORS["jobs"]["scroll_sentinel"])
        )
        if not scroll_sentinel:
            print("❌ Could not find scroll sentinel")
            return
            
        # 2) Find the container (parent of the sentinel)
        jobs_container = scroll_sentinel.find_element(By.XPATH, "./..")
        if not jobs_container:
            print("❌ Could not find jobs container")
            return
            
        print("Found jobs container, starting to scroll...")
        
        # 3) Count how many cards are currently in that container
        last_card_count = len(
            jobs_container.find_elements(By.XPATH, SELECTORS["jobs"]["job_cards"])
        )
        print(f"Initial number of job cards: {last_card_count}")
        
        while True:
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
                        print(f"    Intermediate batch: {current_count - last_card_count} more cards (total so far: {current_count})")
                        last_card_count = current_count
                        continue
                    # If we slept 2s and saw no increase, assume batch is done
                    break

                print(f"Loaded batch; total cards now: {last_card_count}")
                continue  # Go to the next scroll iteration

            except TimeoutException:
                # 8) If no card appeared in 3 s, check if we're truly at the bottom
                new_scroll = int(self.driver.execute_script(
                    "return Math.round(arguments[0].scrollTop);", jobs_container
                ))
                new_height = int(self.driver.execute_script(
                    "return Math.round(arguments[0].scrollHeight);", jobs_container
                ))

                # If scroll + viewport ≥ height − 5px, we're at the bottom
                if new_scroll + viewport_height >= new_height - 5:
                    print("No additional cards detected; bottom reached.")
                    break

                # Otherwise, we're not at the bottom yet—loop again to scroll further
                continue

        # 9) Pagination check (still expect 25 on non‐last pages)
        has_next = self._has_next_page()
        
        if has_next and last_card_count != 25:
            print(f"⚠️ Warning: Expected 25 cards on a page with next button, but found {last_card_count} cards")
        elif not has_next:
            print(f"Last page contains {last_card_count} cards")
        else:
            print(f"✅ Verified: Found expected 25 cards on page")
            
        # 10) Scroll back to top for cleanliness
        self.driver.execute_script("arguments[0].scrollTo(0, 0);", jobs_container)
        time.sleep(1)
        
        final_cards = len(
            jobs_container.find_elements(By.XPATH, SELECTORS["jobs"]["job_cards"])
        )
        print(f"Final number of job cards after scrolling: {final_cards}")

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

    def _has_next_page(self):
        """Check if there is a next page of results."""
        next_button = self.browser.wait_for_element(
            (By.XPATH, SELECTORS["jobs"]["next_page_button"])
        )
        return bool(next_button and next_button.is_enabled())

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
                (By.XPATH, "//div[contains(@class, 'job-details-jobs-unified-top-card__company-name')]//a")
            )
            if company_div:
                company_name = company_div.text.strip()
                company_url = company_div.get_attribute('href')
                return company_name, company_url
            return None, None
        except TimeoutException:
            return None, None

    def _extract_job_url_and_title(self):
        """Extract job title and LinkedIn URL from the job details."""
        try:
            job_title_div = self.browser.wait_for_element(
                (By.XPATH, "//div[contains(@class, 'job-details-jobs-unified-top-card__job-title')]//a")
            )
            if job_title_div:
                job_title = job_title_div.text.strip()
                job_url = job_title_div.get_attribute('href')
                return job_title, job_url
            return None, None
        except TimeoutException:
            return None, None

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
                (By.XPATH, "//div[contains(@class, 'jobs-search-results-list__subtitle')]//span")
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

    def process_job_listings(self):
        """Process all job listings across all pages."""
        all_job_descriptions = []
        page_number = 1
        
        # Get total job count at the start
        total_jobs = self._get_total_job_count()
        if not total_jobs:
            print("❌ Could not determine total number of jobs")
            return all_job_descriptions

        while True:
            print(f"\nProcessing page {page_number}...")
            
            # Get all job cards on current page
            job_cards = self._get_job_cards_on_current_page()
            if not job_cards:
                print("No job cards found on this page.")
                break

            # Process each job card
            for index, job_card in enumerate(job_cards, 1):
                try:
                    # Scroll job card into view and click
                    self.browser.ensure_element_in_viewport(job_card)
                    print("job_card.text.strip(): ", job_card.text.strip().split('\n')[0])
                    job_title = job_card.text.strip().split('\n')[0]
                    print(f"\nProcessing job {index}/{len(job_cards)}: {job_title}")
                    
                    job_card.click()
                    time.sleep(1)  # Wait for job details to load

                    # Extract all job information
                    company_name, company_url = self._extract_company_info()
                    job_title, job_url = self._extract_job_url_and_title()
                    job_description = self._extract_job_description()

                    if all([company_name, company_url, job_title, job_url, job_description]):
                        # Generate unique job ID including job description
                        job_id = self._generate_job_id(company_name, company_url, job_title, job_url, job_description)
                        
                        all_job_descriptions.append({
                            'job_id': job_id,
                            'company_name': company_name,
                            'company_url': company_url,
                            'job_title': job_title,
                            'job_url': job_url,
                            'description': job_description
                        })
                        print("✅ Successfully extracted job information")
                    else:
                        print("❌ Failed to extract complete job information")

                except Exception as e:
                    print(f"Error processing job card: {str(e)}")
                    continue

            # Check if we've processed all jobs
            if len(all_job_descriptions) >= total_jobs:
                print(f"\n✅ Successfully processed all {total_jobs} jobs!")
                break

            # Check if there's a next page
            if not self._has_next_page():
                print("\nReached last page of results.")
                break

            # Go to next page
            if not self._go_to_next_page():
                print("\nFailed to navigate to next page.")
                break

            page_number += 1

        # Validate total count
        if len(all_job_descriptions) != total_jobs:
            print(f"\n⚠️ Warning: Expected {total_jobs} jobs but processed {len(all_job_descriptions)} jobs")
            print("This might indicate some jobs were missed")
        else:
            print(f"\n✅ Successfully processed all {total_jobs} jobs!")

        return all_job_descriptions 