# BUG: コンテンツ・アウトライナーのMutationObserver無限ループ

**Status:** CLOSED ✅  
**Date:** 2026-01-14  
**Type:** Bug Fix

## 問題

コンテンツ・アウトライナーを有効化すると、ページがハングする。

## 原因

MutationObserverがDOMの変更を監視しているが、`refresh()`関数自体がDOMを変更（`list.innerHTML=''`や要素追加）するため、無限ループが発生していた。

### 問題のあったコードフロー

1. MutationObserverがDOM変更を検知
2. `refresh()`を呼び出し
3. `refresh()`がDOMを変更
4. MutationObserverがその変更を検知 → 1に戻る（無限ループ）

## 修正内容

- `refresh()`実行中は`observer.disconnect()`でMutationObserverを一時切断
- 処理完了後に`observer.observe()`で再接続
- アウトライナー要素自身の変更は無視するよう条件追加
- 連続した変更に対応するため`scheduleRefresh()`でデバウンス処理（100ms）を追加
- `isRefreshing`フラグで再入を防止

## 対象ファイル

- `public/features/modules/content-outliner.js`

## 解決日

2026-01-14
