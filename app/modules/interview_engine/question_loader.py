import pandas as pd
import os


class QuestionLoader:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        base_dir = os.path.abspath(os.path.join(current_dir, "../../../"))

        # ✅ FIXED PATH
        self.file_path = os.path.join(
            base_dir,
            "app",
            "datasets",
            "interview_question_bank_technical.csv"
        )

        self.df = None

    def load_questions(self):
        try:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"File not found at: {self.file_path}")

            if self.file_path.endswith(".csv"):
                self.df = pd.read_csv(self.file_path)
            elif self.file_path.endswith(".xlsx"):
                self.df = pd.read_excel(self.file_path)
            else:
                raise ValueError("Unsupported file format. Use CSV or XLSX.")

            self.df.columns = self.df.columns.str.strip().str.lower()

            return self.df

        except Exception as e:
            raise Exception(f"Error loading dataset: {str(e)}")