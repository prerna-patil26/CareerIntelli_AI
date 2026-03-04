"""Resume scoring module for evaluating resume quality."""

from typing import Dict, Any


class ResumeScorer:
    """Score and evaluate resume quality."""
    
    def __init__(self):
        """Initialize the resume scorer."""
        self.max_score = 100
    
    def score_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score resume based on various criteria.
        
        Args:
            resume_data: Parsed resume data
        
        Returns:
            Dictionary with scoring results
        """
        score = 0
        details = {}
        
        # Check contact information
        contact_score = self._score_contact_info(resume_data)
        score += contact_score
        details['contact_info'] = contact_score
        
        # Check work experience
        experience_score = self._score_experience(resume_data.get('experience', []))
        score += experience_score
        details['experience'] = experience_score
        
        # Check education
        education_score = self._score_education(resume_data.get('education', []))
        score += education_score
        details['education'] = education_score
        
        # Check skills
        skills_score = self._score_skills(resume_data.get('skills', []))
        score += skills_score
        details['skills'] = skills_score
        
        return {
            'overall_score': min(score, self.max_score),
            'max_score': self.max_score,
            'percentage': (min(score, self.max_score) / self.max_score) * 100,
            'breakdown': details
        }
    
    def _score_contact_info(self, resume_data: Dict) -> int:
        """Score based on contact information completeness."""
        score = 0
        if resume_data.get('name'):
            score += 5
        if resume_data.get('email'):
            score += 5
        if resume_data.get('phone'):
            score += 5
        return score
    
    def _score_experience(self, experience: list) -> int:
        """Score based on work experience."""
        if len(experience) >= 5:
            return 25
        elif len(experience) >= 3:
            return 20
        elif len(experience) >= 1:
            return 10
        return 0
    
    def _score_education(self, education: list) -> int:
        """Score based on education."""
        if len(education) >= 2:
            return 20
        elif len(education) >= 1:
            return 15
        return 0
    
    def _score_skills(self, skills: list) -> int:
        """Score based on skills listed."""
        if len(skills) >= 15:
            return 25
        elif len(skills) >= 10:
            return 20
        elif len(skills) >= 5:
            return 15
        elif len(skills) > 0:
            return 10
        return 0
