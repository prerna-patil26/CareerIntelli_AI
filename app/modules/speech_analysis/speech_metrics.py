class SpeechMetrics:

    def calculate_communication_score(self, filler_count, word_count):
        if word_count == 0:
            return 0

        filler_ratio = filler_count / word_count

        # 🔥 Less filler → better score
        if filler_ratio < 0.02:
            return 90
        elif filler_ratio < 0.05:
            return 75
        elif filler_ratio < 0.1:
            return 60
        else:
            return 40

    def calculate_confidence_score(self, word_count):
        # 🔥 based on answer length
        if word_count > 40:
            return 90
        elif word_count > 20:
            return 75
        elif word_count > 10:
            return 60
        else:
            return 40