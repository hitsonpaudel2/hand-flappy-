const webcam = document.getElementById("webcam");
const handCanvas = document.getElementById("handCanvas");
const handCtx = handCanvas.getContext("2d");
let previousHandY = null;
let smoothHandY = null;
let handHistory = [];
let lastHandY = null;
let lastFlapTime = 0;

const HAND_HISTORY_SIZE = 7;
const FLAP_THRESHOLD = 0.014;
const FLAP_COOLDOWN = 160;

// ==============================
// START WEBCAM
// ==============================

async function startWebcam() {

    try {

        const stream =
            await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: false
            });

        webcam.srcObject = stream;

        console.log("WEBCAM STARTED");

    } catch (error) {

        console.error(
            "WEBCAM ERROR:",
            error
        );

        alert(
            "Camera permission was denied or the camera is unavailable."
        );
    }
}


// Start camera

startWebcam();
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const startButton = document.getElementById("startButton");

canvas.width = 480;
canvas.height = 640;


// =====================================================
// GAME STATE
// =====================================================

let state = "ready";

let score = 0;
let bestScore = Number(localStorage.getItem("handFlappyBest")) || 0;

let pipes = [];
let pipeTimer = 0;

let celebrationTimer = 0;
let celebrationScore = 0;

let particles = [];


// =====================================================
// GAME SETTINGS
// =====================================================

const GAME = {
    gravity: 0.45,
    flapPower: -6,
    pipeSpeed: 4,
    pipeWidth: 72,
    pipeGap: 175,
    pipeInterval: 105
};


// =====================================================
// THEMES
// =====================================================

const themes = [
    {
        skyTop: "#55c7ff",
        skyBottom: "#d8f4ff",
        ground: "#76b852",
        groundDark: "#4c8c35",
        pipe: "#35a83a",
        pipeDark: "#1f7225"
    },

    {
        skyTop: "#ff9a9e",
        skyBottom: "#fad0c4",
        ground: "#7cbd5b",
        groundDark: "#4d8c35",
        pipe: "#35a83a",
        pipeDark: "#1f7225"
    },

    {
        skyTop: "#667eea",
        skyBottom: "#764ba2",
        ground: "#4e8c42",
        groundDark: "#315d2a",
        pipe: "#48b84d",
        pipeDark: "#247128"
    },

    {
        skyTop: "#ff9966",
        skyBottom: "#ff5e62",
        ground: "#66a64f",
        groundDark: "#3f7130",
        pipe: "#43ad47",
        pipeDark: "#216b25"
    },

    {
        skyTop: "#36d1dc",
        skyBottom: "#5b86e5",
        ground: "#5ca64d",
        groundDark: "#3c7032",
        pipe: "#48b84d",
        pipeDark: "#247128"
    },

    {
        skyTop: "#141e30",
        skyBottom: "#243b55",
        ground: "#4d7942",
        groundDark: "#304d29",
        pipe: "#4caf50",
        pipeDark: "#256628"
    }
];


// =====================================================
// GET CURRENT THEME
// =====================================================

function getTheme() {

    const themeIndex =
        Math.floor(score / 10) % themes.length;

    return themes[themeIndex];
}


// =====================================================
// BIRD
// =====================================================

const bird = {
    x: 120,
    y: 300,
    radius: 19,
    velocity: 0,
    rotation: 0,
    wingAngle: 0
};


// =====================================================
// RESET
// =====================================================

function resetGame() {

    bird.x = 120;
    bird.y = 300;
    bird.velocity = 0;
    bird.rotation = 0;
    bird.wingAngle = 0;

    pipes = [];
    pipeTimer = 0;

    score = 0;

    celebrationTimer = 0;
    celebrationScore = 0;

    particles = [];
}


// =====================================================
// START
// =====================================================

function startGame() {

    resetGame();

    state = "playing";

    startButton.textContent = "RESTART";

    flap();
}


// =====================================================
// GAME OVER
// =====================================================

function gameOver() {

    if (state !== "playing") {
        return;
    }

    state = "gameover";

    if (score > bestScore) {

        bestScore = score;

        localStorage.setItem(
            "handFlappyBest",
            bestScore
        );
    }

    startButton.textContent = "PLAY AGAIN";
}


