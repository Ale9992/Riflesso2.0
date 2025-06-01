from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from app.models import db
from app.models.journal_entry import JournalEntry
from app.models.message import Message
from app.services.text_analyzer import TextAnalyzer
from collections import Counter
from sqlalchemy import select, func

class ProcessedEntry:
    def __init__(self, text: str, mood: float, created_at: datetime, themes: List[str] = None, triggers: Dict[str, List[str]] = None):
        self.text = text
        self.mood = mood
        self.created_at = created_at
        self.themes = themes if themes is not None else []
        self.trigger_words = triggers if triggers is not None else {'positivi': [], 'negativi': []}

class EmotionalPattern:
    def __init__(self):
        self.mood_trend: List[float] = []
        self.themes: Dict[str, int] = {}
        self.trigger_words: Dict[str, int] = {}
        self.weekly_pattern: Dict[str, List[float]] = {}
        self.monthly_pattern: Dict[int, List[float]] = {}

class EmotionalContext:
    def __init__(self):
        self.current_mood: float = 3.0
        self.mood_trend: List[float] = []
        self.dominant_themes: List[Tuple[str, int]] = []
        self.emotional_triggers: List[Tuple[str, int]] = []
        self.wellness_score: float = 50.0
        self.last_updated: datetime = datetime.now()

class EmotionalPatternAnalyzer:
    def __init__(self):
        self.text_analyzer = TextAnalyzer()

    def analyze(self, entries: List[ProcessedEntry]) -> EmotionalPattern:
        pattern = EmotionalPattern()
        if not entries:
            return pattern

        pattern.mood_trend = [entry.mood for entry in entries if entry.mood is not None]

        themes_counter = Counter()
        triggers_counter = Counter()

        for entry in entries:
            current_themes = entry.themes if entry.themes else self.text_analyzer.extract_themes(entry.text)
            themes_counter.update(current_themes)

            current_triggers = entry.trigger_words
            if not current_triggers or (not current_triggers.get('positivi') and not current_triggers.get('negativi')):
                current_triggers = self.text_analyzer.identify_triggers(entry.text)

            triggers_counter.update(current_triggers.get('positivi', []))
            triggers_counter.update(current_triggers.get('negativi', []))

            emotional_intensity = self.text_analyzer.analyze_emotional_intensity(entry.text)
            self._update_time_patterns(pattern, entry.created_at, emotional_intensity)

        pattern.themes = dict(themes_counter)
        pattern.trigger_words = dict(triggers_counter)
        return pattern

    def _update_time_patterns(self, pattern: EmotionalPattern, timestamp: datetime, intensity: float):
        weekday = timestamp.strftime('%A')
        if weekday not in pattern.weekly_pattern:
            pattern.weekly_pattern[weekday] = []
        pattern.weekly_pattern[weekday].append(intensity)

        month_day = timestamp.day
        if month_day not in pattern.monthly_pattern:
            pattern.monthly_pattern[month_day] = []
        pattern.monthly_pattern[month_day].append(intensity)

class WellnessAnalyzer:
    def __init__(self):
        self.text_analyzer = TextAnalyzer()

    def calculate_score(self, pattern: EmotionalPattern) -> float:
        if not pattern.mood_trend:
            return 50.0

        mood_score = self._calculate_mood_score(pattern.mood_trend)
        stability_score = self._calculate_stability_score(pattern)
        trigger_score = self._calculate_trigger_score(pattern.trigger_words)

        final_score = (mood_score * 0.4 + stability_score * 0.3 + trigger_score * 0.3)
        return min(max(final_score, 0.0), 100.0)

    def _calculate_mood_score(self, mood_trend: List[float]) -> float:
        if not mood_trend: return 0.0
        avg_mood = sum(mood_trend) / len(mood_trend)
        return (avg_mood / 5.0) * 100

    def _calculate_stability_score(self, pattern: EmotionalPattern) -> float:
        if not pattern.mood_trend or len(pattern.mood_trend) < 2:
            return 50.0

        mean = sum(pattern.mood_trend) / len(pattern.mood_trend)
        variance = sum((x - mean) ** 2 for x in pattern.mood_trend) / len(pattern.mood_trend)
        std_dev = variance ** 0.5

        max_expected_mood_swing = 2.5 # Assuming mood is on a 0-5 scale
        stability = 1 - (std_dev / max_expected_mood_swing)
        return max(0.0, stability * 100)

    def _calculate_trigger_score(self, trigger_words: Dict[str, int]) -> float:
        if not trigger_words: return 50.0

        positive_triggers = sum(count for word, count in trigger_words.items()
                              if word in self.text_analyzer.emotional_triggers_lexicon['positivi'])
        negative_triggers = sum(count for word, count in trigger_words.items()
                              if word in self.text_analyzer.emotional_triggers_lexicon['negativi'])

        total_triggers = positive_triggers + negative_triggers
        if total_triggers == 0: return 50.0

        positive_ratio = positive_triggers / total_triggers
        return positive_ratio * 100

