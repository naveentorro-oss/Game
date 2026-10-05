import streamlit as st
import streamlit.components.v1 as components

# Page config layout configuration 
st.set_page_config(page_title="Streamlit Arcade Racing Setup", layout="centered", page_icon="🏎️")

st.title("🏎️ Instant-Response Streamlit Arcade Canvas")
st.write("This instance utilizes custom structural elements to monitor real-time local hardware events.")

# Embed HTML/JS canvas code into Streamlit
arcade_game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            background-color: #0e1117;
            display: flex;
            flex-direction: column;
            align-items: center;
            font-family: sans-serif;
            color: white;
        }
        #gameCanvas {
            border: 4px solid #333;
            background: #222;
            border-radius: 8px;
            box-shadow: 0px 4px 20px rgba(0,0,0,0.5);
        }
        .controls-hint {
            margin-top: 10px;
            color: #aaa;
            font-size: 14px;
        }
    </style>
</head>
<body>

<canvas id="gameCanvas" width="400" height="500"></canvas>
<div class="controls-hint">Use <b>Left / Right Arrow Keys</b> or <b>A / D</b> to steer the car</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Game Variables
let player = { x: 175, y: 400, width: 50, height: 80, speed: 7 };
let obstacles = [];
let keys = {};
let score = 0;
let gameOver = false;
let gameSpeed = 5;

// Handle Keyboard Events
window.addEventListener("keydown", (e) => { keys[e.key] = true; });
window.addEventListener("keyup", (e) => { keys[e.key] = false; });

function spawnObstacle() {
    let roadWidth = 300; // Road runs between x=50 and x=350
    let obsWidth = 50;
    let obsX = 50 + Math.random() * (roadWidth - obsWidth);
    obstacles.push({ x: obsX, y: -80, width: obsWidth, height: 80, speed: gameSpeed });
}

function checkCollision(rect1, rect2) {
    return rect1.x < rect2.x + rect2.width &&
           rect1.x + rect1.width > rect2.x &&
           rect1.y < rect2.y + rect2.height &&
           rect1.y + rect1.height > rect2.y;
}

function resetGame() {
    player.x = 175;
    obstacles = [];
    score = 0;
    gameSpeed = 5;
    gameOver = false;
}

// Game Loop
function update() {
    if (gameOver) {
        if (keys["r"] || keys["R"]) resetGame();
        return;
    }

    // Player Horizontal Steer Input Processing
    if (keys["ArrowLeft"] || keys["a"] || keys["A"]) {
        if (player.x > 50) player.x -= player.speed;
    }
    if (keys["ArrowRight"] || keys["d"] || keys["D"]) {
        if (player.x < 350 - player.width) player.x += player.speed;
    }

    // Process Obstacles
    if (Math.random() < 0.02 && (obstacles.length === 0 || obstacles[obstacles.length - 1].y > 150)) {
        spawnObstacle();
    }

    for (let i = obstacles.length - 1; i >= 0; i--) {
        obstacles[i].y += obstacles[i].speed;

        // Check Crashes
        if (checkCollision(player, obstacles[i])) {
            gameOver = true;
        }

        // Clean out of bounds objects & increment score metrics
        if (obstacles[i].y > canvas.height) {
            obstacles.splice(i, 1);
            score++;
            if (score % 5 === 0) gameSpeed += 0.8; // Scaling difficulty spikes
        }
    }
}

function draw() {
    // Clear Viewport Matrix
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw Grass Terrain
    ctx.fillStyle = "#2e7d32";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw Main Asphalt Strip Road Layer
    ctx.fillStyle = "#424242";
    ctx.fillRect(50, 0, 300, canvas.height);

    // White Lane Markings
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(45, 0, 5, canvas.height);
    ctx.fillRect(350, 0, 5, canvas.height);

    // Draw Player Car (Blue Accent Profile)
    ctx.fillStyle = "#1e88e5";
    ctx.fillRect(player.x, player.y, player.width, player.height);
    // Windshield detail
    ctx.fillStyle = "#e0e0e0";
    ctx.fillRect(player.x + 5, player.y + 20, player.width - 10, 15);

    // Draw Incoming Obstacle Traffic (Red Cars)
    ctx.fillStyle = "#e53935";
    for (let obs of obstacles) {
        ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
        ctx.fillStyle = "#333333";
        ctx.fillRect(obs.x + 5, obs.y + 45, obs.width - 10, 15);
        ctx.fillStyle = "#e53935"; // Reset for next rendering sequences
    }

    // Telemetry Scoreboard Overlays
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 20px sans-serif";
    ctx.fillText("Score: " + score, 15, 30);

    // Game Over UI Layout Window
    if (gameOver) {
        ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = "#ff1744";
        ctx.font = "bold 36px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("CRASH DETECTED", canvas.width / 2, canvas.height / 2 - 20);
        
        ctx.fillStyle = "#ffffff";
        ctx.font = "18px sans-serif";
        ctx.fillText("Press 'R' to Restart Race Track", canvas.width / 2, canvas.height / 2 + 30);
        ctx.textAlign = "left"; // reset alignment configuration settings
    }
}

function loop() {
    update();
    draw();
    requestAnimationFrame(loop);
}

// Fire up Engine loop runtime
loop();
</script>

</body>
</html>
"""

# Render component directly onto layout screen
components.html(arcade_game_html, height=550)