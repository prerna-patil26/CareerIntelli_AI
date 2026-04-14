"""Utility helpers for career prediction modules."""

from __future__ import annotations

from ast import literal_eval
from typing import Any, Iterable, List


def normalize_whitespace(text: str) -> str:
    """Strip text and collapse repeated spaces into one."""
    return " ".join(text.strip().split())


def clean_skill_text(skill: Any) -> str:
    """Convert a single skill value to lowercase cleaned text."""
    return normalize_whitespace(str(skill)).lower()


def parse_list_like_skills(value: Any) -> Any:
    """Parse list-like string values, for example "['Python', 'SQL']"."""
    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        try:
            return literal_eval(stripped)
        except (ValueError, SyntaxError):
            return value
    return value


def format_skills(skills: Any) -> str:
    """Convert skill input into one lowercase space-separated string."""
    parsed_skills = parse_list_like_skills(skills)

    if isinstance(parsed_skills, list):
        cleaned_items = [clean_skill_text(item) for item in parsed_skills]
        return " ".join(item for item in cleaned_items if item)

    return clean_skill_text(parsed_skills)


def ensure_string_list(values: Iterable[Any]) -> List[str]:
    """Convert iterable values to a list of non-empty cleaned strings."""
    cleaned = [clean_skill_text(value) for value in values]
    return [value for value in cleaned if value]
