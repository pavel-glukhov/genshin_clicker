import logging
import pickle
import sys
import time
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        NoSuchElementException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.config import load_config

logger = logging.getLogger(__name__)

_thread_target_key, _thread_args_key, _thread_kwargs_key = (
    ('_target', '_args', '_kwargs')
    if sys.version_info >= (3, 0) else
    ('_Thread__target', '_Thread__args', '_Thread__kwargs')
)


class ParserClient:
    def __init__(self):
        self.driver = self._driver_init()
        self.log_browser_visibility()
        self.cookies_folder = load_config().sessions_folder
        self._open_site()

    def authentication(self, username, password, chat_id) -> tuple[bool, str]:
        try:
            self.driver.find_element(By.CLASS_NAME, "mhy-hoyolab-account-block__avatar").click()

            self.driver.switch_to.frame('hyv-account-frame')

            dialog_element = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
                (By.XPATH,
                 '//div[@class="el-dialog hyv-web-login-dialog iframe-level-1"]')))

            username_form = dialog_element.find_element(By.CSS_SELECTOR,
                                                        "input.el-input__inner[type='text']")
            password_form = dialog_element.find_element(By.CSS_SELECTOR,
                                                        "input.el-input__inner[type='password']")
            username_form.send_keys(username)
            password_form.send_keys(password)

            general_credentials_form = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cmn-form-web")))

            login_button = general_credentials_form.find_element(
                By.XPATH,
                './/button[@class="el-button el-button--primary el-button--large cmn-button cmn-button__block mt-p40"]')

            login_button.click()

        except (NoSuchElementException, ElementClickInterceptedException):
            return False, "Ошибка входа. Повторите позже"

        try:
            toast_text = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'van-toast__text'))
            )
            return False, toast_text.text

        except (NoSuchElementException, TimeoutException):
            self.export_cookies(f'{self.cookies_folder}\\{chat_id}.pkl')
            return True, 'Авторизация прошла успешно'

    def get_daily_award(self) -> tuple[bool, dict | str]:

        award_img_src = None
        time.sleep(7)
        try:
            actived_day_div = self.driver.find_element(
                By.XPATH,
                '//div[@class="components-home-assets-__sign-content-test_---actived-day---34r3rb"]').find_element(
                By.XPATH,
                'following-sibling::div[@class="components-home-assets-__sign-content-test_---sign-award---2rJ6SD"]')

            sign_content_div_2_div = actived_day_div.find_element(
                By.XPATH,
                'following-sibling::div[@class="components-home-assets-__sign-content-test_---item-cnt---2s89sH"]')
            item_day_div = sign_content_div_2_div.find_element(
                By.XPATH,
                'following-sibling::div[@class="components-home-assets-__sign-content-test_---item-day---1C_BmH pc-item-day"]')
            award_img_src = actived_day_div.find_element(
                By.XPATH, './/img').get_attribute("src")
            count_text = sign_content_div_2_div.text
            day = item_day_div.text
            div_element = self.driver.find_element(By.CLASS_NAME,
                                                   "components-home-assets-__sign-content-test_---actived-day---34r3rb")
            time.sleep(5)
            div_element.find_element(By.CLASS_NAME,
                                     "components-home-assets-__sign-content-test_---red-point---2jUBf9").click()

            message_text = (f'{datetime.now().strftime("%A")} '
                            f'({day}).'
                            f' Сегодня ты получил '
                            f'{count_text} ед:')

            return True, {'img': award_img_src, 'text': message_text}

        except (NoSuchElementException, TimeoutException):
            return False, "User does not have day's awards"

    def get_next_award_information(self) -> tuple[bool, dict | str]:
        try:
            award_text = self.driver.find_element(
                By.XPATH,
                '//div[@class="components-common-common-dialog-__index_---next-info---3oTiNW"]').text

            award_img_src = self.driver.find_element(
                By.XPATH,
                '//div[@class="components-common-common-dialog-__index_---award-wrapper---kzgudv"]'
            ).find_element(By.XPATH, './/img').get_attribute("src")

            message_text = f'Следующая награда: {award_text}'

            self.driver.find_element("class name",
                                     "components-common-common-dialog-__index_---dialog-close---1Yc84V").click()
            return True, {'img': award_img_src, 'text': message_text}

        except (NoSuchElementException, AttributeError):
            return False, "User does not have next day's awards"

    def export_cookies(self, save_path):
        cookies = self.driver.get_cookies()
        pickle.dump(cookies, open(save_path, "wb"))

    def import_cookies(self, file):
        cookies = pickle.load(open(f'{self.cookies_folder}\\{file}', "rb"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()

    def _open_site(self):
        self.driver.get(
            'https://act.hoyolab.com/ys/event/signin-sea-v3/'
            'index.html?act_id=e202102251931481&lang=ru-ru')

        try:
            self.driver.find_element("class name",
                                     "components-home-assets-__sign-guide_"
                                     "---guide-close---2VvmzE").click()

        except NoSuchElementException:
            return None

    def log_browser_visibility(self):
        """
        Execute JS to collect what the page can see: navigator.*, plugins, languages, webdriver.
        Also open httpbin.org/headers and log the HTTP headers of the response (how the server sees them).
        """
        try:
            js = """
             return {
                 userAgent: navigator.userAgent,
                 webdriver: navigator.webdriver === undefined ? null : navigator.webdriver,
                 languages: navigator.languages || null,
                 platform: navigator.platform || null,
                 pluginsLength: (navigator.plugins && navigator.plugins.length) || 0,
                 vendor: navigator.vendor || null,
                 hardwareConcurrency: navigator.hardwareConcurrency || null,
                 deviceMemory: navigator.deviceMemory || null
             }
             """
            info = self.driver.execute_script(js)
            logger.info("Browser JS-visible properties:")
            logger.info("  userAgent: %s", info.get("userAgent"))
            logger.info("  navigator.webdriver: %s", info.get("webdriver"))
            logger.info("  languages: %s", info.get("languages"))
            logger.info("  platform: %s", info.get("platform"))
            logger.info("  plugins length: %s", info.get("pluginsLength"))
            logger.info("  vendor: %s", info.get("vendor"))
            logger.info("  hardwareConcurrency: %s", info.get("hardwareConcurrency"))
            logger.info("  deviceMemory: %s", info.get("deviceMemory"))

            try:
                self.driver.get("https://httpbin.org/headers")
                time.sleep(1)
                pre = self.driver.find_element(By.TAG_NAME, "pre").text
                logger.info("httpbin.org/headers response (headers the server saw):\n%s", pre)
            except Exception as e:
                logger.warning("Failed to fetch headers from httpbin: %s", e)

            try:
                cookies = self.driver.get_cookies()
                logger.info("Cookies (count=%d): %s", len(cookies), cookies)
            except Exception as e:
                logger.warning("Failed to read cookies: %s", e)

        except Exception as exc:
            logger.exception("Error collecting browser visibility: %s", exc)

    def _driver_init(self) -> webdriver.Chrome:
        logger.info("Initializing WebDriver")

        options = webdriver.ChromeOptions()
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

        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/119.0.0.0 Safari/537.36")

        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(15)

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            """
        })

        logger.info("WebDriver initialized")
        return driver

    @property
    def get_driver(self) -> webdriver:
        return self.driver
