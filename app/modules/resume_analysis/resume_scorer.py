"""Resume scoring module for evaluating resume quality with relevance weighting."""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ResumeScorer:
    """Score and evaluate resume quality with AI-aware metrics."""

    # Score weights for different components
    WEIGHTS = {
        "contact_info": 0.10,
        "skills": 0.35,
        "experience": 0.25,
        "education": 0.15,
        "projects": 0.15,
    }

    # Maximum points for each category
    MAX_POINTS = {
        "contact_info": 10,
        "skills": 40,
        "experience": 25,
        "education": 15,
        "projects": 15,
    }

    def __init__(self):
        """Initialize resume scorer."""
        self.max_score = 100

    def score_resume(
        self, 
        resume_data: Dict[str, Any],
        target_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Score resume with detailed breakdown and suggestions.
        
        Args:
            resume_data: Parsed resume data
            target_role: Target job role for relevance scoring (optional)
            
        Returns:
            Dictionary with scores, breakdown, and suggestions
        """
        try:
            score = 0
            details = {}
            suggestions = []
            relevance_scores = {}

            # Contact Info
            contact_score = self._score_contact_info(resume_data)
            score += contact_score
            details["contact"] = contact_score

            if contact_score < 8:
                suggestions.append("✉️ Add complete contact information (email + phone)")

            # Skills
            skills = resume_data.get("skills", [])
            if isinstance(skills, dict):
                skills = [s for v in skills.values() for s in v]

            skills_score, skill_relevance = self._score_skills(
                skills, 
                resume_data, 
                target_role
            )
            score += skills_score
            details["skills"] = skills_score
            relevance_scores["skills"] = skill_relevance

            if skills_score < 20:
                suggestions.append("🔧 Add more relevant technical skills to match job requirements")

            # Experience
            experience = resume_data.get("experience", [])
            exp_score = self._score_experience(experience)
            score += exp_score
            details["experience"] = exp_score

            if exp_score == 0:
                suggestions.append("💼 Add internship or professional work experience")
            elif exp_score < 15:
                suggestions.append("📈 Highlight more work experience or internships")

            # Education
            education = resume_data.get("education", [])
            edu_score = self._score_education(education)
            score += edu_score
            details["education"] = edu_score

            if edu_score == 0:
                suggestions.append("🎓 Add your academic qualifications and degrees")

            # Projects
            projects = resume_data.get("projects", [])
            project_score = self._score_projects(projects)
            score += project_score
            details["projects"] = project_score

            if project_score == 0:
                suggestions.append("🚀 Showcase personal or academic projects")

            final_score = min(score, self.max_score)

            return {
                "overall_score": final_score,
                "percentage": round((final_score / self.max_score) * 100, 2),
                "breakdown": details,
                "suggestions": suggestions,
                "relevance_scores": relevance_scores,
            }

        except Exception as e:
            logger.error(f"Error scoring resume: {e}")
            return {
                "overall_score": 0,
                "percentage": 0,
                "breakdown": {},
                "suggestions": ["Error in scoring. Please try again."],
                "relevance_scores": {},
            }

    def _score_contact_info(self, resume_data: Dict) -> int:
        """Score contact information completeness."""
        score = 0

        if resume_data.get("email"):
            score += 5

        if resume_data.get("phone"):
            score += 5

        return min(score, self.MAX_POINTS["contact_info"])

    def _score_skills(
        self, 
        skills: List[str],
        resume_data: Dict[str, Any],
        target_role: Optional[str] = None
    ) -> tuple:
        """
        Score skills with relevance weighting if target role provided.
        
        Args:
            skills: List of extracted skills
            resume_data: Full resume data
            target_role: Optional target role for relevance scoring
            
        Returns:
            Tuple of (score, relevance_percentage)
        """
        if not skills:
            return 0, 0.0

        count = len(skills)
        
        # Base score from skill count
        if count >= 15:
            base_score = 40
        elif count >= 12:
            base_score = 38
        elif count >= 9:
            base_score = 35
        elif count >= 6:
            base_score = 28
        elif count >= 3:
            base_score = 18
        else:
            base_score = 10

        relevance_score = 0.0

        # Bonus points for relevance if we have target role
        if target_role:
            try:
                from app.modules.resume_analysis.skill_gap_analysis import SkillGapAnalyzer
                
                gap_analyzer = SkillGapAnalyzer()
                gap_result = gap_analyzer.analyze_gap(skills, target_role)
                
                matched = len(gap_result.get("matched_skills", []))
                required = len(gap_result.get("matched_skills", [])) + len(
                    gap_result.get("missing_skills", [])
                )
                
                if required > 0:
                    relevance_score = (matched / required) * 100
                    
                    # Add relevance bonus (up to 10 points)
                    relevance_bonus = min((matched / max(required, 1)) * 10, 10)
                    base_score = min(base_score + relevance_bonus, self.MAX_POINTS["skills"])
                    
            except Exception as e:
                logger.warning(f"Could not calculate skill relevance: {e}")
                relevance_score = 0.0

        return min(base_score, self.MAX_POINTS["skills"]), relevance_score

    def _score_experience(self, experience: List[str]) -> int:
        """
        Score work experience.
        
        Args:
            experience: List of experience entries
            
        Returns:
            Experience score
        """
        if not experience:
            return 0

        count = len(experience)

        if count >= 5:
            return 25
        elif count >= 3:
            return 22
        elif count >= 2:
            return 18
        elif count >= 1:
            return 12

        return 0

    def _score_education(self, education: List[str]) -> int:
        """
        Score educational qualifications.
        
        Args:
            education: List of education entries
            
        Returns:
            Education score
        """
        if not education:
            return 0

        count = len(education)

        # Higher degree scores more
        higher_degrees = [
            "phd", "master", "mtech", "mca", "msc", "m.s.", "m.tech"
        ]
        bachelor_degrees = [
            "bachelor", "btech", "bsc", "b.tech", "b.s.", "diploma"
        ]

        score = 0
        for degree in education:
            if any(hd in degree.lower() for hd in higher_degrees):
                score += 10
            elif any(bd in degree.lower() for bd in bachelor_degrees):
                score += 7
            else:
                score += 5

        return min(score, self.MAX_POINTS["education"])

    def _score_projects(self, projects: List[str]) -> int:
        """
        Score personal and academic projects.
        
        Args:
            projects: List of project entries
            
        Returns:
            Projects score
        """
        if not projects:
            return 0

        count = len(projects)

        if count >= 5:
            return 15
        elif count >= 3:
            return 13
        elif count >= 2:
            return 11
        elif count >= 1:
            return 8

        return 0