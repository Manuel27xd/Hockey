import streamlit as st
import streamlit.components.v1 as components

# Configuración de página en modo ancho para aprovechar pantallas móviles y de PC
st.set_page_config(
    page_title="Air Hockey Arcade Pro",
    page_icon="🏒",
    layout="wide"
)

# Estilos CSS avanzados para la interfaz y barra lateral
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0d1322 100%);
        border-right: 2px solid #1f2937;
        padding-top: 15px;
    }

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #00f3ff !important;
        font-weight: 800 !important;
        text-shadow: 0 0 10px rgba(0, 243, 255, 0.4);
        border-bottom: 2px solid #1f2937;
        padding-bottom: 8px;
        margin-bottom: 20px;
    }

    [data-testid="stSidebar"] label p {
        color: #e5e7eb !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1f2937 !important;
        border: 1.5px solid #3b82f6 !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    [data-testid="stSidebar"] div[role="slider"] {
        background-color: #ff0055 !important;
        border: 2px solid #ffffff !important;
        box-shadow: 0 0 10px rgba(255, 0, 85, 0.8) !important;
    }

    .main-title {
        text-align: center;
        font-weight: 800;
        background: linear-gradient(90deg, #00f3ff, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.3rem;
        margin-bottom: 0px;
        text-shadow: 0 0 20px rgba(0, 243, 255, 0.2);
    }
    .sub-title {
        text-align: center;
        color: #9ca3af;
        font-size: 0.95rem;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🏒 AIR HOCKEY ARCADE PRO</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Adaptado automáticamente a la pantalla de tu celular, tablet o computadora.</p>',
            unsafe_allow_html=True)

# --- Barra Lateral de Configuración ---
st.sidebar.header("🕹️ Ajustes de Partida")
game_mode = st.sidebar.selectbox(
    "Modo de Juego",
    ["Jugador vs IA", "Jugador vs Jugador"]
)

difficulty = "Medio"
if game_mode == "Jugador vs IA":
    difficulty = st.sidebar.selectbox(
        "Dificultad de la IA",
        ["Fácil", "Medio", "Difícil"],
        index=1
    )

winning_score = st.sidebar.slider("Goles necesarios para ganar", 3, 10, 5)

ai_speed = {"Fácil": 0.05, "Medio": 0.09, "Difícil": 0.16}[difficulty]
p2_label = f"IA ({difficulty})" if game_mode == "Jugador vs IA" else "Jugador 2"

# --- Panel de Instrucciones ---
with st.expander("📖 Guía de Controles"):
    st.markdown("""
    - **📱 En Celular / Tablet:** Toca y desliza el dedo en la mitad izquierda de la pantalla para mover tu paleta al instante. El tablero se escala solo a tu pantalla.
    - **💻 En Computadora:** Teclas **`W`, `S`, `A`, `D`** para el Jugador 1 y **`Flechas`** para el Jugador 2.
    - **🤖 Inteligencia Artificial:** Activa con sistema anti-atasco en esquinas.
    """)

# --- Código HTML y Motor del Juego Responsivo (Seguro sin f-string) ---
game_html = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body {
        background-color: #0b0f19;
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 0;
        padding: 5px;
        overflow: hidden;
        touch-action: none;
    }
    .hud {
        display: flex;
        justify-content: space-around;
        width: 100%;
        max-width: 760px;
        background: rgba(31, 41, 55, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 6px 10px;
        border-radius: 10px;
        margin-bottom: 8px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.5);
    }
    .score-box {
        font-size: 14px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .p1-text { color: #00f3ff; text-shadow: 0 0 8px rgba(0,243,255,0.5); }
    .p2-text { color: #ff0055; text-shadow: 0 0 8px rgba(255,0,85,0.5); }
    .score-num { font-size: 18px; font-weight: 900; margin-left: 4px; }

    /* Contenedor responsivo para ajustar el tablero perfectamente a celulares */
    .canvas-container {
        width: 100%;
        max-width: 760px;
        aspect-ratio: 2 / 1;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    canvas {
        border: 3px solid #1f2937;
        background: radial-gradient(circle, #111827 0%, #030712 100%);
        box-shadow: 0 15px 35px rgba(0,0,0,0.8), inset 0 0 30px rgba(0,0,0,0.8);
        border-radius: 14px;
        outline: none;
        width: 100% !important;
        height: 100% !important;
    }
</style>
</head>
<body>

<div class="hud">
    <div class="score-box p1-text">Jugador 1: <span id="s1" class="score-num">0</span></div>
    <div class="score-box p2-text"><span id="p2_name">P2</span>: <span id="s2" class="score-num">0</span></div>
</div>

<div class="canvas-container">
    <canvas id="cv" width="760" height="380" tabindex="1"></canvas>
</div>

<script>
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');
window.onload = () => cv.focus();
cv.onclick = () => cv.focus();

const mode = "GAME_MODE_VAL";
const aiSpd = AI_SPEED_VAL;
const winScore = WINNING_SCORE_VAL;
document.getElementById('p2_name').innerText = "P2_LABEL_VAL";

let s1 = 0, s2 = 0, over = false;
const w = cv.width, h = cv.height, gw = 110;

let puck = { x: w/2, y: h/2, r: 11, vx: 5, vy: 3, max: 10 };
let p1 = { x: 150, y: h/2, r: 24 };
let p2 = { x: w - 150, y: h/2, r: 24 };

let keys = {};
window.onkeydown = e => {
    if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"," "].includes(e.code) || ["w","W","s","S","a","A","d","D"].includes(e.key)) e.preventDefault();
    keys[e.key] = true;
};
window.onkeyup = e => { keys[e.key] = false; };

// --- SOPORTE TÁCTIL FLUIDO PARA MÓVILES Y TABLETS ---
function handleTouch(e) {
    e.preventDefault();
    let rect = cv.getBoundingClientRect();
    let scaleX = cv.width / rect.width;
    let scaleY = cv.height / rect.height;

    let touch = e.touches[0];
    let touchX = (touch.clientX - rect.left) * scaleX;
    let touchY = (touch.clientY - rect.top) * scaleY;

    // Restricción estricta para P1 en su mitad izquierda
    p1.x = Math.max(p1.r, Math.min(w/2 - p1.r, touchX));
    p1.y = Math.max(p1.r, Math.min(h - p1.r, touchY));
}

cv.addEventListener('touchstart', handleTouch, { passive: false });
cv.addEventListener('touchmove', handleTouch, { passive: false });

function reset(sc) {
    puck.x = w/2; puck.y = h/2;
    puck.vx = (sc === 1 ? -1 : 1) * (4 + Math.random() * 2);
    puck.vy = (Math.random() - 0.5) * 5;
}

function update() {
    if (over) return;

    if (keys['w'] || keys['W']) p1.y -= 7;
    if (keys['s'] || keys['S']) p1.y += 7;
    if (keys['a'] || keys['A']) p1.x -= 7;
    if (keys['d'] || keys['D']) p1.x += 7;

    p1.x = Math.max(p1.r, Math.min(w/2 - p1.r, p1.x));
    p1.y = Math.max(p1.r, Math.min(h - p1.r, p1.y));

    if (mode === "Jugador vs Jugador") {
        if (keys['ArrowUp']) p2.y -= 7;
        if (keys['ArrowDown']) p2.y += 7;
        if (keys['ArrowLeft']) p2.x -= 7;
        if (keys['ArrowRight']) p2.x += 7;
    } else {
        let ty = puck.y, tx = puck.x;
        if (puck.x < w/2) {
            tx = w * 0.75;
            ty = (h/2) + Math.sin(Date.now() * 0.005) * 80;
        } else {
            if (puck.y < 80 || puck.y > h - 80) {
                tx = puck.x + 20;
                ty = puck.y < 80 ? puck.y + 45 : puck.y - 45;
            } else {
                tx = Math.max(w/2 + p2.r, Math.min(w - p2.r, puck.x + 10));
                ty = puck.y;
            }
        }
        p2.y += (ty - p2.y) * aiSpd;
        p2.x += (tx - p2.x) * aiSpd;
    }

    p2.x = Math.max(w/2 + p2.r, Math.min(w - p2.r, p2.x));
    p2.y = Math.max(p2.r, Math.min(h - p2.r, p2.y));

    puck.x += puck.vx;
    puck.y += puck.vy;

    if (puck.y - puck.r < 0) { puck.y = puck.r; puck.vy *= -1; }
    if (puck.y + puck.r > h) { puck.y = h - puck.r; puck.vy *= -1; }

    let gt = (h - gw)/2;
    if (puck.x - puck.r < 0) {
        if (puck.y > gt && puck.y < gt + gw) {
            s2++; document.getElementById('s2').innerText = s2;
            if (s2 >= winScore) over = true; else reset(1);
        } else { puck.x = puck.r; puck.vx *= -1; }
    }
    if (puck.x + puck.r > w) {
        if (puck.y > gt && puck.y < gt + gw) {
            s1++; document.getElementById('s1').innerText = s1;
            if (s1 >= winScore) over = true; else reset(2);
        } else { puck.x = w - puck.r; puck.vx *= -1; }
    }

    col(p1); col(p2);
    puck.vx *= 0.995; puck.vy *= 0.995;
}

function col(p) {
    let dx = puck.x - p.x, dy = puck.y - p.y, dist = Math.sqrt(dx*dx + dy*dy);
    if (dist < puck.r + p.r) {
        let ang = Math.atan2(dy, dx);
        let spd = Math.min(puck.max, Math.max(5, Math.sqrt(puck.vx*puck.vx + puck.vy*puck.vy) * 1.05));
        puck.vx = Math.cos(ang) * spd; puck.vy = Math.sin(ang) * spd;
        puck.x = p.x + Math.cos(ang) * (p.r + puck.r);
        puck.y = p.y + Math.sin(ang) * (p.r + puck.r);
    }
}

function draw() {
    ctx.clearRect(0, 0, w, h);

    ctx.strokeStyle = 'rgba(55, 65, 81, 0.6)';
    ctx.lineWidth = 4;
    ctx.setLineDash([10, 10]);
    ctx.beginPath(); ctx.moveTo(w/2, 0); ctx.lineTo(w/2, h); ctx.stroke();
    ctx.setLineDash([]);

    ctx.beginPath();
    ctx.arc(w/2, h/2, 55, 0, Math.PI*2);
    ctx.strokeStyle = 'rgba(55, 65, 81, 0.4)';
    ctx.lineWidth = 3;
    ctx.stroke();

    let gt = (h - gw)/2;

    ctx.shadowBlur = 15;
    ctx.shadowColor = '#00f3ff';
    ctx.strokeStyle = '#00f3ff'; ctx.lineWidth = 6;
    ctx.beginPath(); ctx.moveTo(0, gt); ctx.lineTo(0, gt + gw); ctx.stroke();

    ctx.shadowBlur = 15;
    ctx.shadowColor = '#ff0055';
    ctx.strokeStyle = '#ff0055'; 
    ctx.beginPath(); ctx.moveTo(w, gt); ctx.lineTo(w, gt + gw); ctx.stroke();
    ctx.shadowBlur = 0;

    ctx.shadowBlur = 15;
    ctx.shadowColor = '#00f3ff';
    ctx.beginPath(); ctx.arc(p1.x, p1.y, p1.r, 0, Math.PI*2);
    ctx.fillStyle = '#00f3ff'; ctx.fill();
    ctx.lineWidth = 3; ctx.strokeStyle = '#ffffff'; ctx.stroke();

    ctx.shadowBlur = 15;
    ctx.shadowColor = '#ff0055';
    ctx.beginPath(); ctx.arc(p2.x, p2.y, p2.r, 0, Math.PI*2);
    ctx.fillStyle = '#ff0055'; ctx.fill();
    ctx.lineWidth = 3; ctx.strokeStyle = '#ffffff'; ctx.stroke();

    ctx.shadowBlur = 15;
    ctx.shadowColor = '#fbbf24';
    ctx.beginPath(); ctx.arc(puck.x, puck.y, puck.r, 0, Math.PI*2);
    ctx.fillStyle = '#fbbf24'; ctx.fill();
    ctx.lineWidth = 2; ctx.strokeStyle = '#fff'; ctx.stroke();
    ctx.shadowBlur = 0;

    if (over) {
        ctx.fillStyle = 'rgba(3, 7, 18, 0.85)';
        ctx.fillRect(0, 0, w, h);

        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 26px sans-serif';
        ctx.textAlign = 'center';
        let winnerText = s1 > s2 ? "🎉 ¡JUGADOR 1 GANA!" : (mode === "Jugador vs IA" ? "🤖 ¡LA IA TE HA VENCIDO!" : "🎉 ¡JUGADOR 2 GANA!");
        ctx.fillText(winnerText, w/2, h/2 - 10);

        ctx.font = '14px sans-serif';
        ctx.fillStyle = '#9ca3af';
        ctx.fillText("Recarga la página para jugar otra vez", w/2, h/2 + 25);
    }
}

function loop() {
    update();
    draw();
    requestAnimationFrame(loop);
}

loop();
</script>

</body>
</html>
"""

# Inyección segura de variables
game_html = game_html.replace("GAME_MODE_VAL", str(game_mode))
game_html = game_html.replace("AI_SPEED_VAL", str(ai_speed))
game_html = game_html.replace("WINNING_SCORE_VAL", str(winning_score))
game_html = game_html.replace("P2_LABEL_VAL", str(p2_label))

components.html(game_html, height=420)