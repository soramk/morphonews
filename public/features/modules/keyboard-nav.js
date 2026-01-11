/**
 * MorphoNews Keyboard Navigation
 * キーボードショートカットで前後のアーカイブに移動
 */
(function () {
    'use strict';

    class KeyboardNav {
        constructor() {
            this.prevLink = null;
            this.nextLink = null;
        }

        init() {
            this.findNavigationLinks();
            this.bindEvents();
            this.showHint();
        }

        findNavigationLinks() {
            // 前のリンクを探す
            this.prevLink = document.querySelector('a[href*="archives/"][href$=".html"]:not([href*="history"])');

            // data属性でも探す
            const prevEl = document.querySelector('[data-prev-link]');
            if (prevEl) {
                this.prevLink = prevEl.dataset.prevLink;
            }
        }

        bindEvents() {
            document.addEventListener('keydown', (e) => this.handleKeydown(e));
        }

        handleKeydown(e) {
            // 入力フィールドでは無効
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            // 修飾キーが押されている場合は無効
            if (e.ctrlKey || e.altKey || e.metaKey) return;

            switch (e.key) {
                case 'ArrowLeft':
                case 'h':
                case 'H':
                    this.goToPrev();
                    break;
                case 'ArrowRight':
                case 'l':
                case 'L':
                    this.goToNext();
                    break;
                case 'a':
                case 'A':
                    this.goToArchive();
                    break;
                case '?':
                    this.showHelp();
                    break;
            }
        }

        goToPrev() {
            if (this.prevLink && this.prevLink !== '#') {
                window.location.href = typeof this.prevLink === 'string' ? this.prevLink : this.prevLink.href;
            }
        }

        goToNext() {
            // 次のリンクは通常index.htmlにリダイレクトされる
            window.location.href = '../index.html';
        }

        goToArchive() {
            window.location.href = '../history.html';
        }

        showHint() {
            // ヒントを表示（初回のみ）
            const hintShown = localStorage.getItem('morpho-keyboard-hint-shown');
            if (hintShown) return;

            setTimeout(() => {
                const hint = document.createElement('div');
                hint.id = 'keyboard-hint';
                hint.innerHTML = `
          <span>💡 キーボードナビ: ← 前 / → 次 / A アーカイブ / ? ヘルプ</span>
          <button onclick="this.parentElement.remove(); localStorage.setItem('morpho-keyboard-hint-shown', 'true');">×</button>
        `;

                const style = document.createElement('style');
                style.textContent = `
          #keyboard-hint {
            position: fixed;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(30, 41, 59, 0.95);
            color: white;
            padding: 10px 16px;
            border-radius: 8px;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 12px;
            z-index: 9997;
            animation: fadeIn 0.3s ease;
          }
          #keyboard-hint button {
            background: none;
            border: none;
            color: white;
            font-size: 18px;
            cursor: pointer;
            opacity: 0.7;
          }
          #keyboard-hint button:hover {
            opacity: 1;
          }
          @keyframes fadeIn {
            from { opacity: 0; transform: translateX(-50%) translateY(10px); }
            to { opacity: 1; transform: translateX(-50%) translateY(0); }
          }
        `;
                document.head.appendChild(style);
                document.body.appendChild(hint);

                // 5秒後に自動で消える
                setTimeout(() => {
                    hint.remove();
                    localStorage.setItem('morpho-keyboard-hint-shown', 'true');
                }, 5000);
            }, 2000);
        }

        showHelp() {
            const existing = document.getElementById('keyboard-help');
            if (existing) {
                existing.remove();
                return;
            }

            const help = document.createElement('div');
            help.id = 'keyboard-help';
            help.innerHTML = `
        <div class="keyboard-help-content">
          <h3>⌨️ キーボードショートカット</h3>
          <ul>
            <li><kbd>←</kbd> / <kbd>H</kbd> 前のアーカイブ</li>
            <li><kbd>→</kbd> / <kbd>L</kbd> 次のアーカイブ（最新）</li>
            <li><kbd>A</kbd> アーカイブ一覧</li>
            <li><kbd>?</kbd> このヘルプを表示/非表示</li>
          </ul>
          <button onclick="this.closest('#keyboard-help').remove()">閉じる</button>
        </div>
      `;

            const style = document.createElement('style');
            style.textContent = `
        #keyboard-help {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 10000;
        }
        .keyboard-help-content {
          background: white;
          padding: 24px 32px;
          border-radius: 16px;
          box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25);
          max-width: 400px;
        }
        .keyboard-help-content h3 {
          margin: 0 0 16px 0;
          font-size: 18px;
          color: #1e293b;
        }
        .keyboard-help-content ul {
          list-style: none;
          padding: 0;
          margin: 0 0 20px 0;
        }
        .keyboard-help-content li {
          padding: 8px 0;
          color: #475569;
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .keyboard-help-content kbd {
          background: #f1f5f9;
          border: 1px solid #e2e8f0;
          border-radius: 4px;
          padding: 4px 8px;
          font-family: monospace;
          font-size: 13px;
          color: #334155;
        }
        .keyboard-help-content button {
          background: linear-gradient(135deg, #6366f1, #8b5cf6);
          color: white;
          border: none;
          padding: 10px 24px;
          border-radius: 8px;
          font-size: 14px;
          cursor: pointer;
          width: 100%;
        }
      `;
            document.head.appendChild(style);
            document.body.appendChild(help);

            // 背景クリックで閉じる
            help.addEventListener('click', (e) => {
                if (e.target === help) help.remove();
            });
        }
    }

    // 初期化
    const keyboardNav = new KeyboardNav();

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => keyboardNav.init());
    } else {
        keyboardNav.init();
    }

    window.MorphoKeyboardNav = keyboardNav;
})();
