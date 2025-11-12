#!/usr/bin/env python3
"""
Тестирование расширенной валидации данных
"""

import requests
import json

BASE_URL = "http://localhost:5050"

def test_validation():
    print("🧪 Тестирование расширенной валидации")
    print("=" * 50)
    
    # Тест HTML тегов
    print("\n1. Тест HTML тегов в заголовке...")
    html_post = {
        "title": "<script>alert('hack')</script>Вредоносный заголовок",
        "content": "Это тестовый пост с HTML тегами в заголовке."
    }
    try:
        response = requests.post(f"{BASE_URL}/posts", json=html_post)
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест спама
    print("\n2. Тест повторяющихся символов...")
    spam_post = {
        "title": "aaaaaaaaaaaaaaaaaaaa",
        "content": "Это тестовый пост с подозрительными повторениями символов."
    }
    try:
        response = requests.post(f"{BASE_URL}/posts", json=spam_post)
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест опасного кода
    print("\n3. Тест опасного кода...")
    dangerous_post = {
        "title": "Опасный пост",
        "content": "<script>alert('XSS')</script>Это содержимое содержит опасный код."
    }
    try:
        response = requests.post(f"{BASE_URL}/posts", json=dangerous_post)
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест валидного поста
    print("\n4. Тест валидного поста...")
    valid_post = {
        "title": "Валидный заголовок поста",
        "content": "Это валидное содержимое поста без подозрительных элементов."
    }
    try:
        response = requests.post(f"{BASE_URL}/posts", json=valid_post)
        print(f"   Статус: {response.status_code}")
        result = response.json()
        print(f"   Ответ: {result}")
        post_id = result.get('data', {}).get('id') if result.get('success') else None
    except Exception as e:
        print(f"   Ошибка: {e}")
        post_id = None
    
    # Тест валидации комментариев
    if post_id:
        print(f"\n5. Тест валидации комментариев...")
        invalid_comment = {
            "content": "Hi",
            "author": "A"
        }
        try:
            response = requests.post(f"{BASE_URL}/posts/{post_id}/comments", json=invalid_comment)
            print(f"   Статус: {response.status_code}")
            print(f"   Ответ: {response.json()}")
        except Exception as e:
            print(f"   Ошибка: {e}")
    
    print("\n✅ Тестирование валидации завершено!")

if __name__ == "__main__":
    test_validation()
