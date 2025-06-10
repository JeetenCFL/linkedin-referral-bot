import logging
import os
from datetime import datetime
from typing import Optional

class LogManager:
    _instance = None
    _initialized = False
    _timestamp = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._setup_logging()
            self._initialized = True

    @property
    def timestamp(self) -> str:
        return self._timestamp

    def _setup_logging(self):
        """Configure logging for the entire application"""
        # Create logs directory
        os.makedirs('logs', exist_ok=True)

        # Get the root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)  # Changed from DEBUG to INFO

        # Remove any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )

        # Create file handler for all logs
        file_handler = logging.FileHandler(f'logs/linkedin_bot_{self._timestamp}.log')
        file_handler.setLevel(logging.INFO)  # Changed from DEBUG to INFO
        file_handler.setFormatter(detailed_formatter)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)

        # Add handlers to root logger
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        # Log the start of a new session
        root_logger.info(f"=== New Session Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    @staticmethod
    def get_logger(name: Optional[str] = None) -> logging.Logger:
        """Get a logger instance for a module"""
        return logging.getLogger(name)

# Create a global instance
log_manager = LogManager() 