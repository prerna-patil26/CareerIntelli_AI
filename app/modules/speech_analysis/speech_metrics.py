"""Speech metrics analysis module."""

from typing import Dict, Any


class SpeechMetrics:
    """Analyze speech metrics like pace, clarity, and confidence."""
    
    def __init__(self):
        """Initialize speech metrics analyzer."""
        pass
    
    def calculate_speech_rate(self, text: str, duration_seconds: float) -> float:
        """
        Calculate speech rate (words per minute).
        
        Args:
            text: Transcribed text
            duration_seconds: Duration of speech in seconds
        
        Returns:
            Words per minute
        """
        if duration_seconds == 0:
            return 0
        
        word_count = len(text.split())
        minutes = duration_seconds / 60
        
        return word_count / minutes if minutes > 0 else 0
    
    def analyze_confidence(self, text: str) -> Dict[str, Any]:
        """
        Analyze speech confidence indicators.
        
        Args:
            text: Transcribed text
        
        Returns:
            Dictionary with confidence indicators
        """
        confidence_indicators = {
            'strong_language': ['definitely', 'certainly', 'absolutely', 'confident'],
            'weak_language': ['maybe', 'perhaps', 'might', 'could', 'somewhat']
        }
        
        text_lower = text.lower()
        strong_count = sum(1 for word in confidence_indicators['strong_language'] 
                          if word in text_lower)
        weak_count = sum(1 for word in confidence_indicators['weak_language'] 
                        if word in text_lower)
        
        confidence_score = strong_count - weak_count
        
        return {
            'confidence_indicators': confidence_score,
            'strong_language_count': strong_count,
            'weak_language_count': weak_count,
            'confidence_level': 'High' if confidence_score > 0 else 'Moderate' if confidence_score == 0 else 'Low'
        }
    
    def analyze_clarity(self, text: str) -> float:
        """
        Analyze speech clarity (0-1 scale).
        
        Args:
            text: Transcribed text
        
        Returns:
            Clarity score
        """
        if not text:
            return 0
        
        # Simple clarity metric based on sentence structure
        sentences = len([s for s in text.split('.') if s.strip()])
        words = len(text.split())
        
        avg_sentence_length = words / sentences if sentences > 0 else 0
        
        # Optimal sentence length is 15-20 words
        if 15 <= avg_sentence_length <= 20:
            clarity = 1.0
        elif 10 <= avg_sentence_length <= 25:
            clarity = 0.8
        elif 5 <= avg_sentence_length <= 30:
            clarity = 0.6
        else:
            clarity = 0.4
        
        return clarity
