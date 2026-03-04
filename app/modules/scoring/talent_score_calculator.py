"""Talent score calculator module."""

from typing import Dict, Any


class TalentScoreCalculator:
    """Calculate comprehensive talent score for candidates."""
    
    def __init__(self):
        """Initialize talent score calculator."""
        self.max_score = 100
    
    def calculate_talent_score(self, 
                              resume_score: float,
                              interview_score: float,
                              engagement_score: float,
                              skill_match: float) -> Dict[str, Any]:
        """
        Calculate overall talent score.
        
        Args:
            resume_score: Score from resume analysis (0-100)
            interview_score: Score from interview (0-100)
            engagement_score: Score from engagement analysis (0-100)
            skill_match: Skill match percentage (0-100)
        
        Returns:
            Dictionary with talent score and breakdown
        """
        # Weighted average
        total_score = (
            resume_score * 0.25 +
            interview_score * 0.40 +
            engagement_score * 0.20 +
            skill_match * 0.15
        )
        
        return {
            'overall_talent_score': total_score,
            'max_score': self.max_score,
            'percentile': total_score,
            'talent_level': self._get_talent_level(total_score),
            'breakdown': {
                'resume_score': resume_score,
                'interview_score': interview_score,
                'engagement_score': engagement_score,
                'skill_match': skill_match
            }
        }
    
    def _get_talent_level(self, score: float) -> str:
        """
        Determine talent level based on score.
        
        Args:
            score: Overall score
        
        Returns:
            Talent level description
        """
        if score >= 85:
            return 'Exceptional'
        elif score >= 70:
            return 'Strong'
        elif score >= 55:
            return 'Moderate'
        elif score >= 40:
            return 'Developing'
        else:
            return 'Needs Improvement'
