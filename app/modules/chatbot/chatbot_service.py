"""Shared chatbot response service for CareerIntelli AI."""

from __future__ import annotations

import os
from typing import Dict

import requests


PAGE_CONTEXTS: Dict[str, str] = {
    "general": (
        "CareerIntelli AI is a career guidance platform. The dashboard gives an overview, "
        "the resume page uploads and analyzes resumes, the career page predicts suitable paths, "
        "the interview page helps practice interviews, the roadmap page builds a learning path, "
        "the report page summarizes scores, and the profile page stores user details."
    ),
    "dashboard": (
        "Dashboard: a home overview with career stats, quick access cards, search, profile access, "
        "and shortcuts to resume, career prediction, interview, and roadmap features."
    ),
    "resume": (
        "Resume page: users upload PDF or DOCX resumes, the app extracts text, calculates an ATS-style score, "
        "detects skills, and shows feedback plus suggestions to improve the resume."
    ),
    "career": (
        "Career page: users select or enter skills and career preferences, then the app suggests suitable career paths "
        "and helps the user compare strengths, skill gaps, and next steps."
    ),
    "interview": (
        "Interview page: users choose an interview domain, see domain-specific questions, record spoken answers, "
        "and receive interview feedback and performance insights."
    ),
    "roadmap": (
        "Roadmap page: users choose a target role and skills, generate a step-by-step learning roadmap, "
        "track progress, and see the next recommended learning step."
    ),
    "report": (
        "Report page: users see a combined summary of career, resume, and interview performance with recommendations."
    ),
    "profile": (
        "Profile page: users update their personal information, skills, interests, experience, CGPA, "
        "and upload profile photo or resume files."
    ),
    "career-result": (
        "Career result page: users review recommended career paths and can continue to interview practice or roadmap planning."
    ),
    "interview-result": (
        "Interview result page: users review technical, communication, and confidence feedback with suggestions to improve."
    ),
}

RELATED_KEYWORDS = (
    "dashboard",
    "resume",
    "career",
    "interview",
    "roadmap",
    "report",
    "profile",
    "skill",
    "analysis",
    "prediction",
    "roadmap",
    "progress",
    "feedback",
    "question",
    "score",
    "upload",
    "ats",
    "job ready",
    "learn next",
    "learning path",
    "career path",
)

UNRELATED_REPLY = (
    "I can only answer questions about CareerIntelli pages: dashboard, resume, career, interview, roadmap, report, and profile."
)


class CareerChatbotService:
    """Generate safe chatbot replies for the CareerIntelli app."""

    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    def generate_reply(self, message: str, page: str = "general") -> str:
        page_key = self._normalize_page(page)
        question = (message or "").strip()

        if not question:
            return "Please ask a question about CareerIntelli pages."

        if not self._is_related(question, page_key):
            return UNRELATED_REPLY

        context = PAGE_CONTEXTS.get(page_key, PAGE_CONTEXTS["general"])
        if not self.api_key:
            return self._fallback_reply(question, page_key)

        prompt = self._build_prompt(question, page_key, context)
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}",
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.35,
                        "maxOutputTokens": 220,
                    },
                },
                timeout=20,
            )
            response.raise_for_status()
            payload = response.json()
            text = (
                payload.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
                .strip()
            )
            if not text:
                return self._fallback_reply(question, page_key)
            return self._sanitize(text)
        except Exception:
            return self._fallback_reply(question, page_key)

    def _normalize_page(self, page: str) -> str:
        value = (page or "general").strip().lower()
        if value in {"career-result", "career_result"}:
            return "career-result"
        if value in {"interview-result", "interview_result"}:
            return "interview-result"
        if value not in PAGE_CONTEXTS:
            return "general"
        return value

    def _is_related(self, question: str, page_key: str) -> bool:
        lower = question.lower()
        if any(keyword in lower for keyword in RELATED_KEYWORDS):
            return True
        if page_key != "general" and page_key.replace("-", " ") in lower:
            return True
        if any(phrase in lower for phrase in ("this page", "current page", "how does this work", "what does this page do")):
            return True
        return False

    def _build_prompt(self, question: str, page_key: str, context: str) -> str:
        return (
            "You are CareerIntelli AI chatbot. Answer only about the CareerIntelli application. "
            "Supported pages are dashboard, resume, career, interview, roadmap, report, profile, career result, and interview result. "
            f"Current page context: {page_key}. "
            f"Page details: {context} "
            f"User question: {question} "
            "Rules: If the question is outside CareerIntelli, say you can only help with the app pages. "
            "Keep the answer concise, accurate, and limited to the relevant page feature."
        )

    def _fallback_reply(self, question: str, page_key: str) -> str:
        context = PAGE_CONTEXTS.get(page_key, PAGE_CONTEXTS["general"])
        lower = question.lower()

        if any(term in lower for term in ("how", "work", "what", "explain", "use", "does")):
            return context

        return (
            f"CareerIntelli page guidance: {context} "
            f"If you want, ask about resume, career, interview, roadmap, dashboard, report, or profile features."
        )

    def _sanitize(self, text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("{") and cleaned.endswith("}"):
            return cleaned
        return cleaned


def generate_chatbot_reply(message: str, page: str = "general") -> str:
    """Return a safe chatbot reply for the requested page context."""
    return CareerChatbotService().generate_reply(message=message, page=page)
