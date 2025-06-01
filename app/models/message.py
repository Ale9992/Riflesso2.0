from app.models import db # Assuming db is initialized in app/models/__init__.py

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    is_user_message = db.Column(db.Boolean, default=True, nullable=False) # True if from user, False if from AI
    emotional_analysis_summary = db.Column(db.JSON, nullable=True) # Store emotional context from AI

    def __repr__(self):
        return f'<Message {self.id} by User {self.user_id}>'
