
import os
import json
import math
import random
import time
import uuid
from collections import deque

import cv2
import mediapipe as mp
import numpy as np
import pygame

try:
    import pyvirtualcam
except Exception:
    pyvirtualcam = None


# ============================================================
# HAND FLAPPY PRO
# A webcam-controlled Flappy Bird style game.
# ============================================================

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60

BIRD_X = 130
BIRD_RADIUS = 16

GRAVITY = 0.42
FLAP_POWER = -8.0
MAX_FALL_SPEED = 10.5

PIPE_WIDTH = 72
BASE_GAP = 205
PIPE_SPEED = 3.2
MAX_PIPE_SPEED = 7.0

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

HIGH_SCORE_FILE = "hand_flappy_highscore.json"


# ---------------- Window layout ----------------

def get_screen_size():
    try:
        import ctypes
        user32 = ctypes.windll.user32
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    except Exception:
        return 1366, 768


def calculate_window_layout():
    sw, sh = get_screen_size()
    margin = 20
    gap = 20

    game_w = SCREEN_WIDTH
    game_h = SCREEN_HEIGHT

    # Scale the game down only when the monitor is too small.
    max_game_h = sh - 80
    if game_h > max_game_h:
        scale = max_game_h / game_h
        game_w = max(480, int(game_w * scale))
        game_h = max(640, int(game_h * scale))

    total_width = game_w + gap + CAMERA_WIDTH
    if total_width > sw - margin * 2:
        game_w = max(480, sw - margin * 2 - gap - CAMERA_WIDTH)

    game_x = margin
    game_y = max(20, (sh - game_h) // 2)

    camera_x = min(sw - CAMERA_WIDTH - margin, game_x + game_w + gap)
    camera_y = max(20, (sh - CAMERA_HEIGHT) // 2)

    return game_w, game_h, game_x, game_y, camera_x, camera_y


# ---------------- Saved data ----------------

def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as f:
            return max(0, int(json.load(f).get("high_score", 0)))
    except Exception:
        return 0


def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump({"high_score": int(score)}, f, indent=2)
    except Exception:
        pass


# ---------------- Sound ----------------

class SoundManager:
    def __init__(self):
        self.enabled = True
        self.sounds = {}

        try:
            pygame.mixer.init()
            self.sounds["flap"] = self.make_beep(520, 0.07)
            self.sounds["score"] = self.make_beep(820, 0.09)
            self.sounds["hit"] = self.make_beep(150, 0.18)
            self.sounds["milestone"] = self.make_beep(1100, 0.15)
        except Exception:
            self.enabled = False

    def make_beep(self, frequency, duration):
        sample_rate = 44100
        count = int(sample_rate * duration)
        wave = np.zeros((count, 2), dtype=np.int16)

        for i in range(count):
            envelope = 1.0 - (i / max(1, count))
            value = int(7000 * envelope * math.sin(
                2 * math.pi * frequency * i / sample_rate
            ))
            wave[i] = (value, value)

        return pygame.sndarray.make_sound(wave)

    def play(self, name):
        if self.enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception:
                pass

    def toggle(self):
        self.enabled = not self.enabled


# ---------------- Hand tracking ----------------

class HandSensor:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.65,
            min_tracking_confidence=0.65,
        )

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

        self.history = deque(maxlen=7)
        self.last_y = None
        self.velocity = 0.0
        self.last_flap = 0.0
        self.flap_cooldown = 0.16

        self.baseline = None
        self.calibrating = True
        self.calibration_samples = deque(maxlen=30)

        self.camera_open = True
        self.window_name = "Hand Flappy Camera"

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, CAMERA_WIDTH, CAMERA_HEIGHT)

        try:
            self.virtual_camera = pyvirtualcam.Camera(
                width=CAMERA_WIDTH,
                height=CAMERA_HEIGHT,
                fps=CAMERA_FPS,
            )
        except Exception:
            self.virtual_camera = None

    def calibrate(self):
        self.baseline = None
        self.calibrating = True
        self.calibration_samples.clear()

    def detect(self, mirror=True):
        if not self.cap.isOpened():
            return False, None, False

        ok, frame = self.cap.read()
        if not ok:
            return False, None, False

        if mirror:
            frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)

        flap = False
        hand_found = bool(result.multi_hand_landmarks)

        if hand_found:
            hand = result.multi_hand_landmarks[0]

            # Use several fingertips instead of a single noisy point.
            points = [
                hand.landmark[4],
                hand.landmark[8],
                hand.landmark[12],
                hand.landmark[16],
                hand.landmark[20],
            ]

            raw_y = sum(p.y for p in points) / len(points)
            self.history.append(raw_y)

            smooth_y = sum(self.history) / len(self.history)

            if self.calibrating:
                self.calibration_samples.append(smooth_y)
                if len(self.calibration_samples) >= 15:
                    self.baseline = sum(self.calibration_samples) / len(
                        self.calibration_samples
                    )
                    self.calibrating = False

            if self.last_y is not None:
                self.velocity = self.last_y - smooth_y

                # Positive velocity means the hand moved upward.
                now = time.monotonic()
                if (
                    self.velocity > 0.014
                    and now - self.last_flap >= self.flap_cooldown
                ):
                    flap = True
                    self.last_flap = now

            self.last_y = smooth_y

            self.mp_draw.draw_landmarks(
                frame, hand, self.mp_hands.HAND_CONNECTIONS
            )

            if self.baseline is not None:
                baseline_px = int(self.baseline * frame.shape[0])
                cv2.line(
                    frame,
                    (0, baseline_px),
                    (frame.shape[1], baseline_px),
                    (255, 180, 40),
                    2,
                )

        # Camera UI.
        status = "HAND: OK" if hand_found else "HAND: SEARCHING"
        if self.calibrating:
            status = "CALIBRATING..."

        cv2.rectangle(frame, (10, 10), (250, 55), (20, 20, 20), -1)
        cv2.putText(
            frame,
            status,
            (22, 42),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            "Move hand UP to flap",
            (18, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
        )

        try:
            cv2.imshow(self.window_name, frame)
            if self.virtual_camera is not None:
                self.virtual_camera.send(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                self.virtual_camera.sleep_until_next_frame()
        except Exception:
            self.camera_open = False

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            return False, frame, hand_found

        return flap, frame, hand_found

    def close(self):
        try:
            self.cap.release()
        except Exception:
            pass
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
        try:
            if self.virtual_camera is not None:
                self.virtual_camera.close()
        except Exception:
            pass


# ---------------- Visual effects ----------------

class Particle:
    def __init__(self, x, y, vx, vy, life, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08
        self.life -= 1

    def draw(self, screen):
        if self.life <= 0:
            return

        alpha = max(0, min(255, int(255 * self.life / self.max_life)))
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            surf,
            (255, 210, 70, alpha),
            (self.size, self.size),
            self.size,
        )
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))


