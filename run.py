#!/usr/bin/env python3
"""
Точка входа для запуска Flask приложения с CRUD операциями для постов
"""

from app import app, db

if __name__ == '__main__':
    with app.app_context():
        # Создание всех таблиц в базе данных
        db.create_all()
        print("База данных инициализирована")

    print("Запуск сервера на http://localhost:5050")
    print("Доступные эндпоинты:")
    print("  GET    /posts          - получить все посты")
    print("  GET    /posts/{id}     - получить пост по ID")
    print("  POST   /posts          - создать новый пост")
    print("  PUT    /posts/{id}     - обновить пост")
    print("  DELETE /posts/{id}     - удалить пост")

    app.run(debug=True, host='0.0.0.0', port=5050)
