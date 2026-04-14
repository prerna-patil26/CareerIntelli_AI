"""Career prediction module backed by trained model artifacts and dataset analysis."""

from __future__ import annotations

from ast import literal_eval
from collections import Counter
from pathlib import Path
import re
from typing import Dict, List, Sequence, Tuple

import numpy as np
import pandas as pd

from . import feature_builder, model_loader
from .data_preprocessing import clean_skills_text


class CareerPredictor:
    """Predict careers and generate dataset-driven guidance."""

    def __init__(self) -> None:
        self.model, self.vectorizer = model_loader.load_model_and_vectorizer()
        self.dataset = self._load_dataset()
        self.career_skills_map = self._build_career_skills_map()

    def _dataset_path(self) -> Path:
        return Path(__file__).resolve().parents[2] / "datasets" / "career_prediction_dataset.csv"

    def _load_dataset(self) -> pd.DataFrame:
        dataset_path = self._dataset_path()
        if not dataset_path.exists():
            raise FileNotFoundError(f"Missing dataset file: {dataset_path}")

        df = pd.read_csv(dataset_path)
        if "skills" not in df.columns:
            raise ValueError("Dataset must contain a 'skills' column.")

        if "career_label" in df.columns:
            df = df.rename(columns={"career_label": "career"})
        elif "career" not in df.columns:
            raise ValueError("Dataset must contain either 'career' or 'career_label'.")

        cleaned = df[["skills", "career"]].dropna().copy()
        cleaned["career"] = cleaned["career"].astype(str).str.strip()
        cleaned["skills"] = cleaned["skills"].apply(self._split_skills)
        return cleaned

    def _split_skills(self, raw_value: object) -> List[str]:
        if isinstance(raw_value, list):
            values = raw_value
        else:
            text = str(raw_value).strip()
            if text.startswith("[") and text.endswith("]"):
                try:
                    parsed = literal_eval(text)
                    values = parsed if isinstance(parsed, list) else [text]
                except (ValueError, SyntaxError):
                    values = text.split(",")
            else:
                values = text.split(",")

        normalized = [self._normalize_skill(value) for value in values]
        return [skill for skill in normalized if skill]

    def _normalize_skill(self, skill: object) -> str:
        normalized = " ".join(str(skill).strip().lower().split())
        replacements = {
            r"\bml\b": "machine learning",
            r"\bai\b": "artificial intelligence",
            r"\bqa\b": "quality assurance",
            r"\bnlp\b": "natural language processing",
            r"\bllm\b": "large language model",
            r"\bux\b": "user experience",
            r"\bui\b": "user interface",
        }
        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized)
        return " ".join(normalized.split())

    def _format_skill(self, skill: str) -> str:
        return " ".join(part.capitalize() for part in skill.split())

    def _build_career_skills_map(self, max_skills: int = 8) -> Dict[str, List[str]]:
        career_skills_map: Dict[str, List[str]] = {}

        for career, group in self.dataset.groupby("career"):
            counter: Counter[str] = Counter()
            for skills in group["skills"]:
                counter.update(skills)

            ranked_skills = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
            career_skills_map[str(career)] = [skill for skill, _ in ranked_skills[:max_skills]]

        return career_skills_map

    def _format_skills_for_model(self, skills: Sequence[str]) -> str:
        return clean_skills_text([self._normalize_skill(skill) for skill in skills])

    def _predict_primary_career(self, skills: Sequence[str]) -> str:
        input_text = self._format_skills_for_model(skills)
        features = feature_builder.build_prediction_features(input_text, self.vectorizer)
        prediction = self.model.predict(features)
        if len(prediction) == 0:
            raise ValueError("Model did not return a prediction.")
        return str(prediction[0])

    def _model_probabilities(self, skills: Sequence[str]) -> Tuple[np.ndarray, np.ndarray]:
        input_text = self._format_skills_for_model(skills)
        features = feature_builder.build_prediction_features(input_text, self.vectorizer)

        if not hasattr(self.model, "predict_proba"):
            raise AttributeError("Loaded model does not support predict_proba().")

        probabilities = self.model.predict_proba(features)[0]
        labels = np.array([str(label) for label in self.model.classes_])
        return probabilities, labels

    def _top_careers_from_probabilities(
        self,
        probabilities: np.ndarray,
        class_labels: np.ndarray,
        predicted_career: str,
        top_k: int,
    ) -> List[str]:
        ranked_indices = np.argsort(probabilities)[::-1]
        ranked_labels = [str(class_labels[index]) for index in ranked_indices]

        ordered_labels = [predicted_career]
        ordered_labels.extend(label for label in ranked_labels if label != predicted_career)
        return ordered_labels[:top_k]

    def _skill_match_status(self, user_skills: Sequence[str], required_skill: str) -> str:
        required_tokens = set(required_skill.split())
        best_status = "Missing"

        for raw_user_skill in user_skills:
            user_skill = self._normalize_skill(raw_user_skill)
            user_tokens = set(user_skill.split())

            if user_skill == required_skill:
                return "Strong"

            if required_skill in user_skill or user_skill in required_skill:
                best_status = "Strong"
                continue

            if required_tokens & user_tokens:
                best_status = "Basic"

        return best_status

    def _build_skill_analysis(
        self,
        user_skills: Sequence[str],
        career: str,
        skill_ratings: Dict[str, int] | None = None,
    ) -> Tuple[Dict[str, str], List[str], List[str]]:
        required_skills = self.career_skills_map.get(career, [])
        analysis: Dict[str, str] = {}
        matched_skills: List[str] = []
        missing_skills: List[str] = []
        normalized_ratings = {self._normalize_skill(skill): int(value) for skill, value in (skill_ratings or {}).items()}

        for required_skill in required_skills:
            status = self._skill_match_status(user_skills, required_skill)
            if status != "Missing":
                matched_user_skill = next(
                    (
                        self._normalize_skill(skill)
                        for skill in user_skills
                        if self._skill_match_status([skill], required_skill) != "Missing"
                    ),
                    "",
                )
                rating = normalized_ratings.get(matched_user_skill)
                if rating is not None and rating <= 3:
                    status = "Basic"
                elif rating is not None and rating >= 4:
                    status = "Strong"
            analysis[self._format_skill(required_skill)] = status
            if status == "Missing":
                missing_skills.append(self._format_skill(required_skill))
            else:
                matched_skills.append(self._format_skill(required_skill))

        return analysis, matched_skills, missing_skills

    def _build_dynamic_insight(
        self,
        career: str,
        matched_skills: List[str],
        missing_skills: List[str],
        target_career: str | None = None,
        top_careers: Sequence[str] | None = None,
    ) -> str:
        goal_hint = ""
        if target_career:
            normalized_target = self._normalize_skill(target_career)
            normalized_prediction = self._normalize_skill(career)
            normalized_top = {self._normalize_skill(role) for role in (top_careers or [])}
            if normalized_target == normalized_prediction:
                goal_hint = f" Your selected goal also matches this result."
            elif normalized_target in normalized_top:
                goal_hint = f" Your selected goal is also a close match based on your skills."

        if matched_skills and missing_skills:
            return (
                f"You have strong skills in {', '.join(matched_skills[:4])}, "
                f"but you need to improve in {', '.join(missing_skills[:4])} for {career}."
                f"{goal_hint}"
            )
        if matched_skills:
            return (
                f"Your current skills in {', '.join(matched_skills[:4])} align well with {career}. "
                f"The next step is building deeper, role-specific projects."
                f"{goal_hint}"
            )
        if missing_skills:
            return (
                f"Your current skill set is still developing for {career}. "
                f"Start by building capability in {', '.join(missing_skills[:4])}."
                f"{goal_hint}"
            )
        return (
            f"Your profile shows early alignment with {career}. "
            f"Keep strengthening practical skills and project depth.{goal_hint}"
        )

    def _build_action_plan(self, career: str, missing_skills: List[str], matched_skills: List[str]) -> List[str]:
        actions = [f"Learn {skill}" for skill in missing_skills[:3]]
        actions.append(f"Practice projects related to {career}")
        if matched_skills:
            actions.append(f"Build portfolio work around {matched_skills[0]}")
        return actions[:4]

    def predict_career_with_details(
        self,
        skills: List[str],
        top_k: int = 3,
        target_career: str | None = None,
        skill_ratings: Dict[str, int] | None = None,
    ) -> Dict[str, object]:
        if not isinstance(skills, list):
            raise ValueError("skills must be provided as a list of strings.")
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        predicted_career = self._predict_primary_career(skills)
        probabilities, class_labels = self._model_probabilities(skills)
        top_labels = self._top_careers_from_probabilities(probabilities, class_labels, predicted_career, top_k)

        if predicted_career in class_labels.tolist():
            predicted_index = class_labels.tolist().index(predicted_career)
            confidence_score = float(probabilities[predicted_index]) * 100
        else:
            confidence_score = 0.0

        analysis, matched_skills, missing_skills = self._build_skill_analysis(
            skills,
            predicted_career,
            skill_ratings=skill_ratings,
        )
        insight = self._build_dynamic_insight(
            predicted_career,
            matched_skills,
            missing_skills,
            target_career=target_career,
            top_careers=top_labels,
        )
        action_plan = self._build_action_plan(predicted_career, missing_skills, matched_skills)

        current_level = "Beginner"
        if confidence_score >= 80:
            current_level = "Advanced"
        elif confidence_score >= 60:
            current_level = "Intermediate"

        return {
            "career": predicted_career,
            "confidence": round(confidence_score, 2),
            "top_3": top_labels,
            "skills_analysis": analysis,
            "missing_skills": missing_skills,
            "insight": insight,
            "action_plan": action_plan,
            "current_level": current_level,
            "predicted_career": predicted_career,
        }
