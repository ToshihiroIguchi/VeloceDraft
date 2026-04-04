# VeloceDraft 詳細テスト計画 (Detailed Test Plan)

本ドキュメントは、VeloceDraft の全機能に対する検証項目と、それぞれのテスト手法（Unit, Integration, E2E）を定義します。

## 1. テスト戦略
*   **Unit Test (Backend)**: `pytest` を使用し、幾何計算ロジック、DXF 生成ロジック、Pydantic モデルのバリデーションを検証。
*   **Unit Test (Frontend)**: `vitest` を使用し、`cadReducer` の状態遷移と、Fabric.js オブジェクトへの反映ロジックを検証。
*   **Integration Test**: FastAPI エンドポイントと React Frontend 間の `fetch` 通信、CORS 設定、Blob ダウンロードを検証。
*   **E2E Test**: `Playwright` を使用し、ユーザーの一連の操作（描画→配列化→エクスポート）がヘッドレスブラウザで完遂できるかを検証。

## 2. 機能別テストマトリクス

| カテゴリ | 機能名 | テスト項目（検証内容） | 手法 | 期待される結果 |
|:---|:---|:---|:---|:---|
| **描画** | Rounded Rect | ドラッグにより矩形が作成され、rx/ry が適用される | E2E | キャンバス上に角丸矩形が表示される |
| | Line | 始点・終点を指定して線分が描画される | E2E | キャンバス上に青色の線分が表示される |
| **操作** | Select | 配置済みオブジェクトをクリックで選択できる | E2E | オブジェクトがアクティブ（青枠）になる |
| | Pan / Zoom | Alt+ドラッグおよびホイールで描画位置・倍率が変わる | E2E | `viewportTransform` が更新される |
| | Distance Overlay | 操作中に相対座標 (dx, dy) が表示される | E2E | オーバーレイテキストが動的に更新される |
| **MLCC特殊** | Electrode Array | 送信図形から 2D 配列が生成される | Integration | 内部モデルに配列要素が追加される |
| | Array Sync | ソース図形の rx 変更が配列全体に波及する | Unit (FE) | 全配列要素の rx が同期して再描画される |
| **計算** | Area Calculation | Rounded Rect および Array の総面積を算出 | Unit (BE) | `w*h - (4-PI)r^2` の式と一致する |
| **データ** | DXF Export | 内部モデルから DXF 文字列を生成 | Unit (BE) | `ezdxf` 経由で開ける有効な DXF が生成される |
| | SVG / PDF Export | 物理ファイル（Blob）として書き出される | Integration | 適切な Content-Type のバイナリが返る |
| | DXF Import | DXF をアップロードして内部モデルに変換 | Unit (BE) | 座標やサイズが正しく JSON に復元される |
| | **Round-Trip** | Export した DXF を再度 Import する | Integration | 元の Entity 数と主要寸法が一致する |
| **API** | Fillet API | 2本の線分の交点と Fillet 可能性を算出 | Unit (BE) | 正しい交点座標が返される |

## 3. 特殊な境界条件テスト (Edge Cases)
*   **ゼロ/負数入力**: 配列個数に 0 や負の値を指定した場合のエラーハンドリング。
*   **超巨大配列**: 100x100 等の巨大配列生成時のメモリ消費と描画パフォーマンス。
*   **極小 R**: rx < 1e-6 等、事実上の Rect となる場合の面積計算の安定性。

## 4. 実行ワークフロー
1.  **Backend Unit**: `pytest tests/backend/`
2.  **Frontend Unit**: `npm run test`
3.  **E2E (Main)**: `python tests/e2e_screenshot.py`
4.  **Manual Check**: 生成された DXF/SVG を外部ビューア（AutoCAD / Illustrator）で開き、目視確認。

---
> [!IMPORTANT]
> **GitHub Actions 連携**: 全自動テストスイートは Linux (Ubuntu) 環境でも動作するように、パス区切り文字や Python 実行パスを環境変数で制御します。
