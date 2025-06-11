import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config.logging_config import log_manager

class SessionManager:
    def __init__(self):
        self.logger = log_manager.get_logger(__name__)
        self.cookies_dir = Path('data/cookies')
        self.cookies_file = self.cookies_dir / 'linkedin_cookies.json'
        self._ensure_cookies_dir()

    def _ensure_cookies_dir(self):
        """Create cookies directory if it doesn't exist."""
        self.cookies_dir.mkdir(parents=True, exist_ok=True)

    def save_cookies(self, cookies: list) -> bool:
        """Save cookies to file with timestamp."""
        try:
            # Add timestamp to cookies data
            cookies_data = {
                'timestamp': datetime.now().isoformat(),
                'cookies': cookies
            }
            
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies_data, f)
            
            self.logger.info("Successfully saved cookies")
            return True
        except Exception as e:
            self.logger.error(f"Error saving cookies: {str(e)}")
            return False

    def load_cookies(self) -> Optional[list]:
        """Load cookies from file if they exist and are not expired."""
        try:
            if not self.cookies_file.exists():
                self.logger.info("No cookies file found")
                return None

            with open(self.cookies_file, 'r') as f:
                cookies_data = json.load(f)

            # Check if cookies are expired (older than 24 hours)
            saved_time = datetime.fromisoformat(cookies_data['timestamp'])
            if datetime.now() - saved_time > timedelta(hours=24):
                self.logger.info("Cookies are expired")
                return None

            self.logger.info("Successfully loaded cookies")
            return cookies_data['cookies']
        except Exception as e:
            self.logger.error(f"Error loading cookies: {str(e)}")
            return None

    def clear_cookies(self) -> bool:
        """Clear saved cookies."""
        try:
            if self.cookies_file.exists():
                self.cookies_file.unlink()
            self.logger.info("Successfully cleared cookies")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing cookies: {str(e)}")
            return False 