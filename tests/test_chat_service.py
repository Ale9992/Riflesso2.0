from unittest.mock import patch, MagicMock
from app.services.chat_service import ChatService
from app.models.user import User
from app.models.message import Message
from app.models import db


def test_send_and_get_ai_response(app, init_database): # app fixture provides context
    with app.app_context():
        user = User(username="chatuser", email="chat@example.com")
        user.set_password("chatpass")
        db.session.add(user)
        db.session.commit()

        chat_service = ChatService() # ChatService will use TestConfig's DEEPSEEK_API_KEY
        user_message = "Hello AI"

        mock_deepseek_response = MagicMock()
        mock_deepseek_response.choices = [MagicMock()]
        mock_deepseek_response.choices[0].message.content = "Hello User, I am AI."

        # Patch deepseek.Client which is instantiated inside ChatService
        with patch('deepseek.Client') as MockDeepSeekClient:
            mock_client_instance = MagicMock()
            mock_client_instance.chat.completions.create.return_value = mock_deepseek_response
            MockDeepSeekClient.return_value = mock_client_instance

            # ChatService in TestConfig uses 'test_deepseek_api_key', so client should init
            # Re-initialize chat_service to ensure it picks up the mocked client if it's created in __init__
            chat_service_patched = ChatService()

            ai_text, emo_summary = chat_service_patched.get_ai_response(user_message, user.id)

            assert ai_text == "Hello User, I am AI."
            assert emo_summary is not None # In the test, this will be from EmotionalMemory with TestConfig
            mock_client_instance.chat.completions.create.assert_called_once()

        # Use the original chat_service (or chat_service_patched if db operations are also mocked)
        # For saving, as long as db is correctly configured for tests, it's fine.
        msg_obj = chat_service.save_message(user.id, user_message, True, emo_summary)
        assert msg_obj.id is not None

        saved_msg = Message.query.filter_by(user_id=user.id, text=user_message).first()
        assert saved_msg is not None
        assert saved_msg.emotional_analysis_summary is not None

def test_get_message_history(app, init_database):
    with app.app_context():
        user = User(username="historyuser", email="history@example.com")
        user.set_password("historypass")
        db.session.add(user)
        db.session.commit()

        chat_service = ChatService()
        chat_service.save_message(user.id, "Message 1", True)
        chat_service.save_message(user.id, "Response 1", False)
        chat_service.save_message(user.id, "Message 2", True)

        history = chat_service.get_message_history(user.id, limit=2)
        assert len(history) == 2
        # History is fetched desc from DB, then reversed in service for API (oldest of limit is first)
        assert history[0]['content'] == "Response 1"
        assert history[1]['content'] == "Message 2"
        assert history[0]['role'] == "assistant"
        assert history[1]['role'] == "user"
