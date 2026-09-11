# 🐦 Hand Flappy PRO

A hand-controlled Flappy Bird-style game built with computer vision.

## 🎮 Two Ways to Play

Hand Flappy PRO is available in two versions:

### 💻 Desktop Version

A Windows desktop game built with Python, Pygame, OpenCV, and MediaPipe.

Download and run the desktop version on your computer.

### 🌐 Browser Version

A web version built with HTML, CSS, JavaScript, and MediaPipe, allowing you to play directly in your browser.


👉 PLAY HAND FLAPPY PRO ONLINE 
**[▶️ PLAY HAND FLAPPY PRO](https://hitsonpaudel2.github.io/hand-flappy-/)**

---

## 🎮 About the Project

**Hand Flappy PRO** is a hand-controlled Flappy Bird-style game that lets you control the bird using **real-time hand movement** instead of a keyboard.

The project started as a **Python desktop game** and was later expanded into a **browser version**, allowing people to play directly from a website.

### ✋ How it works


Hand Flappy PRO has **two versions**: a Python desktop version and a browser version.

### 💻 Desktop Version

The original game runs on Windows using Python.

```text
Webcam
   ↓
OpenCV
   ↓
MediaPipe Hands
   ↓
Hand Movement Detection
   ↓
Python
   ↓
Pygame
   ↓
🐦 Hand Flappy PRO
```

The desktop version uses **OpenCV** to capture the webcam, **MediaPipe** to detect the hand, and **Pygame** to run the game.

Move your hand upward quickly to make the bird flap.

---

### 🌐 Browser Version

The browser version brings the same idea to the web, so players can play without installing Python.

```text
Webcam
   ↓
MediaPipe Hands
   ↓
JavaScript Hand Movement Detection
   ↓
HTML Canvas
   ↓
🐦 Hand Flappy PRO
```

The browser version uses the **Web Camera API**, **MediaPipe Hands**, **JavaScript**, and **HTML Canvas**.

Players simply open the game in their browser, allow camera access, and use their hand to control the bird.

### ✋ Hand Control

Both versions use a similar movement-based control system.

The game tracks the five fingertips:

```text
Thumb    → 4
Index    → 8
Middle   → 12
Ring     → 16
Pinky    → 20
```

Their positions are averaged and smoothed to reduce noise. The game then detects **upward hand movement** and triggers the bird's flap.

```text
✋ Hand moves UP
       ↓
Movement detected
       ↓
Flap triggered
       ↓
🐦 Bird jumps
```

This allows the player to control the game naturally using hand movement instead of relying entirely on traditional keyboard controls.


---

## 🌐 Play Online

### 🎮 Browser Version

No Python installation is required.

Just:

1. Open the game.
2. Allow camera access.
3. Click **START GAME**.
4. Move your hand upward to flap.
5. Avoid the pipes.
6. Try to beat your high score!

> 📷 Camera access is required for hand control.

---

## ✨ Features

* ✋ Real-time hand tracking
* 📷 Webcam control
* 🧠 MediaPipe hand detection
* 🐦 Flappy Bird-style gameplay
* 💥 Pipe collision detection
* 🏆 Score system
* 💾 Best score saved in the browser
* 🎨 Multiple visual themes
* 🎉 Score milestone celebrations
* 💻 Python desktop version
* 🌐 Browser version
* 📱 Touch support
* ⌨️ Keyboard testing controls
* ⚡ Runs directly in the browser

---

### ✋ Move hand upward

```text
Hand moves UP
      ↓
Upward velocity detected
      ↓
Flap triggered
      ↓
🐦 Bird jumps
```

This makes the control feel more natural than simply checking whether your finger is pointing upward.

---

## 🛠️ Technologies Used

### Desktop Version

* 🐍 Python
* 🎮 Pygame
* 📷 OpenCV
* ✋ MediaPipe
* 📦 PyInstaller

### Browser Version

* 🌐 HTML
* 🎨 CSS
* ⚡ JavaScript
* ✋ MediaPipe Hands
* 🎥 Web Camera API
* 🖼️ HTML Canvas
* 🚀 GitHub Pages

---

## 📁 Project Structure

```text
hand-flappy-/
│
├── browser/
│   ├── index.html
│   ├── style.css
│   └── game.js
│
├── hand_flappy_PRO.py
│
├── dist/
│   └── HandFlappyPRO/
│
└── README.md
```

> The exact files in the repository may change as the project continues to develop.

---

## 💻 Desktop Version

The original version of Hand Flappy PRO was created with Python.

The desktop version uses:

* OpenCV for the webcam
* MediaPipe for hand tracking
* Pygame for the game
* PyInstaller to create a Windows executable

### Run from source

Install the required Python packages:

```bash
pip install pygame opencv-python mediapipe
```

Then run:

```bash
python hand_flappy_PRO.py
```

---

## 📦 Windows Executable

A Windows executable version can also be created using **PyInstaller**.

Example:

```bash
pyinstaller --onedir --windowed --name HandFlappyPRO hand_flappy_PRO.py
```

The generated application can then be found inside:

```text
dist/HandFlappyPRO/
```

---

## 🌐 Browser Version

The browser version was created so that people don't need to install Python or download the game.

It uses:

```text
HTML
CSS
JavaScript
   +
MediaPipe Hands
   +
Webcam
   ↓
Browser Game
```

The game is hosted using **GitHub Pages**.


---

## 🎯 Goal

The goal is simple:

> **Move your hand upward and keep the bird flying.**

Avoid the pipes and try to get the highest score possible.

---

## 🚀 Future Plans

This project is still being developed.

Possible future improvements include:

* 🌐 Online multiplayer
* 🏆 Global leaderboard
* 👥 Player profiles
* 🎵 Sound effects and music
* 🎨 More themes
* 🐦 More characters
* 📱 Better mobile support
* 🎮 More control methods
* ☁️ Online score storage
* 🔥 Difficulty progression
* 📊 Player statistics
* 🥇 Global high-score system

---

## 📸 Screenshots

Screenshots and gameplay videos will be added here as the project develops.

```text
Coming soon...
```

---

## 📚 What I Learned

This project helped me learn and practice:

* Python programming
* JavaScript programming
* HTML and CSS
* Game development
* Game physics
* Collision detection
* Computer vision
* Hand tracking
* MediaPipe
* Webcam APIs
* Canvas rendering
* Git
* GitHub
* GitHub Pages
* PyInstaller
* Debugging
* Building a project from desktop → web

---

## 👨‍💻 Developer

**Hitson**

Built as a learning project to explore **game development, computer vision, hand tracking, and web development**.

---

## ⭐ Support the Project

If you like the project, consider giving it a ⭐ on GitHub!

Every star helps motivate further development. 🚀

---

## 📜 License

This project is currently intended as a personal learning project.

More information about the license will be added as the project develops.

---

# 🐦 Keep Flying!

**Move your hand. Control the bird. Beat your score.**