class EmotionalMemory:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.pattern_analyzer = EmotionalPatternAnalyzer()
        self.wellness_analyzer = WellnessAnalyzer()
        self.text_analyzer = TextAnalyzer()

    def get_user_context(self, days: int = 30) -> EmotionalContext:
        processed_entries = self._get_recent_processed_entries(days)

        if not processed_entries:
            return EmotionalContext() # Return default context if no entries

        patterns = self.pattern_analyzer.analyze(processed_entries)
        wellness_score = self.wellness_analyzer.calculate_score(patterns)

        context = EmotionalContext()
        context.current_mood = patterns.mood_trend[-1] if patterns.mood_trend else 3.0
        context.mood_trend = patterns.mood_trend
        context.dominant_themes = self._get_top_items(patterns.themes)
        context.emotional_triggers = self._get_top_items(patterns.trigger_words)
        context.wellness_score = wellness_score
        context.last_updated = datetime.now()

        return context

    def _get_recent_processed_entries(self, days: int) -> List[ProcessedEntry]:
        cutoff_date = datetime.now() - timedelta(days=days)

        journal_db_entries = db.session.scalars(
            select(JournalEntry).where(
                JournalEntry.user_id == self.user_id,
                JournalEntry.created_at >= cutoff_date
            ).order_by(JournalEntry.created_at.asc())
        ).all()

        processed_entries: List[ProcessedEntry] = []
        for entry in journal_db_entries:
            themes_list = list(entry.themes.keys()) if entry.themes else []

            processed_entries.append(ProcessedEntry(
                text=entry.text,
                mood=entry.mood if entry.mood is not None else self.text_analyzer.analyze_sentiment_score(entry.text),
                created_at=entry.created_at,
                themes=themes_list,
                # Triggers are not directly stored in ProcessedEntry from DB, will be re-analyzed if needed by PatternAnalyzer
            ))
        return processed_entries

    def _get_top_items(self, items: Dict[str, int], limit: int = 3) -> List[Tuple[str,int]]:
        return sorted(items.items(), key=lambda x: x[1], reverse=True)[:limit]

    def record_journal_entry(self, text: str, mood_rating: Optional[float] = None) -> JournalEntry:
        analyzed_mood = mood_rating if mood_rating is not None else self.text_analyzer.analyze_sentiment_score(text)
        themes = self.text_analyzer.extract_themes(text)
        triggers = self.text_analyzer.identify_triggers(text)
        themes_dict = {theme: 1 for theme in themes} # Simple count for now

        # Consolidate positive and negative triggers into one dictionary for storage
        trigger_words_dict = Counter()
        trigger_words_dict.update(triggers.get('positivi', []))
        trigger_words_dict.update(triggers.get('negativi', []))


        entry = JournalEntry(
            user_id=self.user_id,
            text=text,
            mood=analyzed_mood,
            themes=themes_dict,
            trigger_words=dict(trigger_words_dict) # Store consolidated triggers
        )
        db.session.add(entry)
        db.session.commit()
        return entry