// =====================================================
// FLAP
// =====================================================

function flap() {

    if (state === "ready") {
        startGame();
        return;
    }

    if (state === "gameover") {
        startGame();
        return;
    }

    bird.velocity = GAME.flapPower;
}


// =====================================================
// CREATE PIPE
// =====================================================

function createPipe() {

    const minimumTop = 80;

    const maximumTop =
        canvas.height -
        GAME.pipeGap -
        100;

    const topHeight =
        Math.random() *
        (maximumTop - minimumTop)
        + minimumTop;

    pipes.push({

        x: canvas.width,

        top: topHeight,

        bottom:
            topHeight + GAME.pipeGap,

        scored: false
    });
}


// =====================================================
// UPDATE BIRD
// =====================================================

function updateBird() {

    if (state !== "playing") {
        return;
    }

    bird.velocity += GAME.gravity;

    bird.y += bird.velocity;

    bird.rotation =
        Math.max(
            -0.5,
            Math.min(
                1,
                bird.velocity * 0.06
            )
        );

    bird.wingAngle += 0.25;


    // Ceiling

    if (
        bird.y - bird.radius <= 0
    ) {

        bird.y = bird.radius;

        bird.velocity = 0;
    }


    // Ground

    if (
        bird.y + bird.radius >=
        canvas.height - 55
    ) {

        bird.y =
            canvas.height - 55 -
            bird.radius;

        gameOver();
    }
}


// =====================================================
// UPDATE PIPES
// =====================================================

function updatePipes() {

    if (state !== "playing") {
        return;
    }

    for (const pipe of pipes) {

        pipe.x -= GAME.pipeSpeed;


        // Score

        if (
            !pipe.scored &&
            pipe.x + GAME.pipeWidth < bird.x
        ) {

            pipe.scored = true;

            score++;

            checkCelebration();
        }
    }


    pipes = pipes.filter(
        pipe =>
            pipe.x + GAME.pipeWidth > 0
    );


    pipeTimer++;

    if (
        pipeTimer >=
        GAME.pipeInterval
    ) {

        createPipe();

        pipeTimer = 0;
    }
}


// =====================================================
// CELEBRATION CHECK
// =====================================================

function checkCelebration() {

    if (
        score > 0 &&
        score % 20 === 0
    ) {

        celebrationTimer = 180;

        celebrationScore = score;

        createConfetti();
    }
}


// =====================================================
// CONFETTI
// =====================================================

function createConfetti() {

    for (let i = 0; i < 80; i++) {

        particles.push({

            x: canvas.width / 2,

            y: 180,

            vx:
                (Math.random() - 0.5) * 8,

            vy:
                (Math.random() - 0.8) * 8,

            size:
                Math.random() * 7 + 3,

            life: 120,

            rotation:
                Math.random() * Math.PI
        });
    }
}


// =====================================================
// UPDATE CONFETTI
// =====================================================

function updateParticles() {

    for (const particle of particles) {

        particle.x += particle.vx;

        particle.y += particle.vy;

        particle.vy += 0.12;

        particle.life--;

        particle.rotation += 0.1;
    }

    particles =
        particles.filter(
            particle =>
                particle.life > 0
        );
}


// =====================================================
// DRAW CONFETTI
// =====================================================

function drawParticles() {

    for (const particle of particles) {

        ctx.save();

        ctx.translate(
            particle.x,
            particle.y
        );

        ctx.rotate(
            particle.rotation
        );

        ctx.fillStyle =
            `hsl(${Math.random() * 360}, 90%, 60%)`;

        ctx.fillRect(
            -particle.size / 2,
            -particle.size / 2,
            particle.size,
            particle.size
        );

        ctx.restore();
    }
}


// =====================================================
// COLLISION
// =====================================================

