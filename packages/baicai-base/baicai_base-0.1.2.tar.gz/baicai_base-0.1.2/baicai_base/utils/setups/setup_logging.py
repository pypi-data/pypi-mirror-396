import logging
import os
import sys
from datetime import datetime

from baicai_base.utils.data.storage import get_tmp_folder


class _ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "CRITICAL": "\033[95m",
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        return f"{log_color}{message}{self.RESET}"


def setup_logging(level=logging.INFO):
    """
    Sets up the root logger with the given log level, color formatting, and Markdown file logging.
    Ensures UTF-8 encoding support for all platforms.
    """
    logger = logging.getLogger()  # Get the root logger
    logger.setLevel(level)  # Set the global log level

    # Ensure the output/logs directory exists
    log_dir = get_tmp_folder("log")
    os.makedirs(log_dir, exist_ok=True)

    # Generate a log file name with the current timestamp
    log_file = os.path.join(log_dir, datetime.now().strftime("app_log_%Y%m%d_%H%M%S.md"))

    # Create a console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    # Explicitly set UTF-8 encoding for Windows compatibility
    if hasattr(console_handler.stream, "reconfigure"):
        console_handler.stream.reconfigure(encoding="utf-8")
    console_handler.setLevel(level)

    # Use the custom colored formatter for the console
    formatter = _ColoredFormatter("%(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    # Create a file handler for Markdown logging with UTF-8 encoding
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)

    # Use a Markdown formatter for the file handler
    md_formatter = logging.Formatter("%(message)s\n")
    file_handler.setFormatter(md_formatter)

    # Clear any existing handlers (this should avoid duplicates)
    logger.handlers.clear()

    # Add the handlers to the root logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


if __name__ == "__main__":
    # Set UTF-8 as default encoding for the environment
    if sys.platform.startswith("win"):
        import subprocess

        # Force console to use UTF-8
        subprocess.run(["chcp", "65001"], shell=True)

    verbose_logger = setup_logging(level=logging.DEBUG)

    # Example usage of the verbose logger
    verbose_logger = logging.getLogger(__name__)
    verbose_logger.debug("This is a verbose debug message.")
    verbose_logger.info("This is a verbose log message.")
    verbose_logger.warning("This is a verbose warning message.")
    verbose_logger.error("This is a verbose error message.")
    verbose_logger.critical("This is a verbose critical message.")

    # Test Unicode characters
    verbose_logger.info("测试中文日志输出")
    verbose_logger.info("Test emoji 🚀 🎉 🐍")
