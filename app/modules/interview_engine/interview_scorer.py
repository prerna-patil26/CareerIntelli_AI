"""Interview scorer module for calculating interview scores."""

from typing import Dict, Any, List


class InterviewScorer:
    """Calculate and track interview performance scores."""
    
    def __init__(self):
        """Initialize the interview scorer."""
        self.max_score = 100
        self.individual_scores = []
    
    def add_score(self, score: float) -> None:
        """
        Add an individual question score.
        
        Args:
            score: Score for this question (0-1)
        """
        self.individual_scores.append(score)
    
    def calculate_overall_score(self) -> float:
        """
        Calculate overall interview score.
        
        Returns:
            Overall score (0-100)
        """
        if not self.individual_scores:
            return 0
        
        average = sum(self.individual_scores) / len(self.individual_scores)
        return average * self.max_score
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive performance summary.
        
        Returns:
            Performance summary with various metrics
        """
        if not self.individual_scores:
            return {'error': 'No scores available'}
        
        overall_score = self.calculate_overall_score()
        average_score = sum(self.individual_scores) / len(self.individual_scores)
        
        return {
            'overall_score': overall_score,
            'average_score': average_score,
            'total_questions': len(self.individual_scores),
            'min_score': min(self.individual_scores),
            'max_score': max(self.individual_scores),
            'performance_level': self._get_performance_level(overall_score)
        }
    
    def _get_performance_level(self, score: float) -> str:
        """
        Determine performance level based on score.
        
        Args:
            score: Overall score
        
        Returns:
            Performance level (Excellent, Good, Average, Poor)
        """
        if score >= 80:
            return 'Excellent'
        elif score >= 60:
            return 'Good'
        elif score >= 40:
            return 'Average'
        else:
            return 'Needs Improvement'