function checkCollision() {

    if (state !== "playing") {
        return;
    }

    for (const pipe of pipes) {

        const birdLeft =
            bird.x - bird.radius;

        const birdRight =
            bird.x + bird.radius;

        const birdTop =
            bird.y - bird.radius;

        const birdBottom =
            bird.y + bird.radius;


        const pipeLeft =
            pipe.x;

        const pipeRight =
            pipe.x + GAME.pipeWidth;


        const horizontalCollision =
            birdRight > pipeLeft &&
            birdLeft < pipeRight;


        if (!horizontalCollision) {
            continue;
        }


        const hitTop =
            birdTop < pipe.top;

        const hitBottom =
            birdBottom > pipe.bottom;


        if (
            hitTop ||
            hitBottom
        ) {

            gameOver();

            return;
        }
    }
}


// =====================================================
// DRAW BACKGROUND
// =====================================================

function drawBackground() {

    const theme = getTheme();

    const gradient =
        ctx.createLinearGradient(
            0,
            0,
            0,
            canvas.height
        );

    gradient.addColorStop(
        0,
        theme.skyTop
    );

    gradient.addColorStop(
        1,
        theme.skyBottom
    );

    ctx.fillStyle = gradient;

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );


    // Clouds

    ctx.fillStyle =
        "rgba(255,255,255,0.65)";

    drawCloud(80, 110, 1);

    drawCloud(350, 180, 0.8);

    drawCloud(240, 70, 0.6);


    // Ground

    ctx.fillStyle =
        theme.ground;

    ctx.fillRect(
        0,
        canvas.height - 55,
        canvas.width,
        55
    );


    ctx.fillStyle =
        theme.groundDark;

    ctx.fillRect(
        0,
        canvas.height - 55,
        canvas.width,
        8
    );
}


// =====================================================
// CLOUD
// =====================================================

function drawCloud(
    x,
    y,
    scale
) {

    ctx.beginPath();

    ctx.arc(
        x,
        y,
        22 * scale,
        0,
        Math.PI * 2
    );

    ctx.arc(
        x + 25 * scale,
        y - 10 * scale,
        28 * scale,
        0,
        Math.PI * 2
    );

    ctx.arc(
        x + 55 * scale,
        y,
        22 * scale,
        0,
        Math.PI * 2
    );

    ctx.fill();
}


// =====================================================
// DRAW PIPES
// =====================================================

function drawPipes() {

    const theme = getTheme();

    for (const pipe of pipes) {

        drawPipe(
            pipe.x,
            0,
            GAME.pipeWidth,
            pipe.top,
            true,
            theme
        );


        drawPipe(
            pipe.x,
            pipe.bottom,
            GAME.pipeWidth,
            canvas.height -
                55 -
                pipe.bottom,
            false,
            theme
        );
    }
}


// =====================================================
// DRAW SINGLE PIPE
// =====================================================

function drawPipe(
    x,
    y,
    width,
    height,
    topPipe,
    theme
) {

    if (height <= 0) {
        return;
    }


    ctx.fillStyle =
        theme.pipe;

    ctx.fillRect(
        x,
        y,
        width,
        height
    );


    // Highlight

    ctx.fillStyle =
        "rgba(255,255,255,0.25)";

    ctx.fillRect(
        x + 8,
        y,
        10,
        height
    );


    // Border

    ctx.strokeStyle =
        theme.pipeDark;

    ctx.lineWidth = 3;

    ctx.strokeRect(
        x,
        y,
        width,
        height
    );


    // Cap

    const capHeight = 25;

    const capY =
        topPipe
            ? height - capHeight
            : y;


    ctx.fillStyle =
        theme.pipe;

    ctx.fillRect(
        x - 5,
        capY,
        width + 10,
        capHeight
    );


    ctx.strokeStyle =
        theme.pipeDark;

    ctx.strokeRect(
        x - 5,
        capY,
        width + 10,
        capHeight
    );
}


// =====================================================
// DRAW BIRD
// =====================================================

