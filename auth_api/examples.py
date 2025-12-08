import requests
import json

# Адреса API
BASE_URL = "http://localhost:8001"

def print_response(response, description):
    """Функція для зручного виведення відповідей API"""
    print(f"\n{description}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print("-" * 50)

# 1. Успішний login для user
print("1. Успішний /login для user:")
response = requests.post(f"{BASE_URL}/login", json={
    "username": "user",
    "password": "user123"
})
user_token = response.json().get("access_token") if response.status_code == 200 else None
print_response(response, "Login для user")

# 2. Успішний login для admin
print("2. Успішний /login для admin:")
response = requests.post(f"{BASE_URL}/login", json={
    "username": "admin",
    "password": "admin123"
})
admin_token = response.json().get("access_token") if response.status_code == 200 else None
print_response(response, "Login для admin")

# 3. /profile без токена (401)
print("3. /profile без токена:")
response = requests.get(f"{BASE_URL}/profile")
print_response(response, "Profile без токена (401)")

# 4. /profile з токеном user (200)
print("4. /profile з токеном user:")
if user_token:
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BASE_URL}/profile", headers=headers)
    print_response(response, "Profile з токеном user (200)")

# 5. DELETE /users/:id з токеном user (403)
print("5. DELETE /users/1 з токеном user:")
if user_token:
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.delete(f"{BASE_URL}/users/1", headers=headers)
    print_response(response, "DELETE /users/1 з токеном user (403)")

# 6. DELETE /users/:id з токеном admin (200)
print("6. DELETE /users/1 з токеном admin:")
if admin_token:
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.delete(f"{BASE_URL}/users/1", headers=headers)
    print_response(response, "DELETE /users/1 з токеном admin (200)")

print("\nПриклади виконані!")
print(f"User token: {user_token}")
print(f"Admin token: {admin_token}")