from app.models import db # Assuming db is initialized in app/models/__init__.py

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    mood = db.Column(db.Float, nullable=True) # Overall mood score
    themes = db.Column(db.JSON, nullable=True) # Extracted themes: {'theme': count}
    trigger_words = db.Column(db.JSON, nullable=True) # Trigger words: {'word': count}

    def __repr__(self):
        return f'<JournalEntry {self.id} by User {self.user_id}>'
