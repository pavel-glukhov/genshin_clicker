import os
from dataclasses import dataclass
from selenium import webdriver

from dotenv import load_dotenv

ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(ROOT_PATH, '.env')
load_dotenv(dotenv_path)


@dataclass
class Config:
    token: str
    sessions_folder: str


def load_config() -> Config:
    """
    Load general config of the application
    :return: Config dataclass instance
    """
    return Config(
        token=os.getenv('TELEGRAM_TOKEN'),
        sessions_folder=os.path.join(ROOT_PATH, 'sessions')
    )


def get_chrome_config(headless: bool = True):
    """
    Returns Chrome options and the CDP script for bypassing detection.

    :param headless: whether to run in headless mode
    :return: tuple(ChromeOptions, cdp_script)
    """
    options = webdriver.ChromeOptions()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-webgl")
    options.add_argument("--mute-audio")
    options.add_argument("--log-level=3")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("detach", True)

    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/119.0.0.0 Safari/537.36"
    )

    cdp_script = """
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
    """

    return options, cdp_script
