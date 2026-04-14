"""Resume parser module for extracting text and data from resume files."""

import re
import logging
from typing import Dict, Any
from pdfminer.high_level import extract_text
import docx

logger = logging.getLogger(__name__)


class ResumeParser:
    """Parse and extract information from resume files."""

    # Compiled regex patterns for performance
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    # Improved phone pattern: supports +1-234-567-8900, (234) 567-8900, 234-567-8900, etc.
    PHONE_PATTERN = re.compile(
        r"(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\b\d{10}\b"
    )
    
    # Education keywords
    EDUCATION_KEYWORDS = [
        "btech", "bachelor", "mca", "msc", "bsc", "phd", "master", 
        "diploma", "associate", "degree", "b.tech", "m.tech", "b.s.", "m.s."
    ]
    
    # Experience pattern - matches "X years", "X+ years", "X months", etc.
    EXPERIENCE_PATTERN = re.compile(r"\b\d+\+?\s*(?:years?|yrs?|months?)\b")

    def __init__(self):
        """Initialize the resume parser."""
        self.extracted_data = {}

    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse resume file and extract structured information.
        
        Args:
            file_path: Path to resume file (PDF or DOCX)
            
        Returns:
            Dictionary with extracted resume data
            
        Raises:
            ValueError: If file format is unsupported or extraction fails
        """
        try:
            # Extract raw text
            text = self._extract_text_from_file(file_path)
            
            if not text or not text.strip():
                raise ValueError("Resume file appears to be empty or unreadable")
            
            # Clean text
            cleaned_text = self._clean_text(text)

            # Extract components
            contact = self._extract_contact_info(cleaned_text)
            education = self._extract_education(cleaned_text)
            experience = self._extract_experience(cleaned_text)

            # Note: Skills are extracted separately using SkillExtractor for better accuracy
            self.extracted_data = {
                "text": cleaned_text,
                "email": contact["email"],
                "phone": contact["phone"],
                "education": education,
                "experience": experience,
                "skills": [],  # Will be populated by SkillExtractor
            }

            logger.info(f"Successfully parsed resume: {file_path}")
            return self.extracted_data

        except FileNotFoundError as e:
            logger.error(f"Resume file not found: {file_path}")
            raise ValueError(f"Resume file not found: {file_path}") from e
        except Exception as e:
            logger.error(f"Failed to parse resume: {str(e)}")
            raise ValueError(f"Failed to parse resume: {str(e)}") from e

    def _extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from PDF or DOCX file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted text
            
        Raises:
            ValueError: If file format is unsupported
        """
        if file_path.endswith(".pdf"):
            try:
                text = extract_text(file_path)
                if not text:
                    raise ValueError("PDF extraction resulted in empty text")
                return text
            except Exception as e:
                raise ValueError(f"Failed to extract text from PDF: {str(e)}") from e

        elif file_path.endswith(".docx"):
            try:
                doc = docx.Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])
                if not text:
                    raise ValueError("DOCX extraction resulted in empty text")
                return text
            except Exception as e:
                raise ValueError(f"Failed to extract text from DOCX: {str(e)}") from e

        else:
            raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")

    def _clean_text(self, content: str) -> str:
        """
        Clean and normalize resume text.
        
        Args:
            content: Raw text content
            
        Returns:
            Cleaned text
        """
        # Normalize whitespace
        text = re.sub(r"\s+", " ", content)
        # Convert to lowercase for matching
        return text.lower().strip()

    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """
        Extract email and phone from resume text.
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary with email and phone (if found)
        """
        email_matches = self.EMAIL_PATTERN.findall(text)
        phone_matches = self.PHONE_PATTERN.findall(text)

        return {
            "email": email_matches[0] if email_matches else "",
            "phone": self._clean_phone(phone_matches[0]) if phone_matches else ""
        }

    @staticmethod
    def _clean_phone(phone: str) -> str:
        """
        Clean phone number to standard format.
        
        Args:
            phone: Raw phone string
            
        Returns:
            Cleaned phone number
        """
        # Remove all non-digit characters except leading +
        cleaned = re.sub(r"[^\d+]", "", phone)
        return cleaned

    def _extract_education(self, text: str) -> list:
        """
        Extract education from resume text.
        
        Args:
            text: Resume text
            
        Returns:
            List of education qualifications found
        """
        found = []
        for edu in self.EDUCATION_KEYWORDS:
            if f" {edu} " in text or text.startswith(edu) or text.endswith(edu):
                if edu not in found:
                    found.append(edu)
        
        return found

    def _extract_experience(self, text: str) -> list:
        """
        Extract experience mentions from resume text.
        
        Args:
            text: Resume text
            
        Returns:
            List of experience strings found (e.g., "5 years", "2+ years")
        """
        matches = self.EXPERIENCE_PATTERN.findall(text)
        return list(set(matches))  # Remove duplicates