function drawBird() {

    ctx.save();

    ctx.translate(
        bird.x,
        bird.y
    );

    ctx.rotate(
        bird.rotation
    );


    // Tail

    ctx.fillStyle =
        "#f2a900";

    ctx.beginPath();

    ctx.moveTo(-15, 5);

    ctx.lineTo(-31, -7);

    ctx.lineTo(-27, 9);

    ctx.lineTo(-15, 12);

    ctx.closePath();

    ctx.fill();


    // Body

    ctx.fillStyle =
        "#ffd83d";

    ctx.strokeStyle =
        "#b77b00";

    ctx.lineWidth = 2;

    ctx.beginPath();

    ctx.ellipse(
        0,
        0,
        20,
        17,
        0,
        0,
        Math.PI * 2
    );

    ctx.fill();

    ctx.stroke();


    // Wing

    const wingY =
        Math.sin(
            bird.wingAngle
        ) * 3;

    ctx.fillStyle =
        "#f2b632";

    ctx.beginPath();

    ctx.ellipse(
        -5,
        7 + wingY,
        13,
        7,
        -0.3,
        0,
        Math.PI * 2
    );

    ctx.fill();

    ctx.stroke();


    // Eye white

    ctx.fillStyle = "white";

    ctx.beginPath();

    ctx.arc(
        8,
        -7,
        7,
        0,
        Math.PI * 2
    );

    ctx.fill();


    // Eye

    ctx.fillStyle = "#111";

    ctx.beginPath();

    ctx.arc(
        10,
        -7,
        3,
        0,
        Math.PI * 2
    );

    ctx.fill();


    // Beak

    ctx.fillStyle =
        "#ff8c22";

    ctx.beginPath();

    ctx.moveTo(16, -1);

    ctx.lineTo(33, 5);

    ctx.lineTo(16, 11);

    ctx.closePath();

    ctx.fill();

    ctx.stroke();


    // Small cheek

    ctx.fillStyle =
        "rgba(255,120,120,0.6)";

    ctx.beginPath();

    ctx.arc(
        5,
        4,
        3,
        0,
        Math.PI * 2
    );

    ctx.fill();


    ctx.restore();
}


// =====================================================
// SCORE
// =====================================================

function drawScore() {

    if (state === "ready") {
        return;
    }

    ctx.textAlign = "center";

    ctx.font =
        "bold 48px Arial";

    ctx.fillStyle = "white";

    ctx.strokeStyle =
        "rgba(0,0,0,0.45)";

    ctx.lineWidth = 5;

    ctx.strokeText(
        score,
        canvas.width / 2,
        70
    );

    ctx.fillText(
        score,
        canvas.width / 2,
        70
    );
}


// =====================================================
// THEME DISPLAY
// =====================================================

function drawThemeName() {

    if (state !== "playing") {
        return;
    }

    const themeNumber =
        Math.floor(score / 10) + 1;

    ctx.textAlign = "left";

    ctx.font =
        "bold 14px Arial";

    ctx.fillStyle =
        "rgba(255,255,255,0.8)";

    ctx.fillText(
        `THEME ${themeNumber}`,
        15,
        25
    );
}


// =====================================================
// CELEBRATION
// =====================================================

function drawCelebration() {

    if (celebrationTimer <= 0) {
        return;
    }

    celebrationTimer--;


    // Dark overlay

    ctx.fillStyle =
        "rgba(0,0,0,0.18)";

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );


    // Main text

    ctx.textAlign = "center";

    ctx.fillStyle = "white";

    ctx.strokeStyle =
        "rgba(0,0,0,0.5)";

    ctx.lineWidth = 6;

    ctx.font =
        "bold 44px Arial";

    ctx.strokeText(
        "🎉 AMAZING! 🎉",
        canvas.width / 2,
        220
    );

    ctx.fillText(
        "🎉 AMAZING! 🎉",
        canvas.width / 2,
        220
    );


    ctx.font =
        "bold 28px Arial";

    ctx.fillText(
        `${celebrationScore} POINTS!`,
        canvas.width / 2,
        265
    );


    ctx.font =
        "20px Arial";

    ctx.fillText(
        "KEEP FLYING!",
        canvas.width / 2,
        305
    );
}


// =====================================================
// READY SCREEN
// =====================================================

