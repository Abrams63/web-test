import pytest
import os
import tempfile
from pathlib import Path
from config import Settings, settings
from main import create_email_template, load_config
from search import list_files, find_in_text, get_file_extension
from recaptcha import verify_recaptcha
from pydantic import ValidationError
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch, MagicMock


class TestSettings:
    """Тестування класу Settings та пов'язаних функцій"""
    
    def test_smtp_start_tls_property(self):
        """Тестування властивості smtp_start_tls"""
        # Створюємо налаштування з різними параметрами
        settings_obj = Settings()
        
        # Якщо використовується SSL, STARTTLS не повинен використовуватися
        settings_obj.smtp_use_tls = True
        settings_obj.smtp_use_ssl = True
        settings_obj.smtp_port = 587
        assert settings_obj.smtp_start_tls == False
        
        # Якщо використовується TLS, але не SSL, і порт 587 або 25
        settings_obj.smtp_use_tls = True
        settings_obj.smtp_use_ssl = False
        settings_obj.smtp_port = 587
        assert settings_obj.smtp_start_tls == True
        
        # Якщо використовується TLS, але не SSL, і порт не 587 або 25
        settings_obj.smtp_use_tls = True
        settings_obj.smtp_use_ssl = False
        settings_obj.smtp_port = 465
        assert settings_obj.smtp_start_tls == False
        
        # Якщо не використовується TLS
        settings_obj.smtp_use_tls = False
        settings_obj.smtp_use_ssl = False
        settings_obj.smtp_port = 587
        assert settings_obj.smtp_start_tls == False


class TestEmailFunctions:
    """Тестування функцій, пов'язаних з електронною поштою"""
    
    def test_load_config(self):
        """Тестування функції load_config"""
        config = load_config()
        
        assert config.useSmtp == True
        assert config.host == settings.smtp_host
        assert config.port == settings.smtp_port
        assert config.username == settings.smtp_username
        assert config.password == settings.smtp_password
        assert config.recipientEmail == settings.smtp_recipient_email
    
    def test_create_email_template_contact_form(self):
        """Тестування функції create_email_template для контактної форми"""
        from main import MailFormData, MailConfig
        
        # Створюємо тестові дані
        mail_data = MailFormData(
            name="Test User",
            email="test@example.com",
            message="Test message",
            phone="+1234567890",
            form_type="contact"
        )
        
        config = MailConfig(
            useSmtp=True,
            host="smtp.gmail.com",
            port=587,
            username="test@gmail.com",
            password="password",
            recipientEmail="recipient@gmail.com"
        )
        
        template = create_email_template(mail_data, config, "localhost")
        
        # Перевіряємо, що шаблон містить необхідні елементи
        assert "A message from your site visitor" in template
        assert "Test User" in template
        assert "test@example.com" in template
        assert "Test message" in template
        assert "+1234567890" in template
    
    def test_create_email_template_subscribe_form(self):
        """Тестування функції create_email_template для форми підписки"""
        from main import MailFormData, MailConfig
        
        # Створюємо тестові дані
        mail_data = MailFormData(
            name="Test User",
            email="test@example.com",
            message="Test message",
            form_type="subscribe"
        )
        
        config = MailConfig(
            useSmtp=True,
            host="smtp.gmail.com",
            port=587,
            username="test@gmail.com",
            password="password",
            recipientEmail="recipient@gmail.com"
        )
        
        template = create_email_template(mail_data, config, "localhost")
        
        # Перевіряємо, що шаблон містить правильний заголовок для підписки
        assert "Subscribe request" in template
        assert "test@example.com" in template
        assert "Test message" in template
    
    def test_create_email_template_order_form(self):
        """Тестування функції create_email_template для форми замовлення"""
        from main import MailFormData, MailConfig
        
        # Створюємо тестові дані
        mail_data = MailFormData(
            name="Test User",
            email="test@example.com",
            message="Test message",
            form_type="order"
        )
        
        config = MailConfig(
            useSmtp=True,
            host="smtp.gmail.com",
            port=587,
            username="test@gmail.com",
            password="password",
            recipientEmail="recipient@gmail.com"
        )
        
        template = create_email_template(mail_data, config, "localhost")
        
        # Перевіряємо, що шаблон містить правильний заголовок для замовлення
        assert "Order request" in template
        assert "test@example.com" in template
        assert "Test message" in template


