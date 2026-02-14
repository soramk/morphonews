/**
 * MorphoNews Feature: エージェンティック・リキッド・フェーズ・トランジショナー
 * Generated: 2026-02-14_0956
 * Description: ページ内の要素切り替え時やセクション移動時に、液体が混ざり合うような有機的なフェーズ遷移（メタモルフォーゼ）を視覚化します。SVGフィルタを活用したGooey効果により、情報の断絶を「流体」として繋ぎ合わせます。
 */
(function() {
  const style = document.createElement('style');
  style.textContent = `
    .liquid-transition-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      pointer-events: none;
      z-index: 99999;
      filter: url('#morpho-goo');
      opacity: 0;
      transition: opacity 0.5s;
    }
    .liquid-transition-overlay.active {
      opacity: 1;
    }
    .liquid-drop {
      position: absolute;
      background: linear-gradient(135deg, #4f46e5, #ec4899);
      border-radius: 50%;
      transform: scale(0);
    }
    @keyframes liquid-expand {
      0% { transform: scale(0); opacity: 0.8; }
      50% { opacity: 1; }
      100% { transform: scale(4); opacity: 0; }
    }
  `;
  document.head.appendChild(style);

  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("style", "position:fixed; width:0; height:0;");
  svg.innerHTML = `
    <defs>
      <filter id="morpho-goo">
        <feGaussianBlur in="SourceGraphic" stdDeviation="12" result="blur" />
        <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -9" result="goo" />
        <feComposite in="SourceGraphic" in2="goo" operator="atop" />
      </filter>
    </defs>`;
  document.body.appendChild(svg);

  const overlay = document.createElement('div');
  overlay.className = 'liquid-transition-overlay';
  document.body.appendChild(overlay);

  const triggerTransition = (x, y) => {
    overlay.classList.add('active');
    const dropCount = 8;
    for (let i = 0; i < dropCount; i++) {
      const drop = document.createElement('div');
      drop.className = 'liquid-drop';
      const size = 150 + Math.random() * 200;
      drop.style.width = `${size}px`;
      drop.style.height = `${size}px`;
      drop.style.left = `${x - size / 2 + (Math.random() - 0.5) * 100}px`;
      drop.style.top = `${y - size / 2 + (Math.random() - 0.5) * 100}px`;
      
      drop.style.animation = `liquid-expand ${0.8 + Math.random() * 0.4}s ease-in forwards`;
      overlay.appendChild(drop);

      setTimeout(() => {
        drop.remove();
        if (overlay.children.length === 0) {
          overlay.classList.remove('active');
        }
      }, 1200);
    }
  };

  // Intercept navigation-like clicks to perform transition
  document.addEventListener('click', (e) => {
    const target = e.target.closest('a, button, .interactive-element');
    if (target) {
      triggerTransition(e.clientX, e.clientY);
    }
  }, true);

  // Custom event for other modules to trigger
  window.addEventListener('morpho-transition-trigger', (e) => {
    const x = e.detail?.x || window.innerWidth / 2;
    const y = e.detail?.y || window.innerHeight / 2;
    triggerTransition(x, y);
  });

  console.log("Agentic Liquid Phase Transitioner activated. Transitions are now fluid.");
})();
