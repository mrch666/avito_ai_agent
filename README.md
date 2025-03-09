# Avito Agent

Автоматизированный агент для работы с Avito.ru с использованием Selenium.

## Возможности

- Автоматическая публикация объявлений
- Управление существующими объявлениями
- Загрузка изображений
- Работа с категориями и параметрами
- Защита от блокировок

## Требования

- Python 3.11+
- Docker
- Docker Compose

## Установка

1. Клонируйте репозиторий:
```bash
git clone git@github.com:your-username/avito.git
cd avito
```

2. Создайте файл .env на основе .env.example:
```bash
cp .env.example .env
# Отредактируйте .env и добавьте ваши значения
```

## Безопасность

### Локальная разработка
- Никогда не коммитьте файл `.env` с реальными данными
- Используйте `.env.example` как шаблон
- Храните чувствительные данные только локально

### CI/CD
1. Добавьте секреты в GitHub Repository Secrets:
   - `AVITO_LOGIN` - логин для авторизации
   - `AVITO_PASSWORD` - пароль для авторизации
   - `SSH_HOST` - хост удаленного сервера
   - `SSH_USERNAME` - имя пользователя для SSH
   - `SSH_PRIVATE_KEY` - приватный SSH ключ

2. Генерация SSH ключей:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Сохраните в ~/.ssh/github_deploy
```

3. Настройка сервера:
```bash
# Добавьте публичный ключ на сервер
cat ~/.ssh/github_deploy.pub | ssh user@your_server 'cat >> ~/.ssh/authorized_keys'

# Создайте отдельного пользователя для деплоя
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy

# Ограничьте доступ по IP если возможно
```

## Тестирование

Для запуска тестов выполните:
```bash
python -m pytest -v
```

## CI/CD

Проект использует GitHub Actions для автоматического тестирования и деплоя.

## Лицензия

MIT

## Использование

```python
from avito_agent import AvitoAgent

agent = AvitoAgent()
agent.login()
agent.create_listing(
    title="Название объявления",
    description="Описание объявления",
    price=1000,
    category="Электроника",
    images=["path/to/image1.jpg"]
)
```

## Безопасность

- Используйте прокси для защиты от блокировок
- Не публикуйте слишком много объявлений за короткий промежуток времени
- Следуйте правилам Авито 