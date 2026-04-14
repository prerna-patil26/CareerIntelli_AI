class InterviewScorer:

    def calculate_score(self, scores):
        return round(sum(scores) / len(scores), 2)

    def get_detailed_scores(self, scores, answers):
        total_score = self.calculate_score(scores)

        # 🎯 Technical (based on evaluator)
        technical_score = round(total_score / 10, 1)

        # 💬 Communication (based on answer length)
        avg_length = sum(len(ans.split()) for ans in answers) / len(answers)

        if avg_length > 20:
            communication_score = 8
        elif avg_length > 10:
            communication_score = 6
        else:
            communication_score = 4

        # 🎯 Confidence (basic logic)
        if avg_length > 20:
            confidence_score = 8
        elif avg_length > 10:
            confidence_score = 6
        else:
            confidence_score = 5

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