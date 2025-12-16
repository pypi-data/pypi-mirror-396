"""Legacy session manager - kept for backward compatibility."""

import logging
from typing import Optional, Dict

import requests
from fake_useragent import UserAgent

from .browser import StealthChrome
from .proxy import ProxyManager


class StealthSession:
    """
    Legacy session manager for creating requests sessions with browser headers.
    
    Note: For new code, consider using StealthChrome directly, which is a
    drop-in replacement for webdriver.Chrome.
    """

    def __init__(
        self,
        use_browser_headers: bool = True,
        logger: Optional[logging.Logger] = None,
        proxy_host: Optional[str] = None,
        proxy_port: Optional[int] = None,
        proxy_user: Optional[str] = None,
        proxy_password: Optional[str] = None,
        browser_url: str = 'https://www.google.com',
        headless: bool = True
    ):
        """
        Initializes the StealthSession.

        :param use_browser_headers: Whether to extract headers from a real browser session.
                                   If False, uses predefined headers with random user agent.
        :param logger: Optional logger instance. If not provided, creates a basic logger.
        :param proxy_host: Optional proxy host.
        :param proxy_port: Optional proxy port.
        :param proxy_user: Optional proxy username.
        :param proxy_password: Optional proxy password.
        :param browser_url: URL to use when extracting headers from browser. Defaults to Google.
        :param headless: Whether to run browser in headless mode when extracting headers.
        """
        self.driver: Optional[StealthChrome] = None
        self.__use_browser_headers = use_browser_headers
        self.headers: Dict[str, str] = {}
        self.session: Optional[requests.Session] = None
        self.proxy_manager: Optional[ProxyManager] = None
        
        # Setup logger
        if logger is None:
            logger = logging.getLogger('stealthium')
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
        
        self.__logger = logger
        self.__init_session(browser_url, headless)
        
        # Setup proxy if provided
        if proxy_host and proxy_port:
            if self.session is None:
                raise RuntimeError("Session not initialized")
            self.proxy_manager = ProxyManager(logger=self.__logger, session=self.session)
            self.proxy_manager.set_proxy(proxy_host, proxy_port, proxy_user, proxy_password)
        
        self.__logger.info('StealthSession initialized successfully')

    def __init_browser_session(self, url: str, headless: bool) -> None:
        """Initializes a browser session to extract real headers."""
        self.driver = StealthChrome(headless=headless, logger=self.__logger)
        self.driver.get(url)
        self.headers = self.driver.get_headers()
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.__logger.info("Headers extracted from browser session")

    def __init_session(self, browser_url: str, headless: bool) -> None:
        """Initializes the session based on whether browser headers are used."""
        if self.__use_browser_headers:
            self.__init_browser_session(browser_url, headless)
        else:
            # Use predefined headers with random user agent
            self.headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'en-US,en;q=0.9',
                'priority': 'u=0, i',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
            }

            ua = UserAgent()
            self.headers['user-agent'] = ua.chrome
            self.session = requests.Session()
            self.session.headers.update(self.headers)
            self.__logger.info("Using predefined headers with random user agent")

    def get_session(self) -> requests.Session:
        """Get the requests session with stealth headers."""
        if self.session is None:
            raise RuntimeError("Session not initialized")
        return self.session

    def get_headers(self) -> Dict[str, str]:
        """Get the current headers being used."""
        return self.headers.copy()

    def get_driver(self) -> Optional[StealthChrome]:
        """Get the StealthChrome instance if browser headers are being used."""
        return self.driver

    def close(self) -> None:
        """Close the session and cleanup resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None
        if self.session:
            self.session.close()
        self.__logger.info("StealthSession closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
