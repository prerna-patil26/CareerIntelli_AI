"""Question selector module for intelligent question selection."""

from typing import List, Dict, Any
import random


class QuestionSelector:
    """Intelligently select interview questions."""
    
    def __init__(self):
        """Initialize the question selector."""
        self.question_history = {}
        self.difficulty_progression = ['easy', 'medium', 'hard']
    
    def select_next_question(self, 
                            available_questions: List[Dict[str, Any]],
                            asked_questions: List[str],
                            user_performance: float = 0.5) -> Dict[str, Any]:
        """
        Select next question based on available questions and user performance.
        
        Args:
            available_questions: List of available questions
            asked_questions: List of already asked question IDs
            user_performance: User's current performance score (0-1)
        
        Returns:
            Selected question
        """
        # Filter out already asked questions
        remaining = [q for q in available_questions if q['id'] not in asked_questions]
        
        if not remaining:
            return {}
        
        # Select based on performance (adaptive difficulty)
        if user_performance > 0.8:
            # Ask harder questions
            selected = [q for q in remaining if q.get('difficulty') == 'hard']
        elif user_performance < 0.4:
            # Ask easier questions
            selected = [q for q in remaining if q.get('difficulty') == 'easy']
        else:
            # Mixed difficulty
            selected = remaining
        
        if not selected:
            selected = remaining
        
        return random.choice(selected)
    
    def get_question_sequence(self, 
                             available_questions: List[Dict[str, Any]], 
                             number_of_questions: int = 5) -> List[Dict[str, Any]]:
        """
        Get a sequence of questions for the interview.
        
        Args:
            available_questions: List of available questions
            number_of_questions: Number of questions to select
        
        Returns:
            List of selected questions
        """
        return random.sample(available_questions, min(number_of_questions, len(available_questions)))
