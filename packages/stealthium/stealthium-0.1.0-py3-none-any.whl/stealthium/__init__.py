"""
Stealthium - Create undetectable browser sessions for web scraping.

This package provides a drop-in replacement for Selenium WebDriver with
anti-detection features. Use it exactly like webdriver.Chrome, but with
additional methods for extracting headers and managing proxies.

Copyright (c) 2025 BENSERYA MOHAMED
"""

from .browser import StealthChrome
from .session import StealthSession

__version__ = "0.1.0"
__author__ = "BENSERYA MOHAMED"
__email__ = "benseryamohammed1@gmail.com"
__all__ = ["StealthChrome", "StealthSession"]

# For convenience, you can also import it as Chrome
Chrome = StealthChrome
