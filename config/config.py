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
        "email_field": "username",
        "password_field": "password",
        "submit_button": "//button[@type='submit']",
        "feed_button": "//a[contains(@href, '/feed/')]"
    },
    "jobs": {
        "search_input": "//input[contains(@aria-label, 'Search by title, skill, or company')]",
        "location_input": "//input[contains(@aria-label, 'City, state, or zip code')]",
        "search_button": "//button[contains(@type, 'submit')]",
        "job_cards": "//div[contains(@class, 'job-card-list--underline-title-on-hover')]",
        "date_posted_button": "//button[contains(@aria-label, 'Date posted filter. Clicking this button displays all Date posted filter options.')]",
        "date_posted_options": {
            "past_24_hours": "//input[@id='timePostedRange-r86400']",
            "past_week": "//input[@id='timePostedRange-r604800']",
            "past_month": "//input[@id='timePostedRange-r2592000']",
            "any_time": "//input[@id='timePostedRange-']"
        },
        "apply_filter_button": "//button[contains(@class, 'artdeco-button--primary') and contains(@aria-label, 'Apply current filter')]",
        "scroll_sentinel": "//div[@data-results-list-top-scroll-sentinel]",
        "next_page_button": "//button[contains(@class, 'jobs-search-pagination__button--next')]",
        "job_description": "//div[contains(@class, 'jobs-description-content__text')]"
    }
} 