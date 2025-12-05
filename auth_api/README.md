# JWT Auth API

Це REST API з автентифікацією через JWT та авторизацією на основі ролей (RBAC).

## Встановлення

1. Встановіть залежності:
```bash
pip install -r requirements.txt
```

2. Запустіть сервер:
```bash
python run.py
```

Сервер буде доступний за адресою: `http://localhost:8001`

## Авторизація на основі ролей (RBAC)

У цьому API реалізовано систему ролей:
- `admin`: має доступ до всіх ендпоїнтів
- `moderator`: має обмежений доступ до певних ендпоїнтів
- `user`: має доступ тільки до своїх даних

## Ендпоїнти

### POST /login
Автентифікація користувача та отримання JWT токену.

Тіло запиту:
```json
{
  "username": "string",
  "password": "string"
}
```

Відповідь:
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### GET /profile
Отримання профілю поточного користувача (потребує валідний токен).

Відповідь:
```json
{
  "username": "string",
  "email": "string",
  "role": "string"
}
```

### DELETE /users/{user_id}
Видалення користувача (тільки для адмінів).

Відповідь:
```json
{
  "message": "User {user_id} deleted successfully by {username}"
}
```

### GET /admin
Доступ тільки для адмінів.

### GET /moderator
Доступ тільки для модераторів.

### GET /admin-or-moderator
Доступ для адмінів та модераторів.

### GET /user-data
Доступ тільки для звичайних користувачів.

### GET /users
Отримання списку всіх користувачів (тільки для адмінів).

## Приклади облікових даних

- Адміністратор: `username: "admin"`, `password: "admin123"`
- Звичайний користувач: `username: "user"`, `password: "user123"`
- Модератор: `username: "moderator"`, `password: "modpass"`