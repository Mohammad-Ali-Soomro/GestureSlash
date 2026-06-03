import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, camera_index=0, detection_confidence=0.7):
        self.cap = cv2.VideoCapture(camera_index)
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=detection_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def get_frame_and_landmarks(self):
        success, frame = self.cap.read()
        if not success:
            return None, None
            
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        landmarks_list = None
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            self.mp_drawing.draw_landmarks(
                frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
            landmarks_list = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
            
        return frame, landmarks_list

    def get_fingertip_pixel(self, landmarks, frame_width, frame_height):
        if not landmarks or len(landmarks) <= 8:
            return None
        
        x_norm = landmarks[8][0]
        y_norm = landmarks[8][1]
        return (int(x_norm * frame_width), int(y_norm * frame_height))

    def release(self):
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
