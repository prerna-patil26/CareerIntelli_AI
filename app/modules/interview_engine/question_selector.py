import random


class QuestionSelector:
    def __init__(self, df):
        self.df = df

        # ❌ REMOVE THIS LINE (VERY IMPORTANT)
        # self.df.columns = self.df.columns.str.strip().str.lower()

        # ✅ ONLY CLEAN VALUES
        self.df['role'] = self.df['role'].astype(str).str.strip()
        self.df['question_type'] = self.df['question_type'].astype(str).str.strip().str.lower()

    # ✅ Get domains
    def get_available_domains(self):
        return self.df['role'].dropna().unique().tolist()

    # ✅ Select 15 questions
    def select_questions(self, domain, total_questions=15, hr_count=4):

        role_df = self.df[
            self.df['role'].str.lower() == domain.lower().strip()
        ]

        if role_df.empty:
            print("❌ No data found for domain:", domain)
            return []

        hr_df = role_df[
            role_df['question_type'] == 'hr'
        ]

        tech_df = role_df[
            role_df['question_type'] == 'technical'
        ]

        hr_questions = hr_df['question'].dropna().tolist()
        tech_questions = tech_df['question'].dropna().tolist()

        print("HR:", len(hr_questions), "TECH:", len(tech_questions))

        selected_hr = random.sample(
            hr_questions,
            min(hr_count, len(hr_questions))
        )

        remaining = total_questions - len(selected_hr)

        selected_tech = random.sample(
            tech_questions,
            min(remaining, len(tech_questions))
        )

        final_questions = selected_hr + selected_tech
        random.shuffle(final_questions)

        return final_questions