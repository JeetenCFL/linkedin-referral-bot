from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
BROWSER_DIR = BASE_DIR.parent / "browser"

# Browser paths
CHROME_BINARY_PATH = str(BROWSER_DIR / "chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing")
CHROMEDRIVER_PATH = str(BROWSER_DIR / "chromedriver-mac-arm64/chromedriver")

# LinkedIn credentials
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# URLs
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
LINKEDIN_JOBS_URL = "https://www.linkedin.com/jobs/"

# Timeouts (in seconds)
DEFAULT_TIMEOUT = 10
LOGIN_TIMEOUT = 30

# Selectors
SELECTORS = {
    "login": {
        "email_field": "username",  # ID selector for email input field
        "password_field": "password",  # ID selector for password input field
        "submit_button": "//button[@type='submit']",  # XPath for login submit button
        "feed_button": "//a[contains(@href, '/feed/')]"  # XPath for feed button (indicates successful login)
    },
    "jobs": {
        # Search and Filter Elements
        "search_input": "//input[contains(@aria-label, 'Search by title, skill, or company')]",  # XPath for job search input
        "location_input": "//input[contains(@aria-label, 'City, state, or zip code')]",  # XPath for location input
        "date_posted_button": "//button[contains(@aria-label, 'Date posted filter. Clicking this button displays all Date posted filter options.')]",  # XPath for date filter dropdown
        "date_posted_options": {
            "past_24_hours": "//input[@id='timePostedRange-r86400']",  # XPath for "Past 24 hours" option
            "past_week": "//input[@id='timePostedRange-r604800']",  # XPath for "Past week" option
            "past_month": "//input[@id='timePostedRange-r2592000']",  # XPath for "Past month" option
            "any_time": "//input[@id='timePostedRange-']"  # XPath for "Any time" option
        },
        "apply_filter_button": "//button[contains(@class, 'artdeco-button--primary') and contains(@aria-label, 'Apply current filter')]",  # XPath for apply filter button
        
        # Job List Elements
        "job_cards": "//div[contains(@class, 'job-card-list--underline-title-on-hover')]",  # XPath for job listing cards
        "scroll_sentinel": "//div[@data-results-list-top-scroll-sentinel]",  # XPath for scroll sentinel (used for infinite scroll)
        "next_page_button": "//button[contains(@class, 'jobs-search-pagination__button--next')]",  # XPath for next page button
        
        # Job Detail Elements
        "job_description": "//div[contains(@class, 'jobs-description-content__text')]",  # XPath for job description text
        "company_name": "//div[contains(@class, 'job-details-jobs-unified-top-card__company-name')]//a",  # XPath for company name link
        "job_title": "//div[contains(@class, 'job-details-jobs-unified-top-card__job-title')]//a",  # XPath for job title link
        "results_count": "//div[contains(@class, 'jobs-search-results-list__subtitle')]//span"  # XPath for total results count
    }
} 