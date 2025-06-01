from flask import Blueprint, request, jsonify, current_app
from app.routes.auth import token_required # Import the decorator
from app.services.chat_service import ChatService
from app.models.user import User # To get user object from token

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/send', methods=['POST'])
@token_required
def send_message(current_user: User):
    data = request.get_json()
    if not data or not data.get('message'):
        return jsonify({'message': 'No message provided'}), 400

    user_message_text = data['message']

    chat_service = ChatService()

    # Save user message
    chat_service.save_message(user_id=current_user.id, text=user_message_text, is_user_message=True)

    # Get recent conversation history for context
    conversation_history_for_api = []
    raw_history = chat_service.get_message_history(current_user.id, limit=10) # Get last 10 messages
    for msg_data in raw_history:
        conversation_history_for_api.append({"role": msg_data["role"], "content": msg_data["content"]})


    # Get AI response
    ai_response_text, emotional_summary = chat_service.get_ai_response(
        user_message_text,
        current_user.id,
        conversation_history=conversation_history_for_api # Pass history to AI
    )

    if "Error:" in ai_response_text or "Sorry," in ai_response_text:
         # Save AI error message (or a generic one)
        chat_service.save_message(user_id=current_user.id, text=ai_response_text, is_user_message=False, emotional_summary=emotional_summary)
        return jsonify({'error': ai_response_text}), 500

    # Save AI response
    chat_service.save_message(user_id=current_user.id, text=ai_response_text, is_user_message=False, emotional_summary=emotional_summary)

    return jsonify({
        'user_message': user_message_text,
        'ai_response': ai_response_text,
        'emotional_summary': emotional_summary
    }), 200

@chat_bp.route('/history', methods=['GET'])
@token_required
def get_history(current_user: User):
    limit = request.args.get('limit', 50, type=int)
    chat_service = ChatService()
    history = chat_service.get_message_history(current_user.id, limit=limit)
    return jsonify(history), 200
