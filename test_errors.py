#!/usr/bin/env python3
"""
Скрипт для тестирования обработки ошибок в API
"""

import requests
import json

BASE_URL = "http://localhost:5050"

def test_error_handling():
    """Тестирование различных сценариев ошибок"""
    
    print("🧪 Тестирование обработки ошибок")
    print("=" * 50)
    
    # 1. Тест несуществующего эндпоинта
    print("\n1. Тест несуществующего эндпоинта...")
    try:
        response = requests.get(f"{BASE_URL}/nonexistent")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 2. Тест получения несуществующего поста
    print("\n2. Тест получения несуществующего поста...")
    try:
        response = requests.get(f"{BASE_URL}/posts/999")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 3. Тест создания поста без данных
    print("\n3. Тест создания поста без данных...")
    try:
        response = requests.post(f"{BASE_URL}/posts")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 4. Тест создания поста с пустыми полями
    print("\n4. Тест создания поста с пустыми полями...")
    try:
        response = requests.post(f"{BASE_URL}/posts", json={})
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 5. Тест создания поста с невалидными данными
    print("\n5. Тест создания поста с невалидными данными...")
    invalid_post = {
        "title": "ab",  # Слишком короткий заголовок
        "content": "123"  # Слишком короткое содержимое
    }
    try:
        response = requests.post(f"{BASE_URL}/posts", json=invalid_post)
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 6. Тест создания поста с слишком длинным заголовком
    print("\n6. Тест создания поста с слишком длинным заголовком...")
    long_title_post = {
        "title": "a" * 201,  # Слишком длинный заголовок
        "content": "Это валидное содержимое поста с достаточным количеством символов."
    }
    try:
        response = requests.post(f"{BASE_URL}/posts", json=long_title_post)
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 7. Тест обновления несуществующего поста
    print("\n7. Тест обновления несуществующего поста...")
    try:
        response = requests.put(f"{BASE_URL}/posts/999", json={"title": "Новый заголовок"})
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 8. Тест удаления несуществующего поста
    print("\n8. Тест удаления несуществующего поста...")
    try:
        response = requests.delete(f"{BASE_URL}/posts/999")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 9. Тест неверного HTTP метода
    print("\n9. Тест неверного HTTP метода...")
    try:
        response = requests.patch(f"{BASE_URL}/posts")  # PATCH не поддерживается
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 10. Тест успешного создания поста для проверки валидации
    print("\n10. Тест успешного создания поста...")
    valid_post = {
        "title": "Валидный заголовок",
        "content": "Это валидное содержимое поста с достаточным количеством символов для прохождения валидации."
    }
    try:
        response = requests.post(f"{BASE_URL}/posts", json=valid_post)
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Тестирование обработки ошибок завершено!")
    print("📝 Проверьте файл blog_api.log для просмотра логов")

if __name__ == "__main__":
    test_error_handling()
