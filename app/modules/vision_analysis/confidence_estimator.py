class ConfidenceEstimator:

    def estimate_confidence(self, engagement_score, communication_score):
        confidence = (engagement_score * 0.5) + (communication_score * 0.5)
        return round(confidence, 2)