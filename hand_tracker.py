import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

HAND_CONNECTIONS = [
    (0,1), (1,2), (2,3), (3,4),
    (0,5), (5,6), (6,7), (7,8),
    (5,9), (9,10), (10,11), (11,12),
    (9,13), (13,14), (14,15), (15,16),
    (13,17), (17,18), (18,19), (19,20),
    (0,17)
]

class HandTracker:
    def __init__(self, camera_index=0, detection_confidence=0.7):
        self.cap = cv2.VideoCapture(camera_index)
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=detection_confidence,
            min_tracking_confidence=detection_confidence
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.prev_time = 0

    def get_frame_and_landmarks(self):
        success, frame = self.cap.read()
        if not success:
            return None, None
            
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        results = self.detector.detect(mp_image)
        
        landmarks_list = None
        if results.hand_landmarks:
            hand_landmarks = results.hand_landmarks[0]
            
            for lm in hand_landmarks:
                x, y = int(lm.x * self.frame_width), int(lm.y * self.frame_height)
                cv2.circle(frame, (x, y), 4, (0, 0, 255), -1)
            for conn in HAND_CONNECTIONS:
                p1 = hand_landmarks[conn[0]]
                p2 = hand_landmarks[conn[1]]
                x1, y1 = int(p1.x * self.frame_width), int(p1.y * self.frame_height)
                x2, y2 = int(p2.x * self.frame_width), int(p2.y * self.frame_height)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
            landmarks_list = [(lm.x, lm.y, getattr(lm, 'z', 0)) for lm in hand_landmarks]
            
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
