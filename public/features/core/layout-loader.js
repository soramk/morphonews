/**
 * MorphoNews Layout Loader
 * レイアウトモジュールを動的に読み込む
 */
class MorphoLayoutLoader {
    constructor() {
        this.currentLayout = null;
        this.availableLayouts = [];
    }

    /**
     * 初期化：layouts.json を読み込み、保存されたレイアウトを適用
     */
    async init() {
        try {
            // 1. layouts.json を読み込み
            const response = await fetch('../layouts/layouts.json');
            if (!response.ok) {
                console.warn('layouts.json not found, using default');
                return;
            }
            const data = await response.json();
            this.availableLayouts = data.layouts || [];

            // 2. 保存されたレイアウトまたはデフォルトを適用
            const savedLayout = localStorage.getItem('morpho-layout') || 'default';
            await this.applyLayout(savedLayout);

            console.log(`🎨 MorphoLayoutLoader: Layout "${savedLayout}" applied`);
        } catch (error) {
            console.error('MorphoLayoutLoader init error:', error);
        }
    }

    /**
     * レイアウトを適用
     */
    async applyLayout(layoutId) {
        const layout = this.availableLayouts.find(l => l.id === layoutId);
        if (!layout) {
            console.warn(`Layout "${layoutId}" not found, falling back to default`);
            layoutId = 'default';
        }

        // 既存のレイアウトCSSを削除
        const existingLink = document.getElementById('morpho-layout-css');
        if (existingLink) {
            existingLink.remove();
        }

        // 新しいレイアウトCSSを追加
        const link = document.createElement('link');
        link.id = 'morpho-layout-css';
        link.rel = 'stylesheet';
        link.href = `../layouts/${layout?.file || 'default.css'}`;

        // テーマCSSの後に挿入
        const themeLink = document.getElementById('morpho-theme-css');
        if (themeLink && themeLink.nextSibling) {
            themeLink.parentNode.insertBefore(link, themeLink.nextSibling);
        } else {
            document.head.appendChild(link);
        }

        this.currentLayout = layoutId;
        localStorage.setItem('morpho-layout', layoutId);

        // レイアウト変更イベントを発火
        window.dispatchEvent(new CustomEvent('morpho-layout-change', {
            detail: { layoutId, layout }
        }));
    }

    /**
     * 利用可能なレイアウト一覧を取得
     */
    getAvailableLayouts() {
        return this.availableLayouts;
    }

    /**
     * 現在のレイアウトIDを取得
     */
    getCurrentLayout() {
        return this.currentLayout;
    }
}

// グローバルインスタンスを作成
window.MorphoLayoutLoader = new MorphoLayoutLoader();

// DOMContentLoaded で初期化
document.addEventListener('DOMContentLoaded', () => {
    window.MorphoLayoutLoader.init();
});
