"""Proxy management for stealth sessions."""

import requests
from typing import Optional, Dict
import logging


class ProxyManager:
    """
    Manages proxy settings and validation for HTTP requests.
    """

    def __init__(self, logger: logging.Logger, session: requests.Session):
        """
        Initializes the ProxyManager with a logger and a session.

        :param logger: Logger instance for logging information and errors.
        :param session: Session instance for making HTTP requests.
        """
        self.__logger = logger
        self.session = session
        self.__proxies: Dict[str, str] = {}

    def __validate_proxy(self) -> bool:
        """
        Validates the current proxy settings by checking the IP address.

        This method sends a request to 'https://api.ipify.org' using the current proxy settings
        and compares the IP address before and after setting the proxy. If the IP addresses
        are different, the proxy is considered valid.

        :return: True if the proxy is valid, False otherwise.
        """
        try:
            # Get IP through proxy
            response = requests.get("https://api.ipify.org?format=text", proxies=self.__proxies, timeout=10)
            if response.status_code == 200:
                current_ip = response.text.strip()
                # Get original IP without proxy
                response = requests.get("https://api.ipify.org?format=text", timeout=10)
                if response.status_code == 200:
                    original_ip = response.text.strip()
                    if current_ip != original_ip:
                        self.__logger.info(f"Proxy validated. Original IP: {original_ip}, Proxy IP: {current_ip}")
                        return True
                    else:
                        self.__logger.warning("Proxy IP matches original IP. Proxy may not be working.")
        except Exception as e:
            self.__logger.error(f"Proxy validation failed: {e}")
        self.__logger.error("Proxy validation failed")
        return False

    def set_proxy(self, host: str, port: int, user: Optional[str] = None, password: Optional[str] = None) -> None:
        """
        Sets the proxy settings.

        :param host: Proxy host.
        :param port: Proxy port.
        :param user: (Optional) Username for proxy authentication.
        :param password: (Optional) Password for proxy authentication.
        """
        if user and password:
            proxy = f"http://{user}:{password}@{host}:{port}"
        else:
            proxy = f"http://{host}:{port}"

        self.__proxies = {
            "http": proxy,
            "https": proxy,
        }
        self.update_proxy()

    def get_proxy(self) -> Dict[str, str]:
        """
        Returns the current proxy settings.

        :return: Dictionary containing the current proxy settings.
        """
        return self.__proxies.copy()

    def update_proxy(self) -> bool:
        """
        Updates the session's proxy settings if the current proxy is valid.

        :return: True if proxy was successfully set, False otherwise.
        """
        if self.session is None:
            self.__logger.error("Session is not initialized.")
            return False
        
        if self.__validate_proxy():
            self.session.proxies.update(self.__proxies)
            self.__logger.info("Proxy successfully set on session.")
            return True
        else:
            self.__logger.warning("Proxy validation failed. Proxy not set.")
            return False
