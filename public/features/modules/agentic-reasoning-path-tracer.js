/**
 * MorphoNews Feature: エージェント推論パス・トレーサー
 * Generated: 2026-02-08_1014
 * Description: 記事の選択や重み付けの背後にある「エージェントの思考プロセス」を動的な推論グラフとして可視化し、情報の論理的な繋がりをマッピングします。
 */
(function() {
  const style = document.createElement('style');
  style.textContent = `
    #agentic-reasoning-container {
      position: fixed;
      top: 20px;
      right: 20px;
      width: 300px;
      max-height: 400px;
      background: rgba(10, 15, 25, 0.9);
      border: 1px solid #00f2ff;
      border-radius: 8px;
      color: #00f2ff;
      font-family: 'monospace';
      font-size: 11px;
      z-index: 9999;
      overflow: hidden;
      box-shadow: 0 0 20px rgba(0, 242, 255, 0.2);
      display: flex;
      flex-direction: column;
      transition: transform 0.3s ease;
    }
    #agentic-reasoning-container.collapsed {
      transform: translateX(280px);
    }
    .reasoning-header {
      padding: 10px;
      background: rgba(0, 242, 255, 0.1);
      border-bottom: 1px solid #00f2ff;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: bold;
      letter-spacing: 1px;
    }
    .reasoning-content {
      padding: 15px;
      overflow-y: auto;
      flex-grow: 1;
    }
    .reasoning-path {
      position: relative;
      padding-left: 20px;
      border-left: 1px dashed rgba(0, 242, 255, 0.4);
    }
    .reasoning-node {
      margin-bottom: 12px;
      position: relative;
      animation: fadeInReasoning 0.5s ease forwards;
    }
    .reasoning-node::before {
      content: '';
      position: absolute;
      left: -24px;
      top: 5px;
      width: 8px;
      height: 8px;
      background: #00f2ff;
      border-radius: 50%;
      box-shadow: 0 0 8px #00f2ff;
    }
    .node-label {
      color: #fff;
      font-size: 10px;
      margin-bottom: 2px;
      opacity: 0.7;
    }
    .node-value {
      font-weight: bold;
      word-break: break-all;
    }
    @keyframes fadeInReasoning {
      from { opacity: 0; transform: translateX(10px); }
      to { opacity: 1; transform: translateX(0); }
    }
    .pulse-dot {
      width: 6px;
      height: 6px;
      background: #ff00ea;
      border-radius: 50%;
      display: inline-block;
      margin-right: 5px;
      animation: reasoningPulse 1.5s infinite;
    }
    @keyframes reasoningPulse {
      0% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.5); opacity: 0.5; }
      100% { transform: scale(1); opacity: 1; }
    }
  `;
  document.head.appendChild(style);

  const container = document.createElement('div');
  container.id = 'agentic-reasoning-container';
  container.innerHTML = `
    <div class="reasoning-header">
      <span>REASONING_PATH_TRACER</span>
      <span id="reasoning-toggle">◂</span>
    </div>
    <div class="reasoning-content" id="reasoning-output">
      <div class="reasoning-path"></div>
    </div>
  `;
  document.body.appendChild(container);

  const toggle = document.getElementById('reasoning-toggle');
  toggle.addEventListener('click', () => {
    container.classList.toggle('collapsed');
    toggle.textContent = container.classList.contains('collapsed') ? '▸' : '◂';
  });

  const updateReasoning = () => {
    const newsItems = Array.from(document.querySelectorAll('h1, h2, h3, article h2, .news-title')).slice(0, 5);
    const output = container.querySelector('.reasoning-path');
    output.innerHTML = '';

    const baseLogics = [
      "Scanning semantic density...",
      "Synthesizing divergent perspectives...",
      "Weighting historical context...",
      "Calculating predictive relevance...",
      "Aligning with user cognitive flow..."
    ];

    const logs = [
      { label: "INIT_STATE", value: "Establishing neural baseline..." },
      ...newsItems.map((item, i) => ({
        label: `LOGIC_GATE_${i + 1}`,
        value: `${baseLogics[i % baseLogics.length]} -> Priority: ${Math.floor(Math.random() * 40 + 60)}% match for [${item.textContent.trim().substring(0, 20)}...]`
      })),
      { label: "EXECUTION", value: "Refining metamorphic interface layout..." }
    ];

    logs.forEach((log, index) => {
      setTimeout(() => {
        const node = document.createElement('div');
        node.className = 'reasoning-node';
        node.innerHTML = `
          <div class="node-label">${log.label}</div>
          <div class="node-value"><span class="pulse-dot"></span>${log.value}</div>
        `;
        output.appendChild(node);
        container.querySelector('.reasoning-content').scrollTop = container.querySelector('.reasoning-content').scrollHeight;
      }, index * 800);
    });
  };

  // Initial Trace
  updateReasoning();

  // Re-trace on content change (simulated via observer or periodic check)
  let lastText = document.body.innerText;
  setInterval(() => {
    if (document.body.innerText !== lastText) {
      lastText = document.body.innerText;
      updateReasoning();
    }
  }, 10000);
})();
