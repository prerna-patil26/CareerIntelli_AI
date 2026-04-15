import os
import logging
from typing import List
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

logger = logging.getLogger(__name__)


class FeedbackGenerator:
    def __init__(self):
        # 🔥 Direct API key (no env)
        api_key = "AIzaSyD6L6n1PV_BymX6YyyLIpL8AINuMeA9AH4"

        if not api_key:
            logger.warning("API key not found")
            self.model = None
            return

        try:
            genai.configure(api_key=api_key)

            # ✅ MAIN MODEL
            self.primary_model = "gemini-2.0-flash"

            # ✅ FALLBACK MODELS
            self.fallback_models = [
                "gemini-2.0-flash",
                "gemini-2.5-flash",
                "gemini-flash-lite-latest",
                "gemini-flash-latest",
            ]

            self.model = None
            self.model_name = None

            # 🔥 Try models one by one
            for model_name in dict.fromkeys(self.fallback_models):
                try:
                    self.model = genai.GenerativeModel(model_name)
                    self.model_name = model_name
                    logger.info(f"Using Gemini model: {model_name}")
                    break
                except Exception as e:
                    logger.warning(f"Model {model_name} failed: {e}")

            if not self.model:
                raise RuntimeError("No model available")

        except Exception as e:
            logger.error(f"Gemini setup failed: {e}")
            self.model = None

    def get_ai_resume_feedback(self, resume_text: str) -> List[str]:

        if not resume_text.strip():
            return ["Resume text is empty."]

        if not self.model:
            return ["AI service not available."]

        try:
            prompt = f"""
You are an expert resume reviewer.

Analyze the resume and give EXACTLY 5 specific improvement suggestions.
Each suggestion should start with "- "

Resume:
{resume_text}
"""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.7,
                )
            )

            # ✅ SAFE CHECK
            if not response or not response.text:
                raise Exception("Empty response")

            raw_text = response.text
            print("🔍 GEMINI RESPONSE:", raw_text)

            feedback = self._parse_feedback(raw_text)

            if not feedback:
                return ["AI response format issue"]

            return feedback[:5]

        except google_exceptions.ResourceExhausted:
            logger.warning("Quota exceeded, switching model...")

            if self._switch_model():
                return self.get_ai_resume_feedback(resume_text)

            return ["API quota exceeded. Try later."]

        except Exception as e:
            logger.error(f"Error: {e}")
            return ["AI feedback failed."]

    def _parse_feedback(self, text: str) -> List[str]:
        lines = text.split("\n")
        feedback = []

        for line in lines:
            line = line.strip()

            if line.startswith("- "):
                suggestion = line[2:].strip()
                if suggestion:
                    feedback.append(suggestion)

        return feedback

    def _switch_model(self):
        for model_name in self.fallback_models:
            if model_name == self.model_name:
                continue

            try:
                self.model = genai.GenerativeModel(model_name)
                self.model_name = model_name
                logger.info(f"Switched to {model_name}")
                return True
            except:
                continue

        return False