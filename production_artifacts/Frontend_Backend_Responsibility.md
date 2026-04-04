# フロントエンド・バックエンド責務分担

## 理念
SRP（単一責任の原則）に則り、UIとインタラクションはFrontend、ファイルI/Oおよび高負荷な幾何・変換処理はBackendが担当する。

## Frontend の責務
1. **Canvas Rendering**: Fabric.js を用いた図形の描画。
2. **Mouse Interaction**: 選択、ドラッグ、拡縮、パン。
3. **Internal JSON Model Operations**: React useReducer を介した状態管理。データの正本は Fabric.js ではなく State 側に持つ。
4. **Tool/UI States**: Electrode Array のプレビュー更新、Area Check 表示、距離ダイナミックオーバーレイ。
5. **API Calling**: DXF 送信/受信 API のコール。

*見送った代替案: フロントでのDXF処理 (WASMやdxf-parser等) - 実装の不確実性とMLCCの要件に対してオーバースペックであること、ezdxf が成熟していることから不採用。*

## Backend の責務
1. **DXF Import Handling**: アップロードされた DXF ファイルを ezdxf でパースし、Internal JSON Format に変換して返す。
2. **DXF/SVG/PDF Export Handling**: 送られた Internal JSON Format を ezdxf を用いて目的のフォーマットに変換し、バイナリとして返す。
3. **Error Handling**: 未対応エンティティなどの明示的なエラー・警告レスポンスの生成。

*見送った代替案: フルオンプレミスDB構成 - MVPではファイルをベースとし、永続化のための重厚なDBは必要としない（YAGNI原則適用）。*
