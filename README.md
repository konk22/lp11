# lp1
## Цель: Простой REST API для блога
### Участники:
Тормышев Игорь Валерьевич  
Резников Дмитрий Игоревич  


# Задача 1-1: Настройка Flask, модели Post/Comment, SQLite

## Описание
Настройка базовой инфраструктуры Flask приложения с моделями данных для блога.

## Что реализовано

### 1. Настройка Flask приложения
- Создан основной файл `app.py` с конфигурацией Flask
- Настроена SQLite база данных
- Добавлена поддержка Flask-Migrate для миграций

### 2. Модели данных

#### Модель Post
- `id` - уникальный идентификатор
- `title` - заголовок поста (максимум 200 символов)
- `content` - содержимое поста
- `created_at` - дата создания
- `updated_at` - дата последнего обновления
- `comments` - связь с комментариями (один-ко-многим)

#### Модель Comment
- `id` - уникальный идентификатор
- `post_id` - ссылка на пост
- `content` - содержимое комментария
- `author` - автор комментария
- `created_at` - дата создания

### 3. Функциональность
- Автоматическое создание таблиц при запуске
- Методы `to_dict()` для сериализации в JSON
- Базовый маршрут `/` для проверки работы API

## Установка и запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите приложение:
```bash
python run.py
```

3. Проверьте работу:
```bash
curl http://localhost:5050/
```

## Структура файлов
```
1-1/
├── app.py              # Основное приложение Flask
├── run.py              # Точка входа
├── requirements.txt    # Зависимости Python
└── README.md          # Документация
```

## Следующие шаги
- Реализация CRUD операций для постов (задача 1-2)
- Добавление API эндпоинтов для комментариев (задача 2-1)

# Задача 1-2: Модели данных

## Описание
Создание моделей данных для блога с настройкой связей между сущностями.

## Реализованные модели

### 1. Модель Post
```python
class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связь с комментариями (один-ко-многим)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
```

**Поля:**
- `id` - уникальный идентификатор (автоинкремент)
- `title` - заголовок поста (максимум 200 символов)
- `content` - содержимое поста (текст)
- `created_at` - дата создания (автоматически)
- `updated_at` - дата обновления (автоматически)

### 2. Модель Comment
```python
class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Поля:**
- `id` - уникальный идентификатор (автоинкремент)
- `post_id` - ссылка на пост (внешний ключ)
- `content` - содержимое комментария
- `author` - автор комментария (максимум 100 символов)
- `created_at` - дата создания (автоматически)

## Связи между моделями

### Один-ко-многим (Post → Comment)
- Один пост может иметь много комментариев
- Один комментарий принадлежит одному посту
- При удалении поста все комментарии удаляются автоматически (cascade)

### Настройка связей
```python
# В модели Post
comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

# В модели Comment
post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
```

## Методы моделей

### to_dict()
Каждая модель имеет метод `to_dict()` для сериализации в JSON:
```python
def to_dict(self):
    return {
        'id': self.id,
        'title': self.title,
        'content': self.content,
        'created_at': self.created_at.isoformat(),
        'updated_at': self.updated_at.isoformat()
    }
```

## Миграции базы данных

### Автоматическое создание таблиц
```python
@app.before_first_request
def create_tables():
    db.create_all()
```

### Flask-Migrate
Настроен Flask-Migrate для управления миграциями:
```python
migrate = Migrate(app, db)
```

## Установка и запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите приложение:
```bash
python run.py
```

3. Проверьте работу:
```bash
curl http://localhost:5050/
```

## Структура файлов
```
1-2/
├── app.py              # Flask приложение с моделями
├── run.py              # Точка входа
├── requirements.txt    # Зависимости Python
└── README.md          # Документация
```

## Следующие шаги
- Реализация CRUD операций для постов (задача 1-3)
- Добавление обработки ошибок (задача 1-4)