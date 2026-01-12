/**
 * MorphoNews Feature Loader
 * 機能モジュールを動的に読み込むエントリーポイント
 */
class MorphoLoader {
    constructor() {
        this.loadedModules = new Map();
        this.userSettings = this.loadUserSettings();
    }

    /**
     * 初期化：features.json を読み込み、有効な機能を動的にロード
     */
    async init() {
        try {
            // 1. features.json を読み込み
            const response = await fetch('../features/features.json');
            if (!response.ok) {
                console.error('Failed to load features.json');
                return;
            }
            const data = await response.json();

            // 2. 有効な機能のみ読み込み
            for (const feature of data.features) {
                if (this.isEnabled(feature)) {
                    await this.loadModule(feature);
                }
            }

            console.log(`✨ MorphoLoader: ${this.loadedModules.size} modules loaded`);
        } catch (error) {
            console.error('MorphoLoader init error:', error);
        }
    }

    /**
     * 機能が有効かどうかを判定
     */
    isEnabled(feature) {
        // 必須機能は常に有効
        if (feature.required) return true;

        // ユーザー設定を確認
        const userSetting = this.userSettings.features?.[feature.id];
        if (userSetting !== undefined) {
            return userSetting;
        }

        // デフォルト設定を使用
        return feature.enabled;
    }

    /**
     * モジュールを動的に読み込み
     */
    async loadModule(feature) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = `../features/${feature.file}`;
            script.async = true;

            script.onload = () => {
                this.loadedModules.set(feature.id, feature);
                console.log(`✅ Loaded: ${feature.name}`);
                resolve();
            };

            script.onerror = () => {
                console.warn(`⚠️ Failed to load: ${feature.name}`);
                resolve(); // エラーでも継続
            };

            document.body.appendChild(script);
        });
    }

    /**
     * ユーザー設定を読み込み
     */
    loadUserSettings() {
        try {
            const saved = localStorage.getItem('morpho-settings');
            return saved ? JSON.parse(saved) : {};
        } catch {
            return {};
        }
    }

    /**
     * ユーザー設定を保存
     */
    saveUserSettings(settings) {
        this.userSettings = { ...this.userSettings, ...settings };
        localStorage.setItem('morpho-settings', JSON.stringify(this.userSettings));
    }

    /**
     * 機能の有効/無効を切り替え
     */
    toggleFeature(featureId, enabled) {
        if (!this.userSettings.features) {
            this.userSettings.features = {};
        }
        this.userSettings.features[featureId] = enabled;
        this.saveUserSettings(this.userSettings);
    }

    /**
     * 読み込み済みモジュールを取得
     */
    getLoadedModules() {
        return Array.from(this.loadedModules.values());
    }
}

// グローバルインスタンスを作成
window.MorphoLoader = new MorphoLoader();

// DOMContentLoaded で初期化
document.addEventListener('DOMContentLoaded', () => {
    window.MorphoLoader.init();
});
