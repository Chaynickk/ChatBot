import React, { createContext, useContext, useState, ReactNode } from 'react';
import { useUser } from './UserContext';
import { apiService, API_BASE_URL } from '../services/api';

export interface Chat {
  id: number;
  title: string;
  project_id?: number;
  created_at?: string;
  updated_at?: string;
}

interface ChatsContextType {
  chats: Chat[];
  activeChatId: number | null;
  loadChats: () => Promise<void>;
  createChat: (title?: string, project_id?: number, model_id?: number) => Promise<number | null>;
  selectChat: (id: number | null) => void;
}

const ChatsContext = createContext<ChatsContextType | undefined>(undefined);

export const useChats = () => {
  const ctx = useContext(ChatsContext);
  if (!ctx) throw new Error('useChats must be used within ChatsProvider');
  return ctx;
};

interface ChatsProviderProps {
  children: ReactNode;
  onNotification?: (notification: { type: 'success' | 'error'; message: string } | null) => void;
}

export const ChatsProvider: React.FC<ChatsProviderProps> = ({ children, onNotification }) => {
  const { user } = useUser();
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatId, setActiveChatId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const loadChats = async () => {
    if (!user || isLoading) return;
    try {
      setIsLoading(true);
      const res = await fetch(`${API_BASE_URL}/api/chats/?telegram_id=${user.telegram_id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
    });
      
    if (res.ok) {
      const data = await res.json();
      setChats(data);
        onNotification?.({
          type: 'success',
          message: 'Список чатов успешно загружен'
        });
      } else {
        const errorData = await res.json().catch(() => ({}));
        console.error('Ошибка при загрузке чатов:', errorData);
        onNotification?.({
          type: 'error',
          message: `Ошибка при загрузке чатов: ${res.status} ${res.statusText}`
        });
      }
    } catch (error) {
      console.error('Ошибка при загрузке чатов:', error);
      onNotification?.({
        type: 'error',
        message: 'Ошибка при загрузке чатов. Пожалуйста, попробуйте позже.'
      });
    } finally {
      setIsLoading(false);
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
      onNotification?.({
        type: 'success',
        message: 'Чат успешно создан'
      });
      console.log('Чат успешно создан:', chat);
      return chat.id;
    } catch (e) {
      console.error('Ошибка при создании чата:', e);
      onNotification?.({
        type: 'error',
        message: 'Ошибка при создании чата. Пожалуйста, попробуйте позже.'
      });
      return null;
    }
  };

  const selectChat = (id: number | null) => {
    setActiveChatId(id);
  };

  return (
    <ChatsContext.Provider value={{ chats, activeChatId, loadChats, createChat, selectChat }}>
      {children}
    </ChatsContext.Provider>
  );
}; 