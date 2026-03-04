"""
Resume Analyzer Module
- Extracts text from PDF resumes
- Identifies skills using a comprehensive skill list
- Integrates with CareerPredictor to recommend careers
"""
import sys
import os
# Add project root to path so that modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import re
import pandas as pd
import fitz  # PyMuPDF
from pathlib import Path
from modules.career_predictor import CareerPredictor

class ResumeAnalyzer:
    def __init__(self, skill_list_path=None):
        """
        Initialize the resume analyzer.
        If skill_list_path is provided, load skills from that CSV.
        Otherwise, build a skill set from multiple datasets.
        """
        self.skill_set = self._build_skill_set(skill_list_path)
        self.predictor = CareerPredictor()
        # Try to load the pre-trained model
        model_path = 'ml_models/saved_models/career_predictor.pkl'
        if os.path.exists(model_path):
            self.predictor.load_model(model_path)
        else:
            print("⚠️  Pre-trained model not found. Please train the model first.")
    
    def _build_skill_set(self, skill_list_path):
        """
        Build a comprehensive set of skills from various sources.
        """
        skills = set()
        
        # 1. If a custom skill list is provided
        if skill_list_path and os.path.exists(skill_list_path):
            df = pd.read_csv(skill_list_path)
            # Assuming the CSV has a column named 'skill' or 'Required_Skills'
            if 'skill' in df.columns:
                for s in df['skill'].dropna():
                    skills.update([skill.strip() for skill in s.split(',')])
            elif 'Required_Skills' in df.columns:
                for s in df['Required_Skills'].dropna():
                    skills.update([skill.strip() for skill in s.split(',')])
        
        # 2. Add skills from industry_skill_benchmark.csv
        benchmark_path = 'datasets/industry_skill_benchmark.csv'
        if os.path.exists(benchmark_path):
            df_bench = pd.read_csv(benchmark_path)
            if 'Required_Skills' in df_bench.columns:
                for s in df_bench['Required_Skills'].dropna():
                    skills.update([skill.strip() for skill in s.split(',')])
        
        # 3. Add skills from career_prediction_dataset.csv
        career_data_path = 'datasets/career_prediction_dataset.csv'
        if os.path.exists(career_data_path):
            df_career = pd.read_csv(career_data_path)
            if 'skills' in df_career.columns:
                for s in df_career['skills'].dropna():
                    # The skills column may be stored as a string representation of a list
                    # e.g., "['Python', 'SQL']" or "Python, SQL"
                    # We'll handle both
                    if s.startswith('[') and s.endswith(']'):
                        # It's a list representation
                        try:
                            lst = eval(s)
                            if isinstance(lst, list):
                                for skill in lst:
                                    skills.add(skill.strip())
                        except:
                            pass
                    else:
                        # Assume comma-separated
                        for skill in s.split(','):
                            skills.add(skill.strip())
        
        # Normalise skills to lowercase for matching
        skills = {skill.lower() for skill in skills if skill}
        print(f"📚 Loaded {len(skills)} unique skills for matching.")
        return skills
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract all text from a PDF file using PyMuPDF.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Resume not found: {pdf_path}")
        
        text = ""
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            print(f"❌ Error reading PDF: {e}")
            return ""
        return text
    
    def extract_skills(self, text):
        """
        Extract skills from text by matching against the skill set.
        Returns a list of unique skills found.
        """
        text_lower = text.lower()
        found = set()
        
        # For each skill, check if it appears as a whole word
        # We use word boundaries to avoid partial matches
        for skill in self.skill_set:
            # Escape special regex characters in skill name
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill)
        
        # Return sorted list for consistency
        return sorted(found)
    
    def analyze(self, resume_path, cgpa=None, interest=None, internship=None,
                projects_count=None, communication_score=None):
        """
        Analyze a resume and predict suitable careers.
        
        Parameters:
        - resume_path: path to the PDF resume
        - cgpa, interest, internship, projects_count, communication_score: optional
          additional information. If not provided, they default to None and the
          predictor will use average values (or you may want to ask the user).
        
        Returns:
        - Dictionary with extracted skills and prediction results.
        """
        # Extract text and skills
        text = self.extract_text_from_pdf(resume_path)
        if not text:
            return {"error": "Could not extract text from resume."}
        
        skills_found = self.extract_skills(text)
        
        # If additional info not provided, set sensible defaults or prompt user?
        # Here we set defaults that might be reasonable, but you could also raise an error.
        if cgpa is None:
            cgpa = 7.0  # default average CGPA
        if interest is None:
            interest = "General"
        if internship is None:
            internship = "No"
        if projects_count is None:
            projects_count = 2
        if communication_score is None:
            communication_score = 5
        
        # Use the predictor
        prediction = self.predictor.predict(
            skills=skills_found,
            cgpa=cgpa,
            interest=interest,
            internship=internship,
            projects_count=projects_count,
            communication_score=communication_score
        )
        
        result = {
            "extracted_skills": skills_found,
            "skill_count": len(skills_found),
            "prediction": prediction
        }
        return result

# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = ResumeAnalyzer()
    
    # Path to a sample resume (you can place a dummy PDF for testing)
    sample_pdf = "data/samples/resume_sample.pdf"
    
    # If sample exists, run analysis
    if os.path.exists(sample_pdf):
        result = analyzer.analyze(
            resume_path=sample_pdf,
            cgpa=8.2,
            interest="AI",
            internship="Yes",
            projects_count=3,
            communication_score=7
        )
        
        print("\n📄 Resume Analysis Result:")
        print(f"   Extracted skills ({result['skill_count']}): {', '.join(result['extracted_skills'])}")
        pred = result['prediction']
        print(f"\n🔮 Predicted Career: {pred['predicted_career']} (confidence: {pred['confidence']:.2f})")
        print("   Top 3 alternatives:")
        for alt in pred['top_3_careers']:
            print(f"   - {alt['career']} ({alt['probability']:.2f})")
    else:
        print(f"⚠️  Sample resume not found at {sample_pdf}. Please add a PDF for testing.")
        print("   You can still use the analyzer programmatically with a valid path.")