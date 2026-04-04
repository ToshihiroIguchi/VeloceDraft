import React, { useEffect } from 'react';
import type { CadAction } from '../store/cadReducer';
import type { Notification } from '../model';
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react';

interface ToastProps {
  notifications: Notification[];
  dispatch: React.Dispatch<CadAction>;
}

export const Toast: React.FC<ToastProps> = ({ notifications, dispatch }) => {
  return (
    <div style={{
      position: 'fixed',
      top: '20px',
      right: '20px',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
      gap: '10px'
    }}>
      {notifications.map(n => (
        <ToastItem key={n.id} notification={n} dispatch={dispatch} />
      ))}
    </div>
  );
};

const ToastItem: React.FC<{ notification: Notification; dispatch: React.Dispatch<CadAction> }> = ({ notification, dispatch }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      dispatch({ type: 'REMOVE_NOTIFICATION', id: notification.id });
    }, 4000);
    return () => clearTimeout(timer);
  }, [notification.id, dispatch]);

  const bg = {
    success: '#4caf50',
    error: '#f44336',
    info: '#2196f3'
  }[notification.type];

  const Icon = {
    success: CheckCircle,
    error: AlertCircle,
    info: Info
  }[notification.type];

  return (
    <div style={{
      background: bg,
      color: 'white',
      padding: '12px 16px',
      borderRadius: '8px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      minWidth: '250px',
      animation: 'slideIn 0.3s ease-out'
    }}>
      <Icon size={20} />
      <div style={{ flex: 1, fontSize: '14px' }}>{notification.message}</div>
      <button 
        onClick={() => dispatch({ type: 'REMOVE_NOTIFICATION', id: notification.id })}
        style={{ background: 'transparent', border: 'none', color: 'white', cursor: 'pointer', padding: 0, display: 'flex' }}
      >
        <X size={16} />
      </button>
      <style>{`
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
};
