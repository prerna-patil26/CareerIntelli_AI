class AnswerEvaluator:

    def evaluate_answer(self, answer):
        if not answer or not isinstance(answer, str):
            return 0

        words = answer.strip().split()

        # Length score (0–5)
        length_score = min(len(words) / 20, 1) * 5

        # Quality score (0–5)
        if len(words) > 10:
            quality_score = 5
        elif len(words) > 5:
            quality_score = 3
        else:
            quality_score = 1

        total_score = length_score + quality_score

        return round(min(total_score, 10), 2)