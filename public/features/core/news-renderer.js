/**
 * MorphoNews News Renderer
 * ニュースデータをページに表示する基本機能
 */
(function () {
    'use strict';

    class NewsRenderer {
        constructor() {
            this.newsData = null;
            this.container = null;
        }

        /**
         * 初期化
         */
        async init() {
            // ページからARTICLE_IDを取得
            const articleId = document.body.dataset.articleId;
            if (!articleId) {
                console.warn('NewsRenderer: No article ID found');
                return;
            }

            // ニュースデータを取得
            await this.loadNewsData(articleId);

            // 表示を更新
            this.render();
        }

        /**
         * ニュースデータを読み込み
         */
        async loadNewsData(articleId) {
            try {
                const response = await fetch(`/data/${articleId}.json`);
                if (!response.ok) throw new Error('Failed to load news data');
                this.newsData = await response.json();
            } catch (error) {
                console.error('NewsRenderer: Failed to load news data', error);
            }
        }

        /**
         * ニュースを表示
         */
        render() {
            if (!this.newsData) return;

            // トップニュースを表示
            this.renderTopNews();

            // メタ情報を表示
            this.renderMeta();
        }

        /**
         * トップニュースを表示
         */
        renderTopNews() {
            const container = document.getElementById('news-container');
            if (!container || !this.newsData.top_news) return;

            const html = this.newsData.top_news.map((news, index) => `
        <article class="news-card" data-index="${index}">
          <div class="news-number">${String(index + 1).padStart(2, '0')}</div>
          <div class="news-content">
            <h3 class="news-title">
              <a href="${this.escapeHtml(news.link)}" target="_blank" rel="noopener noreferrer">
                ${this.escapeHtml(news.title)}
              </a>
            </h3>
            <p class="news-description">${this.escapeHtml(news.description)}</p>
          </div>
        </article>
      `).join('');

            container.innerHTML = html;
        }

        /**
         * メタ情報を表示
         */
        renderMeta() {
            const meta = this.newsData.meta;
            if (!meta) return;

            // 各メタ要素を更新
            this.updateElement('meta-fetch-time', meta.fetch_time_jst);
            this.updateElement('meta-article-count', meta.article_count);
            this.updateElement('meta-model', meta.model_name);
            this.updateElement('meta-summary-tokens',
                `入力=${meta.summary_tokens?.input}, 出力=${meta.summary_tokens?.output}, 合計=${meta.summary_tokens?.total}`
            );
            this.updateElement('meta-design-tokens',
                `入力=${meta.design_tokens?.input || 0}, 出力=${meta.design_tokens?.output || 0}, 合計=${meta.design_tokens?.total || 0}`
            );
            this.updateElement('meta-summary-time', `${meta.summary_generation_time_sec}秒`);
            this.updateElement('meta-design-time', `${meta.design_generation_time_sec || 0}秒`);
            this.updateElement('meta-total-time', `${meta.total_processing_time_sec}秒`);
        }

        /**
         * 要素のテキストを更新
         */
        updateElement(id, text) {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = text;
            }
        }

        /**
         * HTMLエスケープ
         */
        escapeHtml(text) {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    }

    // インスタンスを作成して初期化
    const renderer = new NewsRenderer();

    // DOMContentLoaded で初期化（ローダーより先に実行される可能性があるため）
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => renderer.init());
    } else {
        renderer.init();
    }

    // グローバルに公開
    window.MorphoNewsRenderer = renderer;
})();
