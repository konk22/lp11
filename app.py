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

# Валидация данных
def validate_post_data(data):
    """Валидация данных для поста"""
    errors = []
    
    if not data:
        errors.append("Данные не предоставлены")
        return errors
    
    if not data.get('title'):
        errors.append("Поле 'title' обязательно")
    elif len(data['title'].strip()) < 3:
        errors.append("Заголовок должен содержать минимум 3 символа")
    elif len(data['title']) > 200:
        errors.append("Заголовок не должен превышать 200 символов")
    
    if not data.get('content'):
        errors.append("Поле 'content' обязательно")
    elif len(data['content'].strip()) < 10:
        errors.append("Содержимое должно содержать минимум 10 символов")
    
    return errors

def validate_comment_data(data):
    """Валидация данных для комментария"""
    errors = []
    
    if not data:
        errors.append("Данные не предоставлены")
        return errors
    
    if not data.get('content'):
        errors.append("Поле 'content' обязательно")
    elif len(data['content'].strip()) < 5:
        errors.append("Содержимое комментария должно содержать минимум 5 символов")
    elif len(data['content']) > 1000:
        errors.append("Содержимое комментария не должно превышать 1000 символов")
    
    if not data.get('author'):
        errors.append("Поле 'author' обязательно")
    elif len(data['author'].strip()) < 2:
        errors.append("Имя автора должно содержать минимум 2 символа")
    elif len(data['author']) > 100:
        errors.append("Имя автора не должно превышать 100 символов")
    
    return errors

# API Эндпоинты для постов

@app.route('/')
@log_request
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
        
        # Валидация данных
        validation_errors = validate_post_data(data)
        if validation_errors:
            logger.warning(f"Ошибки валидации при создании поста: {validation_errors}")
            return jsonify({
                'success': False,
                'error': 'Ошибки валидации',
                'message': '; '.join(validation_errors)
            }), 400
        
        # Создание нового поста
        post = Post(
            title=data['title'].strip(),
            content=data['content'].strip()
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
        
        # Валидация данных (если они предоставлены)
        if 'title' in data or 'content' in data:
            validation_data = {
                'title': data.get('title', post.title),
                'content': data.get('content', post.content)
            }
            validation_errors = validate_post_data(validation_data)
            if validation_errors:
                logger.warning(f"Ошибки валидации при обновлении поста {post_id}: {validation_errors}")
                return jsonify({
                    'success': False,
                    'error': 'Ошибки валидации',
                    'message': '; '.join(validation_errors)
                }), 400
        
        # Обновление полей
        if 'title' in data:
            post.title = data['title'].strip()
        if 'content' in data:
            post.content = data['content'].strip()
        
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

# API Эндпоинты для комментариев

@app.route('/posts/<int:post_id>/comments', methods=['GET'])
@log_request
def get_comments(post_id):
    """Получить все комментарии к посту"""
    try:
        # Проверяем существование поста
        post = Post.query.get(post_id)
        if not post:
            logger.warning(f"Попытка получить комментарии к несуществующему посту {post_id}")
            return jsonify({
                'success': False,
                'error': 'Пост не найден',
                'message': f'Пост с ID {post_id} не существует'
            }), 404
        
        comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
        logger.info(f"Получено {len(comments)} комментариев для поста {post_id}")
        
        return jsonify({
            'success': True,
            'data': [comment.to_dict() for comment in comments],
            'count': len(comments),
            'post_id': post_id
        }), 200
        
    except Exception as e:
        logger.error(f"Ошибка при получении комментариев для поста {post_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка при получении комментариев',
            'message': 'Не удалось получить комментарии'
        }), 500