function drawReadyScreen() {

    if (state !== "ready") {
        return;
    }

    ctx.fillStyle =
        "rgba(0,0,0,0.25)";

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );


    ctx.textAlign = "center";

    ctx.fillStyle = "white";

    ctx.font =
        "bold 42px Arial";

    ctx.fillText(
        "HAND FLAPPY PRO",
        canvas.width / 2,
        180
    );


    ctx.font =
        "bold 24px Arial";

    ctx.fillText(
        "Browser Edition",
        canvas.width / 2,
        225
    );


    ctx.font =
        "20px Arial";

    ctx.fillText(
        "SPACE / TAP TO FLAP",
        canvas.width / 2,
        400
    );


    ctx.font =
        "bold 18px Arial";

    ctx.fillText(
        `BEST SCORE: ${bestScore}`,
        canvas.width / 2,
        440
    );
}


// =====================================================
// GAME OVER SCREEN
// =====================================================

function drawGameOver() {

    if (state !== "gameover") {
        return;
    }

    ctx.fillStyle =
        "rgba(0,0,0,0.45)";

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );


    ctx.textAlign = "center";

    ctx.fillStyle = "white";

    ctx.font =
        "bold 48px Arial";

    ctx.fillText(
        "GAME OVER",
        canvas.width / 2,
        220
    );


    ctx.font =
        "bold 28px Arial";

    ctx.fillText(
        `SCORE: ${score}`,
        canvas.width / 2,
        275
    );


    ctx.font =
        "bold 22px Arial";

    ctx.fillText(
        `BEST: ${bestScore}`,
        canvas.width / 2,
        315
    );
}


// =====================================================
// MAIN LOOP
// =====================================================

function gameLoop() {

    drawBackground();

    updateBird();

    updatePipes();

    checkCollision();

    updateParticles();

    drawPipes();

    drawBird();

    drawScore();

    drawThemeName();

    drawParticles();

    drawCelebration();

    drawReadyScreen();

    drawGameOver();

    requestAnimationFrame(
        gameLoop
    );
}


// =====================================================
// BUTTON
// =====================================================

startButton.addEventListener(
    "click",
    () => {

        startGame();

    }
);


// =====================================================
// KEYBOARD
// =====================================================

document.addEventListener("keydown", (event) => {

    // Keyboard controls disabled.
    // Hand movement controls the bird now.

});


// =====================================================
// MOUSE
// =====================================================

canvas.addEventListener(
    "mousedown",
    () => {

        flap();

    }
);


// =====================================================
// TOUCH
// =====================================================

canvas.addEventListener(
    "touchstart",
    event => {

        event.preventDefault();

        flap();

    },
    {
        passive: false
    }
);


// =====================================================
// START
// =====================================================

resetGame();

gameLoop();
// ==========================================
// HAND TRACKING
// ==========================================

const hands = new Hands({
    locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
    }
});

hands.setOptions({
    maxNumHands: 1,
    modelComplexity: 1,
    minDetectionConfidence: 0.6,
    minTrackingConfidence: 0.6
});