class FloatingText:
    def __init__(self, text, x, y, color=(255, 255, 255)):
        self.text = text
        self.x = x
        self.y = y
        self.life = 70
        self.color = color

    def update(self):
        self.y -= 0.8
        self.life -= 1

    def draw(self, screen, font):
        if self.life <= 0:
            return

        surf = font.render(self.text, True, self.color)
        alpha = int(255 * self.life / 70)
        surf.set_alpha(alpha)
        screen.blit(surf, (int(self.x), int(self.y)))


# ---------------- Game objects ----------------

class Bird:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = BIRD_X
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0.0
        self.rotation = 0
        self.trail = deque(maxlen=12)

    def flap(self):
        self.velocity = FLAP_POWER

    def update(self):
        self.velocity += GRAVITY
        self.velocity = min(self.velocity, MAX_FALL_SPEED)
        self.y += self.velocity

        target_rotation = max(-28, min(85, self.velocity * 6))
        self.rotation += (target_rotation - self.rotation) * 0.18

        self.trail.append((self.x, self.y))

    def draw(self, screen):
        # Trail.
        for i, (x, y) in enumerate(self.trail):
            radius = max(2, int(8 * (i + 1) / len(self.trail)))
            pygame.draw.circle(screen, (255, 220, 90), (int(x), int(y)), radius)

        # Bird body.
        surf = pygame.Surface((58, 48), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (255, 205, 55), (8, 8, 40, 30))
        pygame.draw.ellipse(surf, (245, 175, 35), (17, 22, 25, 15))
        pygame.draw.circle(surf, (255, 255, 255), (39, 14), 7)
        pygame.draw.circle(surf, (20, 20, 20), (41, 14), 3)

        pygame.draw.polygon(
            surf,
            (235, 120, 30),
            [(47, 23), (58, 28), (47, 31)],
        )

        rotated = pygame.transform.rotate(surf, -self.rotation)
        rect = rotated.get_rect(center=(self.x, self.y))
        screen.blit(rotated, rect)


