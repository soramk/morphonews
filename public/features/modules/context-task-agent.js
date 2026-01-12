/**
 * MorphoNews Feature: コンテキスト適応型タスクエージェント
 * Generated: 2026-01-12_1720
 * Description: 閲覧中のコンテンツを自律的に解析し、数値の強調、重要語句の抽出、閲覧モードの切り替えなどの文脈に応じたタスクを提案するフローティングエージェントを追加します。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        #morpho-agent-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 10000;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .agent-bubble {
            background: #2563eb;
            color: white;
            padding: 12px 18px;
            border-radius: 24px 24px 4px 24px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: transform 0.3s ease, background 0.3s ease;
            font-size: 14px;
            font-weight: bold;
        }
        .agent-bubble:hover {
            transform: scale(1.05);
            background: #1d4ed8;
        }
        .agent-tasks {
            position: absolute;
            bottom: 60px;
            right: 0;
            width: 220px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            overflow: hidden;
            display: none;
            flex-direction: column;
            border: 1px solid #e5e7eb;
        }
        .agent-tasks.active {
            display: flex;
            animation: slideUp 0.3s ease-out;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .task-item {
            padding: 12px 16px;
            border-bottom: 1px solid #f3f4f6;
            cursor: pointer;
            font-size: 13px;
            color: #374151;
            transition: background 0.2s;
        }
        .task-item:hover {
            background: #eff6ff;
            color: #2563eb;
        }
        .task-item:last-child { border-bottom: none; }
        .agent-status {
            width: 8px;
            height: 8px;
            background: #4ade80;
            border-radius: 50%;
            display: inline-block;
            animation: blink 2s infinite;
        }
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        .morpho-highlight-num {
            background: #fef08a;
            border-bottom: 2px solid #facc15;
            transition: all 0.3s;
        }
    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.id = 'morpho-agent-container';
    
    const tasksMenu = document.createElement('div');
    tasksMenu.className = 'agent-tasks';
    
    const bubble = document.createElement('div');
    bubble.className = 'agent-bubble';
    bubble.innerHTML = '<span class="agent-status"></span> Morpho Agent';
    
    container.appendChild(tasksMenu);
    container.appendChild(bubble);
    document.body.appendChild(container);

    let isMenuOpen = false;

    const updateTasks = () => {
        const selection = window.getSelection().toString();
        tasksMenu.innerHTML = '';
        
        const tasks = [
            { label: '📊 数値をハイライト', action: highlightNumbers },
            { label: '🔍 重要語句をスキャン', action: scanKeywords },
            { label: '🌑 読書集中モード', action: toggleFocusMode }
        ];

        if (selection.length > 0) {
            tasks.unshift({ label: '❓ 「' + (selection.length > 10 ? selection.substring(0, 10) + '...' : selection) + '」を調査', action: () => alert('調査機能: ' + selection) });
        }

        tasks.forEach(task => {
            const div = document.createElement('div');
            div.className = 'task-item';
            div.textContent = task.label;
            div.onclick = (e) => {
                e.stopPropagation();
                task.action();
                toggleMenu(false);
            };
            tasksMenu.appendChild(div);
        });
    };

    function highlightNumbers() {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
        let node;
        const regex = /\\d+(?:[.,]\\d+)?(?:%|万人|円|ドル|km|kg)?/g;
        const nodesToReplace = [];

        while (node = walker.nextNode()) {
            if (node.parentElement.tagName !== 'SCRIPT' && node.parentElement.tagName !== 'STYLE' && node.parentElement.id !== 'morpho-agent-container') {
                if (regex.test(node.nodeValue)) {
                    nodesToReplace.push(node);
                }
            }
        }

        nodesToReplace.forEach(textNode => {
            const span = document.createElement('span');
            span.innerHTML = textNode.nodeValue.replace(regex, match => `<span class="morpho-highlight-num">${match}</span>`);
            textNode.parentNode.replaceChild(span, textNode);
        });
    }

    function scanKeywords() {
        const text = document.body.innerText;
        const words = text.match(/[\\u3040-\\u309F\\u30A0-\\u30FF\\u4E00-\\u9FFF]{4,}/g) || [];
        const freq = {};
        words.forEach(w => freq[w] = (freq[w] || 0) + 1);
        const sorted = Object.entries(freq).sort((a, b) => b[1] - a[1]).slice(0, 5);
        alert('このページの主要キーワード:\\n' + sorted.map(s => `・${s[0]} (${s[1]}回)`).join('\\n'));
    }

    function toggleFocusMode() {
        const isFocus = document.body.style.filter === 'contrast(1.1) grayscale(0.5)';
        document.body.style.filter = isFocus ? '' : 'contrast(1.1) grayscale(0.5)';
        document.body.style.backgroundColor = isFocus ? '' : '#f9fafb';
        bubble.textContent = isFocus ? 'Morpho Agent' : 'Focus Active';
    }

    function toggleMenu(force) {
        isMenuOpen = force !== undefined ? force : !isMenuOpen;
        if (isMenuOpen) {
            updateTasks();
            tasksMenu.classList.add('active');
        } else {
            tasksMenu.classList.remove('active');
        }
    }

    bubble.onclick = (e) => {
        e.stopPropagation();
        toggleMenu();
    };

    document.addEventListener('click', () => toggleMenu(false));
    
    // Agentic behavior: occasionally pulse when scrolling to new content
    let scrollTimer;
    window.addEventListener('scroll', () => {
        clearTimeout(scrollTimer);
        scrollTimer = setTimeout(() => {
            bubble.style.transform = 'scale(1.2)';
            setTimeout(() => bubble.style.transform = 'scale(1)', 200);
        }, 500);
    });
})();
