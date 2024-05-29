import logging
import pickle
import time
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        NoSuchElementException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.parser.exceptions import CredentialsError, NoAwardsError

logger = logging.getLogger(__name__)


class ParserClient:
    def __init__(self):
        self.driver = self._driver_init()
        self.cookies_folder = 'sessions'
        self._open_site()
    
    def authentication(self, username, password, chat_id):
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
            raise CredentialsError("Ошибка входа. Повторите позже")
        
        try:
            toast_text = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'van-toast__text'))
            )
            raise CredentialsError(toast_text.text)
        
        except (NoSuchElementException, TimeoutException):
            self.export_cookies(f'{self.cookies_folder}\\{chat_id}.pkl')
            return True
    
    def get_daily_award(self):
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
            
            return {'img': award_img_src, 'text': message_text}
        
        except (NoSuchElementException, TimeoutException):
            raise NoAwardsError("User does not have day's awards")
    
    def get_next_award_information(self):
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
            return {'img': award_img_src, 'text': message_text}
        
        except (NoSuchElementException, AttributeError):
            raise NoAwardsError("User does not have next day's awards")
    
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
        
        # Close guide dialog
        try:
            self.driver.find_element("class name",
                                     "components-home-assets-__sign-guide_"
                                     "---guide-close---2VvmzE").click()
        
        except NoSuchElementException:
            return None
    
    def _driver_init(self) -> webdriver:
        logger.info("Initializing WebDriver")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(15)
        
        logger.info("WebDriver initialized")
        return driver
    
    @property
    def get_driver(self) -> webdriver:
        return self.driver
