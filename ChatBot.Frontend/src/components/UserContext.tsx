import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

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

  // login: проверяет или регистрирует пользователя
  const login = async (initData: string) => {
    setInitData(initData);
    try {
      // Пробуем получить пользователя
      const res = await fetch(`/users/users/?init_data=${encodeURIComponent(initData)}`);
      if (res.ok) {
        const data = await res.json();
        setUser(data);
      } else {
        // Если не найден — пробуем зарегистрировать
        const regRes = await fetch(`/users/users/?init_data=${encodeURIComponent(initData)}`, { method: 'POST' });
        if (regRes.ok) {
          const data = await regRes.json();
          setUser(data);
        } else {
          setUser(null);
        }
      }
    } catch {
      setUser(null);
    }
  };

  const logout = () => {
    setUser(null);
    setInitData(null);
  };

  return (
    <UserContext.Provider value={{ user, initData, login, logout }}>
      {children}
    </UserContext.Provider>
  );
}; 