from linkedin.linkedin_bot import LinkedInBot
import time
from config.logging_config import log_manager

def main():
    logger = log_manager.get_logger(__name__)
    
    # Initialize the bot
    bot = LinkedInBot()
    
    try:
        # Start the browser
        logger.info("Starting browser...")
        bot.start()
        
        # Attempt to login
        logger.info("Attempting to log in to LinkedIn...")
        if not bot.login():
            logger.error("Failed to log in to LinkedIn")
            return
        
        logger.info("Successfully logged in!")
        
        # Search for jobs using settings from Settings.json
        logger.info("Searching for jobs using settings...")
        if not bot.search_jobs():
            logger.error("Failed to find job listings")
            return
        
        logger.info("Successfully found job listings!")
        
        # Process job listings
        logger.info("Starting to process job listings...")
        if not bot.process_job_listings():
            logger.error("Failed to process job listings")
            return
        
        logger.info("Job processing completed successfully")

        ## Reaching out logic here
        logger.info("Browser will remain open. Press Enter to exit when you're done.")
        input()  # Wait for user input before closing
            
    except KeyboardInterrupt:
        logger.info("Shutting down due to keyboard interrupt...")
    except Exception as e:
        logger.exception("An unexpected error occurred")
    finally:
        logger.info("Cleaning up and closing browser...")
        bot.quit()

if __name__ == "__main__":
    main()
