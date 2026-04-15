import os
import logging
from typing import List

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

import os
import logging
from typing import List

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class FeedbackGenerator:
    def __init__(self):
        api_key = (
            os.getenv("GEMINI_API_KEY_1")
            or os.getenv("GEMINI_API_KEY_2")
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )

        if not api_key:
            logger.warning("API key not found")
            self.client = None
            return

        try:
            self.client = genai.Client(api_key=api_key)

            # ✅ STABLE MODELS ONLY
            self.fallback_models = [
                "gemini-2.5-flash",
                "gemini-2.0-flash",
            ]

            self.model_index = 0
            self.model_name = self.fallback_models[self.model_index]

        except Exception as e:
            logger.error(f"Gemini setup failed: {e}")
            self.client = None

    def get_ai_resume_feedback(self, resume_text: str, retry_count=0) -> List[str]:

        if not resume_text.strip():
            return ["Resume text is empty."]

        if not self.client:
            return ["AI service not available."]

        try:
            prompt = f"""
You are a professional resume reviewer.

Analyze the resume and give EXACTLY 5 HIGH-QUALITY improvement suggestions.

STRICT RULES:
- Each suggestion MUST start with "- "
- Each suggestion MUST be ONE SINGLE LINE
- Each suggestion MUST be a COMPLETE sentence
- Each suggestion MUST be at least 12–15 words long
- Do NOT give short or incomplete suggestions like "Reformat"
- Be specific, detailed, and practical
- Do NOT include any introduction like "Here are 5 suggestions"
- Only output bullet points

Resume:
{resume_text}
"""

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=500,
                    temperature=0.7,
                ),
            )

            if not response or not response.text:
                raise Exception("Empty response")

            raw_text = response.text
            print("🔍 GEMINI RESPONSE:\n", raw_text)

            feedback = self._parse_feedback(raw_text)

            # ✅ CLEAN + FIX MULTILINE
            feedback = [f.replace("\n", " ").strip() for f in feedback]

            # ❌ REMOVE WEAK SUGGESTIONS
            feedback = [f for f in feedback if len(f.split()) >= 8]

            # 🔁 RETRY IF BAD OUTPUT
            if len(feedback) < 3 and retry_count < 2:
                return self.get_ai_resume_feedback(resume_text, retry_count + 1)

            # 🔥 FALLBACK (ENSURE 5)
            if len(feedback) < 5:
                feedback.extend([
                    "Add measurable achievements using numbers and impact to demonstrate real results.",
                    "Improve formatting to ensure consistent spacing, alignment, and readability across sections.",
                    "Highlight relevant technical and soft skills aligned with the target job role.",
                    "Ensure consistency in dates, headings, and structure throughout the resume.",
                    "Optimize the resume with ATS-friendly keywords based on job descriptions.",
                ])

            return feedback[:5]

        except Exception as e:
            error_str = str(e).lower()
            print("🔥 ERROR:", e)

            # 🔥 HANDLE 503 / SERVER BUSY
            if "503" in error_str or "unavailable" in error_str:
                if retry_count < 2:
                    return self.get_ai_resume_feedback(resume_text, retry_count + 1)
                return ["AI is busy right now. Please try again in a few seconds."]

            # 🔥 HANDLE QUOTA
            if "429" in error_str or "quota" in error_str:
                return ["API quota exceeded. Try again later or switch API key."]

            logger.error(f"Error: {e}")
            return ["Unable to generate feedback at the moment."]

    def _parse_feedback(self, text: str) -> List[str]:
        feedback = []
        current = ""

        for line in text.split("\n"):
            line = line.strip()

            if not line:
                continue

            # ❌ skip intro lines
            if "here are" in line.lower():
                continue

            if line.startswith("- "):
                if current:
                    feedback.append(current.strip())
                current = line[2:].strip()
            else:
                current += " " + line

        if current:
            feedback.append(current.strip())

        return feedback