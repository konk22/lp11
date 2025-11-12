#!/usr/bin/env python3
"""
Комплексные тесты для Blog API с использованием pytest
"""

import pytest
import json
import os
import tempfile
from app import app, db, Post, Comment

@pytest.fixture
def client():
    """Создание тестового клиента"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def sample_post():
    """Создание тестового поста"""
    post = Post(
        title="Тестовый пост",
        content="Это содержимое тестового поста для проверки функциональности API."
    )
    db.session.add(post)
    db.session.commit()
    return post

@pytest.fixture
def sample_comment(sample_post):
    """Создание тестового комментария"""
    comment = Comment(
        post_id=sample_post.id,
        content="Тестовый комментарий",
        author="Тестовый автор"
    )
    db.session.add(comment)
    db.session.commit()
    return comment

class TestPostsAPI:
    """Тесты для API постов"""
    
    def test_get_posts_empty(self, client):
        """Тест получения пустого списка постов"""
        response = client.get('/posts')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['count'] == 0
        assert data['data'] == []
    
    def test_create_post_success(self, client):
        """Тест успешного создания поста"""
        post_data = {
            "title": "Новый пост",
            "content": "Содержимое нового поста для тестирования."
        }
        response = client.post('/posts', 
                             data=json.dumps(post_data),
                             content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['title'] == "Новый пост"
        assert 'id' in data['data']
    
    def test_create_post_validation_error(self, client):
        """Тест ошибки валидации при создании поста"""
        post_data = {
            "title": "ab",  # Слишком короткий
            "content": "123"  # Слишком короткий
        }
        response = client.post('/posts',
                             data=json.dumps(post_data),
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'validation_errors' in data
    
    def test_get_post_success(self, client, sample_post):
        """Тест успешного получения поста"""
        response = client.get(f'/posts/{sample_post.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['id'] == sample_post.id
        assert data['data']['title'] == sample_post.title
    
    def test_get_post_not_found(self, client):
        """Тест получения несуществующего поста"""
        response = client.get('/posts/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'не найден' in data['message']
    
    def test_update_post_success(self, client, sample_post):
        """Тест успешного обновления поста"""
        update_data = {
            "title": "Обновленный заголовок",
            "content": "Обновленное содержимое поста."
        }
        response = client.put(f'/posts/{sample_post.id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['title'] == "Обновленный заголовок"
    
    def test_delete_post_success(self, client, sample_post):
        """Тест успешного удаления поста"""
        response = client.delete(f'/posts/{sample_post.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        
        # Проверяем, что пост действительно удален
        response = client.get(f'/posts/{sample_post.id}')
        assert response.status_code == 404

class TestCommentsAPI:
    """Тесты для API комментариев"""
    
    def test_get_comments_empty(self, client, sample_post):
        """Тест получения пустого списка комментариев"""
        response = client.get(f'/posts/{sample_post.id}/comments')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['count'] == 0
        assert data['data'] == []
    
    def test_create_comment_success(self, client, sample_post):
        """Тест успешного создания комментария"""
        comment_data = {
            "content": "Отличный пост!",
            "author": "Алексей"
        }
        response = client.post(f'/posts/{sample_post.id}/comments',
                             data=json.dumps(comment_data),
                             content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['content'] == "Отличный пост!"
        assert data['data']['author'] == "Алексей"
        assert data['data']['post_id'] == sample_post.id
    
    def test_create_comment_validation_error(self, client, sample_post):
        """Тест ошибки валидации при создании комментария"""
        comment_data = {
            "content": "Hi",  # Слишком короткий
            "author": "A"     # Слишком короткий
        }
        response = client.post(f'/posts/{sample_post.id}/comments',
                             data=json.dumps(comment_data),
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'validation_errors' in data
    
    def test_get_comment_success(self, client, sample_comment):
        """Тест успешного получения комментария"""
        response = client.get(f'/comments/{sample_comment.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['id'] == sample_comment.id
        assert data['data']['content'] == sample_comment.content
    
    def test_update_comment_success(self, client, sample_comment):
        """Тест успешного обновления комментария"""
        update_data = {
            "content": "Обновленный комментарий",
            "author": "Новый автор"
        }
        response = client.put(f'/comments/{sample_comment.id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['content'] == "Обновленный комментарий"
    
    def test_delete_comment_success(self, client, sample_comment):
        """Тест успешного удаления комментария"""
        response = client.delete(f'/comments/{sample_comment.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        
        # Проверяем, что комментарий действительно удален
        response = client.get(f'/comments/{sample_comment.id}')
        assert response.status_code == 404

class TestValidation:
    """Тесты валидации данных"""
    
    def test_html_tags_removal(self, client):
        """Тест удаления HTML тегов"""
        post_data = {
            "title": "<script>alert('hack')</script>Заголовок",
            "content": "Содержимое с <b>HTML</b> тегами."
        }
        response = client.post('/posts',
                             data=json.dumps(post_data),
                             content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        # HTML теги должны быть удалены
        assert '<script>' not in data['data']['title']
        assert '<b>' not in data['data']['content']
    
    def test_spam_detection(self, client):
        """Тест обнаружения спама"""
        spam_data = {
            "title": "aaaaaaaaaaaaaaaaaaaa",
            "content": "Это содержимое с подозрительными повторениями символов."
        }
        response = client.post('/posts',
                             data=json.dumps(spam_data),
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'повторения' in data['message']
    
    def test_xss_protection(self, client):
        """Тест защиты от XSS"""
        xss_data = {
            "title": "Опасный пост",
            "content": "<script>alert('XSS')</script>Содержимое"
        }
        response = client.post('/posts',
                             data=json.dumps(xss_data),
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'опасный код' in data['message']

class TestErrorHandling:
    """Тесты обработки ошибок"""
    
    def test_404_error(self, client):
        """Тест обработки 404 ошибки"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_405_error(self, client):
        """Тест обработки 405 ошибки"""
        response = client.patch('/posts')  # PATCH не поддерживается
        assert response.status_code == 405
    
    def test_invalid_json(self, client):
        """Тест обработки невалидного JSON"""
        response = client.post('/posts',
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 400

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
