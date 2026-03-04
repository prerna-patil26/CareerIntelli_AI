"""Resume preprocessing module for cleaning and normalizing resume data."""

from typing import List, Dict, Any
import re


class ResumePreprocessor:
    """Preprocess and normalize resume data."""
    
    def __init__(self):
        """Initialize the preprocessor."""
        self.stopwords = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'])
    
    def preprocess(self, text: str) -> str:
        """
        Preprocess resume text.
        
        Args:
            text: Raw resume text
        
        Returns:
            Cleaned and normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters
        text = re.sub(r'[^a-z0-9\s]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        return text.split()
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove common stopwords from tokens."""
        return [token for token in tokens if token not in self.stopwords]
    
    def normalize_job_titles(self, job_title: str) -> str:
        """Normalize job title variations."""
        job_title = job_title.lower().strip()
        
        # Common normalizations
        normalizations = {
            'sr.': 'senior',
            'jr.': 'junior',
            'dev': 'developer',
            'eng': 'engineer'
        }
        
        for key, value in normalizations.items():
            job_title = job_title.replace(key, value)
        
        return job_title
