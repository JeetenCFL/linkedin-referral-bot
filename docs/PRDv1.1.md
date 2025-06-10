📄 Product Requirements Document (PRD)

Project Name: LinkedIn Job Automation Bot
Owner: [Your Name]
Date: [Today's Date]
Version: 1.1

⸻

🧠 1. Executive Summary

This is a personal-use Python automation project that interacts with LinkedIn to streamline job searching and outreach. The bot logs into LinkedIn, searches for jobs using user-defined filters, evaluates job descriptions via an LLM to check for relevance, and then uses LinkedIn's search functionality to find relevant contacts at target companies. The search is filtered by company, role, and optionally shared university connections. The bot then sends personalized connection requests to these contacts with custom messages. All interactions are logged for future reference.

⸻

🎯 2. Goals & Objectives
	•	Automate the repetitive job search and networking process.
	•	Filter job postings using AI based on semantic fit to personal career goals.
	•	Reach out to relevant employees at target companies with custom messages.
	•	Track the outreach history for future reference.
	•	Learn and apply:
		•	Basic architecture/design principles
		•	Selenium-based browser automation
		•	OpenAI API integration
		•	Modular project structure
		•	GitHub project tracking and versioning

⸻

📋 3. Functional Requirements (FR)

ID	Description
FR1	Log into LinkedIn with user credentials securely.
FR2	Search for jobs using keyword and location filters.
FR3	For each job: extract job title, description, and company info.
FR4	Use an LLM to determine if the job is relevant.
FR5	For relevant jobs, use LinkedIn's search functionality to find contacts:
	•	Filter by company name
	•	Filter by role/title
	•	Optionally filter by shared university
FR6	Send a connection request to identified contacts with a custom message.
FR7	Log the job URL, company name, and contacted people to a tracking system.
FR8	Notify user via email if automation fails or is interrupted (e.g., 2FA). (future)

⸻

⚙️ 4. Non-Functional Requirements (NFR)
	•	Simplicity: Keep design minimal yet robust; avoid overengineering.
	•	Modularity: All configuration (filters, university names, prompts) is externalized.
	•	Scalability: Not designed for scale, but should handle light, automated personal use.
	•	Resilience: Manual override fallback and failure notifications.
	•	Maintainability: Easy to update XPaths/selectors or config.
	•	Privacy/Security: No sensitive data hardcoded; use .env.

⸻

🏗️ 5. Architecture Overview

📌 Components
	•	Config Layer
		•	config/config.py: Browser settings, selectors, and constants
		•	config/settings.json: User preferences and filters
		•	.env: Sensitive data (credentials, API keys)
	
	•	Automation Layer
		•	linkedin/browser_manager.py: Selenium browser management
		•	linkedin/linkedin_bot.py: Core LinkedIn interaction logic
	
	•	AI Layer
		•	linkedin/ai_matcher.py: OpenAI integration for job matching
		•	linkedin/job_scorer.py: Job processing and scoring
	
	•	Control Layer
		•	main.py: Project orchestration and entry point

⸻

🧩 6. Design Decisions

Decision	Rationale
Use Python only	Core skillset; no unnecessary tech complexity
Use Selenium	Precise control over browser automation
OpenAI API in JSON mode	More reliable, structured outputs
JSON file storage	Simple, portable solution for job data storage
Use .env + settings.json	Secure separation of secrets and dynamic input
Focus on robust minimalism	Avoid premature optimization; optimize for learning

⸻

🧱 7. Project Structure

├── browser/				  # where chrome for testing lives
│   ├── chrome-headless-shell-mac-arm64
│   ├── chrome-headless-shell-mac-arm64.zip
│   ├── chrome-mac-arm64
│   ├── chrome-mac-arm64.zip
│   ├── chromedriver-mac-arm64
│   └── chromedriver-mac-arm64.zip
│
├── linkedin-referral-bot/
│   ├── config/
│   │   ├── config.py          # Browser settings and constants
│   │   ├── settings.json      # User preferences
│   │   └── resume.pdf         # User's resume for matching
│   │
│   ├── linkedin/
│   │   ├── browser_manager.py # Browser automation
│   │   ├── linkedin_bot.py    # Core LinkedIn logic
│   │   ├── ai_matcher.py      # OpenAI integration
│   │   └── job_scorer.py      # Job processing
│   │
│   ├── docs/
│   │   └── PRDv1.1.md        # This document
│   │
│   ├── main.py               # Project entry point
│   ├── requirements.txt      # Python dependencies
│   ├── README.md            # Project documentation
│   ├── .env                 # Secrets (LinkedIn login, API keys)
│   └── .gitignore          # Git ignore rules

⸻

🚧 8. Implementation Phases

✅ Phase 1: Basic Automation (Completed)
	•	Login
	•	Job search
	•	Click job + extract description

✅ Phase 2: AI Filtering (Completed)
	•	Call OpenAI API with job description
	•	Classify job as relevant or not
	•	Score and save job matches

🔄 Phase 3: People Search & Outreach (In Progress)
	•	Implement LinkedIn search with filters:
		•	Company filter
		•	Role/title filter
		•	University filter (optional)
	•	Send personalized connection requests
	•	Track outreach attempts

🔜 Phase 4: Logging & Notification
	•	Implement robust logging system
	•	Email alert on failures (e.g., 2FA triggered)

⸻

💡 9. Open Questions / Risks
	•	LinkedIn DOM may change → selectors must be easily editable
	•	Captchas and 2FA may interrupt bot flow
	•	Email notification module needs a sender address (Gmail, Mailgun, etc.)
	•	Rate limiting for LinkedIn search and connection requests
	•	Prompt tuning for OpenAI will be trial-and-error initially
	•	Handling of LinkedIn's search result pagination

⸻

🌐 10. GitHub & Documentation
	•	Project will be logged publicly on GitHub
	•	Every feature implemented will be committed with descriptive messages
	•	A README.md will include:
		•	Project overview
		•	Setup instructions
		•	Usage guide
		•	Roadmap / TODO 