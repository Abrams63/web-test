from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from enum import Enum
from config import settings

app = FastAPI(title="JWT Auth API", description="REST API з автентифікацією через JWT та авторизацією на основі ролей")

# Налаштування для хешування паролів
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Налаштування JWT
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# Моделі для запитів та відповідей
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"  # за замовчуванням

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# Модель для користувача
class User(BaseModel):
    username: str
    email: str
    role: str

# Проста "база даних" користувачів (у реальному застосунку використовуйте справжню БД)
fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("admin123"),
        "role": "admin"
    },
    "user": {
        "username": "user",
        "email": "user@example.com",
        "hashed_password": pwd_context.hash("user123"),
        "role": "user"
    },
    "moderator": {
        "username": "moderator",
        "email": "moderator@example.com",
        "hashed_password": pwd_context.hash("modpass"),
        "role": "moderator"
    }
}

# HTTP Bearer токен для автентифікації
security = HTTPBearer()

# Функції для роботи з паролями
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Функції для роботи з користувачами
def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return User(username=user_dict["username"], email=user_dict["email"], role=user_dict["role"])
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, fake_users_db[username]["hashed_password"]):
        return False
    return user

# Функції для роботи з JWT токенами
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=role)
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user

# Ролі для авторизації
class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user

# Створення специфічних ролей для перевірки
admin_only = RoleChecker(["admin"])
moderator_only = RoleChecker(["moderator"])
admin_moderator_only = RoleChecker(["admin", "moderator"])
user_only = RoleChecker(["user"])

# Роути
@app.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/profile")
async def read_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Приклад захищеного ресурсу для адмінів
@app.delete("/users/{user_id}")
async def delete_user(user_id: int, current_user: User = Depends(admin_only)):
    # У реальному застосунку тут буде логіка видалення користувача
    return {"message": f"User {user_id} deleted successfully by {current_user.username}"}

# Додаткові ресурси для перевірки роботи авторизації
@app.get("/admin")
async def read_admin_data(current_user: User = Depends(admin_only)):
    return {"message": "Hello admin!", "user": current_user}

@app.get("/moderator")
async def read_moderator_data(current_user: User = Depends(moderator_only)):
    return {"message": "Hello moderator!", "user": current_user}

@app.get("/admin-or-moderator")
async def read_admin_moderator_data(current_user: User = Depends(admin_moderator_only)):
    return {"message": f"Hello {current_user.role}!", "user": current_user}

@app.get("/user-data")
async def read_user_data(current_user: User = Depends(user_only)):
    return {"message": "Hello regular user!", "user": current_user}

# Ендпоїнт для отримання списку всіх користувачів (тільки для адмінів)
@app.get("/users")
async def get_all_users(current_user: User = Depends(admin_only)):
    users_list = []
    for username, user_data in fake_users_db.items():
        users_list.append({
            "username": user_data["username"],
            "email": user_data["email"],
            "role": user_data["role"]
        })
    return {"users": users_list}