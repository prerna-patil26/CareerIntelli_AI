"""Data preprocessing module for career prediction datasets."""

from __future__ import annotations

from ast import literal_eval
from typing import Any, Tuple, Union

import pandas as pd


REQUIRED_SKILLS_COLUMN = "skills"
REQUIRED_LABEL_COLUMNS = ("career", "career_label")


def load_dataset(csv_path: Union[str, bytes]) -> pd.DataFrame:
    """Load a career dataset from a CSV file path."""
    return pd.read_csv(csv_path)


def validate_required_columns(df: pd.DataFrame) -> None:
    """Ensure dataset contains all required columns."""
    if REQUIRED_SKILLS_COLUMN not in df.columns:
        raise ValueError(f"Missing required column: {REQUIRED_SKILLS_COLUMN}")
    if not any(column in df.columns for column in REQUIRED_LABEL_COLUMNS):
        raise ValueError(f"Missing required label column. Expected one of: {list(REQUIRED_LABEL_COLUMNS)}")


def _parse_list_like_value(value: str) -> Any:
    """Parse list-like string values such as "['python', 'sql']" safely."""
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        try:
            return literal_eval(value)
        except (ValueError, SyntaxError):
            return value
    return value


def _normalize_whitespace(text: str) -> str:
    """Trim text and collapse repeated spaces into a single space."""
    return " ".join(text.strip().split())


def clean_skills_text(skills_value: Any) -> str:
    """Normalize skills text to lowercase and cleaned spacing."""
    if isinstance(skills_value, str):
        skills_value = _parse_list_like_value(skills_value)

    if isinstance(skills_value, list):
        tokens = [_normalize_whitespace(str(item)).lower() for item in skills_value]
        return " ".join(token for token in tokens if token)

    return _normalize_whitespace(str(skills_value)).lower()


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Remove nulls and duplicates, then normalize skills text."""
    cleaned_df = df.dropna().drop_duplicates().copy()
    cleaned_df["skills"] = cleaned_df["skills"].apply(clean_skills_text)
    return cleaned_df


def split_features_and_labels(cleaned_df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """Split cleaned dataframe into skills text and career labels."""
    skills_text = cleaned_df["skills"]
    label_column = "career" if "career" in cleaned_df.columns else "career_label"
    career_labels = cleaned_df[label_column]
    return skills_text, career_labels


def preprocess_career_dataset(csv_path: Union[str, bytes]) -> Tuple[pd.Series, pd.Series]:
    """Load and preprocess dataset, returning cleaned skills text and career labels."""
    df = load_dataset(csv_path)
    validate_required_columns(df)
    cleaned_df = clean_dataset(df)
    return split_features_and_labels(cleaned_df)
