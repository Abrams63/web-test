# Потік OAuth2 (Authorization Code → Access Token → виклик API)

OAuth2 - це протокол авторизації, який дозволяє стороннім додаткам отримувати обмежений доступ до захищених ресурсів без передачі облікових даних користувача.

## Типовий потік OAuth2 (Authorization Code):

1. **Користувач намагається отримати доступ до захищеного ресурсу** через клієнтський додаток
2. **Клієнтський додаток перенаправляє користувача до сервера авторизації** з параметрами:
   - `client_id` - ідентифікатор клієнтського додатку
   - `redirect_uri` - URL для повернення після авторизації
   - `response_type=code` - тип відповіді (код авторизації)
   - `scope` - діапазон дозволів, які запитуються

3. **Сервер авторизації запитує у користувача дозвіл** на надання доступу клієнтському додатку

4. **Після надання дозволу сервер авторизації повертає Authorization Code** на `redirect_uri`

5. **Клієнтський додаток обмінює Authorization Code на Access Token**, надіславши запит до сервера токенів з параметрами:
   - `grant_type=authorization_code`
   - `code` - отриманий Authorization Code
   - `client_id`
   - `client_secret`
   - `redirect_uri`

6. **Сервер токенів перевіряє запит і повертає Access Token** (і, можливо, Refresh Token)

7. **Клієнтський додаток використовує Access Token для доступу до захищених ресурсів**

## Приклад використання в HTTP запитах:

### 1. Запит Authorization Code:
```
GET /authorize?
  response_type=code&
  client_id=client123&
  redirect_uri=https://example.com/callback&
  scope=read_profile
HTTP/1.1
Host: auth-server.com
```

### 2. Обмін Authorization Code на Access Token:
```
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTH_CODE_RECEIVED&
client_id=client123&
client_secret=client_secret_here&
redirect_uri=https://example.com/callback
```

### 3. Використання Access Token для виклику API:
```
GET /api/resource
Authorization: Bearer ACCESS_TOKEN_HERE
Host: api-server.com
```

## Відмінності між OAuth2 та JWT:

- **OAuth2** - це протокол авторизації (як отримати доступ)
- **JWT** - це формат токену (як виглядає доступ)

JWT може бути використаний як токен в рамках OAuth2 протоколу.

## Приклади реалізації OAuth2 серверів:

- Keycloak
- Auth0
- Google OAuth2
- GitHub OAuth
- OAuth Server (PHP)
- Django OAuth Toolkit
- Spring Security OAuth

Цей API використовує JWT для автентифікації, але не реалізує повний OAuth2 протокол, оскільки для цього потрібен окремий сервер авторизації.