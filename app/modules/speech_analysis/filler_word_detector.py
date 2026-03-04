"""Filler word detection module."""

from typing import Dict, List, Any


class FillerWordDetector:
    """Detect filler words and speech disfluencies."""
    
    def __init__(self):
        """Initialize the filler word detector."""
        self.filler_words = [
            'um', 'uh', 'like', 'you know', 'basically', 'actually',
            'literally', 'right', 'okay', 'so', 'well', 'anyway',
            'i mean', 'kind of', 'sort of', 'just', 'really'
        ]
    
    def detect_fillers(self, text: str) -> Dict[str, Any]:
        """
        Detect filler words in transcribed text.
        
        Args:
            text: Transcribed speech text
        
        Returns:
            Dictionary with detected fillers and metrics
        """
        text_lower = text.lower()
        words = text_lower.split()
        
        detected_fillers = []
        filler_count = 0
        
        for filler in self.filler_words:
            count = text_lower.count(filler)
            if count > 0:
                detected_fillers.append({
                    'word': filler,
                    'count': count
                })
                filler_count += count
        
        word_count = len(words)
        filler_percentage = (filler_count / word_count * 100) if word_count > 0 else 0
        
        return {
            'total_fillers': filler_count,
            'unique_fillers': detected_fillers,
            'filler_percentage': filler_percentage,
            'quality_score': max(0, 100 - filler_percentage)
        }
    
    def get_filler_frequency(self, text: str) -> Dict[str, int]:
        """Get frequency of each filler word."""
        text_lower = text.lower()
        frequency = {}
        
        for filler in self.filler_words:
            count = text_lower.count(filler)
            if count > 0:
                frequency[filler] = count
        
        return dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True))
