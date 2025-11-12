#!/usr/bin/env python3
"""
Скрипт для тестирования API эндпоинтов комментариев
"""

import requests
import json

BASE_URL = "http://localhost:5050"

def test_comments_api():
    """Тестирование всех операций с комментариями"""
    
    print("🧪 Тестирование API эндпоинтов для комментариев")
    print("=" * 60)
    
    # Сначала создадим пост для тестирования комментариев
    print("\n1. Создание поста для тестирования комментариев...")
    test_post = {
        "title": "Тестовый пост для комментариев",
        "content": "Это тестовый пост, к которому мы будем добавлять комментарии для проверки функциональности API."
    }
    
    try:
        response = requests.post(f"{BASE_URL}/posts", json=test_post)
        print(f"   Статус: {response.status_code}")
        result = response.json()
        print(f"   Ответ: {result}")
        post_id = result.get('data', {}).get('id') if result.get('success') else None
    except Exception as e:
        print(f"   Ошибка: {e}")
        post_id = None
    
    if not post_id:
        print("❌ Не удалось создать пост. Тестирование комментариев невозможно.")
        return
    
    print(f"✅ Пост создан с ID: {post_id}")
    
    # 2. Получение комментариев к посту (должно быть пусто)
    print(f"\n2. Получение комментариев к посту {post_id}...")
    try:
        response = requests.get(f"{BASE_URL}/posts/{post_id}/comments")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 3. Создание первого комментария
    print(f"\n3. Создание первого комментария к посту {post_id}...")
    comment1 = {
        "content": "Отличный пост! Очень информативно.",
        "author": "Алексей"
    }
    try:
        response = requests.post(f"{BASE_URL}/posts/{post_id}/comments", json=comment1)
        print(f"   Статус: {response.status_code}")
        result = response.json()
        print(f"   Ответ: {result}")
        comment1_id = result.get('data', {}).get('id') if result.get('success') else None
    except Exception as e:
        print(f"   Ошибка: {e}")
        comment1_id = None
    
    # 4. Создание второго комментария
    print(f"\n4. Создание второго комментария к посту {post_id}...")
    comment2 = {
        "content": "Спасибо за полезную информацию! Буду ждать продолжения.",
        "author": "Мария"
    }
    try:
        response = requests.post(f"{BASE_URL}/posts/{post_id}/comments", json=comment2)
        print(f"   Статус: {response.status_code}")
        result = response.json()
        print(f"   Ответ: {result}")
        comment2_id = result.get('data', {}).get('id') if result.get('success') else None
    except Exception as e:
        print(f"   Ошибка: {e}")
        comment2_id = None
    
    # 5. Получение всех комментариев к посту
    print(f"\n5. Получение всех комментариев к посту {post_id}...")
    try:
        response = requests.get(f"{BASE_URL}/posts/{post_id}/comments")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 6. Получение конкретного комментария
    if comment1_id:
        print(f"\n6. Получение комментария с ID {comment1_id}...")
        try:
            response = requests.get(f"{BASE_URL}/comments/{comment1_id}")
            print(f"   Статус: {response.status_code}")
            print(f"   Ответ: {response.json()}")
        except Exception as e:
            print(f"   Ошибка: {e}")
    
    # 7. Обновление комментария
    if comment1_id:
        print(f"\n7. Обновление комментария с ID {comment1_id}...")
        updated_comment = {
            "content": "Обновленный комментарий: Очень понравился пост!",
            "author": "Алексей Петров"
        }
        try:
            response = requests.put(f"{BASE_URL}/comments/{comment1_id}", json=updated_comment)
            print(f"   Статус: {response.status_code}")
            print(f"   Ответ: {response.json()}")
        except Exception as e:
            print(f"   Ошибка: {e}")
    
    # 8. Тест создания комментария к несуществующему посту
    print(f"\n8. Тест создания комментария к несуществующему посту...")
    try:
        response = requests.post(f"{BASE_URL}/posts/999/comments", json=comment1)
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 9. Тест валидации комментария
    print(f"\n9. Тест валидации комментария (слишком короткий)...")
    invalid_comment = {
        "content": "Hi",  # Слишком короткий
        "author": "A"     # Слишком короткое имя
    }
    try:
        response = requests.post(f"{BASE_URL}/posts/{post_id}/comments", json=invalid_comment)
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 10. Удаление комментария
    if comment2_id:
        print(f"\n10. Удаление комментария с ID {comment2_id}...")
        try:
            response = requests.delete(f"{BASE_URL}/comments/{comment2_id}")
            print(f"   Статус: {response.status_code}")
            print(f"   Ответ: {response.json()}")
        except Exception as e:
            print(f"   Ошибка: {e}")
    
    # 11. Проверка удаления
    print(f"\n11. Проверка удаления комментария...")
    try:
        response = requests.get(f"{BASE_URL}/posts/{post_id}/comments")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 12. Удаление поста (комментарии должны удалиться автоматически)
    print(f"\n12. Удаление поста (комментарии должны удалиться автоматически)...")
    try:
        response = requests.delete(f"{BASE_URL}/posts/{post_id}")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 13. Проверка, что комментарии удалились вместе с постом
    if comment1_id:
        print(f"\n13. Проверка, что комментарии удалились вместе с постом...")
        try:
            response = requests.get(f"{BASE_URL}/comments/{comment1_id}")
            print(f"   Статус: {response.status_code}")
            print(f"   Ответ: {response.json()}")
        except Exception as e:
            print(f"   Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Тестирование комментариев завершено!")

if __name__ == "__main__":
    test_comments_api()
