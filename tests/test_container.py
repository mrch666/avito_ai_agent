import unittest
import docker
import requests
import time
import os
from docker.errors import NotFound

class TestContainer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Инициализация перед всеми тестами"""
        cls.client = docker.from_env()
        cls.network_name = "avito_network"
        cls.setup_network()
        cls.start_containers()
        time.sleep(10)  # Ждем запуска контейнеров

    @classmethod
    def tearDownClass(cls):
        """Очистка после всех тестов"""
        try:
            containers = ['avito-agent', 'avito-mcp', 'chrome-node', 'selenium-hub']
            for container_name in containers:
                try:
                    container = cls.client.containers.get(container_name)
                    container.stop(timeout=5)
                    container.remove(force=True)
                except Exception as e:
                    print(f"Ошибка при остановке контейнера {container_name}: {str(e)}")
            
            # Удаляем сеть
            try:
                network = cls.client.networks.get(cls.network_name)
                network.remove()
            except Exception as e:
                print(f"Ошибка при удалении сети {cls.network_name}: {str(e)}")
                
        except Exception as e:
            print(f"Ошибка при очистке: {str(e)}")

    @classmethod
    def setup_network(cls):
        """Создание сети Docker"""
        try:
            cls.client.networks.get(cls.network_name)
        except NotFound:
            cls.client.networks.create(cls.network_name, driver="bridge")

    @classmethod
    def cleanup_network(cls):
        """Удаление сети Docker"""
        try:
            network = cls.client.networks.get(cls.network_name)
            network.remove()
        except NotFound:
            pass

    @classmethod
    def start_containers(cls):
        """Запуск контейнеров"""
        # Selenium Hub
        cls.client.containers.run(
            "selenium/hub:4.16.1",
            name="selenium-hub",
            detach=True,
            network=cls.network_name,
            ports={'4444/tcp': 4444},
            environment={
                "GRID_MAX_SESSION": "16",
                "GRID_BROWSER_TIMEOUT": "3000",
                "GRID_TIMEOUT": "3000"
            }
        )

        # Chrome Node
        cls.client.containers.run(
            "selenium/node-chrome:4.16.1",
            name="chrome-node",
            detach=True,
            network=cls.network_name,
            environment={
                "SE_EVENT_BUS_HOST": "selenium-hub",
                "SE_EVENT_BUS_PUBLISH_PORT": "4442",
                "SE_EVENT_BUS_SUBSCRIBE_PORT": "4443",
                "SE_NODE_MAX_SESSIONS": "4"
            }
        )

        # Avito MCP Service
        cls.client.containers.run(
            "avito-mcp",
            name="avito-mcp",
            detach=True,
            network=cls.network_name,
            ports={'8080/tcp': 8080}
        )

        # Avito Agent
        cls.client.containers.run(
            "avito-agent",
            name="avito-agent",
            detach=True,
            network=cls.network_name,
            environment={
                "SELENIUM_HUB_URL": "http://selenium-hub:4444/wd/hub",
                "MCP_SERVICE_URL": "http://avito-mcp:8080"
            }
        )

    @classmethod
    def stop_containers(cls):
        """Остановка контейнеров"""
        containers = ['avito-agent', 'avito-mcp', 'chrome-node', 'selenium-hub']
        for container_name in containers:
            try:
                container = cls.client.containers.get(container_name)
                container.stop()
                container.remove()
            except NotFound:
                pass

    def test_containers_running(self):
        """Проверка что все контейнеры запущены"""
        containers = self.client.containers.list()
        container_names = [c.name for c in containers]
        
        expected_containers = ['avito-agent', 'avito-mcp', 'chrome-node', 'selenium-hub']
        for name in expected_containers:
            self.assertIn(name, container_names, f"Контейнер {name} не запущен")

    def test_selenium_hub_available(self):
        """Проверка доступности Selenium Hub"""
        response = requests.get('http://localhost:4444/wd/hub/status')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['value']['ready'])

    def test_chrome_node_registered(self):
        """Проверка регистрации Chrome Node в Selenium Hub"""
        response = requests.get('http://localhost:4444/grid/console')
        self.assertEqual(response.status_code, 200)
        self.assertIn('chrome', response.text.lower())

    def test_container_memory_limits(self):
        """Проверка ограничений памяти контейнеров"""
        for container in self.client.containers.list():
            stats = container.stats(stream=False)
            memory_limit = stats['memory_stats']['limit']
            self.assertGreater(memory_limit, 0, 
                             f"Контейнер {container.name} не имеет ограничений памяти")

    def test_avito_agent_logs(self):
        """Проверка логов Avito Agent"""
        container = self.client.containers.get('avito-agent')
        logs = container.logs().decode('utf-8')
        self.assertNotIn('error', logs.lower(), 
                        "В логах Avito Agent обнаружены ошибки")

if __name__ == '__main__':
    unittest.main() 