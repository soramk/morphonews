/**
 * MorphoNews Feature: エージェンティック・アクセラレーション・ワープ
 * Generated: 2026-02-01_1004
 * Description: ユーザーの操作速度（スクロールやカーソル移動）に連動して、情報の断片を3D空間上の視覚的粒子として放射・加速させることで、高速ブラウジング時の認知負荷を興奮と効率に変えるインターフェース。
 */
(function() {
  const id = 'agentic-acceleration-warp-vortex';
  if (document.getElementById(id)) return;

  const style = document.createElement('style');
  style.textContent = `
    #${id}-container {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      pointer-events: none;
      z-index: 99999;
      overflow: hidden;
      perspective: 800px;
    }
    .warp-fragment {
      position: absolute;
      color: #00ffcc;
      font-family: 'Inter', sans-serif;
      font-weight: 800;
      font-size: 14px;
      white-space: nowrap;
      text-transform: uppercase;
      letter-spacing: 2px;
      text-shadow: 0 0 10px rgba(0, 255, 204, 0.8);
      pointer-events: none;
      opacity: 0;
      filter: blur(2px);
    }
    .warp-streak {
      position: absolute;
      height: 1px;
      background: linear-gradient(90deg, transparent, rgba(0, 255, 204, 0.5));
      pointer-events: none;
    }
  `;
  document.head.appendChild(style);

  const container = document.createElement('div');
  container.id = `${id}-container`;
  document.body.appendChild(container);

  let lastX = 0, lastY = 0, lastTime = Date.now();
  let velocity = 0;
  const fragments = [];

  const getInterestingText = () => {
    const tags = ['h1', 'h2', 'h3', 'strong', 'a'];
    const elements = Array.from(document.querySelectorAll(tags.join(','))).filter(el => {
      const rect = el.getBoundingClientRect();
      return rect.top > 0 && rect.bottom < window.innerHeight;
    });
    if (elements.length === 0) return 'ACCELERATING';
    const target = elements[Math.floor(Math.random() * elements.length)];
    return target.innerText.split(' ')[0].substring(0, 15);
  };

  const createFragment = (x, y, v) => {
    const frag = document.createElement('div');
    frag.className = 'warp-fragment';
    frag.innerText = getInterestingText();
    
    const angle = Math.random() * Math.PI * 2;
    const spread = 200 * v;
    const targetX = (Math.cos(angle) * spread);
    const targetY = (Math.sin(angle) * spread);

    frag.style.left = x + 'px';
    frag.style.top = y + 'px';
    container.appendChild(frag);

    const duration = Math.max(400, 1200 - (v * 100));
    
    frag.animate([
      { transform: 'translate(0, 0) translateZ(0px) scale(0.5)', opacity: 0, filter: 'blur(4px)' },
      { opacity: 1, offset: 0.2 },
      { transform: `translate(${targetX}px, ${targetY}px) translateZ(600px) scale(2.5)`, opacity: 0, filter: 'blur(0px)' }
    ], {
      duration: duration,
      easing: 'cubic-bezier(0.165, 0.84, 0.44, 1)'
    }).onfinish = () => frag.remove();

    if (v > 5) {
      const streak = document.createElement('div');
      streak.className = 'warp-streak';
      streak.style.width = (v * 20) + 'px';
      streak.style.left = x + 'px';
      streak.style.top = y + 'px';
      streak.style.transform = `rotate(${angle}rad)`;
      container.appendChild(streak);
      streak.animate([
        { opacity: 0.8, transform: `rotate(${angle}rad) scaleX(1)` },
        { opacity: 0, transform: `rotate(${angle}rad) scaleX(5) translate(100px, 0)` }
      ], { duration: 500 }).onfinish = () => streak.remove();
    }
  };

  const handleInteraction = (e) => {
    const now = Date.now();
    const dt = now - lastTime;
    if (dt === 0) return;

    const clientX = e.clientX || window.innerWidth / 2;
    const clientY = e.clientY || window.innerHeight / 2;

    const dx = clientX - lastX;
    const dy = clientY - lastY;
    const dist = Math.sqrt(dx * dx + dy * dy);
    velocity = dist / dt;

    if (velocity > 1.5) {
      const count = Math.min(8, Math.floor(velocity));
      for (let i = 0; i < count; i++) {
        createFragment(clientX, clientY, velocity);
      }
    }

    lastX = clientX;
    lastY = clientY;
    lastTime = now;
  };

  window.addEventListener('mousemove', handleInteraction, { passive: true });
  window.addEventListener('scroll', () => handleInteraction({ clientX: lastX, clientY: lastY }), { passive: true });

  console.log('MorphoNews: Agentic Acceleration Warp Vortex Initialized.');
})();
