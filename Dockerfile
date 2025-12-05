# Використовуємо офіційний образ Python 3.1
FROM python:3.11-slim

# Встановлюємо змінні середовища
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файли залежностей
COPY requirements.txt .

# Встановлюємо залежності
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копіюємо всі файли додатка
COPY . .

# Створюємо необхідні директорії
RUN mkdir -p cache

# Експортуємо порт, який використовується додатком
EXPOSE 8000

# Команда для запуску додатка
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]