from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config.config import CHROME_BINARY_PATH, CHROMEDRIVER_PATH, DEFAULT_TIMEOUT
import time

class BrowserManager:
    def __init__(self):
        self.driver = None
        self.wait = None

    def initialize_browser(self):
        """Initialize the Chrome browser with custom options."""
        options = Options()
        options.binary_location = CHROME_BINARY_PATH
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Prevent Chrome from pausing JS timers or throttling-
        # invisible‐page rendering when window is hidden/minimized.
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")

        # Set a custom user agent to mimic a regular Chrome browser on macOS
        # This helps avoid detection as an automated browser by websites
        # The user agent string identifies the browser as:
        # - "Mozilla/5.0" is a legacy identifier kept for compatibility (not the actual browser)
        # - Chrome version 122.0.0.0
        # - Running on macOS (Macintosh; Intel Mac OS X 10_15_7)
        # - Using WebKit/537.36 rendering engine
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

        service = Service(executable_path=CHROMEDRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, DEFAULT_TIMEOUT)
        return self.driver

    def wait_for_element(self, locator, timeout=DEFAULT_TIMEOUT):
        """Wait for an element to be present in the DOM."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            print(f"Timeout waiting for element: {locator}")
            return None
        except Exception as e:
            print(f"Unexpected error while waiting for element {locator}: {str(e)}")
            return None

    def wait_for_visible(self, locator, timeout=DEFAULT_TIMEOUT):
        """Wait for an element to be visible (present and displayed)."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return element
        except TimeoutException:
            print(f"Timeout waiting for visible element: {locator}")
            return None
        except Exception as e:
            print(f"Unexpected error while waiting for visible element {locator}: {str(e)}")
            return None

    def wait_for_clickable(self, locator, timeout=DEFAULT_TIMEOUT):
        """Wait for an element to be clickable (present, visible, and enabled)."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return element
        except TimeoutException:
            print(f"Timeout waiting for clickable element: {locator}")
            return None
        except Exception as e:
            print(f"Unexpected error while waiting for clickable element {locator}: {str(e)}")
            return None

    def ensure_element_in_viewport(self, element):
        """Ensure an element is in the viewport before interaction."""
        try:
            # Check if element is in viewport
            is_in_viewport = self.driver.execute_script("""
                var elem = arguments[0];
                var rect = elem.getBoundingClientRect();
                return (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                );
            """, element)
            
            if not is_in_viewport:
                # Scroll element into view if it's not in viewport
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.5)  # Short wait for scroll to complete
        except Exception as e:
            print(f"Error ensuring element in viewport: {str(e)}")

    def quit(self):
        """Close the browser and clean up."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None