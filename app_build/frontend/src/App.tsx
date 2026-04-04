import React, { useReducer } from 'react';
import { cadReducer, initialCadState } from './store/cadReducer';
import { Toolbar } from './components/Toolbar';
import { Sidebar } from './components/Sidebar';
import { CadCanvas } from './components/CadCanvas';
import './index.css';

function App() {
  const [state, dispatch] = useReducer(cadReducer, initialCadState);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <Toolbar state={state} dispatch={dispatch} />
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <CadCanvas state={state} dispatch={dispatch} />
        <Sidebar state={state} dispatch={dispatch} />
      </div>
    </div>
  );
}

export default App;
