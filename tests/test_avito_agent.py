import unittest
from unittest.mock import patch, MagicMock
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from avito_agent import AvitoAgent

class TestAvitoAgent(unittest.TestCase):
    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.config = {
            'username': 'test_user',
            'password': 'test_pass',
            'proxy': {
                'http': 'http://proxy:8080',
                'https': 'https://proxy:8080'
            },
            'user_agent': 'Mozilla/5.0 Test Agent',
            'selenium_hub_url': 'http://localhost:4444/wd/hub'
        }
        self.agent = AvitoAgent(self.config)

    def tearDown(self):
        """Очистка после каждого теста"""
        if hasattr(self, 'agent') and self.agent.driver:
            self.agent.driver.quit()

    @patch('selenium.webdriver.Remote')
    def test_initialization(self, mock_driver):
        """Тест инициализации агента"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.username, 'test_user')
        self.assertEqual(self.agent.password, 'test_pass')
        self.assertEqual(self.agent.proxy, self.config['proxy'])
        self.assertEqual(self.agent.user_agent, self.config['user_agent'])
        self.assertEqual(self.agent.selenium_hub_url, self.config['selenium_hub_url'])

    @patch('selenium.webdriver.Remote')
    def test_login_success(self, mock_driver):
        """Тест успешной авторизации"""
        mock_element = MagicMock()
        mock_driver.return_value.find_element.return_value = mock_element
        mock_driver.return_value.current_url = 'https://www.avito.ru/profile'
        
        result = self.agent.login()
        
        self.assertTrue(result)
        mock_driver.return_value.get.assert_called_with('https://www.avito.ru/profile')
        mock_element.send_keys.assert_any_call('test_user')
        mock_element.send_keys.assert_any_call('test_pass')
        mock_element.click.assert_called()

    @patch('selenium.webdriver.Remote')
    def test_login_failure(self, mock_driver):
        """Тест неудачной авторизации"""
        mock_driver = MagicMock()
        mock_driver.current_url = 'https://www.avito.ru/login'
        mock_driver.find_element.side_effect = Exception('Element not found')
        
        with self.assertRaises(Exception):
            self.agent.login()

    @patch('selenium.webdriver.Remote')
    def test_create_listing(self, mock_driver):
        """Тест создания объявления"""
        mock_element = MagicMock()
        mock_driver.return_value.find_element.return_value = mock_element
        
        listing_data = {
            'title': 'Test Item',
            'description': 'Test Description',
            'price': '1000',
            'category': 'Electronics',
            'images': ['test1.jpg', 'test2.jpg']
        }
        
        result = self.agent.create_listing(listing_data)
        
        self.assertTrue(result)
        mock_driver.return_value.get.assert_called_with('https://www.avito.ru/additem')
        mock_element.send_keys.assert_any_call('Test Item')
        mock_element.send_keys.assert_any_call('Test Description')
        mock_element.send_keys.assert_any_call('1000')

    @patch('selenium.webdriver.Remote')
    def test_proxy_configuration(self, mock_driver):
        """Тест конфигурации прокси"""
        options = mock_driver.return_value.options
        self.assertEqual(self.agent.proxy['http'], 'http://proxy:8080')
        self.assertEqual(self.agent.proxy['https'], 'https://proxy:8080')
        self.assertIn('--proxy-server=proxy:8080', options.arguments)

    @patch('selenium.webdriver.Remote')
    def test_user_agent_configuration(self, mock_driver):
        """Тест конфигурации User-Agent"""
        options = mock_driver.return_value.options
        self.assertEqual(self.agent.user_agent, 'Mozilla/5.0 Test Agent')
        self.assertIn('--user-agent=Mozilla/5.0 Test Agent', options.arguments)

if __name__ == '__main__':
    unittest.main() 