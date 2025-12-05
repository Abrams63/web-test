#!/bin/bash

# Скрипт для автоматичної збірки та запуску додатка BAT API Server

set -e  # Зупинити виконання при будь-якій помилці

echo "Початок збірки BAT API Server..."

# Перевірка наявності Docker
if ! [ -x "$(command -v docker)" ]; then
 echo "Помилка: Docker не встановлено." >&2
  exit 1
fi

# Перевірка наявності docker-compose
if ! [ -x "$(command -v docker-compose)" ]; then
  echo "Помилка: docker-compose не встановлено." >&2
 exit 1
fi

# Перейти до директорії з проектом
cd "$(dirname "$0")"

echo "Виконується збірка докер-контейнерів..."

# Збірка докер-контейнерів
docker-compose build

echo "Збірка завершена. Запуск додатка..."

# Запуск додатка в режимі детачингу
docker-compose up -d

echo "Додаток запущено в фоновому режимі."
echo "API буде доступний на http://localhost:8000"

# Очікування готовності додатка
echo "Очікування готовності додатка..."
sleep 10

# Перевірка статусу сервісів
echo "Статус сервісів:"
docker-compose ps

echo "Збірка та запуск завершені успішно!"