# Веб-сайт з FastAPI backend та контейнеризацією

Цей проект складається з веб-частини (HTML/CSS/JS) та FastAPI backend для обробки форм та API запитів. Проект має повну контейнеризацію за допомогою Docker та Docker Compose, включаючи базу даних PostgreSQL та Redis для кешування.

## Структура проекту

- HTML файли (index.html, about.html і ін.) - веб-інтерфейс
- Папки css/, js/, images/, fonts/ - статичні ресурси
- fastapi_bat/ - FastAPI backend
- .github/workflows/build.yml - конфігурація GitHub Actions
- .gitignore - файл ігнорування для Git
- Dockerfile - інструкції для створення Docker образу
- docker-compose.yml - конфігурація для запуску всіх сервісів
- build.sh - скрипт для автоматичної збірки та запуску

## Особливості

- **Контейнеризація**: Проект повністю контейнеризований з використанням Docker
- **Декілька сервісів**: Включає FastAPI додаток, PostgreSQL базу даних та Redis для кешування
- **Логування**: Повне логування всіх сервісів
- **Конфігурація**: Повна підтримка .env файлів та змінних середовища
- **Тестування**: Модульні тести для всіх логічних функцій
- **Документація**: Повна документація API

## Як працює GitHub Actions

Файл `.github/workflows/build.yml` налаштовує автоматичну збірку та деплой проекту на GitHub Pages при кожному пуше в гілку main.

### GitHub Token

`${{ secrets.GITHUB_TOKEN }}` - це автоматично створюваний GitHub токен, який не потребує додаткової настройки. Він використовується для публікації на GitHub Pages.

### Процес збірки

1. При пуше в гілку main запускається GitHub Actions
2. Встановлюється Python 3.11
3. Встановлюються залежності з requirements.txt
4. Виконуються тести (якщо є)
5. Статичні файли публікуються на гілці gh-pages для GitHub Pages

## Настройка для локальної розробки

### Варіант 1: Запуск через Docker (рекомендовано)

1. Встановіть Docker та Docker Compose
2. Створіть файл `.env` у папці fastapi_bat (див. нижче)
3. Запустіть скрипт автоматичної збірки:
   ```bash
   ./fastapi_bat/build.sh
   ```
   або запустіть вручну:
   ```bash
   docker-compose up --build
   ```

### Варіант 2: Локальний запуск

1. Встановіть Python 3.11+
2. Встановіть залежності:
   ```bash
   pip install -r fastapi_bat/requirements.txt
   ```
3. Створіть файл `.env` у папці fastapi_bat (див. нижче)
4. Запустіть FastAPI сервер:
   ```bash
   cd fastapi_bat
   uvicorn main:app --reload
   ```

## Настройка конфігурації

Створіть файл `.env` у папці fastapi_bat з наступним вмістом:

```
# SMTP Settings
SMTP_USE_TLS=true
SMTP_USE_SSL=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_RECIPIENT_EMAIL=recipient@gmail.com

# reCAPTCHA Settings
RECAPTCHA_SITE_KEY=your_site_key
RECAPTCHA_SECRET_KEY=your_secret_key

# Caching Settings
CACHE_ENABLED=true
CACHE_LIFETIME=3600
CACHE_DIR=cache

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=false

# Search Settings
SEARCH_DIR=..
SEARCH_EXTENSIONS=["html", "htm"]

# Database Settings
DATABASE_URL=postgresql://user:password@db:5432/bat_db

# Redis Settings
REDIS_URL=redis://redis:6379
```

## API Ендпоінти

- `/mailform` - обробка форм та відправка електронної пошти
- `/api/search` - пошук по сайту
- `/api/recaptcha` - перевірка reCAPTCHA
- `/api/recaptcha/config` - отримання налаштувань reCAPTCHA
- `/docs` - автоматично згенерована документація API
- `/redoc` - альтернативна документація API

## Деплой на GitHub Pages

1. Переконайтеся, що в репозиторії увімкнена функція GitHub Pages
2. В налаштуваннях репозиторію вкажіть гілку `gh-pages` як джерело для GitHub Pages
3. При пуше в гілку main автоматично запуститься збірка та деплой

## Контейнеризація

Проект використовує Docker Compose для запуску всіх необхідних сервісів:
- **bat-api**: FastAPI додаток
- **db**: PostgreSQL база даних
- **redis**: Redis для кешування

Конфігурація знаходиться у файлі `docker-compose.yml`.

## Тестування

Для запуску тестів виконайте:
```bash
cd fastapi_bat
python -m pytest test_logic_functions.py -v
```

## Особливості інтеграції

FastAPI backend монтує статичні файли з батьківської директорії, що дозволяє використовувати веб-інтерфейс з одночасною обробкою API запитів. Це дозволяє використовувати GitHub Pages для хостингу статики, а бекенд буде працювати на іншому хостингу або локально.

## Документація

- `fastapi_bat/api_documentation.md` - повна документація API
- `fastapi_bat/logic_functions.md` - опис всіх функцій та класів, що виконують конкретну логіку
- `fastapi_bat/test_logic_functions.py` - модульні тести