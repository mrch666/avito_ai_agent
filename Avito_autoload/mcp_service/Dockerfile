FROM python:3.11-slim

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY . /app/

# Установка зависимостей Python
RUN pip install --no-cache-dir \
    aiohttp==3.9.1 \
    loguru==0.7.2

# Создание директорий для логов и XML
RUN mkdir -p /app/logs /app/out_xml

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1

# Запуск сервиса
CMD ["python", "mcp_service/avito_mcp.py"] 