from app.services.emotional_module import EmotionalMemory, EmotionalContext
from app.models.user import User
from app.models.journal_entry import JournalEntry
from app.models import db
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

def test_record_journal_entry(app, init_database):
    with app.app_context():
        user = User(username="journaluser", email="journal@example.com")
        user.set_password("journalpass")
        db.session.add(user)
        db.session.commit()

        emo_memory = EmotionalMemory(user_id=user.id)
        entry_text = "Feeling great after a morning run!"

        # Mock TextAnalyzer methods used by record_journal_entry
        with patch('app.services.text_analyzer.TextAnalyzer.analyze_sentiment_score', return_value=4.5) as mock_sentiment, \
             patch('app.services.text_analyzer.TextAnalyzer.extract_themes', return_value=['health', 'morning']) as mock_themes, \
             patch('app.services.text_analyzer.TextAnalyzer.identify_triggers', return_value={'positivi': ['great', 'run'], 'negativi': []}) as mock_triggers:

            # Test with provided mood_rating
            journal_entry_with_rating = emo_memory.record_journal_entry(entry_text, mood_rating=4.8)
            assert journal_entry_with_rating.id is not None
            assert journal_entry_with_rating.text == entry_text
            assert journal_entry_with_rating.mood == 4.8 # Provided mood should be used
            assert 'health' in journal_entry_with_rating.themes
            assert 'great' in journal_entry_with_rating.trigger_words
            mock_sentiment.assert_not_called() # analyze_sentiment_score should not be called if mood_rating is provided
            mock_themes.assert_called_once_with(entry_text)
            mock_triggers.assert_called_once_with(entry_text)

            # Reset mocks for the next call
            mock_themes.reset_mock()
            mock_triggers.reset_mock()

            # Test without provided mood_rating (should call analyze_sentiment_score)
            entry_text_2 = "A bit tired today."
            journal_entry_no_rating = emo_memory.record_journal_entry(entry_text_2)
            assert journal_entry_no_rating.mood == 4.5 # From mocked analyze_sentiment_score
            mock_sentiment.assert_called_once_with(entry_text_2)
            mock_themes.assert_called_once_with(entry_text_2)
            mock_triggers.assert_called_once_with(entry_text_2)


def test_get_user_context_no_entries(app, init_database):
     with app.app_context():
        user = User(username="contextuser_no_entry", email="context_no@example.com")
        user.set_password("contextpass")
        db.session.add(user)
        db.session.commit()

        emo_memory = EmotionalMemory(user_id=user.id)
        context = emo_memory.get_user_context()
        assert isinstance(context, EmotionalContext)
        assert context.current_mood == 3.0 # Default mood
        assert context.wellness_score == 50.0 # Default wellness

def test_get_user_context_with_entries(app, init_database):
    with app.app_context():
        user = User(username="contextuser_with_entry", email="context_with@example.com")
        user.set_password("contextpass")
        db.session.add(user)
        db.session.commit()

        # Create entries with data that TextAnalyzer would produce to isolate EmotionalMemory logic
        entry1 = JournalEntry(user_id=user.id, text="First entry, feeling okay", mood=3.5,
                              created_at=datetime.now() - timedelta(days=2),
                              themes={"work":1, "project":1}, trigger_words={"okay":1, "stress":1})
        entry2 = JournalEntry(user_id=user.id, text="Second entry, feeling better", mood=4.5,
                              created_at=datetime.now() - timedelta(days=1),
                              themes={"personal":1, "friends":1}, trigger_words={"better":1, "happy":1})
        db.session.add_all([entry1, entry2])
        db.session.commit()

        emo_memory = EmotionalMemory(user_id=user.id)

        # Mock TextAnalyzer methods that might be called within get_user_context or its sub-methods
        # if entries lack pre-analyzed fields (though our entries have them)
        with patch('app.services.text_analyzer.TextAnalyzer.extract_themes', return_value=['mock_theme']) as mock_extract_themes, \
             patch('app.services.text_analyzer.TextAnalyzer.identify_triggers', return_value={'positivi':['mock_trigger']}) as mock_identify_triggers, \
             patch('app.services.text_analyzer.TextAnalyzer.analyze_emotional_intensity', return_value=0.8) as mock_intensity:

            context = emo_memory.get_user_context(days=3)

            # Ensure TextAnalyzer methods were not called if data was sufficient from DB
            # (In _get_recent_processed_entries, if mood is None, it calls analyze_sentiment_score.
            #  In EmotionalPatternAnalyzer, if themes/triggers are missing, it calls extract/identify)
            # Our test entries have mood, themes, and trigger_words.
            mock_extract_themes.assert_not_called()
            mock_identify_triggers.assert_not_called()
            # analyze_emotional_intensity IS called by _update_time_patterns within EmotionalPatternAnalyzer
            assert mock_intensity.call_count == 2


        assert context.current_mood == 4.5 # From the latest mood in the entries
        assert len(context.mood_trend) == 2
        assert context.mood_trend == [3.5, 4.5]
        assert context.wellness_score != 50.0

        # Check dominant themes (order might vary, so check presence)
        dominant_themes_names = [t[0] for t in context.dominant_themes]
        assert "work" in dominant_themes_names or "project" in dominant_themes_names or \
               "personal" in dominant_themes_names or "friends" in dominant_themes_names

        # Check emotional triggers
        trigger_names = [t[0] for t in context.emotional_triggers]
        assert "okay" in trigger_names or "stress" in trigger_names or \
               "better" in trigger_names or "happy" in trigger_names
