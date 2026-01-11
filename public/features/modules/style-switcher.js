/**
 * MorphoNews Style Switcher
 * テーマを動的に切り替える機能
 */
(function () {
    'use strict';

    class StyleSwitcher {
        constructor() {
            this.currentTheme = 'default';
            this.themes = [];
            this.container = null;
        }

        async init() {
            await this.loadThemes();
            this.loadSavedTheme();
            this.createSwitcher();
            this.applyTheme(this.currentTheme);
        }

        async loadThemes() {
            try {
                const response = await fetch('/styles/styles.json');
                if (!response.ok) throw new Error('Failed to load styles.json');
                const data = await response.json();
                this.themes = data.themes || [];
            } catch (error) {
                console.warn('StyleSwitcher: Failed to load themes', error);
                // デフォルトテーマのみ
                this.themes = [{ id: 'default', name: 'デフォルト' }];
            }
        }

        loadSavedTheme() {
            try {
                const saved = localStorage.getItem('morpho-theme');
                if (saved && this.themes.find(t => t.id === saved)) {
                    this.currentTheme = saved;
                }
            } catch { }
        }

        saveTheme() {
            try {
                localStorage.setItem('morpho-theme', this.currentTheme);
            } catch { }
        }

        createSwitcher() {
            // テーマが1つ以下なら表示しない
            if (this.themes.length <= 1) return;

            // 既存のスイッチャーがあれば削除
            const existing = document.getElementById('style-switcher');
            if (existing) existing.remove();

            // スイッチャーを作成
            this.container = document.createElement('div');
            this.container.id = 'style-switcher';

            const options = this.themes.map(theme =>
                `<option value="${theme.id}" ${theme.id === this.currentTheme ? 'selected' : ''}>
          ${theme.name}
        </option>`
            ).join('');

            this.container.innerHTML = `
        <label for="theme-select">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="5"></circle>
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"></path>
          </svg>
        </label>
        <select id="theme-select">${options}</select>
      `;

            // スタイルを追加
            const style = document.createElement('style');
            style.textContent = `
        #style-switcher {
          position: fixed;
          top: 20px;
          right: 20px;
          display: flex;
          align-items: center;
          gap: 8px;
          background: rgba(255, 255, 255, 0.95);
          border: 1px solid #e2e8f0;
          border-radius: 10px;
          padding: 8px 12px;
          box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
          z-index: 9998;
          font-family: system-ui, sans-serif;
        }
        #style-switcher label {
          display: flex;
          align-items: center;
          color: #64748b;
        }
        #theme-select {
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 6px;
          padding: 6px 10px;
          font-size: 14px;
          color: #334155;
          cursor: pointer;
          outline: none;
        }
        #theme-select:focus {
          border-color: #6366f1;
          box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }
        @media (max-width: 640px) {
          #style-switcher {
            top: auto;
            bottom: 70px;
            right: 10px;
          }
        }
      `;
            document.head.appendChild(style);
            document.body.appendChild(this.container);

            // イベントリスナー
            document.getElementById('theme-select').addEventListener('change', (e) => {
                this.switchTheme(e.target.value);
            });
        }

        switchTheme(themeId) {
            this.currentTheme = themeId;
            this.applyTheme(themeId);
            this.saveTheme();
        }

        applyTheme(themeId) {
            // 現在のテーマCSSを削除
            const existing = document.getElementById('morpho-theme-css');
            if (existing) existing.remove();

            // ベーステーマはスキップ
            if (themeId === 'default') return;

            // 新しいテーマCSSを読み込み
            const link = document.createElement('link');
            link.id = 'morpho-theme-css';
            link.rel = 'stylesheet';
            link.href = `/styles/themes/${themeId}.css`;
            document.head.appendChild(link);
        }

        getThemes() {
            return this.themes;
        }

        getCurrentTheme() {
            return this.currentTheme;
        }
    }

    // 初期化
    const styleSwitcher = new StyleSwitcher();

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => styleSwitcher.init());
    } else {
        styleSwitcher.init();
    }

    window.MorphoStyleSwitcher = styleSwitcher;
})();
