# Документація BAT API Server

## Огляд

BAT API Server - це FastAPI-додаток, який замінює функціональність оригінальної папки `bat`. Він надає можливості для обробки форм, пошуку по сайту та перевірки reCAPTCHA.

## Конфігурація

Для налаштування додатка використовується файл `.env` у директорії `fastapi_bat`:

```env
# SMTP Налаштування
SMTP_USE_TLS=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_RECIPIENT_EMAIL=recipient@gmail.com

# reCAPTCHA Налаштування
RECAPTCHA_SITE_KEY=your_site_key
RECAPTCHA_SECRET_KEY=your_secret_key

# Налаштування кешування
CACHE_ENABLED=true
CACHE_LIFETIME=3600
CACHE_DIR=cache

# Налаштування додатка
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=false

# Налаштування пошуку
SEARCH_DIR=..
SEARCH_EXTENSIONS=["html", "htm"]
```

## API Ендпоінти

### /mailform (POST)

Обробляє форми та надсилає електронні листи.

#### Запит (JSON):
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "message": "Hello world!",
  "phone": "+1234567890",
  "form_type": "contact",
  "g_recaptcha_response": "recaptcha_token_here",
  "additional_fields": {
    "subject": "Inquiry"
  }
}
```

#### Запит (Form Data):
```
name=John Doe
email=john@example.com
message=Hello world!
phone=+1234567890
form_type=contact
g-recaptcha-response=recaptcha_token_here
additional_fields={"subject": "Inquiry"}
```

#### Відповідь:
```json
{
  "status": "success",
  "message": "Form submitted successfully"
}
```

### /api/search (GET)

Функція пошуку по сайту.

#### Параметри:
- `s` (обов'язковий): пошуковий запит
- `filter` (необов'язковий): фільтр для пошуку файлів
- `template` (необов'язковий): шаблон результату
- `liveCount` (необов'язковий): обмеження для результатів живого пошуку
- `liveSearch` (необов'язковий): прапорець живого пошуку

#### Відповідь:
```json
{
  "query": "search_term",
  "results_count": 2,
  "total_matches": 5,
  "results": [...],
  "html": "<div id=\"search-results\">..."
}
```

### /api/recaptcha (POST)

Перевіряє відповідь reCAPTCHA.

#### Запит (Form Data):
```
g-recaptcha-response=token_here
```

#### Відповідь:
```json
{
  "status": "success",
  "message": "CPT000"
}
```

### /api/recaptcha/json (POST)

Перевіряє відповідь reCAPTCHA з JSON-даних.

#### Запит (JSON):
```json
{
  "g-recaptcha-response": "token_here"
}
```

#### Відповідь:
```json
{
  "status": "success",
  "message": "CPT000"
}
```

### /api/recaptcha/config (GET)

Отримує налаштування reCAPTCHA для клієнтської частини.

#### Відповідь:
```json
{
  "site_key": "your_site_key",
  "configured": true
}
```

## Основні класи та функції

### config.py

#### Settings
Клас для конфігурації додатка, що використовує pydantic для валідації.

- `smtp_start_tls` - властивість, що визначає, чи слід використовувати STARTTLS
- `load_settings_from_json` - функція для завантаження налаштувань з JSON-файлу

### main.py

#### MailFormData
Pydantic модель для валідації даних форми.

#### MailConfig
Pydantic модель для конфігурації пошти.

#### load_config()
Функція для завантаження конфігурації пошти з налаштувань.

#### create_email_template(data: MailFormData, config: MailConfig, hostname: str = "localhost") -> str
Функція для створення HTML-шаблону електронного листа.

#### send_email_async(data: MailFormData, hostname: str = "localhost")
Асинхронна функція для надсилання електронного листа через SMTP.

#### handle_mailform(request: Request, background_tasks: BackgroundTasks)
Асинхронна функція для обробки форми та надсилання електронного листа у фоновому режимі.

### search.py

#### list_files(search_dir: Optional[str] = None, search_in: list = None) -> list
Функція для рекурсивного переліку файлів у директорії з певними розширеннями.

#### find_in_text(text: str, search_term: str, case_sensitive: bool = False) -> list
Функція для пошуку всіх входжень пошукового терміну в тексті.

#### search(s: str, filter_pattern: str, template: str, live_count: Optional[int], live_search: Optional[str])
Асинхронна функція для пошуку по сайту.

### recaptcha.py

#### verify_recaptcha(request: Request)
Асинхронна функція для перевірки відповіді reCAPTCHA з форми.

#### verify_recaptcha_json(request: Request)
Асинхронна функція для перевірки відповіді reCAPTCHA з JSON-даних.

#### get_recaptcha_config()
Асинхронна функція для отримання налаштувань reCAPTCHA для клієнтської частини.