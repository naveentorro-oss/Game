import streamlit as st
import streamlit.components.v1 as html

# Configure the Streamlit page layout
st.set_page_config(page_title="Streamlit Snake Game", page_icon="🐍", layout="centered")

st.title("🐍 Classic Snake Game")
st.write("Play a fluid, high-performance Snake game hosted inside a Streamlit web app!")

# Embed the core HTML5 Canvas game script directly into the Streamlit interface
snake_game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background-color: #0e1117;
            color: #ffffff;
            font-family: Arial, sans-serif;
            margin: 0;
        }
        canvas {
            border: 4px solid #4a5568;
            background-color: #1a202c;
            box-shadow: 0px 10px 20px rgba(0,0,0,0.5);
        }
        .score-board {
            font-size: 24px;
            margin-bottom: 10px;
            font-weight: bold;
            color: #00ff66;
        }
        .controls {
            margin-top: 15px;
            font-size: 14px;
            color: #a0aec0;
            text-align: center;
        }
    </style>
</head>
<body>

<div class="score-board">Score: <span id="score">0</span></div>
<canvas id="gameCanvas" width="400" height="400"></canvas>
<div class="controls">Use your keyboard <b>Arrow Keys</b> or <b>W, A, S, D</b> to navigate!</div>

<script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const scoreElement = document.getElementById("score");

    const gridSize = 20;
    const tileCount = canvas.width / gridSize;

    let snake = [{x: 10, y: 10}];
    let food = {x: 5, y: 5};
    let dx = 1;
    let dy = 0;
    let score = 0;
    let gameInterval;
    let gameSpeed = 150; // milliseconds per frame tick

    function main() {
        if (hasGameEnded()) {
            ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "#ff4b4b";
            ctx.font = "30px Arial";
            ctx.fillText("Game Over!", canvas.width / 4, canvas.height / 2);
            ctx.font = "20px Arial";
            ctx.fillStyle = "#ffffff";
            ctx.fillText("Press 'Spacebar' to Restart", canvas.width / 4 - 10, canvas.height / 2 + 40);
            clearInterval(gameInterval);
            return;
        }

        changingDirection = false;
        clearCanvas();
        drawFood();
        moveSnake();
        drawSnake();
    }

    function clearCanvas() {
        ctx.fillStyle = "#1a202c";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    function drawSnake() {
        snake.forEach((part, index) => {
            ctx.fillStyle = index === 0 ? "#00ff66" : "#48bb78"; // Head is brighter green
            ctx.fillRect(part.x * gridSize, part.y * gridSize, gridSize - 2, gridSize - 2);
        });
    }

    function moveSnake() {
        const head = {x: snake[0].x + dx, y: snake[0].y + dy};
        snake.unshift(head);

        const hasEatenFood = snake[0].x === food.x && snake[0].y === food.y;
        if (hasEatenFood) {
            score += 10;
            scoreElement.innerText = score;
            generateFood();
        } else {
            snake.pop();
        }
    }

    function generateFood() {
        food.x = Math.floor(Math.random() * tileCount);
        food.y = Math.floor(Math.random() * tileCount);
        // Ensure food does not spawn on top of the snake body
        snake.forEach(function(part) {
            const hasEaten = part.x === food.x && part.y === food.y;
            if (hasEaten) generateFood();
        });
    }

    function drawFood() {
        ctx.fillStyle = "#ff4b4b";
        ctx.fillRect(food.x * gridSize, food.y * gridSize, gridSize - 2, gridSize - 2);
    }

    function hasGameEnded() {
        // Wall collisions
        if (snake[0].x < 0 || snake[0].x >= tileCount || snake[0].y < 0 || snake[0].y >= tileCount) {
            return true;
        }
        // Self collisions
        for (let i = 4; i < snake.length; i++) {
            if (snake[i].x === snake[0].x && snake[i].y === snake[0].y) return true;
        }
        return false;
    }

    function changeDirection(event) {
        const keyPressed = event.key.toLowerCase();
        const goingUp = dy === -1;
        const goingDown = dy === 1;
        const goingRight = dx === 1;
        const goingLeft = dx === -1;

        if ((keyPressed === 'arrowleft' || keyPressed === 'a') && !goingRight) {
            dx = -1; dy = 0;
        }
        if ((keyPressed === 'arrowup' || keyPressed === 'w') && !goingDown) {
            dx = 0; dy = -1;
        }
        if ((keyPressed === 'arrowright' || keyPressed === 'd') && !goingLeft) {
            dx = 1; dy = 0;
        }
        if ((keyPressed === 'arrowdown' || keyPressed === 's') && !goingUp) {
            dx = 0; dy = 1;
        }
        if (event.key === ' ' && hasGameEnded()) {
            resetGame();
        }
    }

    function resetGame() {
        snake = [{x: 10, y: 10}];
        food = {x: 5, y: 5};
        dx = 1;
        dy = 0;
        score = 0;
        scoreElement.innerText = score;
        clearInterval(gameInterval);
        gameInterval = setInterval(main, gameSpeed);
    }

    document.addEventListener("keydown", changeDirection);
    gameInterval = setInterval(main, gameSpeed);
</script>
</body>
</html>
"""

# Render the embedded HTML framework inside Streamlit
html.html(snake_game_html, height=520)

st.markdown("---")
st.info("💡 **Developer Note:** By utilizing Streamlit's HTML component block, this application bypasses web network latency limitations, running calculations client-side to ensure uninterrupted frame-rates.")
