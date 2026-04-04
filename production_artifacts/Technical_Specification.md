# VeloceDraft 技術仕様

## 1. 概要
MLCCの電極パターン編集専用に特化した小規模 Web 2D CAD である。汎用 CAD 的な機能（複雑な制約、全包括的 DXF 対応、WASM）は排除し、MLCC 専用の配置、反復、閉領域化、面積把握に特化する。内部の正本（Source of Truth）として独自の JSON Drawing Model を用いる。

## 2. 内部 JSON Drawing Model
内部正本は Frontend / Backend 間で以下のような JSON モデルを共有する。

```typescript
type Point = { x: number, y: number };

type EntityBase = {
  id: string;
  layerId: string;
  visible: boolean;
};

type RoundedRect = EntityBase & {
  type: 'roundedRect';
  center: Point;
  width: number;
  height: number;
  rx: number;
  ry: number;
};

type ElectrodeArray = EntityBase & {
  type: 'electrodeArray';
  sourceId: string; // 複製元の Electrode ID
  origin: Point;
  countX: number; // または一方向の count
  pitchX: number;
  pitchY: number;
};

type ClosedRegion = {
  id: string;
  boundarySegments: any[]; // Line や Arc
  area: number;
  sourceEntityIds: string[];
  containsArcs: boolean;
};

type DrawingModel = {
  layers: { id: string, name: string, visible: boolean }[];
  entities: any[]; // Line, Arc, Rect, RoundedRect, ElectrodeArray
  closedRegions: ClosedRegion[];
};
```

## 3. UI 方針
- 自由作図ではなく、Electrode Placement と Pattern Editing を中心コンセプトとする。
- 距離表示は線分の描画中に動的オーバーレイされる。
- 角R（radius）パラメータは RoundedRect のプロパティとしてダイレクトに操作できる。

## 4. DXF の扱い
- フロントエンドのみの DXF 取り扱い（WASM や JS 版パーサ・ライター）は行わない。
- バックエンドが ezdxf を利用して import / export を担当し、必ず Internal JSON との変換を介在させる。
