import unittest
import requests
import time
import subprocess
import os
import json

class TestContainer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Запуск контейнеров перед всеми тестами"""
        cls.compose_up()
        time.sleep(30)  # Увеличиваем время ожидания для полной инициализации
        
    @classmethod
    def tearDownClass(cls):
        """Остановка контейнеров после всех тестов"""
        cls.compose_down()
        
    @classmethod
    def compose_up(cls):
        """Запуск контейнеров через docker compose"""
        subprocess.run(['docker', 'compose', 'up', '-d'], check=True)
            
    @classmethod
    def compose_down(cls):
        """Остановка контейнеров через docker compose"""
        subprocess.run(['docker', 'compose', 'down'], check=True)
            
    def test_containers_running(self):
        """Проверка, что все контейнеры запущены и работают"""
        result = subprocess.run('docker ps --format "{{.Names}}"', 
                              shell=True, capture_output=True, text=True, check=True)
        container_names = result.stdout.strip().split('\n')
        
        expected_containers = ['avito-agent', 'selenium-hub', 'chrome-node']
        for name in expected_containers:
            self.assertIn(name, container_names, f"Контейнер {name} не запущен")
            
    def test_selenium_hub_available(self):
        """Проверка доступности Selenium Hub"""
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                response = requests.get('http://localhost:4444/wd/hub/status')
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertTrue(data['value']['ready'])
                break
            except (requests.exceptions.RequestException, KeyError) as e:
                if attempt == max_retries - 1:
                    self.fail(f"Selenium Hub недоступен после {max_retries} попыток: {str(e)}")
                time.sleep(retry_delay)
            
    def test_chrome_node_registered(self):
        """Проверка регистрации Chrome Node в Selenium Hub"""
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                response = requests.get('http://localhost:4444/wd/hub/status')
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertTrue(data['value']['ready'])
                self.assertGreater(len(data['value']['nodes']), 0)
                break
            except (requests.exceptions.RequestException, KeyError) as e:
                if attempt == max_retries - 1:
                    self.fail(f"Не удалось проверить регистрацию Chrome Node после {max_retries} попыток: {str(e)}")
                time.sleep(retry_delay)
            
    def test_avito_agent_logs(self):
        """Проверка логов контейнера avito-agent"""
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                result = subprocess.run('docker logs avito-agent', 
                                     shell=True, capture_output=True, text=True, check=True)
                logs = result.stdout
                if 'AvitoAgent initialized successfully' in logs:
                    break
                if attempt == max_retries - 1:
                    self.fail("Сообщение об успешной инициализации не найдено в логах")
                time.sleep(retry_delay)
            except subprocess.CalledProcessError:
                if attempt == max_retries - 1:
                    self.fail("Контейнер avito-agent не найден")
                time.sleep(retry_delay)
            
    def test_container_memory_limits(self):
        """Проверка установленных лимитов памяти"""
        try:
            result = subprocess.run('docker inspect avito-agent', 
                                 shell=True, capture_output=True, text=True, check=True)
            inspect = json.loads(result.stdout)[0]
            memory_limit = inspect['HostConfig']['Memory']
            self.assertEqual(memory_limit, 2 * 1024 * 1024 * 1024)  # 2GB
        except subprocess.CalledProcessError:
            self.fail("Контейнер avito-agent не найден")
            
if __name__ == '__main__':
    unittest.main() 