// When a hand is detected
hands.onResults((results) => {

    // Match canvas to camera resolution
    handCanvas.width = webcam.videoWidth || 640;
    handCanvas.height = webcam.videoHeight || 480;

    handCtx.clearRect(
        0,
        0,
        handCanvas.width,
        handCanvas.height
    );


    // No hand detected
    if (
        !results.multiHandLandmarks ||
        results.multiHandLandmarks.length === 0
    ) {
        return;
    }


    const hand = results.multiHandLandmarks[0];
    // =====================================
// SAME CONTROL AS PYTHON VERSION
// =====================================

// Five fingertips:
// 4  = thumb
// 8  = index
// 12 = middle
// 16 = ring
// 20 = pinky

const fingertipIds = [4, 8, 12, 16, 20];


// Average the Y position of all fingertips
let rawY = 0;

for (const id of fingertipIds) {
    rawY += hand[id].y;
}

rawY /= fingertipIds.length;


// Add to history
handHistory.push(rawY);


// Keep only the last 7 frames
if (handHistory.length > HAND_HISTORY_SIZE) {
    handHistory.shift();
}


// Smooth exactly like Python
let smoothY = 0;

for (const value of handHistory) {
    smoothY += value;
}

smoothY /= handHistory.length;


// Calculate upward velocity
let velocity = 0;

if (lastHandY !== null) {
    velocity = lastHandY - smoothY;
}


// Current time
const now = performance.now();


// =====================================
// UPWARD MOVEMENT → FLAP
// =====================================

if (
    lastHandY !== null &&
    velocity > FLAP_THRESHOLD &&
    now - lastFlapTime >= FLAP_COOLDOWN
) {

    flap();

    lastFlapTime = now;

    console.log("✋ FLAP", velocity.toFixed(4));
}


// Remember current position
lastHandY = smoothY;
    // =====================================
// HAND MOVEMENT → FLAP
// =====================================

// =====================================
// SMOOTH HAND MOVEMENT
// =====================================

const rawHandY = hand[9].y;


// Start position
if (smoothHandY === null) {
    smoothHandY = rawHandY;
}


// Smooth the hand position
smoothHandY =
    smoothHandY * 0.75 +
    rawHandY * 0.25;


// Calculate movement
const movement =
    previousHandY === null
        ? 0
        : previousHandY - smoothHandY;


// Cooldown
if (FLAP_COOLDOWN > 0) {
  
}


// =====================================
// HAND UP → FLAP
// =====================================

if (
    movement > 0.018 &&
    FLAP_COOLDOWN === 0
) {

    flap();

    FLAP_COOLDOWN = 160;

    console.log("✋ HAND FLAP");
}


// Remember position
previousHandY = smoothHandY;


    // =====================================
    // HAND CONNECTIONS
    // =====================================

    const connections = [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 4],

        [0, 5],
        [5, 6],
        [6, 7],
        [7, 8],

        [5, 9],
        [9, 10],
        [10, 11],
        [11, 12],

        [9, 13],
        [13, 14],
        [14, 15],
        [15, 16],

        [13, 17],
        [17, 18],
        [18, 19],
        [19, 20],

        [0, 17]
    ];


    // =====================================
    // DRAW GLOWING CONNECTIONS
    // =====================================

    handCtx.lineWidth = 3;

    handCtx.shadowBlur = 12;
    handCtx.shadowColor = "#00ffff";

    handCtx.strokeStyle = "#00ffff";

    connections.forEach(([a, b]) => {

        const p1 = hand[a];
        const p2 = hand[b];

        handCtx.beginPath();

        handCtx.moveTo(
            p1.x * handCanvas.width,
            p1.y * handCanvas.height
        );

        handCtx.lineTo(
            p2.x * handCanvas.width,
            p2.y * handCanvas.height
        );

        handCtx.stroke();
    });


    // =====================================
    // DRAW LANDMARK POINTS
    // =====================================

    hand.forEach((point, index) => {

        const x =
            point.x * handCanvas.width;

        const y =
            point.y * handCanvas.height;


        handCtx.beginPath();

        handCtx.arc(
            x,
            y,
            index === 8 ? 7 : 4,
            0,
            Math.PI * 2
        );


        // Fingertip = special target
        if (index === 8) {

            handCtx.fillStyle = "#ffffff";

            handCtx.shadowBlur = 20;
            handCtx.shadowColor = "#ffffff";

        } else {

            handCtx.fillStyle = "#00ffff";

            handCtx.shadowBlur = 12;
            handCtx.shadowColor = "#00ffff";
        }


        handCtx.fill();
    });


    // Reset glow
    handCtx.shadowBlur = 0;


    // =====================================
    // INDEX FINGER TARGET
    // =====================================

    const indexFinger = hand[8];

    const ix =
        indexFinger.x * handCanvas.width;

    const iy =
        indexFinger.y * handCanvas.height;


    handCtx.beginPath();

    handCtx.arc(
        ix,
        iy,
        13,
        0,
        Math.PI * 2
    );

    handCtx.strokeStyle = "#ffffff";

    handCtx.lineWidth = 2;

    handCtx.stroke();

});


// Connect webcam to MediaPipe

const handCamera = new Camera(webcam, {

    onFrame: async () => {

        await hands.send({
            image: webcam
        });

    },

    width: 640,
    height: 480

});


// Start hand tracking

handCamera.start();

console.log("HAND TRACKING STARTED");