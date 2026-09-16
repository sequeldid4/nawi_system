(function initCursorGrid() {
  const canvas = document.getElementById('cursor-grid-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  // Props configuration
  const config = {
    cellSize: 70,
    color: '#b5d36b',
    radius: 140,
    falloff: 'smooth',
    holdTime: 400,
    fadeDuration: 800,
    lineWidth: 1.2,
    maxOpacity: 1,
    fillOpacity: 0,
    gridOpacity: 0,
    cellRadius: 0,
    clickPulse: true,
    pulseSpeed: 600
  };

  function hexToRgba(hex, alpha) {
    let c = hex.replace('#', '');
    if (c.length === 3) {
      c = c.split('').map(x => x + x).join('');
    }
    const num = parseInt(c, 16);
    const r = (num >> 16) & 255;
    const g = (num >> 8) & 255;
    const b = num & 255;
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  let width = 0;
  let height = 0;
  let dpr = 1;
  let mouseX = -9999;
  let mouseY = -9999;
  let lastMoveTime = 0;
  let pulses = [];
  let animFrameId = null;

  function resize() {
    dpr = window.devicePixelRatio || 1;
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);
  }

  window.addEventListener('resize', resize);
  resize();

  window.addEventListener('pointermove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    lastMoveTime = performance.now();
  });

  window.addEventListener('pointerleave', () => {
    mouseX = -9999;
    mouseY = -9999;
  });

  if (config.clickPulse) {
    window.addEventListener('pointerdown', (e) => {
      pulses.push({
        x: e.clientX,
        y: e.clientY,
        startTime: performance.now(),
        maxRadius: config.radius * 2.2
      });
    });
  }

  function drawCell(x, y, size, opacity) {
    if (opacity <= 0.001) return;
    const strokeCol = hexToRgba(config.color, opacity * config.maxOpacity);
    ctx.strokeStyle = strokeCol;
    ctx.lineWidth = config.lineWidth;

    if (config.fillOpacity > 0) {
      ctx.fillStyle = hexToRgba(config.color, opacity * config.fillOpacity);
      ctx.fillRect(x, y, size, size);
    }

    ctx.strokeRect(x, y, size, size);
  }

  function render(now) {
    ctx.clearRect(0, 0, width, height);

    pulses = pulses.filter(p => {
      const age = now - p.startTime;
      return age < config.pulseSpeed;
    });

    let cursorActiveAlpha = 0;
    if (mouseX >= 0 && mouseY >= 0) {
      const timeSinceMove = now - lastMoveTime;
      if (timeSinceMove < config.holdTime) {
        cursorActiveAlpha = 1;
      } else if (timeSinceMove < config.holdTime + config.fadeDuration) {
        cursorActiveAlpha = 1 - ((timeSinceMove - config.holdTime) / config.fadeDuration);
      }
    }

    const cols = Math.ceil(width / config.cellSize) + 1;
    const rows = Math.ceil(height / config.cellSize) + 1;

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const cellX = c * config.cellSize;
        const cellY = r * config.cellSize;
        const centerX = cellX + config.cellSize / 2;
        const centerY = cellY + config.cellSize / 2;

        let cellOpacity = config.gridOpacity;

        if (cursorActiveAlpha > 0) {
          const dx = mouseX - centerX;
          const dy = mouseY - centerY;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < config.radius) {
            let factor = (config.radius - dist) / config.radius;
            if (config.falloff === 'smooth') {
              factor = factor * factor * (3 - 2 * factor);
            }
            cellOpacity = Math.max(cellOpacity, factor * cursorActiveAlpha);
          }
        }

        for (let i = 0; i < pulses.length; i++) {
          const p = pulses[i];
          const progress = (now - p.startTime) / config.pulseSpeed;
          const currentR = progress * p.maxRadius;
          const bandWidth = 45;
          const dx = p.x - centerX;
          const dy = p.y - centerY;
          const dist = Math.sqrt(dx * dx + dy * dy);
          const distDiff = Math.abs(dist - currentR);

          if (distDiff < bandWidth) {
            const pulseStrength = (1 - distDiff / bandWidth) * (1 - progress);
            cellOpacity = Math.max(cellOpacity, pulseStrength);
          }
        }

        if (cellOpacity > 0) {
          drawCell(cellX, cellY, config.cellSize, cellOpacity);
        }
      }
    }

    animFrameId = requestAnimationFrame(render);
  }

  animFrameId = requestAnimationFrame(render);
})();
