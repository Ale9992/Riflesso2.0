import os
import deepseek
from flask import current_app
from app.models import db
from app.models.message import Message
# from app.models.user import User # User not directly used in ChatService methods after token_required
from app.services.emotional_module import EmotionalMemory # Import new classes

class ChatService:
    def __init__(self):
        self.deepseek_client = None
        api_key = current_app.config.get('DEEPSEEK_API_KEY')
        if not api_key:
            current_app.logger.error("DEEPSEEK_API_KEY not configured.")
        else:
            self.deepseek_client = deepseek.Client(api_key=api_key)

    def get_ai_response(self, user_message_text: str, user_id: int, conversation_history: list = None):
        if not self.deepseek_client:
            return "Error: AI service is not configured.", None

        if conversation_history is None:
            conversation_history = []

        emotional_memory = EmotionalMemory(user_id=user_id)
        user_emotional_context = emotional_memory.get_user_context(days=7) # Analyze last 7 days for context

        prompt_enhancement = f"The user's current estimated mood is {user_emotional_context.current_mood:.1f}/5. "
        if user_emotional_context.dominant_themes:
            themes_str = ", ".join([t[0] for t in user_emotional_context.dominant_themes])
            prompt_enhancement += f"They have recently been focused on: {themes_str}. "
        if user_emotional_context.wellness_score < 40:
             prompt_enhancement += "They may be feeling a bit low. Respond with extra empathy. "
        elif user_emotional_context.wellness_score > 70:
             prompt_enhancement += "They seem to be doing well. Maintain a positive and supportive tone. "

        system_prompt = f"You are a supportive AI assistant. {prompt_enhancement} Adapt your tone accordingly."

        messages_for_api = [{"role": "system", "content": system_prompt}] + \
                           conversation_history + \
                           [{"role": "user", "content": user_message_text}]

        try:
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages_for_api,
                max_tokens=200,
                temperature=0.75
            )
            ai_response_text = response.choices[0].message.content

            # Store information about what context was used for the AI's response
            stored_emotional_summary = {
                "user_mood_at_time": user_emotional_context.current_mood,
                "user_wellness_at_time": user_emotional_context.wellness_score,
                "dominant_themes_considered": [t[0] for t in user_emotional_context.dominant_themes],
                "prompt_enhancement_used": prompt_enhancement # For debugging or logging
            }
            return ai_response_text, stored_emotional_summary
        except Exception as e:
            current_app.logger.error(f"DeepSeek API error: {e}")
            # Return a more generic error to the user, but log details
            return f"Sorry, I encountered an error trying to respond. Details: {str(e)}", None

    def save_message(self, user_id: int, text: str, is_user_message: bool, emotional_summary: dict = None):
        message = Message(
            user_id=user_id,
            text=text,
            is_user_message=is_user_message,
            emotional_analysis_summary=emotional_summary # This will store the summary from get_ai_response
        )
        db.session.add(message)
        db.session.commit()
        return message

    def get_message_history(self, user_id: int, limit: int = 50):
        messages = Message.query.filter_by(user_id=user_id)\
                                .order_by(Message.created_at.desc())\
                                .limit(limit)\
                                .all()
        history = []
        for msg in reversed(messages): # Chronological order for API history
            role = "user" if msg.is_user_message else "assistant"
            history.append({
                "role": role,
                "content": msg.text,
                # Optional: include emotional summary if needed by client, but not for DeepSeek history
                # "emotional_summary": msg.emotional_analysis_summary
            })
        return history
