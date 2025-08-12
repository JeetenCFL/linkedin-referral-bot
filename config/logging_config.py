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
        """Minimal logging: same format and level to console and file."""
        os.makedirs('logs', exist_ok=True)

        # Single level, optional via env; default INFO
        level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
        level = getattr(logging, level_name, logging.INFO)

        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # Remove any existing handlers (idempotent re-init)
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # One formatter for both outputs
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - [%(filename)s:%(lineno)d] - %(message)s'
        )

        # File handler
        file_handler = logging.FileHandler(f'logs/linkedin_bot_{self._timestamp}.log')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        root_logger.info(
            f"=== New Session Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==="
        )

    @staticmethod
    def get_logger(name: Optional[str] = None) -> logging.Logger:
        """Get a logger instance for a module"""
        return logging.getLogger(name)

# Create a global instance
log_manager = LogManager() 