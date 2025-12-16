"""Selenium WebDriver with anti-detection features - drop-in replacement for webdriver.Chrome."""

import logging
import json
import os
import platform
import traceback
from typing import Optional, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

try:
    from pyvirtualdisplay import Display
    VIRTUAL_DISPLAY_AVAILABLE = True
except ImportError:
    VIRTUAL_DISPLAY_AVAILABLE = False


class StealthChrome(webdriver.Chrome):
    """
    A drop-in replacement for webdriver.Chrome with anti-detection features.
    
    Use it exactly like webdriver.Chrome, but with additional methods:
    - get_headers(): Extract HTTP headers from browser
    - set_proxy(): Configure proxy settings
    
    Example:
        from stealthium import StealthChrome
        
        driver = StealthChrome()
        driver.get('https://example.com')
        headers = driver.get_headers()
        driver.quit()
    """

    def __init__(
        self,
        options: Optional[Options] = None,
        service: Optional[Service] = None,
        keep_alive: bool = True,
        headless: bool = True,
        logger: Optional[logging.Logger] = None,
        proxy_host: Optional[str] = None,
        proxy_port: Optional[int] = None,
        proxy_user: Optional[str] = None,
        proxy_password: Optional[str] = None,
        incognito: bool = False,
        **kwargs
    ):
        """
        Initialize StealthChrome with anti-detection features.
        
        All parameters work exactly like webdriver.Chrome, with additional options:
        
        :param options: ChromeOptions instance. If None, creates one with stealth features.
        :param service: ChromeService instance. If None, uses ChromeDriverManager.
        :param keep_alive: Whether to keep the service alive. Default: True.
        :param headless: Whether to run in headless mode. Default: True.
        :param logger: Optional logger instance. If None, creates a basic logger.
        :param proxy_host: Optional proxy host address.
        :param proxy_port: Optional proxy port number.
        :param proxy_user: Optional proxy username for authentication.
        :param proxy_password: Optional proxy password for authentication.
        :param incognito: Whether to run in incognito/private mode. Default: False.
        :param **kwargs: Additional arguments passed to webdriver.Chrome.
        """
        # Setup logger
        if logger is None:
            logger = logging.getLogger('stealthium')
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.setLevel(logging.WARNING)  # Less verbose by default
        
        self.__logger = logger
        self.__display: Optional[Display] = None
        self.__proxy_host = proxy_host
        self.__proxy_port = proxy_port
        self.__proxy_user = proxy_user
        self.__proxy_password = proxy_password
        self.__incognito = incognito
        
        # Setup Chrome options with stealth features
        if options is None:
            options = self._create_stealth_options(headless, proxy_host, proxy_port, proxy_user, proxy_password, incognito)
        else:
            # Merge user-provided options with stealth options
            stealth_options = self._create_stealth_options(headless, proxy_host, proxy_port, proxy_user, proxy_password, incognito)
            options = self._merge_options(options, stealth_options, incognito)
        
        # Setup service if not provided
        if service is None:
            service = Service(ChromeDriverManager().install())
        
        # Setup virtual display for Linux (optional - Chrome can run headless without it)
        if platform.system() != "Windows" and VIRTUAL_DISPLAY_AVAILABLE and headless:
            try:
                self.__display = Display(visible=False, size=(1920, 1080))
                self.__display.start()
                self.__logger.debug("Virtual display started")
            except (FileNotFoundError, OSError) as e:
                # Xvfb not installed - Chrome can still run headless without it
                self.__logger.debug(f"Virtual display not available (Xvfb not installed): {e}. Continuing without it.")
                self.__display = None
        
        # Initialize parent class
        try:
            super().__init__(service=service, options=options, keep_alive=keep_alive, **kwargs)
            
            # Apply additional stealth features after initialization
            self._apply_stealth_features()
            
            self.__logger.info("StealthChrome initialized successfully")
        except Exception as e:
            error_msg = str(e)
            # Provide helpful error message for missing Chrome binary
            if "cannot find Chrome binary" in error_msg or "chrome not found" in error_msg.lower():
                self.__logger.error(
                    "Chrome/Chromium binary not found. Please install Chrome or Chromium:\n"
                    "  Ubuntu/Debian: sudo apt-get install google-chrome-stable\n"
                    "  Fedora/RHEL: sudo dnf install google-chrome-stable\n"
                    "  Arch Linux: sudo pacman -S google-chrome\n"
                    "  Or use Chromium: sudo apt-get install chromium-browser"
                )
            self.__logger.error(f"Error initializing StealthChrome: {error_msg}")
            traceback.print_exc()
            if self.__display:
                try:
                    self.__display.stop()
                except Exception:
                    pass
            raise

    def _merge_options(self, user_options: Options, stealth_options: Options, incognito: bool) -> Options:
        """
        Merge user-provided options with stealth options.
        Applies stealth features to user's options without overwriting user settings.
        
        :param user_options: Options provided by the user.
        :param stealth_options: Options with stealth features.
        :param incognito: Whether to enable incognito mode.
        :return: Merged Options object (user_options with stealth features added).
        """
        # Get existing user arguments to avoid duplicates
        user_args = set(user_options._arguments)
        
        # Add stealth arguments that don't conflict with user arguments
        for stealth_arg in stealth_options._arguments:
            # Extract argument key (part before = if it exists)
            arg_key = stealth_arg.split('=')[0] if '=' in stealth_arg else stealth_arg
            
            # Check if user already has this argument or a conflicting one
            conflict = False
            for user_arg in user_args:
                user_arg_key = user_arg.split('=')[0] if '=' in user_arg else user_arg
                # Skip if user already has this argument
                if arg_key == user_arg_key or user_arg.startswith(arg_key) or stealth_arg.startswith(user_arg_key):
                    conflict = True
                    break
            
            if not conflict:
                user_options.add_argument(stealth_arg)
        
        # Add incognito mode if requested and not already set
        if incognito and '--incognito' not in user_args:
            user_options.add_argument('--incognito')
        
        # Merge experimental options (stealth anti-detection options are critical)
        # Only override if user hasn't set them
        if 'useAutomationExtension' not in user_options._experimental_options:
            user_options.add_experimental_option("useAutomationExtension", False)
        
        if 'excludeSwitches' not in user_options._experimental_options:
            user_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
        
        # Merge capabilities (stealth logging is needed for get_headers())
        if 'goog:loggingPrefs' not in user_options._caps:
            user_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        # Set page load strategy if not set by user
        if not user_options.page_load_strategy:
            user_options.page_load_strategy = "normal"
        
        return user_options

    def _create_stealth_options(
        self,
        headless: bool,
        proxy_host: Optional[str] = None,
        proxy_port: Optional[int] = None,
        proxy_user: Optional[str] = None,
        proxy_password: Optional[str] = None,
        incognito: bool = False
    ) -> Options:
        """Create ChromeOptions with stealth features."""
        options = Options()
        ua = UserAgent()
        user_agent = ua.chrome
        
        # Enable performance logging to capture network headers
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        # Anti-detection options
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--log-level=3")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.page_load_strategy = "normal"
        options.add_argument("--disable-infobars")
        
        # Incognito mode
        if incognito:
            options.add_argument("--incognito")
        
        # User data directory
        current_dir = os.getcwd()
        selenium_dir = os.path.join(current_dir, "selenium")
        os.makedirs(selenium_dir, exist_ok=True)
        options.add_argument(f'--user-data-dir={selenium_dir}')
        
        # Proxy configuration
        if proxy_host and proxy_port:
            if proxy_user and proxy_password:
                proxy_string = f"{proxy_host}:{proxy_port}"
                options.add_argument(f'--proxy-server=http://{proxy_string}')
                # Note: Chrome doesn't support proxy auth via command line
                # You may need to use a proxy extension for authentication
                self.__logger.warning(
                    "Proxy authentication via command line is not supported by Chrome. "
                    "Consider using a proxy extension for authenticated proxies."
                )
            else:
                proxy_string = f"{proxy_host}:{proxy_port}"
                options.add_argument(f'--proxy-server=http://{proxy_string}')
            self.__logger.info(f"Proxy configured: {proxy_host}:{proxy_port}")
        
        # User agent
        options.add_argument(f"user-agent={user_agent}")
        
        if headless:
            options.add_argument("--headless")
        
        return options

    def _apply_stealth_features(self) -> None:
        """Apply additional stealth features via CDP and JavaScript."""
        try:
            # Get user agent from options
            ua = UserAgent()
            user_agent = ua.chrome
            
            # Set window size
            self.set_window_size(1200, 900)
            
            # Override user agent via CDP
            self.execute_cdp_cmd(
                "Network.setUserAgentOverride",
                {
                    "userAgent": user_agent
                },
            )
            
            # Remove webdriver property
            self.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            # Additional stealth scripts
            self.execute_script(
                "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})"
            )
            self.execute_script(
                "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})"
            )
        except Exception as e:
            self.__logger.warning(f"Could not apply some stealth features: {e}")

    def get_headers(self, url: Optional[str] = None) -> Dict[str, str]:
        """
        Extract HTTP headers from the browser's performance log.
        
        This method navigates to a URL (or uses the current page) and extracts
        the actual HTTP headers that were sent by the browser.
        
        :param url: Optional URL to navigate to. If not provided, uses current page.
        :return: Dictionary of HTTP headers.
        
        Example:
            driver = StealthChrome()
            driver.get('https://example.com')
            headers = driver.get_headers()
            print(headers['user-agent'])
        """
        try:
            if url:
                self.get(url)
            
            browser_log = self.get_log('performance')
            events = [self._process_browser_log_entry(entry) for entry in browser_log]
            events = [e for e in events if e is not None]
            
            headers = {}
            for event in events:
                if event.get('method') == 'Network.requestWillBeSentExtraInfo':
                    headers_obj = event.get('params', {}).get('headers', {})
                    headers = {key: value for key, value in headers_obj.items() if key[0] != ":"}
                    break

            if not headers:
                self.__logger.warning("No headers found in browser logs")
            
            return headers
        except Exception as e:
            self.__logger.error(f"Error getting headers: {str(e)}")
            traceback.print_exc()
            return {}

    def _process_browser_log_entry(self, entry: Dict) -> Optional[Dict]:
        """Process a single browser log entry."""
        try:
            response = json.loads(entry['message'])['message']
            return response
        except Exception as e:
            self.__logger.debug(f"Error processing browser log entry: {str(e)}")
            return None

    def set_proxy(
        self,
        host: str,
        port: int,
        user: Optional[str] = None,
        password: Optional[str] = None
    ) -> bool:
        """
        Set proxy configuration for the browser.
        
        Note: Proxy cannot be changed after browser initialization.
        This method is kept for API compatibility but will log a warning.
        To use a proxy, pass proxy_host, proxy_port, etc. to __init__.
        
        :param host: Proxy host address.
        :param port: Proxy port number.
        :param user: Optional username for proxy authentication.
        :param password: Optional password for proxy authentication.
        :return: False (proxy cannot be changed after initialization)
        
        Example (correct usage):
            # Set proxy during initialization
            driver = StealthChrome(proxy_host='proxy.example.com', proxy_port=8080)
            driver.get('https://example.com')
        """
        self.__logger.warning(
            "Proxy cannot be changed after browser initialization. "
            "Please set proxy_host, proxy_port, proxy_user, and proxy_password "
            "when creating StealthChrome instance."
        )
        return False

    def quit(self) -> None:
        """Quit the driver and cleanup resources."""
        try:
            super().quit()
        finally:
            if self.__display:
                try:
                    self.__display.stop()
                except Exception:
                    pass
                self.__display = None
            self.__logger.info("StealthChrome closed successfully")

    def close(self) -> None:
        """Close the current window."""
        super().close()
