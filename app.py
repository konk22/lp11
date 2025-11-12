from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging
from datetime import datetime
from functools import wraps

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('blog_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

# Декоратор для логирования запросов
def log_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"Запрос: {request.method} {request.url} от {request.remote_addr}")
        try:
            result = f(*args, **kwargs)
            logger.info(f"Ответ: {request.method} {request.url} - Успешно")
            return result
        except Exception as e:
            logger.error(f"Ошибка в {request.method} {request.url}: {str(e)}")
            raise
    return decorated_function

# Обработчики ошибок
@app.errorhandler(400)
def bad_request(error):
    logger.warning(f"Ошибка 400: {request.url} - {error.description}")
    return jsonify({
        'success': False,
        'error': 'Неверный запрос',
        'message': str(error.description) if hasattr(error, 'description') else 'Проверьте данные запроса'
    }), 400

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"Ошибка 404: {request.url} - {error.description}")
    return jsonify({
        'success': False,
        'error': 'Ресурс не найден',
        'message': str(error.description) if hasattr(error, 'description') else 'Запрашиваемый ресурс не существует'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    logger.warning(f"Ошибка 405: {request.method} {request.url} - Метод не разрешен")
    return jsonify({
        'success': False,
        'error': 'Метод не разрешен',
        'message': f'Метод {request.method} не поддерживается для данного эндпоинта'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Ошибка 500: {request.url} - {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Внутренняя ошибка сервера',
        'message': 'Произошла неожиданная ошибка. Попробуйте позже.'
    }), 500

# API Эндпоинты для постов

@app.route('/')
@log_request
def index():
    """Базовый маршрут для проверки работы API"""
    return {
        'message': 'Blog API с обработкой ошибок работает!',
        'version': '1.0.0',
        'features': [
            'Логирование запросов',
            'Обработка ошибок',
            'HTTP статус-коды'
        ],
        'endpoints': {
            'posts': '/posts',
            'comments': '/posts/{id}/comments'
        }
    }

@app.route('/posts', methods=['GET'])
@log_request
def get_posts():
    """Получить все посты"""
    try:
        posts = Post.query.all()
        logger.info(f"Получено {len(posts)} постов")
        return jsonify({
            'success': True,
            'data': [post.to_dict() for post in posts],
            'count': len(posts)
        }), 200
    except Exception as e:
        logger.error(f"Ошибка при получении постов: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка при получении постов',
            'message': 'Не удалось получить список постов'
        }), 500

@app.route('/posts/<int:post_id>', methods=['GET'])
@log_request
def get_post(post_id):
    """Получить пост по ID"""
    try:
        post = Post.query.get(post_id)
        if not post:
            logger.warning(f"Пост с ID {post_id} не найден")
            return jsonify({
                'success': False,
                'error': 'Пост не найден',
                'message': f'Пост с ID {post_id} не существует'
            }), 404
        
        logger.info(f"Получен пост с ID {post_id}")
        return jsonify({
            'success': True,
            'data': post.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Ошибка при получении поста {post_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка при получении поста',
            'message': 'Не удалось получить пост'
        }), 500

@app.route('/posts', methods=['POST'])
@log_request
def create_post():
    """Создать новый пост"""
    try:
        data = request.get_json()
        
        # Проверка обязательных полей
        if not data or not data.get('title') or not data.get('content'):
            logger.warning("Попытка создать пост без обязательных полей")
            return jsonify({
                'success': False,
                'error': 'Поля title и content обязательны',
                'message': 'Необходимо предоставить заголовок и содержимое поста'
            }), 400
        
        # Создание нового поста
        post = Post(
            title=data['title'],
            content=data['content']
        )
        
        db.session.add(post)
        db.session.commit()
        
        logger.info(f"Создан новый пост с ID {post.id}: {post.title}")
        return jsonify({
            'success': True,
            'data': post.to_dict(),
            'message': 'Пост успешно создан'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при создании поста: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка при создании поста',
            'message': 'Не удалось создать пост'
        }), 500

@app.route('/posts/<int:post_id>', methods=['PUT'])
@log_request
def update_post(post_id):
    """Обновить пост"""
    try:
        post = Post.query.get(post_id)
        if not post:
            logger.warning(f"Попытка обновить несуществующий пост с ID {post_id}")
            return jsonify({
                'success': False,
                'error': 'Пост не найден',
                'message': f'Пост с ID {post_id} не существует'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Данные не предоставлены',
                'message': 'Необходимо предоставить данные для обновления'
            }), 400
        
        # Обновление полей
        if 'title' in data:
            post.title = data['title']
        if 'content' in data:
            post.content = data['content']
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Обновлен пост с ID {post_id}: {post.title}")
        return jsonify({
            'success': True,
            'data': post.to_dict(),
            'message': 'Пост успешно обновлен'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при обновлении поста {post_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка при обновлении поста',
            'message': 'Не удалось обновить пост'
        }), 500

@app.route('/posts/<int:post_id>', methods=['DELETE'])
@log_request
def delete_post(post_id):
    """Удалить пост"""
    try:
        post = Post.query.get(post_id)
        if not post:
            logger.warning(f"Попытка удалить несуществующий пост с ID {post_id}")
            return jsonify({
                'success': False,
                'error': 'Пост не найден',
                'message': f'Пост с ID {post_id} не существует'
            }), 404
        
        post_title = post.title
        db.session.delete(post)
        db.session.commit()
        
        logger.info(f"Удален пост с ID {post_id}: {post_title}")
        return jsonify({
            'success': True,
            'message': 'Пост успешно удален'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при удалении поста {post_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка при удалении поста',
            'message': 'Не удалось удалить пост'
        }), 500

# Создание таблиц выполняется при запуске приложения в блоке __main__

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    logger.info("Запуск Flask приложения с обработкой ошибок")
    app.run(debug=True, host='0.0.0.0', port=5050)
