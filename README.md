# 🐦 Hand Flappy PRO

> A webcam-controlled Flappy Bird-style game where you control the bird using your hand.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Pygame](https://img.shields.io/badge/Game-Pygame-green)
![OpenCV](https://img.shields.io/badge/Computer%20Vision-OpenCV-red)
![MediaPipe](https://img.shields.io/badge/Hand%20Tracking-MediaPipe-orange)
![Status](https://img.shields.io/badge/Status-Playable-success)

---

## 🎮 About

**Hand Flappy PRO** is a Python game inspired by Flappy Bird.

Instead of pressing a key to make the bird fly, you use your **webcam and hand movement**.

Raise your hand to flap.

Try to pass through as many pipes as possible without crashing.

---

## ✋ How it works

The game uses:

- **MediaPipe** → detects your hand
- **OpenCV** → captures the webcam
- **Pygame** → runs and displays the game
- **Python** → connects everything together

The basic flow is:

```text
Webcam
   ↓
OpenCV
   ↓
MediaPipe hand tracking
   ↓
Hand movement detected
   ↓
Flap
   ↓
Pygame game
```

---

## 🕹️ Controls

| Key | Action |
|---|---|
| `ENTER` | Start / restart |
| `P` | Pause |
| `R` | Reposition windows |
| `K` | Recalibrate hand tracking |
| `C` | Mirror camera |
| `F` | Show FPS |
| `M` | Toggle sound |
| `ESC` | Quit |

### Hand control

Raise your hand upward to make the bird flap.

---

## 💻 Requirements

You need:

- Windows PC
- Python
- Working webcam
- Internet connection for installing dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the game

Clone the repository:

```bash
git clone https://github.com/hitsonpaudel2/hand-flappy-.git
```

Enter the project folder:

```bash
cd hand-flappy-
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the game:

```bash
python hand_flappy_PRO.py
```

Allow camera access if Windows asks for permission.

---

## 📷 Camera

The game uses your webcam for real-time hand tracking.

For the best experience:

- Use a well-lit room
- Keep your hand visible
- Keep your hand inside the camera frame
- Avoid very dark backgrounds

---

## 🏆 Features

- ✋ Real-time hand tracking
- 🎮 Webcam-controlled gameplay
- 📈 Increasing difficulty
- 🏆 High-score system
- 🔥 Combo tracking
- ✨ Particle effects
- 🌅 Changing backgrounds
- 🔊 Sound controls
- ⏸️ Pause system
- 🔄 Hand recalibration
- 🪟 Separate game and camera windows

---

## 🛠️ Built With

- Python
- Pygame
- OpenCV
- MediaPipe
- NumPy
- PyVirtualCam

---

## 🚧 Future Improvements

Planned improvements:

- [ ] Embedded camera inside the game window
- [ ] Better UI
- [ ] More game modes
- [ ] Difficulty settings
- [ ] Online leaderboard
- [ ] Custom skins
- [ ] Sound effects and music improvements
- [ ] Windows executable release

---

## 👨‍💻 Author

**Hitson Paudel**

Built as a learning project while exploring:

- Python
- Game development
- Computer vision
- Hand tracking
- Git & GitHub

---

## ⭐ Support

If you like the project, consider giving it a ⭐ on GitHub!

Thanks for checking out **Hand Flappy PRO** 🐦