class Pipe:
    def __init__(self, x, speed, gap):
        self.x = x
        self.speed = speed
        self.width = PIPE_WIDTH
        self.gap = gap
        self.gap_y = random.randint(155, SCREEN_HEIGHT - 210)
        self.scored = False

    def update(self):
        self.x -= self.speed

    def offscreen(self):
        return self.x + self.width < 0

    def collides(self, bird):
        bx, by = bird.x, bird.y

        horizontal = (
            bx + BIRD_RADIUS > self.x
            and bx - BIRD_RADIUS < self.x + self.width
        )

        if not horizontal:
            return False

        top_end = self.gap_y - self.gap / 2
        bottom_start = self.gap_y + self.gap / 2

        return by - BIRD_RADIUS < top_end or by + BIRD_RADIUS > bottom_start

    def draw(self, screen):
        top_h = int(self.gap_y - self.gap / 2)
        bottom_y = int(self.gap_y + self.gap / 2)

        pygame.draw.rect(
            screen,
            (72, 185, 82),
            (int(self.x), 0, self.width, top_h),
        )
        pygame.draw.rect(
            screen,
            (72, 185, 82),
            (int(self.x), bottom_y, self.width, SCREEN_HEIGHT - bottom_y),
        )

        cap_h = 18
        pygame.draw.rect(
            screen,
            (52, 150, 65),
            (int(self.x - 6), top_h - cap_h, self.width + 12, cap_h),
        )
        pygame.draw.rect(
            screen,
            (52, 150, 65),
            (int(self.x - 6), bottom_y, self.width + 12, cap_h),
        )

        # Highlight stripe.
        pygame.draw.rect(
            screen,
            (125, 225, 125),
            (int(self.x + 9), 0, 7, max(0, top_h - cap_h)),
        )
        pygame.draw.rect(
            screen,
            (125, 225, 125),
            (int(self.x + 9), bottom_y + cap_h, 7,
             max(0, SCREEN_HEIGHT - bottom_y - cap_h)),
        )


# ---------------- Background ----------------

