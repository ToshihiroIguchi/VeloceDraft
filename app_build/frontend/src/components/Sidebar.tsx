import React, { useState } from 'react';
import type { CadAction } from '../store/cadReducer';
import type { CadState, ElectrodeArray, RoundedRect, Line } from '../model';
import { Activity, Database, Link, Link2Off, Settings } from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';

interface SidebarProps {
  state: CadState;
  dispatch: React.Dispatch<CadAction>;
}

export const Sidebar: React.FC<SidebarProps> = ({ state, dispatch }) => {
  const [isRadiusLinked, setIsRadiusLinked] = useState(true);
  const selectedEntities = state.model.entities.filter(e => state.selectedEntityIds.includes(e.id));
  const unitDisplay = state.model.unit === 'um' ? 'μm' : state.model.unit;

  return (
    <div style={{ width: '250px', borderLeft: '1px solid #ccc', background: '#fafafa', padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px', overflowY: 'auto' }}>
      <div>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '16px', margin: '0 0 12px 0' }}>
          <Database size={18} /> Layers
        </h3>
        {state.model.layers.map(layer => (
          <div key={layer.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', fontSize: '14px' }}>
            <input 
              type="checkbox" 
              checked={layer.visible} 
              onChange={() => dispatch({ type: 'TOGGLE_LAYER_VISIBILITY', layerId: layer.id })} 
            />
            <span style={{ flex: 1, fontWeight: state.activeLayerId === layer.id ? 'bold' : 'normal', color: '#444' }}>
              {layer.name}
            </span>
          </div>
        ))}
      </div>

      <hr style={{ border: 'none', borderTop: '1px solid #eee' }} />

      <div>
        <h3 style={{ fontSize: '16px', margin: '0 0 12px 0' }}>Project Units</h3>
        <select 
          value={state.model.unit} 
          onChange={e => dispatch({ type: 'SET_UNIT', unit: e.target.value as any })}
          style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ddd', fontSize: '14px' }}
        >
          <option value="unitless">Unitless</option>
          <option value="mm">Millimeters (mm)</option>
          <option value="um">Micrometers (μm)</option>
          <option value="inch">Inches (in)</option>
        </select>
      </div>

      {selectedEntities.length === 0 && (state.currentTool === 'roundedRect') && (
        <>
          <hr style={{ border: 'none', borderTop: '1px solid #eee' }} />
          <div>
            <h3 style={{ fontSize: '15px', margin: '0 0 10px 0', color: '#333', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Settings size={16} /> Tool Defaults
            </h3>
            <label style={{ fontSize: '13px', color: '#666', display: 'flex', flexDirection: 'column', gap: '4px' }}>
              Initial Radius ({unitDisplay}):
              <input 
                type="number" 
                value={isNaN(state.filletRadius) ? '' : state.filletRadius} 
                onChange={e => {
                  const val = e.target.value === '' ? NaN : parseFloat(e.target.value);
                  dispatch({ type: 'SET_FILLET_RADIUS', radius: val });
                }} 
                style={{ width: '100%', padding: '6px', borderRadius: '4px', border: '1px solid #ddd', fontSize: '13px' }}
              />
            </label>
          </div>
        </>
      )}

      <hr style={{ border: 'none', borderTop: '1px solid #eee' }} />

      <div style={{ flex: 1 }}>
        <h3 style={{ fontSize: '16px', margin: '0 0 12px 0' }}>Properties</h3>
        {selectedEntities.length === 0 && <p style={{ color: '#888', fontSize: '13px' }}>No entities selected.</p>}
        {selectedEntities.map(entity => {
          if (entity.type === 'electrodeArray') {
            const arr = entity as ElectrodeArray;
            return (
              <div key={arr.id} style={{ display: 'flex', flexDirection: 'column', gap: '10px', background: '#fff', padding: '12px', borderRadius: '8px', border: '1px solid #eee', marginBottom: '12px' }}>
                <h4 style={{ margin: 0, fontSize: '14px', color: '#333' }}>Array: {arr.id.substring(0,6)}</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                  <label style={{ fontSize: '12px', color: '#666' }}>Count X: <input type="number" value={arr.countX} onChange={e => dispatch({ type: 'UPDATE_ENTITY', id: arr.id, updates: { countX: parseInt(e.target.value) } })} style={{width: '100%', padding: '4px', border: '1px solid #ddd', borderRadius: '4px'}} /></label>
                  <label style={{ fontSize: '12px', color: '#666' }}>Count Y: <input type="number" value={arr.countY} onChange={e => dispatch({ type: 'UPDATE_ENTITY', id: arr.id, updates: { countY: parseInt(e.target.value) } })} style={{width: '100%', padding: '4px', border: '1px solid #ddd', borderRadius: '4px'}} /></label>
                  <label style={{ fontSize: '12px', color: '#666' }}>Pitch X: <input type="number" value={arr.pitchX} onChange={e => dispatch({ type: 'UPDATE_ENTITY', id: arr.id, updates: { pitchX: parseFloat(e.target.value) } })} style={{width: '100%', padding: '4px', border: '1px solid #ddd', borderRadius: '4px'}} /></label>
                  <label style={{ fontSize: '12px', color: '#666' }}>Pitch Y: <input type="number" value={arr.pitchY} onChange={e => dispatch({ type: 'UPDATE_ENTITY', id: arr.id, updates: { pitchY: parseFloat(e.target.value) } })} style={{width: '100%', padding: '4px', border: '1px solid #ddd', borderRadius: '4px'}} /></label>
                  <label style={{ fontSize: '12px', color: '#666' }}>Stagger X: <input type="number" value={arr.staggerX} onChange={e => dispatch({ type: 'UPDATE_ENTITY', id: arr.id, updates: { staggerX: parseFloat(e.target.value) } })} style={{width: '100%', padding: '4px', border: '1px solid #ddd', borderRadius: '4px'}} /></label>
                </div>
              </div>
            );
          }
          if (entity.type === 'roundedRect') {
            const rr = entity as RoundedRect;
            return (
              <div key={rr.id} style={{ display: 'flex', flexDirection: 'column', gap: '10px', background: '#fff', padding: '12px', borderRadius: '8px', border: '1px solid #eee', marginBottom: '12px' }}>
                 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                   <h4 style={{ margin: 0, fontSize: '14px', color: '#333' }}>Rounded Rect: {rr.id.substring(0,6)}</h4>
                   <button 
                     onClick={() => setIsRadiusLinked(!isRadiusLinked)}
                     style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#007bff', padding: '2px' }}
                     title={isRadiusLinked ? "Unlink RX/RY" : "Link RX/RY"}
                   >
                     {isRadiusLinked ? <Link size={16} /> : <Link2Off size={16} />}
                   </button>
                 </div>
                 
                 {isRadiusLinked ? (
                   <label style={{ fontSize: '12px', color: '#666', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                     Corner Radius: 
                     <input 
                       type="number" 
                       value={rr.rx} 
                       onChange={e => {
                         const val = parseFloat(e.target.value) || 0;
                         dispatch({ type: 'UPDATE_ENTITY', id: rr.id, updates: { rx: val, ry: val } });
                         // Also sync Tool Defaults if linked
                         dispatch({ type: 'SET_FILLET_RADIUS', radius: val });
                       }} 
                       style={{width: '100%', padding: '6px', border: '1px solid #ddd', borderRadius: '4px'}} 
                     />
                   </label>
                 ) : (
                   <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                    <label style={{ fontSize: '12px', color: '#666' }}>RX: <input type="number" value={rr.rx} onChange={e => dispatch({ type: 'UPDATE_ENTITY', id: rr.id, updates: { rx: parseFloat(e.target.value) || 0 } })} style={{width: '100%', padding: '4px', border: '1px solid #ddd', borderRadius: '4px'}} /></label>
                    <label style={{ fontSize: '12px', color: '#666' }}>RY: <input type="number" value={rr.ry} onChange={e => dispatch({ type: 'UPDATE_ENTITY', id: rr.id, updates: { ry: parseFloat(e.target.value) || 0 } })} style={{width: '100%', padding: '4px', border: '1px solid #ddd', borderRadius: '4px'}} /></label>
                   </div>
                 )}
              </div>
            );
          }
          if (entity.type === 'line') {
            const ln = entity as Line;
            return (
              <div key={ln.id} style={{ display: 'flex', flexDirection: 'column', gap: '10px', background: '#fff', padding: '12px', borderRadius: '8px', border: '1px solid #eee', marginBottom: '12px' }}>
                <h4 style={{ margin: 0, fontSize: '14px', color: '#333' }}>Line: {ln.id.substring(0,6)}</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                  <label style={{ fontSize: '10px', color: '#999' }}>Start X: <div style={{padding: '4px', background: '#f9f9f9', borderRadius: '4px'}}>{ln.start.x.toFixed(2)}</div></label>
                  <label style={{ fontSize: '10px', color: '#999' }}>Start Y: <div style={{padding: '4px', background: '#f9f9f9', borderRadius: '4px'}}>{ln.start.y.toFixed(2)}</div></label>
                  <label style={{ fontSize: '10px', color: '#999' }}>End X: <div style={{padding: '4px', background: '#f9f9f9', borderRadius: '4px'}}>{ln.end.x.toFixed(2)}</div></label>
                  <label style={{ fontSize: '10px', color: '#999' }}>End Y: <div style={{padding: '4px', background: '#f9f9f9', borderRadius: '4px'}}>{ln.end.y.toFixed(2)}</div></label>
                </div>
              </div>
            );
          }
          return <div key={entity.id} style={{ fontSize: '13px', color: '#666' }}>Other shape ({entity.type})</div>;
        })}
      </div>
      
      <hr style={{ border: 'none', borderTop: '1px solid #eee' }} />

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <h3 style={{ fontSize: '16px', margin: 0 }}>Analysis</h3>
          <button 
            style={{ 
              padding: '10px', 
              background: '#333', 
              color: 'white', 
              border: 'none', 
              borderRadius: '8px', 
              cursor: 'pointer',
              width: '100%',
              fontSize: '13px',
              fontWeight: '600',
              transition: 'background 0.2s'
            }}
            onMouseOver={e => e.currentTarget.style.background = '#000'}
            onMouseOut={e => e.currentTarget.style.background = '#333'}
            onClick={async () => {
              try {
                const res = await fetch(`${API_BASE_URL}/api/area/calculate`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify(state.model)
                });
                if (!res.ok) throw new Error("Calculation request failed");
                const data = await res.json();
                const area = data.area;
                const suffix = state.model.unit === 'unitless' ? 'units' : unitDisplay;
                dispatch({ type: 'ADD_NOTIFICATION', notification: { 
                  message: `Total Opening Area: ${area.toFixed(2)} ${suffix}²`, 
                  type: 'success' 
                } });
              } catch (e) {
                dispatch({ type: 'ADD_NOTIFICATION', notification: { message: `Calculation failed: ${e}`, type: 'error' } });
              }
            }}
          >
            Calculate Total Opening Area
          </button>
      </div>

      <div style={{ 
        marginTop: 'auto',
        padding: '12px', 
        background: state.serverStatus === 'online' ? '#e8f5e9' : '#ffebee', 
        borderRadius: '10px',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        fontSize: '11px',
        fontWeight: '600',
        color: state.serverStatus === 'online' ? '#2e7d32' : '#c62828',
        border: `1px solid ${state.serverStatus === 'online' ? '#c8e6c9' : '#ffcdd2'}`
      }}>
        <Activity size={14} />
        <div style={{ flex: 1 }}>BACKEND: {state.serverStatus.toUpperCase()}</div>
        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'currentColor', boxShadow: '0 0 4px currentColor' }} />
      </div>

    </div>
  );
};
