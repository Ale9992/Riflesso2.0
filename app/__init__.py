from flask import Flask
from config import Config
from .models import db
from flask_migrate import Migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    Migrate(app, db)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.chat import chat_bp
    app.register_blueprint(chat_bp, url_prefix='/chat')

    from app.routes.journal import journal_bp
    app.register_blueprint(journal_bp, url_prefix='/journal')

    from app.routes.profile import profile_bp # Import new profile blueprint
    app.register_blueprint(profile_bp, url_prefix='/profile') # Register it

    from app.models.user import User
    from app.models.message import Message
    from app.models.journal_entry import JournalEntry

    # from app.services import text_analyzer, emotional_module, chat_service, profile_service

    return app
