#!/usr/bin/env python3
"""
Простой скрипт для тестирования API эндпоинтов постов
"""

import requests
import json

BASE_URL = "http://localhost:5050"

def test_api():
    """Тестирование всех CRUD операций для постов"""
    
    print("🧪 Тестирование API эндпоинтов для постов")
    print("=" * 50)
    
    # 1. Проверка базового эндпоинта
    print("\n1. Проверка базового эндпоинта...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 2. Получение всех постов (должно быть пусто)
    print("\n2. Получение всех постов...")
    try:
        response = requests.get(f"{BASE_URL}/posts")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 3. Создание нового поста
    print("\n3. Создание нового поста...")
    new_post = {
        "title": "Мой первый пост",
        "content": "Это содержимое моего первого поста в блоге."
    }
    try:
        response = requests.post(f"{BASE_URL}/posts", json=new_post)
        print(f"   Статус: {response.status_code}")
        result = response.json()
        print(f"   Ответ: {result}")
        post_id = result.get('data', {}).get('id') if result.get('success') else None
    except Exception as e:
        print(f"   Ошибка: {e}")
        post_id = None
    
    # 4. Получение созданного поста
    if post_id:
        print(f"\n4. Получение поста с ID {post_id}...")
        try:
            response = requests.get(f"{BASE_URL}/posts/{post_id}")
            print(f"   Статус: {response.status_code}")
            print(f"   Ответ: {response.json()}")
        except Exception as e:
            print(f"   Ошибка: {e}")
    
    # 5. Обновление поста
    if post_id:
        print(f"\n5. Обновление поста с ID {post_id}...")
        updated_post = {
            "title": "Обновленный заголовок",
            "content": "Обновленное содержимое поста."
        }
        try:
            response = requests.put(f"{BASE_URL}/posts/{post_id}", json=updated_post)
            print(f"   Статус: {response.status_code}")
            print(f"   Ответ: {response.json()}")
        except Exception as e:
            print(f"   Ошибка: {e}")
    
    # 6. Получение всех постов (должен быть один пост)
    print("\n6. Получение всех постов после создания...")
    try:
        response = requests.get(f"{BASE_URL}/posts")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 7. Удаление поста
    if post_id:
        print(f"\n7. Удаление поста с ID {post_id}...")
        try:
            response = requests.delete(f"{BASE_URL}/posts/{post_id}")
            print(f"   Статус: {response.status_code}")
            print(f"   Ответ: {response.json()}")
        except Exception as e:
            print(f"   Ошибка: {e}")
    
    # 8. Проверка удаления
    print("\n8. Проверка удаления поста...")
    try:
        response = requests.get(f"{BASE_URL}/posts")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено!")

if __name__ == "__main__":
    test_api()
