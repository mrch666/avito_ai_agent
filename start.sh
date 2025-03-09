#!/bin/bash

# Удаляем файл блокировки, если он существует
rm -f /tmp/.X99-lock

# Запускаем Xvfb
Xvfb :99 -screen 0 1024x768x16 &

# Ждем, пока Xvfb запустится
sleep 2

# Запускаем тесты
python3 -m pytest -v

# Держим контейнер запущенным
tail -f /dev/null 