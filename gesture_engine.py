import math
from collections import deque
from dataclasses import dataclass
from config import SLICE_VELOCITY_THRESHOLD

@dataclass
class GestureState:
    cursor_pos: tuple
    is_slicing: bool
    is_pinching: bool
    is_fist: bool
    velocity: tuple
    hand_detected: bool

class GestureEngine:
    def __init__(self):
        self.pos_history = deque(maxlen=5)
        self.prev_cursor = (0, 0)

    def update(self, landmarks, fingertip_pixel, cam_width, cam_height, screen_width, screen_height) -> GestureState:
        if not landmarks or not fingertip_pixel:
            return self.no_hand_state()

        # Map fingertip_pixel to screen coords
        screen_x = int(fingertip_pixel[0] / cam_width * screen_width)
        screen_y = int(fingertip_pixel[1] / cam_height * screen_height)

        # Smooth cursor: average last 3 positions from pos_history
        self.pos_history.append((screen_x, screen_y))
        last_3 = list(self.pos_history)[-3:]
        avg_x = int(sum(p[0] for p in last_3) / len(last_3))
        avg_y = int(sum(p[1] for p in last_3) / len(last_3))
        smoothed_cursor = (avg_x, avg_y)

        # Calculate velocity
        vx = smoothed_cursor[0] - self.prev_cursor[0]
        vy = smoothed_cursor[1] - self.prev_cursor[1]
        velocity = (vx, vy)
        
        self.prev_cursor = smoothed_cursor

        # is_slicing
        is_slicing = (abs(vx) + abs(vy)) > SLICE_VELOCITY_THRESHOLD

        # is_pinching: distance between 4 (thumb tip) and 8 (index tip)
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        dist = math.hypot(thumb_tip[0] - index_tip[0], thumb_tip[1] - index_tip[1])
        is_pinching = dist < 0.05

        # is_fist: checking if fingertips (8, 12, 16, 20) are below their respective joints (6, 10, 14, 18)
        # Note: in normalized coords, y=0 is top, y=1 is bottom, so 'greater than' means lower physically
        is_fist = (
            landmarks[8][1] > landmarks[6][1] and
            landmarks[12][1] > landmarks[10][1] and
            landmarks[16][1] > landmarks[14][1] and
            landmarks[20][1] > landmarks[18][1]
        )

        return GestureState(
            cursor_pos=smoothed_cursor,
            is_slicing=is_slicing,
            is_pinching=is_pinching,
            is_fist=is_fist,
            velocity=velocity,
            hand_detected=True
        )

    def no_hand_state(self) -> GestureState:
        return GestureState(
            cursor_pos=(0, 0),
            is_slicing=False,
            is_pinching=False,
            is_fist=False,
            velocity=(0, 0),
            hand_detected=False
        )
