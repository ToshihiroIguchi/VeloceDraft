import React from 'react';
import type { CadAction } from '../store/cadReducer';
import { MousePointer2, Square, PlusSquare, Network, Layers, FileDown, FileUp, BoxSelect, Minus, CornerDownRight } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';
import type { CadState, ElectrodeArray } from '../model';

interface ToolbarProps {
  state: CadState;
  dispatch: React.Dispatch<CadAction>;
}

export const Toolbar: React.FC<ToolbarProps> = ({ state, dispatch }) => {
  const handleExport = async (format: 'dxf' | 'svg' | 'pdf') => {
    try {
      const res = await fetch(`http://localhost:8000/api/${format}/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(state.model)
      });
      if (!res.ok) throw new Error("Export failed");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `export.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert(`Export failed: ${e}`);
    }
  };

  const handleFillet = async () => {
    const selectedLines = state.model.entities.filter(e => state.selectedEntityIds.includes(e.id) && e.type === 'line');
    if (selectedLines.length !== 2) {
      alert("Please select exactly 2 lines for Fillet");
      return;
    }
    try {
      const res = await fetch(`http://localhost:8000/api/fillet?radius=10.0`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          line1: selectedLines[0],
          line2: selectedLines[1],
          radius: 10.0
        })
      });
      const data = await res.json();
      alert(`Fillet Result: ${data.message}`);
    } catch (e) {
      alert(`Fillet failed: ${e}`);
    }
  };

  const createArray = () => {
    if (state.selectedEntityIds.length !== 1) {
      alert("Please select exactly one source shape");
      return;
    }
    const arr: ElectrodeArray = {
      id: uuidv4(),
      layerId: state.activeLayerId,
      type: 'electrodeArray',
      sourceId: state.selectedEntityIds[0],
      origin: { x: 0, y: 0 },
      countX: 5,
      countY: 1,
      pitchX: 20,
      pitchY: 0,
      visible: true
    };
    dispatch({ type: 'ADD_ENTITY', entity: arr });
  };

  const toolBtnStyle = (tool: string) => ({
    padding: '8px',
    background: state.currentTool === tool ? '#007bff' : 'transparent',
    color: state.currentTool === tool ? 'white' : '#333',
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    gap: '4px',
    fontSize: '12px'
  });

  return (
    <div style={{ height: '60px', borderBottom: '1px solid #ccc', display: 'flex', alignItems: 'center', padding: '0 16px', gap: '16px', background: '#f5f5f5' }}>
      <div style={{ fontWeight: 'bold', marginRight: '32px' }}>VeloceDraft</div>
      
      <button style={toolBtnStyle('select')} onClick={() => dispatch({ type: 'SET_TOOL', tool: 'select' })}>
        <MousePointer2 size={20} /> Select
      </button>
      <button style={toolBtnStyle('roundedRect')} onClick={() => dispatch({ type: 'SET_TOOL', tool: 'roundedRect' })}>
        <Square size={20} /> Rounded Rect
      </button>
      <button style={toolBtnStyle('line')} onClick={() => dispatch({ type: 'SET_TOOL', tool: 'line' })}>
        <Minus size={20} /> Line
      </button>
      <button style={toolBtnStyle('pan')} onClick={() => dispatch({ type: 'SET_TOOL', tool: 'pan' })}>
        <BoxSelect size={20} /> Pan (Alt+Drag)
      </button>

      <div style={{ width: '1px', height: '32px', background: '#ccc', margin: '0 8px' }} />

      <button style={toolBtnStyle('')} onClick={createArray}>
        <Network size={20} /> Create Array
      </button>
      <button style={toolBtnStyle('')} onClick={handleFillet}>
        <CornerDownRight size={20} /> Fillet
      </button>

      <div style={{ flex: 1 }} />

      <button style={toolBtnStyle('')} onClick={() => handleExport('dxf')}>
        <FileDown size={20} /> DXF
      </button>
      <button style={toolBtnStyle('')} onClick={() => handleExport('svg')}>
        <FileDown size={20} /> SVG
      </button>
      <button style={toolBtnStyle('')} onClick={() => handleExport('pdf')}>
        <FileDown size={20} /> PDF
      </button>
      
    </div>
  );
};
