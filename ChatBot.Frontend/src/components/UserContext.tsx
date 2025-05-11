import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { API_BASE_URL, apiService } from '../services/api';

interface User {
  telegram_id: string;
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
  isLoading: boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const useUser = () => {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error('useUser must be used within UserProvider');
  return ctx;
};

interface UserProviderProps {
  children: ReactNode;
  onNotification: (notification: { type: 'success' | 'error'; message: string } | null) => void;
}

export const UserProvider: React.FC<UserProviderProps> = ({ children, onNotification }) => {
  const [user, setUser] = useState<User | null>(null);
  const [initData, setInitData] = useState<string | null>(null);
  const [backendAvailable, setBackendAvailable] = useState(true);
  const [offlineMessage, setOfflineMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoginInProgress, setIsLoginInProgress] = useState(false);

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
          telegram_id: '1',
          username: 'local',
          full_name: 'Local User',
          is_plus: false,
        });
      }
    })();
  }, []);

  // login: проверяет или регистрирует пользователя
  const login = async (initData: string) => {
    // Защита от повторных вызовов
    if (isLoginInProgress) {
      console.log('Авторизация уже выполняется...');
      return;
    }

    try {
      setIsLoginInProgress(true);
      setIsLoading(true);
      setInitData(initData);
      localStorage.setItem('initData', initData);
      
      // Сначала пробуем получить пользователя
      const user = await apiService.getUserByInitData(initData);
      if (user && (user.telegram_id || user.id)) {
        setUser(user as User);
        if (user.telegram_id) {
          localStorage.setItem('user_id', user.telegram_id);
        }
        onNotification({
          type: 'success',
          message: 'Авторизация успешно выполнена'
        });
        return;
      }

      // Если пользователь не найден, регистрируем его
      const newUser = await apiService.registerUserByInitData(initData);
      if (newUser && (newUser.telegram_id || newUser.id)) {
        setUser(newUser as User);
        if (newUser.telegram_id) {
          localStorage.setItem('user_id', newUser.telegram_id);
        }
        onNotification({
          type: 'success',
          message: 'Регистрация успешно выполнена'
        });
        return;
      }

      throw new Error('Не удалось получить или создать пользователя');
    } catch (error) {
      console.error('Ошибка при авторизации:', error);
      setUser(null);
      setOfflineMessage('Ошибка авторизации. Пожалуйста, попробуйте перезагрузить страницу.');
      setBackendAvailable(false);
      onNotification({
        type: 'error',
        message: 'Ошибка авторизации. Пожалуйста, попробуйте перезагрузить страницу.'
      });
      throw error;
    } finally {
      setIsLoading(false);
      setIsLoginInProgress(false);
    }
  };

  const logout = () => {
    setUser(null);
    setInitData(null);
    localStorage.removeItem('initData');
    localStorage.removeItem('user_id');
  };

  return (
    <UserContext.Provider value={{ 
      user, 
      initData, 
      login, 
      logout, 
      backendAvailable, 
      offlineMessage,
      isLoading
    }}>
      {children}
    </UserContext.Provider>
  );
}; 