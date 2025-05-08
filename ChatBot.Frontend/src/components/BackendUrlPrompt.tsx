import React, { useState } from 'react';
import { setBackendUrl, getSavedBackendUrl } from '../services/api';

export const BackendUrlPrompt: React.FC = () => {
  const [input, setInput] = useState('');
  const [show, setShow] = useState(!getSavedBackendUrl());

  const handleSave = () => {
    if (input.trim()) {
      setBackendUrl(input.trim());
      setShow(false);
      window.location.reload(); // Перезагрузить страницу, чтобы все сервисы использовали новый URL
    }
  };

  if (!show) return null;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
      background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
    }}>
      <div style={{ background: '#fff', padding: 32, borderRadius: 8, minWidth: 320 }}>
        <h2>Введите ссылку на backend</h2>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="https://your-backend.loca.lt"
          style={{ width: '100%', marginBottom: 16, padding: 8 }}
        />
        <button onClick={handleSave} style={{ width: '100%', padding: 8 }}>Сохранить</button>
      </div>
    </div>
  );
}; 