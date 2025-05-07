import React, { createContext, useContext, useState, ReactNode } from 'react';
import { useUser } from './UserContext';

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
  createChat: (title?: string, project_id?: number) => Promise<number | null>;
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

  const loadChats = async () => {
    if (!user) return;
    const res = await fetch(`/api/chats/?telegram_id=${user.telegram_id}`);
    if (res.ok) {
      const data = await res.json();
      setChats(data);
    }
  };

  const createChat = async (title?: string, project_id?: number) => {
    if (!user) {
      // Fallback: временный чат для офлайн-режима
      setChats(prev => [{ id: 1, title: title || 'Локальный чат' }, ...prev]);
      setActiveChatId(1);
      return 1;
    }
    const body: any = { user_id: user.telegram_id };
    if (title) body.title = title;
    if (project_id) body.project_id = project_id;
    const res = await fetch('/api/chats/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (res.ok) {
      const chat = await res.json();
      setChats(prev => [chat, ...prev]);
      setActiveChatId(chat.id);
      return chat.id;
    }
    return null;
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