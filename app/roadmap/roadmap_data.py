"""Load and manage career roadmap data with richer skill hierarchy."""

from __future__ import annotations

import os
from typing import Dict, List, Optional

import pandas as pd


DEFAULT_TIME_ESTIMATE = "3-4 weeks"
LEVEL_STAGE_MAP = {0: "Start", 1: "Build", 2: "Advance"}


SKILL_METADATA = {
    "Python": {
        "description": "Core programming language for data, automation, and backend work",
        "level": 0,
        "why": "Python gives you a practical foundation for scripting, problem solving, automation, and many AI workflows.",
        "concepts": ["Syntax and control flow", "Functions and modules", "OOP and clean code", "Problem solving patterns"],
        "tools": ["NumPy", "Pandas", "Requests", "Jupyter"],
        "sub_skills": ["Basic Syntax", "OOP Concepts", "Functions", "Libraries"],
        "libraries": ["NumPy", "Pandas", "Matplotlib", "Scikit-learn"],
        "time_estimate": "4-6 weeks",
        "real_world_usage": "Used in automation pipelines, backend APIs, data notebooks, and ML projects.",
        "usage_examples": ["Automating reports", "Cleaning datasets", "Building backend services"],
        "start_steps": ["Learn variables, loops, and functions", "Solve small coding problems", "Use one library in a mini project"],
    },
    "SQL": {
        "description": "Essential query language for structured data and analytics",
        "level": 0,
        "why": "SQL is how teams retrieve, validate, and analyze the data behind products and dashboards.",
        "concepts": ["SELECT and filtering", "JOINs", "Aggregations", "Subqueries"],
        "tools": ["PostgreSQL", "MySQL", "SQLite", "DB Browser"],
        "sub_skills": ["SELECT Queries", "JOINs", "Aggregations", "Indexing"],
        "libraries": [],
        "time_estimate": "2-3 weeks",
        "real_world_usage": "Used for analytics, QA validation, product reporting, and backend data access.",
        "usage_examples": ["Building reports", "Validating app data", "Exploring user behavior"],
        "start_steps": ["Practice simple queries", "Move to joins and grouping", "Answer real business questions with sample data"],
    },
    "Machine Learning": {
        "description": "Build predictive models and systems that learn from data",
        "level": 2,
        "why": "Machine learning turns raw data into predictions, recommendations, and intelligent product features.",
        "concepts": ["Supervised learning", "Model evaluation", "Feature engineering", "Bias and overfitting"],
        "tools": ["Scikit-learn", "XGBoost", "Jupyter", "TensorFlow"],
        "sub_skills": ["Supervised Learning", "Unsupervised Learning", "Model Evaluation", "Feature Engineering"],
        "libraries": ["Scikit-learn", "XGBoost", "LightGBM"],
        "time_estimate": "8-12 weeks",
        "real_world_usage": "Used in recommendation engines, fraud detection, forecasting, and personalization systems.",
        "usage_examples": ["Churn prediction", "Recommendation models", "Classification systems"],
        "start_steps": ["Learn statistics basics", "Train simple models", "Compare results on one real dataset"],
    },
    "React": {
        "description": "Component-based library for modern, interactive frontends",
        "level": 1,
        "why": "React helps you build reusable interfaces and is widely used in production frontend teams.",
        "concepts": ["Components", "Props and state", "Hooks", "Data fetching"],
        "tools": ["React DevTools", "Vite", "Next.js", "React Router"],
        "sub_skills": ["Components", "Hooks", "State Management", "Routing"],
        "libraries": ["Redux", "Next.js", "Material UI"],
        "time_estimate": "4-6 weeks",
        "real_world_usage": "Used in dashboards, SaaS products, e-commerce interfaces, and admin tools.",
        "usage_examples": ["Building dashboards", "Creating dynamic forms", "Shipping single-page apps"],
        "start_steps": ["Learn JSX and components", "Build a small app", "Connect the UI to an API"],
    },
    "Statistics": {
        "description": "Math foundation for data analysis, experimentation, and decision-making",
        "level": 0,
        "why": "Statistics helps you reason about uncertainty, evidence, and the meaning behind data.",
        "concepts": ["Probability", "Distributions", "Hypothesis testing", "Correlation and regression"],
        "tools": ["SciPy", "Statsmodels", "Excel", "Jupyter"],
        "sub_skills": ["Descriptive Statistics", "Probability", "Hypothesis Testing", "Regression"],
        "libraries": ["SciPy", "Statsmodels"],
        "time_estimate": "6-8 weeks",
        "real_world_usage": "Used in A/B testing, model evaluation, trend analysis, and forecasting.",
        "usage_examples": ["Experiment analysis", "Confidence interval reporting", "Trend validation"],
        "start_steps": ["Start with descriptive statistics", "Study probability and distributions", "Apply concepts to one dataset"],
    },
    "Data Analysis": {
        "description": "Turn raw data into patterns, answers, and business insight",
        "level": 0,
        "why": "Data analysis is the bridge between raw datasets and practical decision-making.",
        "concepts": ["Cleaning data", "Exploratory analysis", "Finding trends", "Communicating insights"],
        "tools": ["Excel", "Pandas", "Jupyter", "Tableau"],
        "sub_skills": ["Data Cleaning", "EDA", "Trend Analysis", "Reporting"],
        "libraries": ["Pandas", "Matplotlib", "Seaborn"],
        "time_estimate": "4-5 weeks",
        "real_world_usage": "Used in product analytics, finance reporting, marketing insights, and operations tracking.",
        "usage_examples": ["Customer behavior analysis", "Sales dashboards", "Product KPI reviews"],
        "start_steps": ["Analyze CSV data", "Create simple charts", "Write a short insight summary for stakeholders"],
    },
    "Pandas": {
        "description": "Work efficiently with tabular data in Python projects",
        "level": 1,
        "why": "Pandas speeds up cleaning, transforming, and inspecting large datasets.",
        "concepts": ["DataFrames", "Filtering", "Grouping", "Merging data"],
        "tools": ["Jupyter", "CSV/Excel datasets", "NumPy"],
        "sub_skills": ["DataFrames", "Filtering", "Grouping", "Merging"],
        "libraries": ["NumPy", "Matplotlib"],
        "time_estimate": "2-4 weeks",
        "real_world_usage": "Used in analytics notebooks, feature engineering, and reporting pipelines.",
        "usage_examples": ["Cleaning spreadsheets", "Transforming datasets", "Building data prep pipelines"],
        "start_steps": ["Load CSV files", "Practice filtering and grouping", "Build a mini cleaning workflow"],
    },
    "Data Visualization": {
        "description": "Present insights through clear, decision-friendly visuals",
        "level": 1,
        "why": "Visualization makes analysis easier to understand, act on, and communicate.",
        "concepts": ["Chart selection", "Storytelling with data", "Dashboard clarity", "Annotation and context"],
        "tools": ["Matplotlib", "Seaborn", "Tableau", "Power BI"],
        "sub_skills": ["Chart Types", "Dashboards", "Storytelling", "Insight Communication"],
        "libraries": ["Matplotlib", "Seaborn", "Plotly"],
        "time_estimate": "2-4 weeks",
        "real_world_usage": "Used in stakeholder dashboards, reports, BI tools, and presentations.",
        "usage_examples": ["Executive dashboards", "KPI trend charts", "Product review decks"],
        "start_steps": ["Learn common chart types", "Visualize one cleaned dataset", "Explain the key takeaway from each chart"],
    },
}


