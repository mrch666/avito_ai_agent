import os
import time
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
from loguru import logger
from fake_useragent import UserAgent

class AvitoAgent:
    def __init__(self, headless: bool = False, proxy: Optional[str] = None):
        """
        Инициализация агента для работы с Авито
        
        Args:
            headless (bool): Запуск браузера в фоновом режиме
            proxy (str): Прокси сервер в формате 'ip:port' или 'username:password@ip:port'
        """
        load_dotenv()
        self.username = os.getenv('AVITO_LOGIN')
        self.password = os.getenv('AVITO_PASSWORD')
        
        options = Options()
        if headless:
            options.add_argument('--headless')
        
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
            
        ua = UserAgent()
        options.add_argument(f'user-agent={ua.random}')
        
        # Подключаемся к Selenium Grid
        selenium_host = os.getenv('SELENIUM_HUB_HOST', 'selenium-hub')
        self.driver = webdriver.Remote(
            command_executor=f'http://{selenium_host}:4444/wd/hub',
            options=options
        )
        self.wait = WebDriverWait(self.driver, 10)
        logger.info("AvitoAgent initialized successfully")
        
    def login(self) -> bool:
        """Авторизация на сайте"""
        try:
            self.driver.get('https://www.avito.ru/profile/login')
            
            # Ждем загрузки формы логина
            login_form = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='login']"))
            )
            
            # Вводим логин и пароль
            login_form.send_keys(self.username)
            password_form = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
            password_form.send_keys(self.password)
            
            # Нажимаем кнопку входа
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Проверяем успешность входа
            time.sleep(3)
            if 'profile' in self.driver.current_url:
                logger.success("Successfully logged in")
                return True
            else:
                logger.error("Login failed")
                return False
                
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return False
            
    def create_listing(
        self,
        title: str,
        description: str,
        price: int,
        category: str,
        images: List[str],
        params: Optional[Dict] = None
    ) -> bool:
        """
        Создание нового объявления
        
        Args:
            title (str): Заголовок объявления
            description (str): Описание объявления
            price (int): Цена
            category (str): Категория товара
            images (List[str]): Список путей к изображениям
            params (Dict): Дополнительные параметры объявления
        """
        try:
            # Переходим на страницу создания объявления
            self.driver.get('https://www.avito.ru/additem')
            
            # Ждем загрузки формы
            title_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-marker='title']"))
            )
            
            # Заполняем заголовок
            title_input.send_keys(title)
            
            # TODO: Реализовать заполнение остальных полей
            # - Выбор категории
            # - Загрузка изображений
            # - Заполнение описания
            # - Установка цены
            # - Заполнение дополнительных параметров
            
            logger.info("Listing created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating listing: {str(e)}")
            return False
            
    def __del__(self):
        """Закрытие браузера при удалении объекта"""
        try:
            self.driver.quit()
        except:
            pass 