import pytest
from app import create_app, db
from app.models.user import User
from config import Config
import os

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use in-memory SQLite for tests
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    DEEPSEEK_API_KEY = 'test_deepseek_api_key'

@pytest.fixture(scope='session')
def app():
    app_instance = create_app(TestConfig)
    with app_instance.app_context():
        yield app_instance

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def init_database(app):
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def new_user_data():
    return {
        "username": "testuser1",
        "email": "test1@example.com",
        "password": "password123"
    }
