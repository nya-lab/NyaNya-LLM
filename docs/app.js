const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* ── Logo mark cycling ── */
const logoMark = document.querySelector(".mark-symbol");
const logoFaces = [
  "ฅ nya-lab", "ฅ^ nya-lab", "^._.^ nya-lab", "=^.^= nya-lab",
  "ᓚᘏᗢ nya-lab", "^•ﻌ•^ nya-lab", "/ᐠ nya-lab", "ᐠ｡ nya-lab",
  "꒰ঌ nya-lab", "：꒱ nya-lab"
];

function cycleLogoMark() {
  if (!logoMark || reduceMotion) return;
  let step = 0;
  logoMark.classList.add("is-flashing");
  const burst = window.setInterval(() => {
    logoMark.textContent = logoFaces[Math.floor(Math.random() * logoFaces.length)];
    step += 1;
    if (step >= 6) {
      window.clearInterval(burst);
      logoMark.innerHTML = `：꒱ <span class="lab-name"><strong>n</strong>ya-lab</span>`;
      logoMark.classList.remove("is-flashing");
    }
  }, 145);
}

/* ── Canvas field visualization ── */
const canvas = document.querySelector("#fieldCanvas");
if (canvas) {
  const ctx = canvas.getContext("2d");
  const pointer = { x: 0, y: 0, active: false };

  const nodes = Array.from({ length: 32 }, (_, i) => ({
    phase: i * 0.47,
    orbit: i / 32,
    radius: 2.2 + (i % 6) * 0.36,
    speed: reduceMotion ? 0 : 0.0032 + (i % 9) * 0.0007,
    x: 0, y: 0,
    signal: i % 11 === 0
  }));

  function resize() {
    const box = canvas.parentElement.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.max(1, Math.floor(box.width * dpr));
    canvas.height = Math.max(1, Math.floor(box.height * dpr));
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function placeNodes(time) {
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    const cx = w * 0.5;
    const cy = h * 0.5;
    const sx = w * 0.38;
    const sy = h * 0.36;

    nodes.forEach((n, i) => {
      const t = time * n.speed + n.phase;
      const wave = Math.sin(t * 0.71 + i) * 0.08;
      n.x = cx + Math.cos(t + n.orbit * 6.283) * sx * (0.22 + n.orbit + wave);
      n.y = cy + Math.sin(t * 1.19 + n.orbit * 5.1) * sy * (0.28 + n.orbit * 0.76);

      if (pointer.active && !reduceMotion) {
        const dx = n.x - pointer.x;
        const dy = n.y - pointer.y;
        const d = Math.hypot(dx, dy);
        if (d < 150) {
          const f = (1 - d / 150) * 26;
          n.x += (dx / Math.max(d, 1)) * f;
          n.y += (dy / Math.max(d, 1)) * f;
        }
      }
    });
  }

  function drawGrid(w, h) {
    ctx.strokeStyle = "rgba(243, 241, 234, 0.05)";
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 38) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for (let y = 0; y < h; y += 38) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }
  }

  function draw(time = 0) {
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    const pulse = reduceMotion ? 0.5 : 0.5 + Math.sin(time * 0.0017) * 0.5;

    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = "#090b0a";
    ctx.fillRect(0, 0, w, h);
    drawGrid(w, h);
    placeNodes(time);

    for (let a = 0; a < nodes.length; a++) {
      for (let b = a + 1; b < nodes.length; b++) {
        const d = Math.hypot(nodes[a].x - nodes[b].x, nodes[a].y - nodes[b].y);
        if (d < 136) {
          ctx.strokeStyle = `rgba(143, 214, 180, ${Math.max(0, 1 - d / 136) * 0.28})`;
          ctx.lineWidth = 1;
          ctx.beginPath(); ctx.moveTo(nodes[a].x, nodes[a].y); ctx.lineTo(nodes[b].x, nodes[b].y); ctx.stroke();
        }
      }
    }

    nodes.forEach((n) => {
      if (n.signal) {
        ctx.beginPath();
        ctx.strokeStyle = `rgba(215, 184, 111, ${0.14 + pulse * 0.16})`;
        ctx.arc(n.x, n.y, 20 + pulse * 16, 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.beginPath();
      ctx.fillStyle = n.signal ? "#d7b86f" : "#f3f1ea";
      ctx.arc(n.x, n.y, n.radius + (n.signal ? pulse * 1.4 : 0), 0, Math.PI * 2);
      ctx.fill();
    });

    if (!reduceMotion) requestAnimationFrame(draw);
  }

  canvas.addEventListener("pointermove", (e) => {
    const r = canvas.getBoundingClientRect();
    pointer.x = e.clientX - r.left;
    pointer.y = e.clientY - r.top;
    pointer.active = true;
  });

  canvas.addEventListener("pointerleave", () => {
    pointer.active = false;
  });

  window.addEventListener("resize", () => {
    resize();
    draw();
  });

  resize();
  requestAnimationFrame(draw);
}

/* ── Init ── */
if (!reduceMotion) {
  window.setInterval(cycleLogoMark, 5200);
  cycleLogoMark();
}