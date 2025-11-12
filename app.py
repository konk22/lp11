from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from datetime import datetime

# Создание экземпляра Flask приложения
app = Flask(__name__)

# Конфигурация базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "blog.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация расширений
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Модель Post
class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связь с комментариями (один-ко-многим)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Post {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


# Модель Comment
class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Comment {self.id} by {self.author}>'

    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'content': self.content,
            'author': self.author,
            'created_at': self.created_at.isoformat()
        }


# API Эндпоинты для постов

@app.route('/')
def index():
    """Базовый маршрут для проверки работы API"""
    return {
        'message': 'Blog API работает!',
        'version': '1.0.0',
        'endpoints': {
            'posts': '/posts',
            'comments': '/posts/{id}/comments'
        }
    }


@app.route('/posts', methods=['GET'])
def get_posts():
    """Получить все посты"""
    try:
        posts = Post.query.all()
        return jsonify({
            'success': True,
            'data': [post.to_dict() for post in posts],
            'count': len(posts)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Получить пост по ID"""
    try:
        post = Post.query.get_or_404(post_id)
        return jsonify({
            'success': True,
            'data': post.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/posts', methods=['POST'])
def create_post():
    """Создать новый пост"""
    try:
        data = request.get_json()

        # Проверка обязательных полей
        if not data or not data.get('title') or not data.get('content'):
            return jsonify({
                'success': False,
                'error': 'Поля title и content обязательны'
            }), 400

        # Создание нового поста
        post = Post(
            title=data['title'],
            content=data['content']
        )

        db.session.add(post)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': post.to_dict(),
            'message': 'Пост успешно создан'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """Обновить пост"""
    try:
        post = Post.query.get_or_404(post_id)
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Данные для обновления не предоставлены'
            }), 400

        # Обновление полей
        if 'title' in data:
            post.title = data['title']
        if 'content' in data:
            post.content = data['content']

        post.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'data': post.to_dict(),
            'message': 'Пост успешно обновлен'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Удалить пост"""
    try:
        post = Post.query.get_or_404(post_id)

        db.session.delete(post)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Пост успешно удален'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Создание таблиц выполняется при запуске приложения в блоке __main__

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5050)