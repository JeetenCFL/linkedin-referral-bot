from linkedin.linkedin_bot import LinkedInBot
import time

def main():
    # Initialize the bot
    bot = LinkedInBot()
    
    try:
        # Start the browser
        bot.start()
        
        # Attempt to login
        print("Attempting to log in to LinkedIn...")
        if bot.login():
            print("Successfully logged in!")
         
            # Search for jobs using settings from Settings.json
            print("Searching for jobs using settings...")
            if bot.search_jobs():
                print("Successfully found job listings!")
                
                # Process all job listings (includes real-time scoring)
                print("\nStarting to process job listings...")
                job_descriptions, jobs_file = bot.process_job_listings()
                
                if not job_descriptions:
                    print("No job descriptions were collected.")
                
                print("\nBrowser will remain open. Press Enter to exit when you're done.")
                input()  # Wait for user input before closing
            else:
                print("Failed to find job listings.")
        else:
            print("Failed to log in to LinkedIn.")
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        bot.quit()

if __name__ == "__main__":
    main()
