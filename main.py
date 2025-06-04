from linkedin.linkedin_bot import LinkedInBot
import time
import json
from datetime import datetime

def save_job_descriptions(job_descriptions):
    """Save job descriptions to a JSON file with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"job_descriptions_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(job_descriptions, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(job_descriptions)} job descriptions to {filename}")

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
            
            # Wait a bit for the page to stabilize
            time.sleep(3)
            
            # Search for jobs using settings from Settings.json
            print("Searching for jobs using settings...")
            if bot.search_jobs():
                print("Successfully found job listings!")
                
                # Process all job listings
                print("\nStarting to process job listings...")
                job_descriptions = bot.process_job_listings()
                
                # Save the results
                if job_descriptions:
                    save_job_descriptions(job_descriptions)
                else:
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
