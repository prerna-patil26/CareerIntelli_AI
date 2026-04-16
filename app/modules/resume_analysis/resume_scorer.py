import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ResumeScorer:
    """Advanced ATS scoring with skills + strength + full resume evaluation."""

    MAX_POINTS = {
        "contact_info": 10,
        "skills": 40,
        "experience": 25,
        "education": 15,
        "projects": 10,
    }

    def __init__(self):
        self.max_score = 100

    def score_resume(self, resume_data: Dict[str, Any], target_role: Optional[str] = None):
        try:
            total_score = 0
            details = {}
            suggestions = []

            # ---------------- CONTACT ----------------
            contact_score = self._score_contact_info(resume_data)
            total_score += contact_score
            details["contact"] = contact_score

            if contact_score < 8:
                suggestions.append("Add complete contact details")

            # ---------------- SKILLS ----------------
            skills = resume_data.get("skills", [])
            skill_scores = resume_data.get("skill_scores", {})

            skills_score = self._score_skills(skills, skill_scores)
            total_score += skills_score
            details["skills"] = skills_score

            if skills_score < 20:
                suggestions.append("Add more relevant and strong skills")

            # ---------------- EXPERIENCE ----------------
            experience = resume_data.get("experience", [])
            exp_score = self._score_experience(experience)
            total_score += exp_score
            details["experience"] = exp_score

            if exp_score == 0:
                suggestions.append("Add work experience or internships")

            # ---------------- EDUCATION ----------------
            education = resume_data.get("education", [])
            edu_score = self._score_education(education)
            total_score += edu_score
            details["education"] = edu_score

            if edu_score == 0:
                suggestions.append("Add educational qualifications")

            # ---------------- PROJECTS ----------------
            projects = resume_data.get("projects", [])
            project_score = self._score_projects(projects)
            total_score += project_score
            details["projects"] = project_score

            if project_score == 0:
                suggestions.append("Add projects to strengthen resume")

            final_score = min(total_score, self.max_score)

            return {
                "overall_score": final_score,
                "percentage": round(final_score, 2),
                "breakdown": details,
                "suggestions": suggestions,
            }

        except Exception as e:
            logger.error(f"Error scoring resume: {e}")
            return {
                "overall_score": 0,
                "percentage": 0,
                "breakdown": {},
                "suggestions": ["Error in scoring"],
            }

    # ---------------- CONTACT ----------------
    def _score_contact_info(self, resume_data):
        score = 0
        if resume_data.get("email"):
            score += 5
        if resume_data.get("phone"):
            score += 5
        return score

    # ---------------- SKILLS (MAIN UPGRADE 🔥) ----------------
    def _score_skills(self, skills: List[str], skill_scores: Dict[str, int]):
        if not skills:
            return 0

        count = len(skills)

        # Skill count score (max 25)
        count_score = min(count * 2, 25)

        # Strength score (max 15)
        if skill_scores:
            avg_strength = sum(skill_scores.values()) / len(skill_scores)
            strength_score = min(avg_strength * 0.3, 15)
        else:
            strength_score = 0

        return min(count_score + strength_score, 40)

    # ---------------- EXPERIENCE ----------------
    def _score_experience(self, experience: List[str]):
        if not experience:
            return 0

        score = 0

        for exp in experience:
            try:
                words = exp.split()
                for w in words:
                    if w.isdigit():
                        years = int(w)
                        score += years * 4
                        break
            except:
                continue

        return min(score, 25)

    # ---------------- EDUCATION ----------------
    def _score_education(self, education: List[str]):
        if not education:
            return 0

        score = 0

        for degree in education:
            d = degree.lower()
            if "phd" in d or "master" in d:
                score += 10
            elif "bachelor" in d or "btech" in d or "bsc" in d:
                score += 7
            else:
                score += 5

        return min(score, 15)

    # ---------------- PROJECTS ----------------
    def _score_projects(self, projects: List[str]):
        if not projects:
            return 0

        score = len(projects) * 3
        return min(score, 10)