"""AI Feedback generator using Gemini API with proper error handling."""

import os
import logging
from typing import List
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)


class FeedbackGenerator:
    """Generate AI-powered feedback using Gemini API."""

    def __init__(self):
        """Initialize Gemini API with environment variable API key."""
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            self.model = None
            return
        
        try:
            genai.configure(api_key=api_key)

            default_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
            fallback_models = [
                default_model,
                "gemini-flash-lite-latest",
                "gemini-flash-latest",
                "gemini-2.0-flash",
                "gemini-2.5-flash",
            ]

            self.model = None
            self.model_name = None
            for model_name in dict.fromkeys(fallback_models):
                try:
                    self.model = genai.GenerativeModel(model_name)
                    self.model_name = model_name
                    logger.info(f"Gemini API configured successfully with model {model_name}")
                    break
                except Exception as e:
                    logger.warning(f"Model {model_name} unavailable: {e}")

            if not self.model:
                raise RuntimeError("No supported Gemini model could be initialized")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            self.model = None
            self.model_name = None

    def get_ai_resume_feedback(self, resume_text: str) -> List[str]:

        """
        Generate AI feedback for resume.
        
        Args:
            resume_text: The resume text to analyze
            
        Returns:
            List of feedback suggestions (up to 5)
        """
        if not resume_text or not resume_text.strip():
            logger.warning("Empty resume text provided")
            return ["Resume text is empty. Please provide resume content."]

        if not self.model:
            logger.error("Gemini model not initialized - check API key")
            return ["AI service is not available. Please check configuration."]

        try:
            prompt = f"""
            You are an expert resume reviewer.
            Analyze only the resume text below and provide EXACTLY 5 specific, actionable improvement suggestions.
            Do not give general career advice or unrelated guidance.
            Each suggestion should be concise and on a new line starting with "- ".

            Focus on the provided resume content, including achievements, skills, role descriptions,
            formatting, and ATS keyword clarity.

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

            if not response or not response.text:
                logger.warning("Gemini returned empty response")
                return ["AI analysis failed: No response received."]

            raw_text = response.text
            logger.debug(f"Gemini response: {raw_text[:200]}...")

            # Parse suggestions
            feedback = self._parse_feedback(raw_text)

            if not feedback:
                logger.warning("No feedback could be parsed from Gemini response")
                feedback = ["AI analysis completed but suggestions format unexpected."]

            return feedback[:5]

        except google_exceptions.InvalidArgument as e:
            logger.error(f"Invalid Gemini request: {e}")
            return ["Invalid resume format for AI analysis. Please check the file."]
        except google_exceptions.ResourceExhausted as e:
            logger.error(f"Gemini API quota exceeded for model {self.model_name}: {e}")

            if self._switch_to_alternate_model():
                try:
                    logger.info(f"Retrying AI request with alternate model {self.model_name}")
                    response = self.model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=500,
                            temperature=0.7,
                        )
                    )

                    if response and response.text:
                        raw_text = response.text
                        logger.debug(f"Gemini response after fallback: {raw_text[:200]}...")
                        feedback = self._parse_feedback(raw_text)
                        if feedback:
                            return feedback[:5]
                        logger.warning("No feedback could be parsed from Gemini response after fallback")
                        return ["AI analysis completed but suggestions format unexpected."]
                except Exception as fallback_error:
                    logger.error(f"Fallback AI model failed: {fallback_error}")

            return [
                "AI service temporarily unavailable due to API quota limits. "
                "Please check your Google Cloud billing/quota or try again later."
            ]
        except google_exceptions.Unauthenticated as e:
            logger.error(f"Gemini authentication failed: {e}")
            return ["AI service authentication failed. Check configuration."]
        except google_exceptions.PermissionDenied as e:
            logger.error(f"Gemini permission denied: {e}")
            return ["AI service permission denied. Check API key permissions."]
        except Exception as e:
            logger.error(f"Unexpected error in AI feedback generation: {e}")
            return ["AI feedback not available. Please try again later."]

    @staticmethod
    def _parse_feedback(raw_text: str) -> List[str]:
        """
        Parse feedback suggestions from raw Gemini response.
        
        Args:
            raw_text: Raw response from Gemini
            
        Returns:
            List of parsed suggestions
        """
        lines = raw_text.split("\n")
        feedback = []

        for line in lines:
            line = line.strip()
            
            # Look for lines starting with "- " or "* " or "• "
            if line.startswith("- ") or line.startswith("* ") or line.startswith("• "):
                suggestion = line.lstrip("-*•").strip()
                if suggestion and len(suggestion) > 5:  # Filter out very short suggestions
                    feedback.append(suggestion)
            
            # Also capture numbered items like "1. ", "2. ", etc.
            elif len(line) > 0 and line[0].isdigit() and ". " in line:
                suggestion = line.split(". ", 1)[1].strip() if ". " in line else ""
                if suggestion and len(suggestion) > 5:
                    feedback.append(suggestion)

        return feedback

    def _switch_to_alternate_model(self) -> bool:
        """Attempt switching to an alternate Gemini model if the current one fails."""
        fallback_models = [
            "gemini-flash-lite-latest",
            "gemini-flash-latest",
            "gemini-2.0-flash",
            "gemini-2.5-flash",
        ]

        for model_name in fallback_models:
            if model_name == self.model_name:
                continue
            try:
                self.model = genai.GenerativeModel(model_name)
                self.model_name = model_name
                logger.info(f"Switched Gemini model to fallback {model_name}")
                return True
            except Exception as e:
                logger.warning(f"Alternate model {model_name} unavailable: {e}")

        return False



