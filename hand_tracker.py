import cv2
import time
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
        self.prev_time = 0

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

    def annotate_frame(self, frame, gesture_state):
        current_time = time.time()
        fps = 0
        if current_time - self.prev_time > 0:
            fps = 1.0 / (current_time - self.prev_time)
        self.prev_time = current_time
        
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        status_text = "IDLE"
        if gesture_state:
            if getattr(gesture_state, 'is_fist', False):
                status_text = "FIST"
            elif getattr(gesture_state, 'is_pinching', False):
                status_text = "PINCHING"
            elif getattr(gesture_state, 'is_slicing', False):
                status_text = "SLICING"
        
        cv2.putText(frame, status_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
