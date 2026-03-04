"""Skill gap analysis module for identifying missing skills."""

from typing import List, Dict, Any


class SkillGapAnalyzer:
    """Analyze skill gaps compared to job requirements."""
    
    def __init__(self):
        """Initialize the skill gap analyzer."""
        pass
    
    def analyze_gap(self, 
                   user_skills: List[str], 
                   required_skills: List[str]) -> Dict[str, Any]:
        """
        Analyze skill gaps between user and job requirements.
        
        Args:
            user_skills: Skills the user has
            required_skills: Skills required for the job
        
        Returns:
            Dictionary with gap analysis results
        """
        user_set = set(s.lower() for s in user_skills)
        required_set = set(s.lower() for s in required_skills)
        
        missing_skills = required_set - user_set
        matched_skills = user_set & required_set
        extra_skills = user_set - required_set
        
        return {
            'matched_skills': list(matched_skills),
            'missing_skills': list(missing_skills),
            'extra_skills': list(extra_skills),
            'gap_percentage': (len(missing_skills) / len(required_set) * 100) if required_set else 0,
            'coverage_percentage': (len(matched_skills) / len(required_set) * 100) if required_set else 0
        }
    
    def prioritize_learning(self, gap_analysis: Dict[str, Any]) -> List[str]:
        """
        Prioritize which missing skills to learn first.
        
        Args:
            gap_analysis: Result from analyze_gap()
        
        Returns:
            Prioritized list of missing skills
        """
        # TODO: Implement priority logic based on market demand, salary impact, etc.
        return gap_analysis.get('missing_skills', [])
