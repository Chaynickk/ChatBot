import React, { createContext, useContext, useState, ReactNode } from 'react';
import { useUser } from './UserContext';
import { apiService } from '../services/api';

export interface Chat {
  id: number;
  title: string;
  project_id?: number;
  // другие поля по необходимости
}

interface ChatsContextType {
  chats: Chat[];
  activeChatId: number | null;
  loadChats: () => Promise<void>;
  createChat: (title?: string, project_id?: number, model_id?: number) => Promise<number | null>;
  selectChat: (id: number) => void;
}

const ChatsContext = createContext<ChatsContextType | undefined>(undefined);

export const useChats = () => {
  const ctx = useContext(ChatsContext);
  if (!ctx) throw new Error('useChats must be used within ChatsProvider');
  return ctx;
};

export const ChatsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { user } = useUser();
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatId, setActiveChatId] = useState<number | null>(null);

  const AUTH_HEADER = "Basic 141.101.142.1";

  const loadChats = async () => {
    if (!user) return;
    const res = await fetch(`/api/chats/?telegram_id=${user.telegram_id}`, {
      headers: { 'Authorization': AUTH_HEADER }
    });
    if (res.ok) {
      const data = await res.json();
      setChats(data);
    }
  };

  const createChat = async (title?: string, project_id?: number, model_id?: number) => {
    if (!user) {
      // Fallback: временный чат для оффлайн-режима
      setChats(prev => [{ id: 1, title: title || 'Локальный чат', model_id }, ...prev]);
      setActiveChatId(1);
      console.log('Создан локальный чат (оффлайн-режим)');
      return 1;
    }
    try {
      const chat = await apiService.createChat({
        user_id: Number(user.telegram_id),
        project_id,
        title: title || 'Новый чат',
        model_id: model_id || 1
      });
      setChats(prev => [chat, ...prev]);
      setActiveChatId(chat.id);
      console.log('Чат успешно создан:', chat);
      return chat.id;
    } catch (e) {
      console.error('Ошибка при создании чата:', e);
      return null;
    }
  };

  const selectChat = (id: number) => {
    setActiveChatId(id);
  };

  return (
    <ChatsContext.Provider value={{ chats, activeChatId, loadChats, createChat, selectChat }}>
      {children}
    </ChatsContext.Provider>
  );
}; 