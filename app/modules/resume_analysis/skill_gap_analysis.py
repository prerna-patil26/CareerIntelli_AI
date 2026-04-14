"""Skill gap analysis module for identifying missing skills."""

from typing import List, Dict, Any
import pandas as pd
import os


class SkillGapAnalyzer:
    """Analyze skill gaps compared to industry/job requirements."""

    def __init__(self, dataset_path: str = None):

        if dataset_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            dataset_path = os.path.join(
                base_dir, "datasets", "industry_skill_benchmark.csv"
            )

        self.dataset_path = dataset_path
        self.role_skills = self.load_role_skills()

    # ---------------------------------------------------

    def load_role_skills(self) -> Dict[str, List[str]]:

        role_skills = {}

        try:

            df = pd.read_csv(self.dataset_path)

            for _, row in df.iterrows():

                role = str(row.get("role", "")).lower().strip()
                skills = str(row.get("skills", "")).lower()

                skill_list = [s.strip() for s in skills.split(",") if s.strip()]

                if role not in role_skills:
                    role_skills[role] = set()

                role_skills[role].update(skill_list)

            # convert set → list
            role_skills = {k: list(v) for k, v in role_skills.items()}

        except Exception:
            role_skills = {}

        return role_skills

    # ---------------------------------------------------

    def analyze_gap(
        self,
        user_skills: List[str],
        target_role: str
    ) -> Dict[str, Any]:

        user_set = set(s.lower() for s in user_skills)

        required_skills = self.role_skills.get(target_role.lower(), [])

        required_set = set(required_skills)

        matched_skills = list(user_set & required_set)
        missing_skills = list(required_set - user_set)
        extra_skills = list(user_set - required_set)

        coverage = (
            (len(matched_skills) / len(required_set)) * 100
            if required_set else 0
        )

        gap = (
            (len(missing_skills) / len(required_set)) * 100
            if required_set else 0
        )

        return {
            "target_role": target_role,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "extra_skills": extra_skills,
            "coverage_percentage": round(coverage, 2),
            "gap_percentage": round(gap, 2)
        }

    # ---------------------------------------------------

    def prioritize_learning(self, gap_analysis: Dict[str, Any]) -> List[str]:

        missing = gap_analysis.get("missing_skills", [])

        # simple importance grouping
        core_skills = [
            "python",
            "machine learning",
            "deep learning",
            "sql",
            "statistics"
        ]

        priority = []

        for skill in core_skills:
            if skill in missing:
                priority.append(skill)

        for skill in missing:
            if skill not in priority:
                priority.append(skill)

        return priority