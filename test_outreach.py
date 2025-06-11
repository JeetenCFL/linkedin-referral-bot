from linkedin.outreach_manager import OutreachManager
from config.logging_config import log_manager
from config.config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import os
import time

# Load environment variables
env_file = find_dotenv()
if not env_file:
    raise FileNotFoundError(
        "No .env file found. Please create a .env file with the following variables:\n"
        "LINKEDIN_EMAIL=your_email@example.com\n"
        "LINKEDIN_PASSWORD=your_password\n"
        "OPENAI_API_KEY=your_openai_api_key"
    )

load_dotenv(env_file, override=True)

# Get credentials
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
    raise ValueError(
        "LinkedIn credentials not found in .env file. Please ensure the following variables are set:\n"
        "LINKEDIN_EMAIL=your_email@example.com\n"
        "LINKEDIN_PASSWORD=your_password\n"
        "OPENAI_API_KEY=your_openai_api_key"
    )

def login_to_linkedin(outreach):
    """Handle LinkedIn login."""
    logger = log_manager.get_logger(__name__)
    
    try:
        # Navigate to login page
        outreach.driver.get("https://www.linkedin.com/login")
        logger.info("Navigated to LinkedIn login page")
        
        # Wait for and fill in email
        email_field = outreach.browser.wait_for_element(
            (By.ID, "username"),
            timeout=30
        )
        if not email_field:
            logger.error("Email field not found")
            return False
        
        email_field.send_keys(LINKEDIN_EMAIL)
        logger.info("Entered email")
        
        # Wait for and fill in password
        password_field = outreach.browser.wait_for_element(
            (By.ID, "password"),
            timeout=30
        )
        if not password_field:
            logger.error("Password field not found")
            return False
        
        password_field.send_keys(LINKEDIN_PASSWORD)
        logger.info("Entered password")
        
        # Click submit button
        submit_button = outreach.browser.wait_for_element(
            (By.XPATH, "//button[@type='submit']"),
            timeout=30
        )
        if not submit_button:
            logger.error("Submit button not found")
            return False
        
        submit_button.click()
        logger.info("Clicked submit button")
        
        # Wait for feed to load (indicating successful login)
        feed_button = outreach.browser.wait_for_element(
            (By.XPATH, "//a[contains(@href, '/feed/')]"),
            timeout=30
        )
        
        if not feed_button:
            logger.error("Feed button not found after login attempt")
            return False
            
        logger.info("Successfully logged in to LinkedIn")
        
        # Save session after successful login
        if outreach.save_session():
            logger.info("Successfully saved session")
        else:
            logger.warning("Failed to save session")
            
        return True
        
    except TimeoutException as e:
        logger.error(f"Login timeout: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        return False

def main():
    logger = log_manager.get_logger(__name__)
    
    # Initialize the outreach manager
    outreach = OutreachManager()
    
    try:
        # Start the browser
        logger.info("Starting browser...")
        if not outreach.start():
            logger.error("Failed to start browser")
            return
        
        # Check if we need to login
        feed_button = outreach.browser.wait_for_element(
            (By.XPATH, "//a[contains(@href, '/feed/')]"),
            timeout=10
        )
        
        if not feed_button:
            # Login to LinkedIn if session restoration failed
            logger.info("No active session found, attempting to log in...")
            if not login_to_linkedin(outreach):
                logger.error("Failed to log in to LinkedIn")
                return
        else:
            logger.info("Using existing session")
        
        # Get the first job ID from the scored jobs
        job_ids = list(outreach.scored_jobs.keys())
        if not job_ids:
            logger.error("No scored jobs found")
            return
        
        # Process outreach for the first job
        job_id = job_ids[0]
        logger.info(f"Processing outreach for job ID: {job_id}")
        
        if outreach.process_job_outreach(job_id):
            logger.info("Successfully completed outreach process")
        else:
            logger.error("Failed to complete outreach process")
            
    except KeyboardInterrupt:
        logger.info("Shutting down due to keyboard interrupt...")
    except Exception as e:
        logger.exception("An unexpected error occurred")
    finally:
        logger.info("Cleaning up and closing browser...")
        outreach.quit()

if __name__ == "__main__":
    main() 