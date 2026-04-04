import React from 'react';
import type { CadAction } from '../store/cadReducer';
import type { ModalState } from '../model';
import { TriangleAlert, X } from 'lucide-react';

interface ModalProps {
  modal: ModalState;
  dispatch: React.Dispatch<CadAction>;
}

export const Modal: React.FC<ModalProps> = ({ modal, dispatch }) => {
  if (!modal.isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.6)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 2000,
      animation: 'fadeIn 0.2s ease-out'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '24px',
        maxWidth: '400px',
        width: '90%',
        boxShadow: '0 10px 40px rgba(0,0,0,0.2)',
        position: 'relative',
        transform: 'translateY(0)',
        animation: 'slideUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)'
      }}>
        <button 
          onClick={() => dispatch({ type: 'HIDE_MODAL' })}
          style={{ position: 'absolute', top: '16px', right: '16px', background: 'transparent', border: 'none', cursor: 'pointer', color: '#666' }}
        >
          <X size={20} />
        </button>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: '16px' }}>
          <div style={{ background: '#fff5f5', color: '#f44336', padding: '12px', borderRadius: '50%' }}>
            <TriangleAlert size={32} />
          </div>
          
          <h2 style={{ margin: 0, fontSize: '20px', color: '#333' }}>{modal.title}</h2>
          <p style={{ margin: 0, color: '#666', lineHeight: 1.5 }}>{modal.message}</p>
          
          <button 
            onClick={() => dispatch({ type: 'HIDE_MODAL' })}
            style={{ 
              marginTop: '8px',
              padding: '10px 24px',
              background: '#333',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 'bold',
              width: '100%',
              transition: 'background 0.2s'
            }}
            onMouseOver={e => e.currentTarget.style.background = '#000'}
            onMouseOut={e => e.currentTarget.style.background = '#333'}
          >
            {modal.confirmLabel || 'OK'}
          </button>
        </div>
      </div>
      <style>{`
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
      `}</style>
    </div>
  );
};
