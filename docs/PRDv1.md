📄 Product Requirements Document (PRD)

Project Name: LinkedIn Job Automation Bot
Owner: [Your Name]
Date: [Today’s Date]
Version: 1.0

⸻

🧠 1. Executive Summary

This is a personal-use Python automation project that interacts with LinkedIn to streamline job searching and outreach. The bot logs into LinkedIn, searches for jobs using user-defined filters, evaluates job descriptions via an LLM to check for relevance, navigates to the company’s People tab, and sends personalized connection requests to potentially useful contacts based on criteria like shared university. It also logs successful interactions to a Google Sheet for tracking.

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
FR5	If relevant, go to the company page and open the People tab.
FR6	Filter and find relevant people (based on shared university, roles — to be defined).
FR7	Send a connection request to those people with a custom message.
FR8	Log the job URL, company name, and contacted people to a Google Sheet.
FR9	Notify user via email if automation fails or is interrupted (e.g., 2FA). (future)


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
settings.json, .env for dynamic parameters (filters, messages, API keys)
	•	Automation Layer
linkedin/bot.py using Selenium for:
	•	Logging in
	•	Job search
	•	Navigation to company/people
	•	AI Layer
job_classifier.py (planned): OpenAI integration for job filtering
	•	Logging Layer
logger.py (planned): Google Sheets API to track interactions
	•	Control Layer
main.py orchestration script

⸻

🧩 6. Design Decisions

Decision	Rationale
Use Python only	Core skillset; no unnecessary tech complexity
Use Selenium	Precise control over browser automation
OpenAI API in JSON mode	More reliable, structured outputs
Google Sheets over Docs	Easier structured logging for outreach history
Use .env + settings.json	Secure separation of secrets and dynamic input
Focus on robust minimalism	Avoid premature optimization; optimize for learning


⸻

🧱 7. Project Structure

linkedin-automation-bot/
│
├── browser/				  # where chrome for testing lives
│   ├── chrome-headless-shell-mac-arm64
│   ├── chrome-headless-shell-mac-arm64.zip
│   ├── chrome-mac-arm64
│   ├── chrome-mac-arm64.zip
│   ├── chromedriver-mac-arm64
│   └── chromedriver-mac-arm64.zip
│
├── config/
│   └── settings.json         # Filters, universities, messages, etc.
│
├── linkedin/
│   └── bot.py                # Core Selenium logic
│
├── main.py                   # Project entry point
├── requirements.txt
├── README.md
├── .env                      # Secrets (LinkedIn login, API keys)
└── .gitignore                # To be added


⸻

🚧 8. Implementation Phases

✅ Phase 1: Basic Automation (in progress)
	•	Login
	•	Job search
	•	Click job + extract description
	•	Navigate to company → people tab

🔜 Phase 2: AI Filtering
	•	Call OpenAI API with job description
	•	Classify job as relevant or not

🔜 Phase 3: People Filtering & Outreach
	•	Identify contacts via shared university or role match
	•	Send personalized connection requests

🔜 Phase 4: Logging & Notification
	•	Append results to Google Sheet
	•	Email alert on failures (e.g., 2FA triggered)

⸻

💡 9. Open Questions / Risks
	•	LinkedIn DOM may change → selectors must be easily editable
	•	Captchas and 2FA may interrupt bot flow
	•	Email notification module needs a sender address (Gmail, Mailgun, etc.)
	•	Exact logic for “relevant person” detection is currently undefined
	•	Prompt tuning for OpenAI will be trial-and-error initially

⸻

🌐 10. GitHub & Documentation
	•	Project will be logged publicly on GitHub
	•	Every feature implemented will be committed with descriptive messages
	•	A README.md will include:
	•	Project overview
	•	Setup instructions
	•	Usage guide
	•	Roadmap / TODO