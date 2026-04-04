import React, { useReducer } from 'react';
import { cadReducer, initialCadState } from './store/cadReducer';
import { Toolbar } from './components/Toolbar';
import { Sidebar } from './components/Sidebar';
import { CadCanvas } from './components/CadCanvas';
import { Toast } from './components/Toast';
import { Modal } from './components/Modal';
import { useEffect } from 'react';
import './index.css';

function App() {
  const [state, dispatch] = useReducer(cadReducer, initialCadState);
  
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('http://localhost:8080/health');
        if (res.ok) {
          dispatch({ type: 'SET_SERVER_STATUS', status: 'online' });
        } else {
          dispatch({ type: 'SET_SERVER_STATUS', status: 'offline' });
        }
      } catch (e) {
        dispatch({ type: 'SET_SERVER_STATUS', status: 'offline' });
      }
    };
    
    checkHealth();
    const timer = setInterval(checkHealth, 5000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <Toolbar state={state} dispatch={dispatch} />
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <CadCanvas state={state} dispatch={dispatch} />
        <Sidebar state={state} dispatch={dispatch} />
      </div>
      <Toast notifications={state.notifications} dispatch={dispatch} />
      <Modal modal={state.modal} dispatch={dispatch} />
    </div>
  );
};

export default App;
