const canvas = document.querySelector("#fieldCanvas");
const readout = document.querySelector("#fieldReadout");
const ctx = canvas.getContext("2d");

const nodes = Array.from({ length: 34 }, (_, index) => ({
  x: 0,
  y: 0,
  phase: index * 0.61,
  radius: 2 + (index % 5) * 0.42,
  speed: 0.004 + (index % 7) * 0.0009
}));

function resizeCanvas() {
  const box = canvas.getBoundingClientRect();
  const ratio = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = Math.floor(box.width * ratio);
  canvas.height = Math.floor(box.height * ratio);
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
}

function placeNodes(time) {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const cx = width * 0.52;
  const cy = height * 0.52;
  const spreadX = width * 0.34;
  const spreadY = height * 0.32;

  nodes.forEach((node, index) => {
    const orbit = index / nodes.length;
    const t = time * node.speed + node.phase;
    node.x = cx + Math.cos(t + orbit * 6.28) * spreadX * (0.28 + orbit);
    node.y = cy + Math.sin(t * 1.23 + orbit * 5.1) * spreadY * (0.34 + orbit * 0.84);
  });
}

function drawGrid(width, height) {
  ctx.strokeStyle = "rgba(255,255,255,0.055)";
  ctx.lineWidth = 1;

  for (let x = 0; x < width; x += 44) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.stroke();
  }

  for (let y = 0; y < height; y += 44) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(width, y);
    ctx.stroke();
  }
}

function draw(time = 0) {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#101215";
  ctx.fillRect(0, 0, width, height);
  drawGrid(width, height);
  placeNodes(time);

  for (let a = 0; a < nodes.length; a += 1) {
    for (let b = a + 1; b < nodes.length; b += 1) {
      const left = nodes[a];
      const right = nodes[b];
      const dx = left.x - right.x;
      const dy = left.y - right.y;
      const distance = Math.hypot(dx, dy);

      if (distance < 150) {
        const alpha = Math.max(0, 1 - distance / 150) * 0.22;
        ctx.strokeStyle = `rgba(120, 190, 170, ${alpha})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(left.x, left.y);
        ctx.lineTo(right.x, right.y);
        ctx.stroke();
      }
    }
  }

  const pulse = 0.5 + Math.sin(time * 0.002) * 0.5;
  nodes.forEach((node, index) => {
    const isPrimary = index % 9 === 0;
    ctx.beginPath();
    ctx.fillStyle = isPrimary ? "#d6b15f" : "#d8ebe5";
    ctx.arc(node.x, node.y, node.radius + (isPrimary ? pulse * 1.6 : 0), 0, Math.PI * 2);
    ctx.fill();
  });

  const k = (0.68 + pulse * 0.09).toFixed(2);
  const d = (0.24 - pulse * 0.08).toFixed(2);
  readout.textContent = `K=${k} D=${d}`;

  requestAnimationFrame(draw);
}

window.addEventListener("resize", resizeCanvas);
resizeCanvas();
requestAnimationFrame(draw);
