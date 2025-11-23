# Веб-сайт с FastAPI backend

Этот проект состоит из веб-части (HTML/CSS/JS) и FastAPI backend для обработки форм и API запросов.

## Структура проекта

- HTML файлы (index.html, about.html и др.) - веб-интерфейс
- Папки css/, js/, images/, fonts/ - статические ресурсы
- fastapi_bat/ - FastAPI backend
- .github/workflows/build.yml - конфигурация GitHub Actions
- .gitignore - файл игнорирования для Git

## Как работает GitHub Actions

Файл `.github/workflows/build.yml` настраивает автоматическую сборку и деплой проекта на GitHub Pages при каждом пуше в ветку main.

### GitHub Token

`${{ secrets.GITHUB_TOKEN }}` - это автоматически создаваемый GitHub токен, который не требует дополнительной настройки. Он используется для публикации на GitHub Pages.

### Процесс сборки

1. При пуше в ветку main запускается GitHub Actions
2. Устанавливается Python 3.11
3. Устанавливаются зависимости из requirements.txt
4. Выполняются тесты (если есть)
5. Статические файлы публикуются на ветке gh-pages для GitHub Pages

## Настройка для локальной разработки

1. Установите Python 3.11+
2. Установите зависимости:
   ```bash
   pip install -r fastapi_bat/requirements.txt
   ```
3. Запустите FastAPI сервер:
   ```bash
   cd fastapi_bat
   uvicorn main:app --reload
   ```

## Настройка почты

Для работы формы обратной связи настройте файл `.env` в папке fastapi_bat с параметрами SMTP:

```
SMTP_HOST=your-smtp-server.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
SMTP_RECIPIENT_EMAIL=recipient@example.com
SMTP_USE_SSL=false
SMTP_START_TLS=true
```

## Деплой на GitHub Pages

1. Убедитесь, что в репозитории включена функция GitHub Pages
2. В настройках репозитория укажите ветку `gh-pages` как источник для GitHub Pages
3. При пуше в ветку main автоматически запустится сборка и деплой

## Особенности интеграции

FastAPI backend монтирует статические файлы из родительской директории, что позволяет использовать веб-интерфейс с одновременной обработкой API запросов. Это позволяет использовать GitHub Pages для хостинга статики, а бэкенд будет работать на другом хостинге или локально.