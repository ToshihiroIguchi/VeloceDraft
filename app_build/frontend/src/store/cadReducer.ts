import type { CadState, Entity } from '../model';
import { v4 as uuidv4 } from 'uuid';

export type CadAction =
  | { type: 'SET_TOOL'; tool: CadState['currentTool'] }
  | { type: 'SET_ACTIVE_LAYER'; layerId: string }
  | { type: 'ADD_ENTITY'; entity: Entity }
  | { type: 'UPDATE_ENTITY'; id: string; updates: Partial<Entity> }
  | { type: 'SET_SELECTED'; entityIds: string[] }
  | { type: 'TOGGLE_LAYER_VISIBILITY'; layerId: string }
  | { type: 'LOAD_MODEL'; model: CadState['model'] }
  | { type: 'UPDATE_DISTANCE_OVERLAY'; p1: { x: number, y: number } | null; p2: { x: number, y: number } | null }
  | { type: 'ADD_NOTIFICATION'; notification: { message: string, type: 'success' | 'error' | 'info' } }
  | { type: 'REMOVE_NOTIFICATION'; id: string }
  | { type: 'SHOW_MODAL'; title: string; message: string; confirmLabel?: string }
  | { type: 'HIDE_MODAL' }
  | { type: 'SET_SERVER_STATUS'; status: 'online' | 'offline' }
  | { type: 'SET_UNIT'; unit: CadState['model']['unit'] }
  | { type: 'SET_FILLET_RADIUS'; radius: number }
  | { type: 'REPLACE_ENTITIES'; originalIds: string[]; newEntities: Entity[] };

export const initialCadState: CadState = {
  model: {
    layers: [
      { id: 'layer1', name: 'Layer 1', visible: true }
    ],
    entities: [],
    closedRegions: [],
    unit: 'unitless'
  },
  activeLayerId: 'layer1',
  selectedEntityIds: [],
  currentTool: 'select',
  distanceOverlay: { active: false, p1: null, p2: null },
  notifications: [],
  modal: { isOpen: false, title: '', message: '' },
  serverStatus: 'offline',
  filletRadius: 10.0
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
    case 'ADD_NOTIFICATION':
      // @ts-ignore
      const newNotif = { ...action.notification, id: uuidv4() };
      return { ...state, notifications: [...state.notifications, newNotif] };
    case 'REMOVE_NOTIFICATION':
      return { ...state, notifications: state.notifications.filter(n => n.id !== action.id) };
    case 'SHOW_MODAL':
      return { ...state, modal: { isOpen: true, title: action.title, message: action.message, confirmLabel: action.confirmLabel } };
    case 'HIDE_MODAL':
      return { ...state, modal: { ...state.modal, isOpen: false } };
    case 'SET_SERVER_STATUS':
      return { ...state, serverStatus: action.status };
    case 'SET_UNIT':
      return {
        ...state,
        model: {
          ...state.model,
          unit: action.unit
        }
      };
    case 'SET_FILLET_RADIUS':
      const isValidRadius = !isNaN(action.radius) && action.radius >= 0;
      return { 
        ...state, 
        filletRadius: action.radius,
        model: {
          ...state.model,
          entities: state.model.entities.map(e => 
            (isValidRadius && state.selectedEntityIds.includes(e.id) && e.type === 'roundedRect')
              ? { ...e, rx: action.radius, ry: action.radius } as Entity
              : e
          )
        }
      };
    case 'REPLACE_ENTITIES':
      return {
        ...state,
        model: {
          ...state.model,
          entities: [
            ...state.model.entities.filter(e => !action.originalIds.includes(e.id)),
            ...action.newEntities
          ]
        },
        selectedEntityIds: []
      };
    default:
      return state;
  }
}
