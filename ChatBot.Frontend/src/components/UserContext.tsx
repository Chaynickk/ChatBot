import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { API_BASE_URL } from '../services/api';

interface User {
  telegram_id: number;
  username: string;
  full_name: string;
  is_plus: boolean;
}

interface UserContextType {
  user: User | null;
  initData: string | null;
  login: (initData: string) => Promise<void>;
  logout: () => void;
  backendAvailable: boolean;
  offlineMessage: string | null;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const useUser = () => {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error('useUser must be used within UserProvider');
  return ctx;
};

export const UserProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [initData, setInitData] = useState<string | null>(null);
  const [backendAvailable, setBackendAvailable] = useState(true);
  const [offlineMessage, setOfflineMessage] = useState<string | null>(null);

  // Проверка доступности бэкенда
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/ping`);
        if (!res.ok) throw new Error();
        setBackendAvailable(true);
        setOfflineMessage(null);
      } catch {
        setBackendAvailable(false);
        setOfflineMessage('Бэкенд недоступен. Включён офлайн-режим.');
        // Fallback: временный пользователь
        setUser({
          telegram_id: 1,
          username: 'local',
          full_name: 'Local User',
          is_plus: false,
        });
      }
    })();
  }, []);

  // login: проверяет или регистрирует пользователя
  const login = async (initData: string) => {
    setInitData(initData);
    try {
      const res = await fetch(`/users/users/?init_data=${encodeURIComponent(initData)}`);
      if (res.ok) {
        const data = await res.json();
        setUser(data);
      } else {
        const regRes = await fetch(`/users/users/?init_data=${encodeURIComponent(initData)}`, { method: 'POST' });
        if (regRes.ok) {
          const data = await regRes.json();
          setUser(data);
        } else {
          setUser(null);
        }
      }
    } catch {
      setUser({
        telegram_id: 1,
        username: 'local',
        full_name: 'Local User',
        is_plus: false,
      });
      setOfflineMessage('Бэкенд недоступен. Включён офлайн-режим.');
      setBackendAvailable(false);
    }
  };

  const logout = () => {
    setUser(null);
    setInitData(null);
  };

  return (
    <UserContext.Provider value={{ user, initData, login, logout, backendAvailable, offlineMessage }}>
      {children}
    </UserContext.Provider>
  );
}; 