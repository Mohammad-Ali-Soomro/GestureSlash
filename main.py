import threading
import time
import cv2
from hand_tracker import HandTracker
from gesture_engine import GestureEngine, GestureState
from game.engine import GameEngine
from config import CAMERA_INDEX, HAND_DETECTION_CONFIDENCE, SHOW_CAMERA_WINDOW, SCREEN_WIDTH, SCREEN_HEIGHT

current_gesture = GestureState(
    cursor_pos=(0, 0),
    is_slicing=False,
    is_pinching=False,
    is_fist=False,
    velocity=(0, 0),
    hand_detected=False
)
gesture_lock = threading.Lock()
stop_event = threading.Event()

def tracking_thread_fn(tracker, gesture_engine):
    global current_gesture
    while not stop_event.is_set():
        frame, landmarks = tracker.get_frame_and_landmarks()
        if frame is None:
            continue
            
        if landmarks:
            fingertip = tracker.get_fingertip_pixel(landmarks, tracker.frame_width, tracker.frame_height)
            state = gesture_engine.update(landmarks, fingertip, tracker.frame_width, tracker.frame_height, SCREEN_WIDTH, SCREEN_HEIGHT, frame)
        else:
            state = gesture_engine.no_hand_state()
            state.frame = frame
        
        with gesture_lock:
            current_gesture = state
        
        if SHOW_CAMERA_WINDOW:
            from config import SHOW_LANDMARKS
            if SHOW_LANDMARKS:
                tracker.annotate_frame(frame, state)
            cv2.imshow("GestureSlash - Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                stop_event.set()
        else:
            from config import SHOW_LANDMARKS
            if SHOW_LANDMARKS:
                tracker.annotate_frame(frame, state)
            # Give UI processing time so OpenCV doesn't hang or buffer infinitely
            cv2.waitKey(1)

def get_gesture():
    with gesture_lock:
        return current_gesture

if __name__ == "__main__":
    print("GestureSlash starting... Position your hand in front of the camera")
    tracker = HandTracker(CAMERA_INDEX, HAND_DETECTION_CONFIDENCE)
    gesture_engine = GestureEngine()
    game = GameEngine()

    thread = threading.Thread(target=tracking_thread_fn, args=(tracker, gesture_engine), daemon=True)
    thread.start()

    try:
        game.run(get_gesture)
    finally:
        stop_event.set()
        tracker.release()
        print("GestureSlash closed.")
