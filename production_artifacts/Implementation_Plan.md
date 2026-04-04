# VeloceDraft 実装計画

## フェーズ1: プロジェクトの初期設定・ベース構築
1. **ディレクトリとファイルの足場固め**:
   - バックエンド (FastAPI) スケルトンの作成。
   - フロントエンド (Vite + React + Fabric.js) スケルトンの作成。
   - 起動用シェルスクリプト、PowerShell スクリプト群の実装。
   - `.agents` と `settings.json` の設定。
2. **基本モデルとバックエンドAPI**:
   - `models.py` (Internal JSON 表現) の作成。
   - Backend の Health サーバー構築。
3. **Canvas 連携**:
   - React 側の `canvas_manager.ts` 的な層の作成。

## フェーズ2: コア機能 (MLCC用) の実装
1. **マウスクラス・状態管理**:
   - Zoom / Pan、Select、Move、Layer toggle 機能の実装。
2. **Electrode 配置**:
   - Rounded Rect の配置機能。
   - Electrode Array パラメータ編集 (Side panel UI)。
   - 配列の動的プレビューおよび生成。
3. **距離表示・面積と領域計算**:
   - dynamic distance overlay (dx, dy, L表示)。
   - Select 等での Auto Join と Closed Region 抽出 (簡易実装) と Area 算出。
4. **I/O API 実装**:
   - ezdxf を使った Import / Export (DXF, SVG)。

## フェーズ3: 最終機能とE2Eテスト・E2E稼働確認
1. **PDF出力追加**: ezdxf add-on のPDFを有効化。
2. **Playwright E2E**: localhost起動と全指定スクリーンの撮影を自動化する。
3. **文書化の完遂**: できたファイルを `Adopted_Libraries` や `browser_screenshots` などのフォルダへ整理。
