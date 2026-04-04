export type Point = { x: number; y: number };

export type EntityBase = {
  id: string;
  layerId: string;
  visible: boolean;
};

export type RoundedRect = EntityBase & {
  type: 'roundedRect';
  center: Point;
  width: number;
  height: number;
  rx: number;
  ry: number;
};

export type Rect = EntityBase & {
  type: 'rect';
  center: Point;
  width: number;
  height: number;
};

export type ElectrodeArray = EntityBase & {
  type: 'electrodeArray';
  sourceId: string;
  origin: Point;
  countX: number;
  countY: number;
  pitchX: number;
  pitchY: number;
};

export type Line = EntityBase & {
  type: 'line';
  start: Point;
  end: Point;
};

export type Arc = EntityBase & {
  type: 'arc';
  center: Point;
  radius: number;
  startAngle: number;
  endAngle: number;
};

export type Entity = RoundedRect | Rect | ElectrodeArray | Line | Arc;

export type Layer = {
  id: string;
  name: string;
  visible: boolean;
};

export type ClosedRegion = {
  id: string;
  boundarySegments: any[]; // Simplified
  area: number;
  sourceEntityIds: string[];
  containsArcs: boolean;
};

export type Notification = {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
};

export type ModalState = {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
};

export type DrawingModel = {
  layers: Layer[];
  entities: Entity[];
  closedRegions: ClosedRegion[];
  unit: 'mm' | 'um' | 'inch' | 'unitless';
};

export type CadState = {
  model: DrawingModel;
  activeLayerId: string;
  selectedEntityIds: string[];
  currentTool: 'select' | 'roundedRect' | 'rect' | 'line' | 'electrodeArray' | 'areaCheck' | 'pan';
  distanceOverlay: { active: boolean; p1: Point | null; p2: Point | null };
  notifications: Notification[];
  modal: ModalState;
  serverStatus: 'online' | 'offline';
  filletRadius: number;
};
