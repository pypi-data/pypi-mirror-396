# Stealthium

Create undetectable browser sessions for web scraping without automation flags. **Stealthium provides a drop-in replacement for Selenium's `webdriver.Chrome`** - use it exactly like Selenium, but with built-in anti-detection features.

## Features

- 🕵️ **Anti-Detection**: Removes automation flags and makes browsers appear as real users
- 🔄 **Drop-in Replacement**: Use `StealthChrome()` exactly like `webdriver.Chrome()`
- 🌐 **Extract Headers**: Get real HTTP headers from browser sessions
- 🔄 **Proxy Support**: Built-in proxy configuration
- 🎭 **Random User Agents**: Automatically uses random, realistic user agents
- 🖥️ **Cross-Platform**: Works on Windows, Linux, and macOS
- ✅ **Full Selenium Compatibility**: All Selenium methods work as expected

## Installation

```bash
pip install stealthium
```

For Linux systems (to enable virtual display):
```bash
pip install stealthium[linux]
```

### Linux System Requirements

#### Install Chrome/Chromium

Stealthium requires Chrome or Chromium to be installed. If you get a "cannot find Chrome binary" error, install one of the following:

**Ubuntu/Debian:**
```bash
# Install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f  # Fix dependencies

# OR install Chromium (lighter alternative)
sudo apt-get update
sudo apt-get install chromium-browser
```

**Fedora/RHEL/CentOS:**
```bash
# Install Google Chrome
sudo dnf install google-chrome-stable

# OR install Chromium
sudo dnf install chromium
```

**Arch Linux:**
```bash
# Install Google Chrome
yay -S google-chrome

# OR install Chromium
sudo pacman -S chromium
```

#### Install Xvfb (Optional - for virtual display)

On Linux systems, if you want to use the virtual display feature (optional), you need to install `Xvfb`:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install xvfb
```

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install xorg-x11-server-Xvfb
```

**Arch Linux:**
```bash
sudo pacman -S xorg-server-xvfb
```

> **Note:** The virtual display is optional. Chrome can run in headless mode without it, so you can skip this step if you don't need the virtual display feature.

Or install from source:
```bash
git clone https://github.com/yourusername/stealthium.git
cd stealthium
pip install -e .
```

## Quick Start

### Basic Usage (Just like Selenium!)

```python
from stealthium import StealthChrome

# Use it exactly like webdriver.Chrome()
driver = StealthChrome(headless=True)

try:
    driver.get('https://example.com')
    print(driver.title)
    
    # All Selenium methods work!
    element = driver.find_element('tag name', 'h1')
    print(element.text)
finally:
    driver.quit()
```

### Extract Headers

```python
from stealthium import StealthChrome

driver = StealthChrome(headless=True)

try:
    driver.get('https://example.com')
    
    # Extract real HTTP headers (new method!)
    headers = driver.get_headers()
    print(f"User-Agent: {headers.get('user-agent')}")
finally:
    driver.quit()
```

### With Proxy

```python
from stealthium import StealthChrome

# Set proxy during initialization
driver = StealthChrome(
    headless=True,
    proxy_host='proxy.example.com',
    proxy_port=8080,
    proxy_user='username',  # Optional
    proxy_password='password'  # Optional
)

try:
    driver.get('https://httpbin.org/ip')
    print(driver.page_source)
finally:
    driver.quit()
```

### Context Manager

```python
from stealthium import StealthChrome

# Automatic cleanup with context manager
with StealthChrome(headless=True) as driver:
    driver.get('https://example.com')
    print(driver.title)
    # Driver automatically quits when exiting
```

### Custom Options

```python
from stealthium import StealthChrome
from selenium.webdriver.chrome.options import Options

# Use custom ChromeOptions (stealth features still applied)
options = Options()
options.add_argument('--window-size=1920,1080')

driver = StealthChrome(options=options, headless=True)
try:
    driver.get('https://example.com')
finally:
    driver.quit()
```

## Migration from Selenium

**It's super easy!** Just replace `webdriver.Chrome` with `StealthChrome`:

```python
# Before (Selenium)
from selenium import webdriver
driver = webdriver.Chrome()
driver.get('https://example.com')

# After (Stealthium)
from stealthium import StealthChrome
driver = StealthChrome()
driver.get('https://example.com')
```

That's it! Everything else works exactly the same.

## How It Works

Stealthium uses several techniques to make automated browsers undetectable:

1. **Removes Automation Flags**: Disables `navigator.webdriver` and other automation indicators
2. **Real Browser Headers**: Extracts actual HTTP headers from Chrome performance logs
3. **Random User Agents**: Uses realistic, random user agents from the `fake-useragent` library
4. **Chrome Options**: Configures Chrome with anti-detection settings
5. **CDP Commands**: Uses Chrome DevTools Protocol to override user agents

## API Reference

### StealthChrome

Drop-in replacement for `webdriver.Chrome` with stealth features.

**Parameters (same as webdriver.Chrome, plus):**
- `headless` (bool): Whether to run in headless mode. Default: `True`
- `logger` (logging.Logger, optional): Logger instance. If None, creates a basic logger.
- `proxy_host` (str, optional): Proxy host address
- `proxy_port` (int, optional): Proxy port number
- `proxy_user` (str, optional): Proxy username for authentication
- `proxy_password` (str, optional): Proxy password for authentication

**Additional Methods:**
- `get_headers(url=None)`: Extract HTTP headers from browser performance logs
  - Returns: Dictionary of HTTP headers
  - Example: `headers = driver.get_headers()`

**All standard Selenium methods work:**
- `get(url)`, `find_element()`, `find_elements()`, `execute_script()`, etc.
- Everything that works with `webdriver.Chrome` works with `StealthChrome`!

## Requirements

- Python 3.8+
- Chrome/Chromium browser installed
- ChromeDriver (automatically managed by `webdriver-manager`)
- **Linux users (optional)**: Xvfb for virtual display support (see [Linux System Requirements](#linux-system-requirements) above)

## Limitations

- Requires Chrome/Chromium to be installed
- Browser header extraction is slower than using predefined headers
- Some websites may still detect automation through other means (behavioral analysis, etc.)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Disclaimer

This tool is for educational and legitimate web scraping purposes only. Always respect websites' terms of service and robots.txt files. Use responsibly and ethically.
