FROM python:3.11-slim

# Установка необходимых пакетов
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    curl \
    unzip \
    xvfb \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Установка Docker
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce docker-ce-cli containerd.io

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка зависимостей Python
RUN pip install -r requirements.txt

# Копирование остальных файлов проекта
COPY . .

# Создание директории для логов
RUN mkdir -p /app/logs

# Установка переменных окружения для Chrome
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_PATH=/usr/bin/chromium
ENV CHROMIUM_PATH=/usr/bin/chromium

# Создание скрипта для запуска Xvfb
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Запуск Xvfb и скрипта
CMD ["/start.sh"]

CMD ["pytest", "-v", "--cov=.", "--cov-report=term-missing"] 