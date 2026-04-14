import random


class QuestionSelector:
    def __init__(self, df):
        self.df = df

    # ✅ Get domains
    def get_available_domains(self):
        return self.df['role'].dropna().unique().tolist()

    # ✅ Select 15 questions (4 HR + rest Technical)
    def select_questions(self, domain, total_questions=15, hr_count=4):
        # Filter domain
        role_df = self.df[
            self.df['role'].str.lower() == domain.lower()
        ]

        if role_df.empty:
            return []

        # Separate HR & Technical
        hr_df = role_df[
            role_df['question_type'].str.lower() == 'hr'
        ]

        tech_df = role_df[
            role_df['question_type'].str.lower() == 'technical'
        ]

        hr_questions = hr_df['question'].dropna().tolist()
        tech_questions = tech_df['question'].dropna().tolist()

        # Select HR questions
        selected_hr = random.sample(
            hr_questions,
            min(hr_count, len(hr_questions))
        )

        # Remaining Technical
        remaining = total_questions - len(selected_hr)

        selected_tech = random.sample(
            tech_questions,
            min(remaining, len(tech_questions))
        )

        final_questions = selected_hr + selected_tech
        random.shuffle(final_questions)

        return final_questions