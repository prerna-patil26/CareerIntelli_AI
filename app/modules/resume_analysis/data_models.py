"""Data models for resume analysis - ensures type consistency."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ContactInfo:
    """Contact information extracted from resume."""
    email: str = ""
    phone: str = ""


@dataclass
class ResumeData:
    """Structured resume data."""
    text: str
    contact: ContactInfo
    skills: List[str] = field(default_factory=list)
    education: List[str] = field(default_factory=list)
    experience: List[str] = field(default_factory=list)
    soft_skills: List[str] = field(default_factory=list)
    projects: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility."""
        return {
            "text": self.text,
            "email": self.contact.email,
            "phone": self.contact.phone,
            "skills": self.skills,
            "soft_skills": self.soft_skills,
            "education": self.education,
            "experience": self.experience,
            "projects": self.projects,
        }


@dataclass
class SkillMatch:
    """Skill matching result for gap analysis."""
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    extra_skills: List[str] = field(default_factory=list)


@dataclass
class ResumeScore:
    """Resume scoring result."""
    overall_score: int
    percentage: float
    breakdown: Dict[str, int] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    relevance_scores: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for templates."""
        return {
            "overall_score": self.overall_score,
            "percentage": self.percentage,
            "breakdown": self.breakdown,
            "suggestions": self.suggestions,
            "relevance_scores": self.relevance_scores,
        }