def _generic_skill_meta(skill: str) -> Dict:
    lower = skill.lower()
    return {
        "description": f"Important {skill} capability for your roadmap",
        "level": 1,
        "why": f"{skill} helps you handle real responsibilities in your target role and makes you more job-ready.",
        "concepts": [f"{skill} fundamentals", f"Common workflows in {skill}", f"Best practices for {skill}"],
        "tools": [skill],
        "sub_skills": [f"{skill} basics", f"{skill} practice", f"{skill} projects"],
        "libraries": [],
        "time_estimate": DEFAULT_TIME_ESTIMATE,
        "real_world_usage": f"{skill} is commonly used in practical project work, collaboration, and production tasks.",
        "usage_examples": [f"Applying {lower} in projects", f"Using {lower} in interviews", f"Demonstrating {lower} on your resume"],
        "start_steps": [f"Learn the basics of {skill}", f"Practice {skill} with guided exercises", f"Build one mini project using {skill}"],
    }


class RoadmapDataManager:
    """Manages career roadmap data with rich skill hierarchy."""

    def __init__(self):
        self.df = None
        self.roles_skills_map: Dict[str, List[str]] = {}
        self.all_roles: List[str] = []
        self.skill_hierarchy: Dict[str, Dict] = {}
        self._load_dataset()
        self._build_skill_hierarchy()

    def _load_dataset(self) -> None:
        dataset_path = os.path.join(os.path.dirname(__file__), "../datasets/career_prediction_dataset.csv")
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset not found at {dataset_path}")

        self.df = pd.read_csv(dataset_path)
        self._build_roles_map()

    def _build_roles_map(self) -> None:
        self.all_roles = sorted(self.df["career_label"].unique().tolist())

        for role in self.all_roles:
            role_df = self.df[self.df["career_label"] == role]
            all_skills_str = role_df["skills"].str.split(", ")
            skills_set = set()

            for skills_list in all_skills_str:
                skills_set.update(skills_list)

            self.roles_skills_map[role] = self._order_skills_by_level(sorted(skills_set))

    def _order_skills_by_level(self, skills: List[str]) -> List[str]:
        skill_priority = {skill: self._resolve_skill_meta(skill).get("level", 1) for skill in skills}
        return sorted(skills, key=lambda skill: (skill_priority.get(skill, 1), skill))

    def _resolve_skill_meta(self, skill: str) -> Dict:
        return {**_generic_skill_meta(skill), **SKILL_METADATA.get(skill, {})}

    def _build_skill_hierarchy(self) -> None:
        for skill in self._get_all_skills():
            meta = self._resolve_skill_meta(skill)
            level = meta.get("level", 1)
            intro = meta.get("description", f"Master {skill} for career advancement")
            self.skill_hierarchy[skill] = {
                "name": skill,
                "intro": intro,
                "description": intro,
                "level": level,
                "stage_label": LEVEL_STAGE_MAP.get(level, "Build"),
                "why": meta.get("why"),
                "why_important": meta.get("why"),
                "concepts": meta.get("concepts", []),
                "tools": meta.get("tools", []),
                "what_to_learn": {
                    "concepts": meta.get("concepts", []),
                    "tools": meta.get("tools", []),
                },
                "sub_skills": meta.get("sub_skills", []),
                "libraries": meta.get("libraries", []),
                "time_estimate": meta.get("time_estimate", DEFAULT_TIME_ESTIMATE),
                "real_world_usage": meta.get("real_world_usage"),
                "how_used": {
                    "summary": meta.get("real_world_usage"),
                    "examples": meta.get("usage_examples", []),
                },
                "how_to_start": meta.get("start_steps", []),
            }

    def _get_all_skills(self) -> List[str]:
        all_skills = set()
        for skills_list in self.roles_skills_map.values():
            all_skills.update(skills_list)
        return sorted(all_skills)

    def get_all_roles(self) -> List[str]:
        return self.all_roles

    def get_role_skills(self, role: str) -> List[str]:
        return self.roles_skills_map.get(role, [])

    def get_role_info(self, role: str) -> Optional[Dict]:
        if role not in self.roles_skills_map:
            return None

        role_df = self.df[self.df["career_label"] == role]
        return {
            "name": role,
            "skills": self.get_role_skills(role),
            "avg_cgpa": round(role_df["cgpa"].mean(), 2),
            "top_interests": role_df["interest"].value_counts().head(3).index.tolist(),
            "total_examples": len(role_df),
            "description": f"Master the skills needed to become a {role}",
        }

    def get_skill_info(self, skill: str) -> Optional[Dict]:
        return self.skill_hierarchy.get(skill)

    def get_all_skills(self) -> List[str]:
        return self._get_all_skills()

    def suggest_similar_skills(self, skill: str, limit: int = 5) -> List[str]:
        similar: Dict[str, int] = {}
        for skills_str in self.df["skills"]:
            skills_list = [item.strip() for item in skills_str.split(",")]
            if skill in skills_list:
                for related in skills_list:
                    if related != skill:
                        similar[related] = similar.get(related, 0) + 1

        return [name for name, _ in sorted(similar.items(), key=lambda item: item[1], reverse=True)[:limit]]

    def build_skill_graph(self, role: str, user_skills: List[str]) -> Dict:
        role_skills = self.get_role_skills(role)
        nodes = []
        first_locked_index = None

        for idx, skill in enumerate(role_skills):
            skill_meta = self.get_skill_info(skill) or {}
            is_completed = skill in user_skills
            status = "completed" if is_completed else "missing"

            if not is_completed and first_locked_index is None:
                first_locked_index = idx + 2

            locked = first_locked_index is not None and idx + 1 > first_locked_index
            if locked:
                status = "locked"
            elif not is_completed and idx == sum(1 for candidate in role_skills[:idx] if candidate in user_skills):
                status = "current"

            nodes.append(
                {
                    "id": skill,
                    "label": skill,
                    "intro": skill_meta.get("intro", skill_meta.get("description", "")),
                    "description": skill_meta.get("description", ""),
                    "level": skill_meta.get("level", 1),
                    "stage_label": skill_meta.get("stage_label", "Build"),
                    "sub_skills": skill_meta.get("sub_skills", []),
                    "time_estimate": skill_meta.get("time_estimate", DEFAULT_TIME_ESTIMATE),
                    "status": status,
                    "position": idx + 1,
                }
            )

        edges = []
        for idx in range(len(role_skills) - 1):
            edges.append({"source": role_skills[idx], "target": role_skills[idx + 1], "type": "prerequisite"})

        return {
            "role": role,
            "nodes": nodes,
            "edges": edges,
            "total_skills": len(role_skills),
            "total_edges": len(edges),
        }


_manager = None


def get_roadmap_data_manager() -> RoadmapDataManager:
    global _manager
    if _manager is None:
        _manager = RoadmapDataManager()
    return _manager


def get_all_roles() -> List[str]:
    return get_roadmap_data_manager().get_all_roles()


def get_role_skills(role: str) -> List[str]:
    return get_roadmap_data_manager().get_role_skills(role)


def get_all_skills() -> List[str]:
    return get_roadmap_data_manager().get_all_skills()


def get_skill_info(skill: str) -> Optional[Dict]:
    return get_roadmap_data_manager().get_skill_info(skill)


def get_role_info(role: str) -> Optional[Dict]:
    return get_roadmap_data_manager().get_role_info(role)


def build_skill_graph(role: str, user_skills: List[str]) -> Dict:
    return get_roadmap_data_manager().build_skill_graph(role, user_skills)