@app.route('/posts/<int:post_id>/comments', methods=['POST'])
@log_request
def create_comment(post_id):
    """Создать новый комментарий к посту"""
    try:
        # Проверяем существование поста
        post = Post.query.get(post_id)
        if not post:
            logger.warning(f"Попытка создать комментарий к несуществующему посту {post_id}")
            return jsonify({
                'success': False,
                'error': 'Пост не найден',
                'message': f'Пост с ID {post_id} не существует'
            }), 404
        
        data = request.get_json()
        
        # Валидация данных
        validation_errors = validate_comment_data(data)
        if validation_errors:
            logger.warning(f"Ошибки валидации при создании комментария: {validation_errors}")
            return jsonify({
                'success': False,
                'error': 'Ошибки валидации',
                'message': '; '.join(validation_errors)
            }), 400
        
        # Создание нового комментария
        comment = Comment(
            post_id=post_id,
            content=data['content'].strip(),
            author=data['author'].strip()
        )
        
        db.session.add(comment)
        db.session.commit()
        
        logger.info(f"Создан новый комментарий с ID {comment.id} к посту {post_id} от {comment.author}")
        return jsonify({
            'success': True,
            'data': comment.to_dict(),
            'message': 'Комментарий успешно создан'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при создании комментария к посту {post_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка при создании комментария',
            'message': 'Не удалось создать комментарий'
        }), 500

@app.route('/comments/<int:comment_id>', methods=['GET'])
@log_request
def get_comment(comment_id):
    """Получить комментарий по ID"""
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            logger.warning(f"Комментарий с ID {comment_id} не найден")
            return jsonify({
                'success': False,
                'error': 'Комментарий не найден',
                'message': f'Комментарий с ID {comment_id} не существует'
            }), 404
        
        logger.info(f"Получен комментарий с ID {comment_id}")
        return jsonify({
            'success': True,
            'data': comment.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Ошибка при получении комментария {comment_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка при получении комментария',
            'message': 'Не удалось получить комментарий'
        }), 500

@app.route('/comments/<int:comment_id>', methods=['PUT'])
@log_request
def update_comment(comment_id):
    """Обновить комментарий"""
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            logger.warning(f"Попытка обновить несуществующий комментарий с ID {comment_id}")
            return jsonify({
                'success': False,
                'error': 'Комментарий не найден',
                'message': f'Комментарий с ID {comment_id} не существует'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Данные не предоставлены',
                'message': 'Необходимо предоставить данные для обновления'
            }), 400
        
        # Валидация данных (если они предоставлены)
        if 'content' in data or 'author' in data:
            validation_data = {
                'content': data.get('content', comment.content),
                'author': data.get('author', comment.author)
            }
            validation_errors = validate_comment_data(validation_data)
            if validation_errors:
                logger.warning(f"Ошибки валидации при обновлении комментария {comment_id}: {validation_errors}")
                return jsonify({
                    'success': False,
                    'error': 'Ошибки валидации',
                    'message': '; '.join(validation_errors)
                }), 400
        
        # Обновление полей
        if 'content' in data:
            comment.content = data['content'].strip()
        if 'author' in data:
            comment.author = data['author'].strip()
        
        db.session.commit()
        
        logger.info(f"Обновлен комментарий с ID {comment_id} от {comment.author}")
        return jsonify({
            'success': True,
            'data': comment.to_dict(),
            'message': 'Комментарий успешно обновлен'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при обновлении комментария {comment_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка при обновлении комментария',
            'message': 'Не удалось обновить комментарий'
        }), 500

@app.route('/comments/<int:comment_id>', methods=['DELETE'])
@log_request
def delete_comment(comment_id):
    """Удалить комментарий"""
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            logger.warning(f"Попытка удалить несуществующий комментарий с ID {comment_id}")
            return jsonify({
                'success': False,
                'error': 'Комментарий не найден',
                'message': f'Комментарий с ID {comment_id} не существует'
            }), 404
        
        comment_author = comment.author
        post_id = comment.post_id
        db.session.delete(comment)
        db.session.commit()
        
        logger.info(f"Удален комментарий с ID {comment_id} от {comment_author} к посту {post_id}")
        return jsonify({
            'success': True,
            'message': 'Комментарий успешно удален'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при удалении комментария {comment_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка при удалении комментария',
            'message': 'Не удалось удалить комментарий'
        }), 500

# Создание таблиц выполняется при запуске приложения в блоке __main__

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    logger.info("Запуск Flask приложения")
    app.run(debug=True, host='0.0.0.0', port=5050)
