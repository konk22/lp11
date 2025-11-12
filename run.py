#!/usr/bin/env python3
"""
Точка входа для запуска Flask приложения
"""

from app import app, db

if __name__ == '__main__':
    with app.app_context():
        # Создание всех таблиц в базе данных
        db.create_all()
        print("База данных инициализирована")
    
    print("Запуск сервера на http://localhost:5050")
    app.run(debug=True, host='0.0.0.0', port=5050)
