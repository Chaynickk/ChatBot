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
    console.log('Начало процесса авторизации');
    setInitData(initData);
    localStorage.setItem('initData', initData);
    try {
      console.log('Попытка получить пользователя по initData');
      const user = await apiService.getUserByInitData(initData);
      if (user && (user.telegram_id || user.id)) {
        console.log('Пользователь успешно получен:', user);
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
    } catch (error: any) {
      console.error('Ошибка при получении пользователя:', error);
      // Проверяем, что ошибка — именно отсутствие пользователя (404)
      if (error.status === 404) {
        try {
          console.log('Попытка зарегистрировать нового пользователя');
          const newUser = await apiService.registerUserByInitData(initData);
          if (newUser && (newUser.telegram_id || newUser.id)) {
            console.log('Новый пользователь успешно зарегистрирован:', newUser);
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
        } catch (regError: any) {
          console.error('Ошибка при регистрации пользователя:', regError);
          const errorMessage = regError.status 
            ? `Ошибка авторизации (${regError.status}): ${regError.statusText}`
            : 'Ошибка авторизации: Не удалось зарегистрировать пользователя';
          setUser(null);
          setOfflineMessage(errorMessage);
          setBackendAvailable(false);
          onNotification({
            type: 'error',
            message: errorMessage
          });
          throw regError;
        }
      }
      // Любая другая ошибка — показываем ошибку авторизации
      const errorMessage = error.status 
        ? `Ошибка авторизации (${error.status}): ${error.statusText}`
        : 'Ошибка авторизации: Не удалось получить данные пользователя';
      setUser(null);
      setOfflineMessage(errorMessage);
      setBackendAvailable(false);
      onNotification({
        type: 'error',
        message: errorMessage
      });
      throw error;
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
    }}>
      {children}
    </UserContext.Provider>
  );
}; 