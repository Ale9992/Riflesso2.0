import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__)) # Base directory of the app

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # Updated SQLALCHEMY_DATABASE_URI for SQLite to be in an instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

    # Create instance folder if it doesn't exist for SQLite
    if SQLALCHEMY_DATABASE_URI.startswith('sqlite:///'):
        instance_path = os.path.dirname(SQLALCHEMY_DATABASE_URI.replace('sqlite:///', ''))
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
