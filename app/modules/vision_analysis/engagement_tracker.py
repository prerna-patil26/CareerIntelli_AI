class EngagementTracker:

    def calculate_engagement(self, face_count):
        if face_count == 0:
            return 20   # no face = low engagement
        elif face_count == 1:
            return 90   # focused
        else:
            return 60   # multiple faces