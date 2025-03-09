import unittest
from unittest.mock import Mock, patch
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from avito_agent import AvitoAgent

class TestAvitoAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Ожидание готовности Selenium Hub"""
        # Устанавливаем хост для тестов
        os.environ['SELENIUM_HUB_HOST'] = 'localhost'
        
        max_retries = 10
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.get('http://localhost:4444/wd/hub/status')
                if response.status_code == 200 and response.json()['value']['ready']:
                    break
            except:
                if attempt == max_retries - 1:
                    raise Exception("Selenium Hub не готов после нескольких попыток")
                time.sleep(retry_delay)
    
    def setUp(self):
        """Подготовка окружения перед каждым тестом"""
        # Создаем тестовые учетные данные
        os.environ['AVITO_LOGIN'] = 'test_user'
        os.environ['AVITO_PASSWORD'] = 'test_password'
        
        # Инициализируем агента в headless режиме
        self.agent = AvitoAgent(headless=True)
        
    def tearDown(self):
        """Очистка после каждого теста"""
        try:
            self.agent.__del__()
        except:
            pass
            
    @patch('selenium.webdriver.Remote')
    def test_initialization(self, mock_remote):
        """Проверка корректной инициализации агента"""
        agent = AvitoAgent(headless=True)
        self.assertIsNotNone(agent.driver)
        self.assertEqual(agent.username, 'test_user')
        self.assertEqual(agent.password, 'test_password')
        
    @patch('selenium.webdriver.Remote')
    def test_login_success(self, mock_remote):
        """Проверка успешной авторизации"""
        # Настраиваем мок для успешной авторизации
        mock_driver = Mock()
        mock_driver.current_url = 'https://www.avito.ru/profile'
        mock_remote.return_value = mock_driver
        
        agent = AvitoAgent(headless=True)
        result = agent.login()
        
        self.assertTrue(result)
        mock_driver.get.assert_called_with('https://www.avito.ru/profile/login')
        
    @patch('selenium.webdriver.Remote')
    def test_login_failure(self, mock_remote):
        """Проверка неуспешной авторизации"""
        # Настраиваем мок для неуспешной авторизации
        mock_driver = Mock()
        mock_driver.current_url = 'https://www.avito.ru/login'
        mock_remote.return_value = mock_driver
        
        agent = AvitoAgent(headless=True)
        result = agent.login()
        
        self.assertFalse(result)
        
    @patch('selenium.webdriver.Remote')
    def test_create_listing(self, mock_remote):
        """Проверка создания объявления"""
        mock_driver = Mock()
        mock_remote.return_value = mock_driver
        
        agent = AvitoAgent(headless=True)
        result = agent.create_listing(
            title="Test Item",
            description="Test Description",
            price=1000,
            category="Электроника",
            images=["test.jpg"]
        )
        
        self.assertTrue(result)
        mock_driver.get.assert_called_with('https://www.avito.ru/additem')
        
    @patch('selenium.webdriver.Remote')
    def test_proxy_configuration(self, mock_remote):
        """Проверка конфигурации прокси"""
        proxy = "127.0.0.1:8080"
        agent = AvitoAgent(headless=True, proxy=proxy)
        
        mock_remote.assert_called_once()
        options = mock_remote.call_args[1]['options']
        self.assertIn(f'--proxy-server={proxy}', 
                     [arg for arg in options.arguments if arg.startswith('--proxy-server')])
        
    @patch('selenium.webdriver.Remote')
    def test_user_agent_configuration(self, mock_remote):
        """Проверка конфигурации User-Agent"""
        agent = AvitoAgent(headless=True)
        
        mock_remote.assert_called_once()
        options = mock_remote.call_args[1]['options']
        self.assertTrue(any(arg.startswith('user-agent=') for arg in options.arguments))
        
if __name__ == '__main__':
    unittest.main() 