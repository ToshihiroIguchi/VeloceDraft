import type { CadState, Entity, Layer, ClosedRegion } from '../model';

export type CadAction =
  | { type: 'SET_TOOL'; tool: CadState['currentTool'] }
  | { type: 'SET_ACTIVE_LAYER'; layerId: string }
  | { type: 'ADD_ENTITY'; entity: Entity }
  | { type: 'UPDATE_ENTITY'; id: string; updates: Partial<Entity> }
  | { type: 'SET_SELECTED'; entityIds: string[] }
  | { type: 'TOGGLE_LAYER_VISIBILITY'; layerId: string }
  | { type: 'LOAD_MODEL'; model: CadState['model'] }
  | { type: 'UPDATE_DISTANCE_OVERLAY'; p1: { x: number, y: number } | null; p2: { x: number, y: number } | null };

export const initialCadState: CadState = {
  model: {
    layers: [
      { id: 'layer1', name: 'Layer 1', visible: true }
    ],
    entities: [],
    closedRegions: []
  },
  activeLayerId: 'layer1',
  selectedEntityIds: [],
  currentTool: 'select',
  distanceOverlay: { active: false, p1: null, p2: null }
};

export function cadReducer(state: CadState, action: CadAction): CadState {
  switch (action.type) {
    case 'SET_TOOL':
      return { ...state, currentTool: action.tool };
    case 'SET_ACTIVE_LAYER':
      return { ...state, activeLayerId: action.layerId };
    case 'ADD_ENTITY':
      return {
        ...state,
        model: {
          ...state.model,
          entities: [...state.model.entities, action.entity]
        }
      };
    case 'UPDATE_ENTITY':
      return {
        ...state,
        model: {
          ...state.model,
          entities: state.model.entities.map(e =>
            e.id === action.id ? { ...e, ...action.updates } as Entity : e
          )
        }
      };
    case 'SET_SELECTED':
      return { ...state, selectedEntityIds: action.entityIds };
    case 'TOGGLE_LAYER_VISIBILITY':
      return {
        ...state,
        model: {
          ...state.model,
          layers: state.model.layers.map(l =>
            l.id === action.layerId ? { ...l, visible: !l.visible } : l
          )
        }
      };
    case 'LOAD_MODEL':
      return { ...state, model: action.model };
    case 'UPDATE_DISTANCE_OVERLAY':
      return { ...state, distanceOverlay: { active: !!action.p1, p1: action.p1, p2: action.p2 }};
    default:
      return state;
  }
}
