import json
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
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
                return False

            # Step 2: Select the date filter option
            if not self._select_date_filter_option():
                return False

            # Step 3: Apply the filter
            if not self._click_apply_filter_button():
                return False

            return True

        except TimeoutException as e:
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
            location_to_use = location if location else self.settings["locations"][0] if self.settings["locations"] else ""
            
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
                self._apply_date_filter()
            
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