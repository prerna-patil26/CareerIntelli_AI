"""Skill extraction module for identifying skills from resume text."""

import logging
import re
from typing import List, Dict
import pandas as pd
import os

logger = logging.getLogger(__name__)


class SkillExtractor:
    """Extract and identify technical and soft skills from resume text."""

    def __init__(self):
        """Initialize skill extractor with skill database."""
        self.skills_database = self._load_skills()
        # Pre-compile regex patterns for performance
        self._compiled_patterns = {}

    def _load_skills(self) -> Dict[str, List[str]]:
        """
        Load skills from CSV dataset.
        
        Returns:
            Dictionary with skill categories and lists
        """
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            dataset_path = os.path.join(
                base_dir, "datasets", "industry_skill_benchmark.csv"
            )

            df = pd.read_csv(dataset_path)
            skills = set()

            for col in df.columns:
                df[col] = df[col].astype(str).str.lower()

                for cell in df[col]:
                    if cell == "nan":
                        continue

                    for s in cell.split(","):
                        s = s.strip()
                        if len(s) > 1:
                            skills.add(s)

            logger.info(f"Loaded {len(skills)} technical skills from CSV")
            return {"technical": list(skills)}

        except Exception as e:
            logger.warning(f"Failed to load skills from CSV: {e}. Using defaults.")
            return {
                "technical": [
                    "python", "java", "javascript", "c++", "c#", "ruby", "php",
                    "sql", "nosql", "mongodb", "postgresql", "mysql",
                    "machine learning", "deep learning", "nlp", "computer vision",
                    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
                    "flask", "django", "fastapi", "spring", "react", "angular", "vue",
                    "docker", "kubernetes", "jenkins", "git", "aws", "gcp", "azure",
                    "tableau", "power bi", "matlab", "r", "scala", "go", "rust",
                    "html", "css", "json", "xml", "rest", "graphql", "oauth",
                    "agile", "scrum", "jira", "linux", "windows", "unix"
                ],
                "soft_skills": [
                    "communication", "leadership", "teamwork", "problem solving",
                    "critical thinking", "project management", "time management"
                ]
            }

    def _build_regex_pattern(self, skills: List[str]) -> re.Pattern:
        """
        Build a single compiled regex pattern for all skills.
        
        Args:
            skills: List of skills to match
            
        Returns:
            Compiled regex pattern
        """
        # Escape and sort by length (longest first) to match multi-word skills
        sorted_skills = sorted(set(skills), key=len, reverse=True)
        pattern_str = r"\b(" + "|".join(re.escape(skill) for skill in sorted_skills) + r")\b"
        return re.compile(pattern_str, re.IGNORECASE)

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """
        Extract all categorized skills from text.
        
        Args:
            text: Resume text to analyze
            
        Returns:
            Dictionary with skill categories and matched skills
        """
        text = text.lower()
        extracted = {}

        for category, skills in self.skills_database.items():
            found_skills = self._extract_skills_with_pattern(text, skills)
            if found_skills:
                extracted[category] = found_skills

        return extracted

    def extract_technical_skills(self, text: str) -> List[str]:
        """
        Extract technical skills from text (optimized).
        
        Args:
            text: Resume text to analyze
            
        Returns:
            List of unique technical skills found
        """
        text = text.lower()
        technical_skills = self.skills_database.get("technical", [])
        return self._extract_skills_with_pattern(text, technical_skills)

    def extract_soft_skills(self, text: str) -> List[str]:
        """
        Extract soft skills from text.
        
        Args:
            text: Resume text to analyze
            
        Returns:
            List of unique soft skills found
        """
        text = text.lower()
        soft_skills = self.skills_database.get("soft_skills", [])
        return self._extract_skills_with_pattern(text, soft_skills)

    def _extract_skills_with_pattern(self, text: str, skills: List[str]) -> List[str]:
        """
        Extract skills using compiled regex pattern (performance optimized).
        
        Args:
            text: Resume text (should be lowercase)
            skills: List of skills to match
            
        Returns:
            List of matched skills
        """
        # Use cached pattern if available
        skills_key = tuple(sorted(skills))
        if skills_key not in self._compiled_patterns:
            self._compiled_patterns[skills_key] = self._build_regex_pattern(skills)
        
        pattern = self._compiled_patterns[skills_key]
        matches = pattern.findall(text)
        
        return list(set(matches))
    def extract_technical_skills_with_score(self, text):
        text = text.lower()
        technical_skills = self.skills_database.get("technical", [])

        skill_scores = {}

    # 🔥 Simple section extraction
        def extract_section(text, keywords):
            for word in keywords:
                if word in text:
                    start = text.find(word)
                    return text[start:start + 500]
            return ""

        projects_section = extract_section(text, ["project", "projects"])
        experience_section = extract_section(text, ["experience", "work experience"])

        for skill in technical_skills:

            count = text.count(skill)

            if count > 0:

                # ✅ Frequency score (0–40)
                frequency_score = min(count * 10, 40)

                # ✅ Project bonus (30)
                project_score = 30 if skill in projects_section else 0

                # ✅ Experience bonus (30)
                experience_score = 30 if skill in experience_section else 0

                # 🔥 FINAL SCORE
                score = frequency_score + project_score + experience_score

                skill_scores[skill] = min(score, 100)

        return skill_scores