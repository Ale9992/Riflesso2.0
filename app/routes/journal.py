from flask import Blueprint, request, jsonify
from app.routes.auth import token_required # Assuming this decorator correctly injects current_user
from app.models.user import User # For type hinting current_user if needed by decorator
from app.services.emotional_module import EmotionalMemory

journal_bp = Blueprint('journal', __name__)

@journal_bp.route('/entry', methods=['POST'])
@token_required
def add_journal_entry(current_user: User): # current_user is injected by @token_required
    data = request.get_json()
    if not data or not data.get('text'):
        return jsonify({'message': 'No text provided for journal entry'}), 400

    text = data['text']
    mood_rating = data.get('mood_rating') # Optional: user can provide a mood rating

    emotional_memory = EmotionalMemory(user_id=current_user.id)
    entry = emotional_memory.record_journal_entry(text, mood_rating)

    return jsonify({
        'message': 'Journal entry added',
        'entry_id': entry.id,
        'analyzed_mood': entry.mood,
        'themes': entry.themes,
        'triggers': entry.trigger_words
    }), 201

@journal_bp.route('/context', methods=['GET'])
@token_required
def get_emotional_context_route(current_user: User): # current_user is injected by @token_required
    days = request.args.get('days', 7, type=int) # Default to 7 days, can be adjusted via query param
    emotional_memory = EmotionalMemory(user_id=current_user.id)
    context = emotional_memory.get_user_context(days=days)

    return jsonify({
        'current_mood': context.current_mood,
        'mood_trend': context.mood_trend,
        'dominant_themes': context.dominant_themes,
        'emotional_triggers': context.emotional_triggers,
        'wellness_score': context.wellness_score,
        'last_updated': context.last_updated.isoformat()
    }), 200
