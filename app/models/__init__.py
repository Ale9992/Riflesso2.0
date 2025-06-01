from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)

# Import models here to ensure they are registered with SQLAlchemy
from .user import User
from .message import Message
from .journal_entry import JournalEntry
