/**
 * MorphoNews Font Resize
 * フォントサイズを調整するボタンを提供
 */
(function () {
    'use strict';

    class FontResize {
        constructor() {
            this.currentSize = 100;
            this.minSize = 70;
            this.maxSize = 150;
            this.step = 10;
            this.container = null;
        }

        init() {
            this.loadSavedSize();
            this.createControls();
            this.applySize();
        }

        loadSavedSize() {
            try {
                const saved = localStorage.getItem('morpho-font-size');
                if (saved) {
                    this.currentSize = parseInt(saved, 10);
                }
            } catch { }
        }

        saveSize() {
            try {
                localStorage.setItem('morpho-font-size', this.currentSize.toString());
            } catch { }
        }

        createControls() {
            // 既存のコントロールがあれば削除
            const existing = document.getElementById('font-resize-controls');
            if (existing) existing.remove();

            // コントロールを作成
            this.container = document.createElement('div');
            this.container.id = 'font-resize-controls';
            this.container.innerHTML = `
        <button id="font-decrease" aria-label="文字を小さく">A-</button>
        <span id="font-size-display">${this.currentSize}%</span>
        <button id="font-increase" aria-label="文字を大きく">A+</button>
      `;

            // スタイルを追加
            const style = document.createElement('style');
            style.textContent = `
        #font-resize-controls {
          position: fixed;
          bottom: 20px;
          right: 20px;
          display: flex;
          align-items: center;
          gap: 8px;
          background: rgba(255, 255, 255, 0.95);
          border: 1px solid #e2e8f0;
          border-radius: 12px;
          padding: 8px 12px;
          box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
          z-index: 9998;
          font-family: system-ui, sans-serif;
        }
        #font-resize-controls button {
          background: linear-gradient(135deg, #6366f1, #8b5cf6);
          color: white;
          border: none;
          border-radius: 6px;
          padding: 6px 12px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: transform 0.1s, opacity 0.2s;
        }
        #font-resize-controls button:hover {
          transform: scale(1.05);
        }
        #font-resize-controls button:active {
          transform: scale(0.95);
        }
        #font-resize-controls button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        #font-size-display {
          min-width: 50px;
          text-align: center;
          font-size: 14px;
          color: #64748b;
        }
        @media (max-width: 640px) {
          #font-resize-controls {
            bottom: 10px;
            right: 10px;
            padding: 6px 10px;
          }
        }
      `;
            document.head.appendChild(style);
            document.body.appendChild(this.container);

            // イベントリスナー
            document.getElementById('font-decrease').addEventListener('click', () => this.decrease());
            document.getElementById('font-increase').addEventListener('click', () => this.increase());
        }

        applySize() {
            document.documentElement.style.fontSize = `${this.currentSize}%`;
            this.updateDisplay();
        }

        updateDisplay() {
            const display = document.getElementById('font-size-display');
            if (display) {
                display.textContent = `${this.currentSize}%`;
            }

            const decreaseBtn = document.getElementById('font-decrease');
            const increaseBtn = document.getElementById('font-increase');
            if (decreaseBtn) decreaseBtn.disabled = this.currentSize <= this.minSize;
            if (increaseBtn) increaseBtn.disabled = this.currentSize >= this.maxSize;
        }

        decrease() {
            if (this.currentSize > this.minSize) {
                this.currentSize -= this.step;
                this.applySize();
                this.saveSize();
            }
        }

        increase() {
            if (this.currentSize < this.maxSize) {
                this.currentSize += this.step;
                this.applySize();
                this.saveSize();
            }
        }
    }

    // 初期化
    const fontResize = new FontResize();

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => fontResize.init());
    } else {
        fontResize.init();
    }

    window.MorphoFontResize = fontResize;
})();
