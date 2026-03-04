"""Skill extraction module for identifying skills from resume text."""

from typing import List, Set
import re


class SkillExtractor:
    """Extract and identify skills from resume text."""
    
    def __init__(self):
        """Initialize the skill extractor."""
        # Common technical skills dictionary
        self.skills_database = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift'],
            'frameworks': ['django', 'flask', 'react', 'angular', 'vue', 'spring', 'laravel'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'redis'],
            'tools': ['git', 'docker', 'kubernetes', 'jenkins', 'aws', 'azure'],
            'soft_skills': ['communication', 'leadership', 'teamwork', 'problem solving']
        }
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """
        Extract skills from resume text.
        
        Args:
            text: Resume text
        
        Returns:
            Dictionary of identified skills by category
        """
        text_lower = text.lower()
        extracted = {}
        
        for category, skills in self.skills_database.items():
            found_skills = []
            for skill in skills:
                if re.search(r'\b' + skill + r'\b', text_lower):
                    found_skills.append(skill)
            
            if found_skills:
                extracted[category] = found_skills
        
        return extracted
    
    def extract_technical_skills(self, text: str) -> List[str]:
        """Extract technical skills specifically."""
        all_technical = [
            skill for skills in [
                self.skills_database['programming'],
                self.skills_database['frameworks'],
                self.skills_database['databases'],
                self.skills_database['tools']
            ]
            for skill in skills
        ]
        
        text_lower = text.lower()
        found = [skill for skill in all_technical if skill in text_lower]
        return found
    
    def extract_soft_skills(self, text: str) -> List[str]:
        """Extract soft skills from text."""
        text_lower = text.lower()
        found = [skill for skill in self.skills_database['soft_skills'] if skill in text_lower]
        return found
