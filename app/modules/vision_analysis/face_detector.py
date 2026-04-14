import cv2


class FaceDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def detect_faces(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5
        )

        return faces

    # 🔥 NEW FUNCTION ADDED (NO OTHER CHANGE)
    def get_face_position(self, image, faces):
        h, w, _ = image.shape

        if len(faces) == 0:
            return "no_face"

        (x, y, fw, fh) = faces[0]

        face_center_x = x + fw / 2

        if face_center_x < w * 0.3:
            return "left"
        elif face_center_x > w * 0.7:
            return "right"
        else:
            return "center"