import React from 'react';
import type { CadAction } from '../store/cadReducer';
import type { CadState, ElectrodeArray, RoundedRect } from '../model';

interface SidebarProps {
  state: CadState;
  dispatch: React.Dispatch<CadAction>;
}

export const Sidebar: React.FC<SidebarProps> = ({ state, dispatch }) => {
  const selectedEntities = state.model.entities.filter(e => state.selectedEntityIds.includes(e.id));

  return (
    <div style={{ width: '250px', borderLeft: '1px solid #ccc', background: '#fafafa', padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px', overflowY: 'auto' }}>
      <div>
        <h3>Layers</h3>
        {state.model.layers.map(layer => (
          <div key={layer.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <input 
              type="checkbox" 
              checked={layer.visible} 
              onChange={() => dispatch({ type: 'TOGGLE_LAYER_VISIBILITY', layerId: layer.id })} 
            />
            <span style={{ fontWeight: state.activeLayerId === layer.id ? 'bold' : 'normal' }}>
              {layer.name}
            </span>
          </div>
        ))}
      </div>

      <hr />

      <div>
        <h3>Properties</h3>
        {selectedEntities.length === 0 && <p style={{ color: '#888' }}>No entities selected.</p>}
        {selectedEntities.map(entity => {
          if (entity.type === 'electrodeArray') {
            const arr = entity as ElectrodeArray;
            return (
              <div key={arr.id} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <h4>Array: {arr.id.substring(0,6)}</h4>
                <label>Count X: <input type="number" value={arr.countX} onChange={e => dispatch({ type: 'UPDATE_ENTITY', id: arr.id, updates: { countX: parseInt(e.target.value) } })} style={{width: '60px'}} /></label>
                <label>Count Y: <input type="number" value={arr.countY} onChange={e => dispatch({ type: 'UPDATE_ENTITY', id: arr.id, updates: { countY: parseInt(e.target.value) } })} style={{width: '60px'}} /></label>
                <label>Pitch X: <input type="number" value={arr.pitchX} onChange={e => dispatch({ type: 'UPDATE_ENTITY', id: arr.id, updates: { pitchX: parseFloat(e.target.value) } })} style={{width: '60px'}} /></label>
                <label>Pitch Y: <input type="number" value={arr.pitchY} onChange={e => dispatch({ type: 'UPDATE_ENTITY', id: arr.id, updates: { pitchY: parseFloat(e.target.value) } })} style={{width: '60px'}} /></label>
              </div>
            );
          }
          if (entity.type === 'roundedRect') {
            const rr = entity as RoundedRect;
            return (
              <div key={rr.id} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                 <h4>Rounded Rect: {rr.id.substring(0,6)}</h4>
                 <label>RX: <input type="number" value={rr.rx} onChange={e => dispatch({ type: 'UPDATE_ENTITY', id: rr.id, updates: { rx: parseFloat(e.target.value) } })} style={{width: '60px'}} /></label>
                 <label>RY: <input type="number" value={rr.ry} onChange={e => dispatch({ type: 'UPDATE_ENTITY', id: rr.id, updates: { ry: parseFloat(e.target.value) } })} style={{width: '60px'}} /></label>
              </div>
            );
          }
          return <div key={entity.id}>Unknown shape</div>;
        })}
      </div>
      
      <hr />

      <div>
         <h3>Area Calculation</h3>
         <button onClick={async () => {
           const res = await fetch('http://localhost:8000/api/area/calculate', {
             method: 'POST',
             headers: { 'Content-Type': 'application/json' },
             body: JSON.stringify(state.model)
           });
           const data = await res.json();
           alert(`Calculated Total Area (Rect/RoundedRect): ${data.area.toFixed(2)} units²`);
         }}>
           Calculate Area of Selected
         </button>
      </div>

    </div>
  );
};
