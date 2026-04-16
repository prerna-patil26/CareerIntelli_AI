import os
import logging
from typing import List

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class FeedbackGenerator:
    def __init__(self):
        self.api_keys = [
            os.getenv("GEMINI_API_KEY"),
            os.getenv("GEMINI_API_KEY_3"),
            os.getenv("GEMINI_API_KEY_2"),
            os.getenv("GEMINI_API_KEY_1"),
            
        ]

        # remove empty keys
        self.api_keys = [k for k in self.api_keys if k]

        self.key_index = 0

        if not self.api_keys:
            logger.warning("No API keys found")
            self.client = None
            return

        self.client = genai.Client(api_key=self.api_keys[self.key_index])

        try:
            self.client = genai.Client(api_key=self.api_keys[self.key_index])

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
            import time

        # 🔥 HANDLE QUOTA + BUSY BOTH
        if "429" in error_str or "quota" in error_str or "503" in error_str or "unavailable" in error_str:

            logger.warning(f"API issue detected (key {self.key_index}), trying next key...")

            # 🔁 Try next API key
            if self.key_index < len(self.api_keys) - 1:
                self.key_index += 1
                self.client = genai.Client(api_key=self.api_keys[self.key_index])

                time.sleep(2)  # avoid hammering API

                return self.get_ai_resume_feedback(resume_text)

            # ❌ All keys exhausted → fallback
            logger.error("All API keys exhausted. Using fallback.")

            return [
                "Improve resume formatting to ensure clarity and professional presentation.",
                "Add measurable achievements with numbers to demonstrate real impact.",
                "Highlight relevant technical and soft skills aligned with your target role.",
                "Include detailed project descriptions with tools and outcomes clearly explained.",
                "Optimize your resume using ATS-friendly keywords from job descriptions."
            ]
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