(function initDotField() {
  const canvas = document.getElementById('dotFieldCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const glowCircle = document.getElementById('cursorGlowCircle');

  const p = {
    dotRadius: 1,
    dotSpacing: 10,
    bulgeStrength: 18,
    glowRadius: 90,
    sparkle: true,
    waveAmplitude: 2,
    cursorRadius: 150,
    cursorForce: 0.06,
    bulgeOnly: false,
    dotColor: 'rgba(13, 13, 13, 0.42)',
    highlightDotColor: 'rgba(0, 0, 0, 0.85)'
  };

  let width = 0;
  let height = 0;
  let dpr = 1;
  let dots = [];

  const m = {
    x: -9999,
    y: -9999,
    prevX: -9999,
    prevY: -9999,
    speed: 0,
    active: false
  };

  function initDots() {
    dots = [];
    const cols = Math.ceil(width / p.dotSpacing) + 2;
    const rows = Math.ceil(height / p.dotSpacing) + 2;
    const offsetX = (width % p.dotSpacing) / 2;
    const offsetY = (height % p.dotSpacing) / 2;

    for (let i = 0; i < cols; i++) {
      for (let j = 0; j < rows; j++) {
        const ax = offsetX + (i - 1) * p.dotSpacing;
        const ay = offsetY + (j - 1) * p.dotSpacing;
        dots.push({
          ax: ax,
          ay: ay,
          x: ax,
          y: ay,
          sx: ax,
          sy: ay,
          vx: 0,
          vy: 0,
          sparkle: p.sparkle && Math.random() < 0.03
        });
      }
    }
  }

  function resize() {
    dpr = window.devicePixelRatio || 1;
    width = window.innerWidth;
    height = window.innerHeight;

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);
    initDots();
  }

  window.addEventListener('resize', resize);

  window.addEventListener('mousemove', (e) => {
    if (!m.active) {
      m.prevX = e.clientX;
      m.prevY = e.clientY;
      m.active = true;
      if (glowCircle) glowCircle.style.opacity = '1';
    }
    m.x = e.clientX;
    m.y = e.clientY;
    const dx = m.x - m.prevX;
    const dy = m.y - m.prevY;
    m.speed = Math.sqrt(dx * dx + dy * dy);
    m.prevX = m.x;
    m.prevY = m.y;
  });

  window.addEventListener('mouseleave', () => {
    m.active = false;
    m.speed = 0;
    if (glowCircle) glowCircle.style.opacity = '0';
  });

  m.x = window.innerWidth / 2;
  m.y = window.innerHeight / 2;
  m.prevX = m.x;
  m.prevY = m.y;
  resize();

  let ambientAngle = 0;
  let startTime = performance.now();

  function draw() {
    ctx.clearRect(0, 0, width, height);

    const t = (performance.now() - startTime) * 0.002;

    if (!m.active) {
      ambientAngle += 0.012;
      m.x = width / 2 + Math.cos(ambientAngle) * 80;
      m.y = height / 2 + Math.sin(ambientAngle * 0.8) * 50;
      m.speed = 0.5;
    } else {
      m.speed *= 0.92;
    }

    if (glowCircle) {
      glowCircle.setAttribute('cx', m.x);
      glowCircle.setAttribute('cy', m.y);
    }

    const cursorR = p.cursorRadius;
    const cursorR2 = cursorR * cursorR;

    for (let idx = 0; idx < dots.length; idx++) {
      const d = dots[idx];

      const dx = d.sx - m.x;
      const dy = d.sy - m.y;
      const distSq = dx * dx + dy * dy;

      if (!p.bulgeOnly && distSq < cursorR2 && distSq > 0.0001) {
        const dist = Math.sqrt(distSq);
        const angle = Math.atan2(dy, dx);
        const move = (500 / dist) * (m.speed * p.cursorForce);
        d.vx += Math.cos(angle) * -move;
        d.vy += Math.sin(angle) * -move;
      }

      d.vx *= 0.9;
      d.vy *= 0.9;
      d.x = d.ax + d.vx;
      d.y = d.ay + d.vy;
      d.sx += (d.x - d.sx) * 0.1;
      d.sy += (d.y - d.sy) * 0.1;

      let drawX = d.sx;
      let drawY = d.sy;

      drawY += Math.sin(d.ax * 0.03 + t) * p.waveAmplitude;
      drawX += Math.cos(d.ay * 0.03 + t * 0.7) * p.waveAmplitude * 0.5;

      let rad = p.dotRadius;
      let color = p.dotColor;

      if (distSq < cursorR2 && distSq > 0.0001) {
        const dist = Math.sqrt(distSq);
        const factor = 1 - (dist / cursorR);
        const bulgeShift = Math.sin(factor * Math.PI) * p.bulgeStrength;
        const dirX = dx / dist;
        const dirY = dy / dist;

        drawX += dirX * bulgeShift;
        drawY += dirY * bulgeShift;

        if (dist < cursorR * 0.55) {
          color = p.highlightDotColor;
          rad = p.dotRadius * (1 + factor * 0.4);
        }
      }

      if (d.sparkle) {
        rad = rad * 1.8;
      }

      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(drawX, drawY, rad, 0, Math.PI * 2);
      ctx.fill();
    }

    requestAnimationFrame(draw);
  }

  requestAnimationFrame(draw);
})();