class TestSearchFunctions:
    """Тестування функцій пошуку"""
    
    def test_get_file_extension(self):
        """Тестування функції get_file_extension"""
        assert get_file_extension("test.html") == "html"
        assert get_file_extension("test.htm") == "htm"
        assert get_file_extension("test.txt") == "txt"
        assert get_file_extension("test") == ""
        assert get_file_extension("test.tar.gz") == "gz"
    
    def test_find_in_text_case_insensitive(self):
        """Тестування функції find_in_text без урахування регістру"""
        text = "This is a test text for testing purposes"
        matches = find_in_text(text, "test")
        
        assert len(matches) == 2
        assert matches[0][0] == "test"  # Знайдений текст
        assert matches[0][1] == 10      # Початкова позиція
        assert matches[0][2] == 14      # Кінцева позиція
        assert matches[1][0] == "test"  # Знайдений текст
        assert matches[1][1] == 24      # Початкова позиція
        assert matches[1][2] == 28      # Кінцева позиція
    
    def test_find_in_text_case_sensitive(self):
        """Тестування функції find_in_text з урахуванням регістру"""
        text = "This is a Test text for testing purposes"
        matches = find_in_text(text, "Test", case_sensitive=True)
        
        assert len(matches) == 1
        assert matches[0][0] == "Test"  # Знайдений текст
        assert matches[0][1] == 10      # Початкова позиція
        assert matches[0][2] == 14      # Кінцева позиція
    
    def test_find_in_text_no_matches(self):
        """Тестування функції find_in_text коли немає збігів"""
        text = "This is a test text"
        matches = find_in_text(text, "xyz")
        
        assert len(matches) == 0
    
    def test_list_files(self):
        """Тестування функції list_files"""
        # Створюємо тимчасову директорію для тестування
        with tempfile.TemporaryDirectory() as temp_dir:
            # Створюємо тестові файли
            test_file1 = Path(temp_dir) / "test.html"
            test_file2 = Path(temp_dir) / "test.txt"
            test_file3 = Path(temp_dir) / "subdir" / "test.htm"
            test_file3.parent.mkdir(parents=True, exist_ok=True)
            
            test_file1.write_text("test content")
            test_file2.write_text("test content")
            test_file3.write_text("test content")
            
            # Тестуємо функцію з розширеннями html та htm
            files = list_files(temp_dir, ["html", "htm"])
            
            # Перевіряємо, що знайдені лише файли з потрібними розширеннями
            assert len(files) == 2
            file_paths = [str(Path(f).relative_to(temp_dir)) for f in files]
            assert "test.html" in file_paths
            assert "subdir\\test.htm" in file_paths or "subdir/test.htm" in file_paths
            assert "test.txt" not in file_paths


class TestRecaptchaFunctions:
    """Тестування функцій reCAPTCHA"""
    
    @pytest.mark.asyncio
    async def test_verify_recaptcha_missing_response(self):
        """Тестування verify_recaptcha коли відсутня відповідь reCAPTCHA"""
        # Створюємо фейковий об'єкт запиту
        request_mock = MagicMock()
        form_data_mock = {}
        request_mock.form = AsyncMock(return_value=form_data_mock)
        
        # Перевіряємо, що виникає HTTPException при відсутності відповіді
        with pytest.raises(HTTPException) as exc_info:
            await verify_recaptcha(request_mock)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "CPT001"
    
    @pytest.mark.asyncio
    async def test_verify_recaptcha_default_secret_key(self):
        """Тестування verify_recaptcha з секретним ключем за замовчуванням"""
        # Зберігаємо оригінальне значення
        original_secret = settings.recaptcha_secret_key
        
        # Встановлюємо секретний ключ за замовчуванням
        settings.recaptcha_secret_key = '6LdbyxUsAAAAAH7ugiBN4F9r1eQoK0YsCScApsN6'
        
        try:
            # Створюємо фейковий об'єкт запиту
            request_mock = MagicMock()
            form_data_mock = {'g-recaptcha-response': 'some_token'}
            request_mock.form = AsyncMock(return_value=form_data_mock)
            
            # Перевіряємо, що виникає HTTPException при використанні ключа за замовчуванням
            with pytest.raises(HTTPException) as exc_info:
                await verify_recaptcha(request_mock)
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "CPT001"
        finally:
            # Відновлюємо оригінальне значення
            settings.recaptcha_secret_key = original_secret


def test_all():
    """Запуск усіх тестів"""
    # Тут ми можемо додати будь-які додаткові перевірки
    pass


if __name__ == "__main__":
    pytest.main([__file__])