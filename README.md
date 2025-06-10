# LinkedIn Referral Automation Bot 🤖

This is a personal-use project built in Python to automate LinkedIn job search and outreach. The bot performs browser automation using Selenium, filters job listings using AI (OpenAI API), and navigates through LinkedIn to identify relevant people at target companies for referral requests for filtered jobs.

---

## 📌 Project Goals

- Automate the job search and filtering process
- Identify potential referrers from target companies and jobs
- Use AI to semantically filter jobs
- Log outreach attempts in a Google Sheet
- Modular, configurable, and well-documented codebase

---

## 🛠️ Current Status

This repository currently contains the base code that navigates to the LinkedIn Jobs page, applies the specified filters and features from the settings.json file, matches each filtered job description with the resume located in the config folder, generates a relevance score, and saves all results in a JSON file.

---

## 🧪 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/LINKEDIN_REFERRAL_AUTOMATION.git
cd LINKEDIN_REFERRAL_AUTOMATION
```

### 2. Create Conda Environment

```bash
conda create -n linkedin_referral_bot python=3.10
conda activate linkedin_referral_bot
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🧰 Chrome & ChromeDriver Setup

### Download Chrome for Testing and ChromeDriver

Download the appropriate version and matching ChromeDriver for your platform from the [Chrome for Testing download page](https://googlechromelabs.github.io/chrome-for-testing/).

Extract and place it inside:

```
../browser/
```
You could check out the PRDv1 file in docs for exact structure that is assumed.
---

## 🔧 Basic Test Script

This is a minimal script to confirm that Selenium can launch a Chrome browser.

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

CHROME_BINARY_PATH = "./browser/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
CHROMEDRIVER_PATH = "./browser/chromedriver-mac-arm64/chromedriver"

options = Options()
options.binary_location = CHROME_BINARY_PATH
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--headless=new")  # Optional

service = Service(executable_path=CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.google.com")
print(driver.title)
driver.quit()
```

---

## 📂 Project Structure (WIP)

```
browser/                      # Chrome & ChromeDriver
    ├── linkedin-referral-bot/
        ├── config/                       # Dynamic config (filters, prompts)
        ├── docs/                         # Documentation (e.g. PRD.md)
        │   └── PRDv1.md
        ├── linkedin/                     # Automation code
        ├── main.py                       # Project entry point
        ├── test_component.ipynb          # For quick testing of features
        ├── requirements.txt
        ├── .env                          # Secrets (not committed)
        └── README.md
```

---

## 🔐 Secrets Management

Create a `.env` file:

```
LINKEDIN_EMAIL=your_email
LINKEDIN_PASSWORD=your_password
OPENAI_API_KEY=your_openai_key
```

---

## 📈 Coming Soon

- Company → People page traversal
- Personalized message delivery
- Google Sheet logging
- Email notification on failure

---

## 📦 License

MIT (or your preferred license)

---