class Background:
    def __init__(self):
        self.clouds = [
            [random.randint(0, SCREEN_WIDTH), random.randint(70, 350),
             random.randint(35, 70), random.uniform(0.15, 0.35)]
            for _ in range(8)
        ]
        self.stars = [
            [random.randint(0, SCREEN_WIDTH), random.randint(20, 560),
             random.randint(1, 3)]
            for _ in range(60)
        ]

    def theme(self, score):
        phase = (score // 5) % 4
        return phase

    def draw(self, screen, score):
        phase = self.theme(score)

        if phase == 0:
            top = (80, 180, 235)
            bottom = (205, 240, 255)
        elif phase == 1:
            top = (220, 120, 100)
            bottom = (255, 205, 120)
        elif phase == 2:
            top = (20, 30, 65)
            bottom = (65, 70, 120)
        else:
            top = (35, 25, 60)
            bottom = (100, 55, 130)

        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))

        if phase >= 2:
            for x, y, r in self.stars:
                pygame.draw.circle(screen, (240, 240, 255), (x, y), r)

        if phase < 2:
            for cloud in self.clouds:
                cloud[0] -= cloud[3]
                if cloud[0] < -120:
                    cloud[0] = SCREEN_WIDTH + random.randint(10, 100)

                x, y, size, _ = cloud
                pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), size // 2)
                pygame.draw.circle(screen, (255, 255, 255),
                                   (int(x + size * .45), int(y - 8)), size // 2)
                pygame.draw.circle(screen, (255, 255, 255),
                                   (int(x + size * .8), int(y + 3)), size // 2)

        # Ground.
        pygame.draw.rect(
            screen,
            (100, 185, 80),
            (0, SCREEN_HEIGHT - 55, SCREEN_WIDTH, 55),
        )
        pygame.draw.rect(
            screen,
            (70, 135, 60),
            (0, SCREEN_HEIGHT - 55, SCREEN_WIDTH, 8),
        )


# ---------------- Main game ----------------

class Game:
    def __init__(self):
        pygame.init()

        self.game_w, self.game_h, self.game_x, self.game_y, self.cam_x, self.cam_y = (
            calculate_window_layout()
        )

        os.environ["SDL_VIDEO_WINDOW_POS"] = f"{self.game_x},{self.game_y}"

        self.screen = pygame.display.set_mode(
            (self.game_w, self.game_h),
            pygame.RESIZABLE,
        )
        pygame.display.set_caption("Hand Flappy PRO")

        self.base_screen_size = (self.game_w, self.game_h)

        try:
            cv2.moveWindow("Hand Flappy Camera", self.cam_x, self.cam_y)
        except Exception:
            pass

        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont("arial", 58, bold=True)
        self.font_title = pygame.font.SysFont("arial", 42, bold=True)
        self.font = pygame.font.SysFont("arial", 27, bold=True)
        self.font_small = pygame.font.SysFont("arial", 19, bold=True)

        self.bird = Bird()
        self.sensor = HandSensor()
        self.background = Background()
        self.sound = SoundManager()

        self.high_score = load_high_score()
        self.score = 0
        self.pipes = []
        self.particles = []
        self.texts = []

        self.state = "menu"
        self.running = True
        self.paused = False

        self.pipe_timer = 0
        self.pipe_interval = 1450
        self.difficulty_speed = PIPE_SPEED

        self.combo = 0
        self.best_combo = 0
        self.last_milestone = 0
        self.screen_shake = 0

        self.show_fps = False
        self.camera_mirror = True

        self.countdown = 0
        self.countdown_start = 0

    def reposition_windows(self):
        (
            self.game_w,
            self.game_h,
            self.game_x,
            self.game_y,
            self.cam_x,
            self.cam_y,
        ) = calculate_window_layout()

        try:
            os.environ["SDL_VIDEO_WINDOW_POS"] = f"{self.game_x},{self.game_y}"
            pygame.display.set_mode((self.game_w, self.game_h), pygame.RESIZABLE)
            cv2.moveWindow("Hand Flappy Camera", self.cam_x, self.cam_y)
        except Exception:
            pass

    def start_game(self):
        self.bird.reset()
        self.pipes.clear()
        self.particles.clear()
        self.texts.clear()

        self.score = 0
        self.combo = 0
        self.last_milestone = 0
        self.difficulty_speed = PIPE_SPEED
        self.pipe_interval = 1450
        self.pipe_timer = 0

        self.state = "countdown"
        self.countdown_start = time.monotonic()
        self.countdown = 3

        self.sensor.calibrate()

    def spawn_pipe(self):
        self.pipes.append(
            Pipe(SCREEN_WIDTH + 40, self.difficulty_speed, self.current_gap())
        )

    def current_gap(self):
        # Slowly tighten the gap, but keep the game fair.
        return max(155, BASE_GAP - self.score * 1.5)

    def add_flap_particles(self):
        for _ in range(8):
            self.particles.append(
                Particle(
                    self.bird.x - 10,
                    self.bird.y + random.randint(-6, 6),
                    random.uniform(-3.0, -0.5),
                    random.uniform(-1.5, 1.5),
                    random.randint(18, 32),
                    random.randint(2, 5),
                )
            )

    def add_score(self):
        self.score += 1
        self.combo += 1
        self.best_combo = max(self.best_combo, self.combo)

        self.sound.play("score")
        self.texts.append(
            FloatingText("+1", self.bird.x + 25, self.bird.y - 35, (255, 245, 100))
        )

        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)

        if self.score % 5 == 0 and self.score != self.last_milestone:
            self.last_milestone = self.score
            self.sound.play("milestone")
            self.screen_shake = 7
            self.texts.append(
                FloatingText(
                    f"{self.score} POINT MILESTONE!",
                    175,
                    220,
                    (255, 255, 255),
                )
            )

        # Difficulty ramps smoothly.
        self.difficulty_speed = min(
            MAX_PIPE_SPEED,
            PIPE_SPEED + self.score * 0.085,
        )
        self.pipe_interval = max(1050, 1450 - self.score * 10)

    def game_over(self):
        if self.state == "gameover":
            return

        self.state = "gameover"
        self.combo = 0
        self.sound.play("hit")
        self.screen_shake = 12

        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)

        for _ in range(30):
            self.particles.append(
                Particle(
                    self.bird.x,
                    self.bird.y,
                    random.uniform(-5, 5),
                    random.uniform(-5, 5),
                    random.randint(20, 45),
                    random.randint(2, 6),
                )
            )

    def update_countdown(self):
        elapsed = time.monotonic() - self.countdown_start
        self.countdown = 3 - int(elapsed)

        if elapsed >= 3:
            self.state = "playing"

    def update_playing(self, flap):
        if flap:
            self.bird.flap()
            self.add_flap_particles()
            self.sound.play("flap")

        self.bird.update()

        self.pipe_timer += 1000 / FPS
        if self.pipe_timer >= self.pipe_interval:
            self.pipe_timer = 0
            self.spawn_pipe()

        for pipe in self.pipes:
            pipe.speed = self.difficulty_speed
            pipe.update()

            if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.add_score()

            if pipe.collides(self.bird):
                self.game_over()

        self.pipes = [p for p in self.pipes if not p.offscreen()]

        if self.bird.y - BIRD_RADIUS <= 0:
            self.bird.y = BIRD_RADIUS
            self.game_over()

        if self.bird.y + BIRD_RADIUS >= SCREEN_HEIGHT - 55:
            self.bird.y = SCREEN_HEIGHT - 55 - BIRD_RADIUS
            self.game_over()

    def update_effects(self):
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.life > 0]

        for text in self.texts:
            text.update()
        self.texts = [t for t in self.texts if t.life > 0]

        if self.screen_shake > 0:
            self.screen_shake -= 1

    def draw_centered(self, text, y, font, shadow=True):
        surf = font.render(text, True, (255, 255, 255))
        rect = surf.get_rect(center=(SCREEN_WIDTH // 2, y))

        if shadow:
            shadow_surf = font.render(text, True, (20, 20, 20))
            shadow_rect = shadow_surf.get_rect(center=(rect.centerx + 3, rect.centery + 3))
            self.screen.blit(shadow_surf, shadow_rect)

        self.screen.blit(surf, rect)

    def draw_hud(self, hand_found):
        panel = pygame.Surface((SCREEN_WIDTH, 92), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 75))
        self.screen.blit(panel, (0, 0))

        score = self.font_big.render(str(self.score), True, (255, 255, 255))
        score_rect = score.get_rect(center=(SCREEN_WIDTH // 2, 48))
        self.screen.blit(score, score_rect)

        best = self.font_small.render(
            f"BEST {self.high_score}", True, (255, 255, 255)
        )
        self.screen.blit(best, (18, 18))

        speed = self.font_small.render(
            f"SPEED {self.difficulty_speed:.1f}", True, (255, 255, 255)
        )
        self.screen.blit(speed, (18, 47))

        hand = "HAND OK" if hand_found else "HAND SEARCHING"
        hand_surf = self.font_small.render(hand, True, (255, 255, 255))
        self.screen.blit(hand_surf, (SCREEN_WIDTH - hand_surf.get_width() - 18, 18))

        combo = self.font_small.render(
            f"COMBO {self.best_combo}", True, (255, 255, 255)
        )
        self.screen.blit(combo, (SCREEN_WIDTH - combo.get_width() - 18, 47))

    def draw_overlay(self, alpha=155):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))

    def draw_menu(self):
        self.draw_overlay(90)

        self.draw_centered("HAND FLAPPY", 220, self.font_big)
        self.draw_centered("PRO", 280, self.font_title)

        self.draw_centered("Wave your hand UP to flap", 370, self.font)
        self.draw_centered("ENTER  •  START GAME", 430, self.font)

        self.draw_centered("P Pause   R Reposition   K Calibrate", 505, self.font_small)
        self.draw_centered("C Mirror Camera   F FPS   M Sound", 535, self.font_small)
        self.draw_centered("ESC Quit", 565, self.font_small)

        self.draw_centered(
            f"BEST SCORE  {self.high_score}",
            650,
            self.font,
        )

    def draw_countdown(self):
        self.draw_overlay(80)
        self.draw_centered("GET READY", 280, self.font_title)
        number = max(1, self.countdown)
        self.draw_centered(str(number), 390, self.font_big)

    def draw_pause(self):
        self.draw_overlay(150)
        self.draw_centered("PAUSED", 330, self.font_big)
        self.draw_centered("Press P to continue", 405, self.font)

    def draw_gameover(self):
        self.draw_overlay(150)
        self.draw_centered("GAME OVER", 260, self.font_big)
        self.draw_centered(f"SCORE  {self.score}", 350, self.font)
        self.draw_centered(f"BEST  {self.high_score}", 395, self.font)
        self.draw_centered("ENTER  •  PLAY AGAIN", 485, self.font)
        self.draw_centered("ESC  •  QUIT", 535, self.font)

    def draw(self, hand_found):
        self.background.draw(self.screen, self.score)

        for pipe in self.pipes:
            pipe.draw(self.screen)

        for particle in self.particles:
            particle.draw(self.screen)

        self.bird.draw(self.screen)
        self.draw_hud(hand_found)

        for text in self.texts:
            text.draw(self.screen, self.font)

        if self.state == "menu":
            self.draw_menu()
        elif self.state == "countdown":
            self.draw_countdown()
        elif self.paused:
            self.draw_pause()
        elif self.state == "gameover":
            self.draw_gameover()

        if self.show_fps:
            fps = self.font_small.render(
                f"FPS {self.clock.get_fps():.0f}", True, (255, 255, 255)
            )
            self.screen.blit(fps, (SCREEN_WIDTH - fps.get_width() - 18, SCREEN_HEIGHT - 35))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_RETURN:
                    if self.state in ("menu", "gameover"):
                        self.start_game()

                elif event.key == pygame.K_p:
                    if self.state == "playing":
                        self.paused = not self.paused

                elif event.key == pygame.K_m:
                    self.sound.toggle()

                elif event.key == pygame.K_r:
                    self.reposition_windows()

                elif event.key == pygame.K_k:
                    self.sensor.calibrate()

                elif event.key == pygame.K_c:
                    self.camera_mirror = not self.camera_mirror

                elif event.key == pygame.K_f:
                    self.show_fps = not self.show_fps

    def run(self):
        print("\n=== HAND FLAPPY PRO ===")
        print("Game window: LEFT")
        print("Camera window: RIGHT")
        print("ENTER = start/restart")
        print("P = pause | R = reposition | K = recalibrate")
        print("C = mirror camera | F = FPS | M = sound | ESC = quit\n")

        try:
            while self.running:
                self.handle_events()

                flap, _, hand_found = self.sensor.detect(self.camera_mirror)

                if self.state == "countdown":
                    self.update_countdown()

                elif self.state == "playing" and not self.paused:
                    self.update_playing(flap)

                self.update_effects()

                # Draw at the original logical resolution.
                frame = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                old_screen = self.screen
                self.screen = frame
                self.draw(hand_found)

                # Scale logical game to actual window size.
                scaled = pygame.transform.smoothscale(
                    frame, old_screen.get_size()
                )

                shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake else 0
                shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake else 0

                old_screen.fill((0, 0, 0))
                old_screen.blit(scaled, (shake_x, shake_y))
                self.screen = old_screen

                pygame.display.flip()
                self.clock.tick(FPS)

        finally:
            save_high_score(self.high_score)
            self.sensor.close()
            pygame.quit()


if __name__ == "__main__":
    Game().run()
