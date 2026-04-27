class InterviewScorer:

    def calculate_score(self, scores):
        return round(sum(scores) / len(scores), 2)

    def get_detailed_scores(self, scores, answers):
        total_score = self.calculate_score(scores)

        # 🎯 Technical (based on evaluator)
        technical_score = round(total_score / 10, 1)

        # 💬 Communication (based on answer length + coverage quality)
        avg_length = sum(len(ans.split()) for ans in answers) / len(answers)
        meaningful_answers = [ans for ans in answers if len(ans.strip().split()) > 5]
        meaningful_ratio = len(meaningful_answers) / len(answers)

        if avg_length > 20 and meaningful_ratio >= 0.7:
            communication_score = 8
        elif avg_length > 10 and meaningful_ratio >= 0.4:
            communication_score = 6
        elif avg_length > 5 and meaningful_ratio >= 0.2:
            communication_score = 4
        else:
            communication_score = 2

        # 🎯 Confidence (based on answer coverage + length, not just length)
        if avg_length > 20 and meaningful_ratio >= 0.7:
            confidence_score = 8
        elif avg_length > 10 and meaningful_ratio >= 0.4:
            confidence_score = 6
        elif avg_length > 5 and meaningful_ratio >= 0.2:
            confidence_score = 4
        else:
            confidence_score = 2

        return {
            "total_score": total_score,
            "technical_score": technical_score,
            "communication_score": communication_score,
            "confidence_score": confidence_score
        }

    def generate_feedback(self, scores_dict):
        total = scores_dict["total_score"]

        if total > 80:
            return "Excellent performance! You are interview ready."
        elif total > 60:
            return "Good performance, but you can improve."
        else:
            return "Needs improvement. Focus on basics."

    def generate_suggestions(self, scores_dict):
        suggestions = []

        if scores_dict["communication_score"] < 7:
            suggestions.append("Improve communication clarity")

        if scores_dict["confidence_score"] < 7:
            suggestions.append("Speak with more confidence")

        if scores_dict["technical_score"] < 7:
            suggestions.append("Strengthen technical concepts")

        if not suggestions:
            suggestions.append("Great job! Keep practicing")

        return suggestions
