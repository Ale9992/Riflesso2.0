from app import create_app, db
from app.models.user import User
from app.models.message import Message
from app.models.journal_entry import JournalEntry
import click # For creating CLI commands

app = create_app()

@app.shell_context_processor
def make_shell_context():
   return {'db': db, 'User': User, 'Message': Message, 'JournalEntry': JournalEntry}

@app.cli.command("seed-db")
def seed_db_command():
    """Seeds the database with initial data."""
    # Add a sample user
    if not User.query.filter_by(username='testuser').first():
        print("Creating test user...")
        test_user = User(username='testuser', email='test@example.com')
        test_user.set_password('password123')
        db.session.add(test_user)
        db.session.commit()

        # Add some journal entries for the test user
        print("Creating journal entries for test user...")
        from app.services.emotional_module import EmotionalMemory
        emo_memory = EmotionalMemory(user_id=test_user.id)
        emo_memory.record_journal_entry("Feeling quite happy today about a small achievement at work!", mood_rating=4.5)
        emo_memory.record_journal_entry("A bit stressed about the upcoming deadline, but trying to stay positive.", mood_rating=2.5)
        emo_memory.record_journal_entry("Had a nice chat with an old friend, it really lifted my spirits.", mood_rating=4.0)

        # Add some messages
        print("Creating sample messages for test user...")
        db.session.add_all([
            Message(user_id=test_user.id, text="Hello AI, how are you?", is_user_message=True),
            Message(user_id=test_user.id, text="I'm doing well, thank you for asking! How can I help you today?", is_user_message=False, emotional_analysis_summary={'user_mood_at_time': 3.0}),
            Message(user_id=test_user.id, text="I'm feeling a bit unsure about my project.", is_user_message=True),
            Message(user_id=test_user.id, text="It's okay to feel unsure. Can you tell me more about what's on your mind?", is_user_message=False, emotional_analysis_summary={'user_mood_at_time': 2.5})
        ])
        db.session.commit()
        print("Database seeded with test user, journal entries, and messages.")
    else:
        print("Test user already exists. Database not seeded.")

if __name__ == '__main__':
   app.run(debug=True)
