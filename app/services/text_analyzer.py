import random

class TextAnalyzer:
    def __init__(self):
        # These would be loaded from a more sophisticated source in a real implementation
        self.emotional_triggers_lexicon = {
            'positivi': ['happy', 'joy', 'good', 'great', 'love', 'excellent', 'wonderful', 'amazing', 'fantastic'],
            'negativi': ['sad', 'bad', 'terrible', 'fear', 'angry', 'hate', 'awful', 'problem', 'stress']
        }
        self.themes_lexicon = ['work', 'family', 'friends', 'health', 'finance', 'hobby', 'future']

    def extract_themes(self, text: str, num_themes: int = 2) -> list:
        # Placeholder: randomly pick some themes
        words = text.lower().split()
        extracted = [theme for theme in self.themes_lexicon if theme in words]
        if not extracted: # if no direct match, pick random
             extracted = random.sample(self.themes_lexicon, min(num_themes, len(self.themes_lexicon)))
        return extracted[:num_themes]

    def identify_triggers(self, text: str) -> dict:
        # Placeholder: very basic trigger identification
        words = text.lower().split()
        positivi = [word for word in words if word in self.emotional_triggers_lexicon['positivi']]
        negativi = [word for word in words if word in self.emotional_triggers_lexicon['negativi']]
        return {'positivi': positivi, 'negativi': negativi}

    def analyze_emotional_intensity(self, text: str) -> float:
        # Placeholder: returns a random intensity score between 0 and 1
        intensity_score = random.uniform(0.0, 1.0) # Example: 0=low, 1=high

        words = text.lower().split()
        positive_count = sum(1 for word in words if word in self.emotional_triggers_lexicon['positivi'])
        negative_count = sum(1 for word in words if word in self.emotional_triggers_lexicon['negativi'])

        if positive_count > negative_count:
            intensity_score = 0.5 + intensity_score * 0.5
        elif negative_count > positive_count:
             intensity_score = 0.5 - intensity_score * 0.5
        return max(0.0, min(1.0, intensity_score))

    def analyze_sentiment_score(self, text: str) -> float:
        # Placeholder: returns a score from 0 (very negative) to 5 (very positive)
        intensity = self.analyze_emotional_intensity(text)
        if intensity < 0.2: return 1.0
        if intensity < 0.4: return 2.0
        if intensity < 0.6: return 3.0
        if intensity < 0.8: return 4.0
        return 5.0
