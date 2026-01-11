/**
 * MorphoNews Reading Progress
 * ページ上部にスクロール進捗バーを表示
 */
(function () {
    'use strict';

    class ReadingProgress {
        constructor() {
            this.progressBar = null;
        }

        init() {
            this.createProgressBar();
            this.bindEvents();
            this.updateProgress();
        }

        createProgressBar() {
            // 既存のバーがあれば削除
            const existing = document.getElementById('reading-progress');
            if (existing) existing.remove();

            // プログレスバーを作成
            this.progressBar = document.createElement('div');
            this.progressBar.id = 'reading-progress';
            this.progressBar.innerHTML = '<div class="reading-progress-fill"></div>';

            // スタイルを追加
            const style = document.createElement('style');
            style.textContent = `
        #reading-progress {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 3px;
          background: rgba(99, 102, 241, 0.1);
          z-index: 9999;
        }
        .reading-progress-fill {
          height: 100%;
          width: 0%;
          background: linear-gradient(90deg, #6366f1, #8b5cf6, #a855f7);
          transition: width 0.1s ease-out;
        }
      `;
            document.head.appendChild(style);
            document.body.prepend(this.progressBar);
        }

        bindEvents() {
            window.addEventListener('scroll', () => this.updateProgress(), { passive: true });
            window.addEventListener('resize', () => this.updateProgress(), { passive: true });
        }

        updateProgress() {
            const scrollTop = window.scrollY;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;

            const fill = this.progressBar.querySelector('.reading-progress-fill');
            if (fill) {
                fill.style.width = `${Math.min(100, Math.max(0, progress))}%`;
            }
        }
    }

    // 初期化
    const readingProgress = new ReadingProgress();

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => readingProgress.init());
    } else {
        readingProgress.init();
    }

    window.MorphoReadingProgress = readingProgress;
})();
