# GestureSlash

A gesture-controlled Fruit Ninja clone using OpenCV, MediaPipe, and Pygame.

## Installation
Ensure you have Python 3.8+ installed, then run:
```bash
pip install -r requirements.txt
```

## Running the Game
To start the gesture engine and the game, simply run:
```bash
python main.py
```
*Note: Make sure your webcam is active and you are positioned correctly in front of the camera.*

## Gesture Controls
| Action | Gesture |
| --- | --- |
| Cursor Movement | Move index fingertip |
| Slice | Fast swiping motion |
| Click/Select | Pinch (Index and Thumb together) |
| UI/Menu | Fist (curled fingers) - mapped internally |

## Known Issues / Troubleshooting
- **Camera not found:** Ensure `CAMERA_INDEX` in `config.py` correctly points to your webcam (usually 0 or 1).
- **MediaPipe on M1 Mac:** If you face MediaPipe installation or import errors on ARM Macs, you may need to use a specific installation method or Rosetta. Note that the latest MediaPipe versions support native arm64 but verify via pip. 
