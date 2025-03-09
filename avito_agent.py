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
import logging

class AvitoAgent:
    def __init__(self, config):
        """Инициализация агента"""
        self.username = config['username']
        self.password = config['password']
        self.proxy = config.get('proxy')
        self.user_agent = config.get('user_agent')
        self.selenium_hub_url = config.get('selenium_hub_url', 'http://localhost:4444/wd/hub')
        self.driver = None
        self.setup_driver()
        
    def setup_driver(self):
        """Настройка и инициализация драйвера"""
        options = Options()
        
        # Настройка прокси
        if self.proxy:
            proxy_server = self.proxy.get('http', '').replace('http://', '')
            options.add_argument(f'--proxy-server={proxy_server}')
            
        # Настройка User-Agent
        if self.user_agent:
            options.add_argument(f'--user-agent={self.user_agent}')
            
        # Общие настройки
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        
        self.driver = webdriver.Remote(
            command_executor=self.selenium_hub_url,
            options=options
        )
        
    def login(self):
        """Авторизация на сайте"""
        try:
            self.driver.get('https://www.avito.ru/profile')
            
            # Ждем появления формы логина
            login_form = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "login"))
            )
            login_form.send_keys(self.username)
            
            password_form = self.driver.find_element(By.NAME, "password")
            password_form.send_keys(self.password)
            
            submit_button = self.driver.find_element(By.CLASS_NAME, "submit-button")
            submit_button.click()
            
            # Проверяем успешность авторизации
            time.sleep(2)
            return 'profile' in self.driver.current_url
            
        except Exception as e:
            logging.error(f"Ошибка при авторизации: {str(e)}")
            raise
            
    def create_listing(self, listing_data):
        """Создание объявления"""
        try:
            self.driver.get('https://www.avito.ru/additem')
            
            # Заполнение основной информации
            title_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "title"))
            )
            title_input.send_keys(listing_data['title'])
            
            description_input = self.driver.find_element(By.NAME, "description")
            description_input.send_keys(listing_data['description'])
            
            price_input = self.driver.find_element(By.NAME, "price")
            price_input.send_keys(listing_data['price'])
            
            # Выбор категории
            category_select = self.driver.find_element(By.NAME, "category")
            category_select.send_keys(listing_data['category'])
            
            # Загрузка изображений
            if 'images' in listing_data:
                for image in listing_data['images']:
                    image_input = self.driver.find_element(By.NAME, "image")
                    image_input.send_keys(image)
                    time.sleep(1)  # Ждем загрузки каждого изображения
            
            # Публикация объявления
            submit_button = self.driver.find_element(By.CLASS_NAME, "submit-button")
            submit_button.click()
            
            # Ждем завершения публикации
            time.sleep(5)
            return True
            
        except Exception as e:
            logging.error(f"Ошибка при создании объявления: {str(e)}")
            return False
            
    def __del__(self):
        """Закрытие драйвера при удалении объекта"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass 