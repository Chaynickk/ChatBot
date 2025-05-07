import React, { createContext, useContext, useState, ReactNode } from 'react';
import { useChats } from './ChatsContext';
import { apiService, MessageStreamEvent, SendMessageRequest } from '../services/api';

interface Message {
  id?: number;
  role: string;
  content: string;
  created_at?: string;
  // другие поля по необходимости
}

interface MessagesContextType {
  messages: Message[];
  loadMessages: () => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
}

const MessagesContext = createContext<MessagesContextType | undefined>(undefined);

export const useMessages = () => {
  const ctx = useContext(MessagesContext);
  if (!ctx) throw new Error('useMessages must be used within MessagesProvider');
  return ctx;
};

export const MessagesProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { activeChatId, createChat } = useChats();
  const [messages, setMessages] = useState<Message[]>([]);

  const loadMessages = async () => {
    if (!activeChatId) return;
    const res = await fetch(`/messages/messages/?chat_id=${activeChatId}`);
    if (res.ok) {
      const data = await res.json();
      setMessages(data);
    }
  };

  const sendMessage = async (content: string) => {
    let chatId = activeChatId;
    if (!chatId) {
      chatId = await createChat();
      if (!chatId) return;
    }
    const userMsg: SendMessageRequest = {
      chat_id: chatId,
      content,
      role: 'user',
      parent_id: 0,
    };
    setMessages(prev => [...prev, { ...userMsg, pending: true, created_at: new Date().toISOString() }]);
    try {
      await apiService.sendMessageToBackend(userMsg, (event: MessageStreamEvent) => {
        if (event.type === 'user_message') {
          setMessages(prev => prev.map((m, i) => i === prev.length - 1 ? { ...event.data, role: 'user' } : m));
        } else if (event.type === 'chunk') {
          setMessages(prev => {
            if (prev.length && prev[prev.length - 1].role === 'assistant') {
              return prev.map((m, i) => i === prev.length - 1 ? { ...m, content: (m.content || '') + event.data } : m);
            } else {
              return [...prev, { role: 'assistant', content: event.data, created_at: new Date().toISOString() }];
            }
          });
        } else if (event.type === 'assistant_message') {
          setMessages(prev => prev.map((m, i) =>
            i === prev.length - 1 && m.role === 'assistant' ? { ...event.data, role: 'assistant' } : m
          ));
        }
      });
    } catch (e) {
      // Заглушка если бэкенд не отвечает
      setMessages(prev => [
        ...prev.slice(0, -1),
        { ...userMsg, role: 'user', created_at: new Date().toISOString() },
        { role: 'assistant', content: 'Извините, сервер временно недоступен.', created_at: new Date().toISOString() }
      ]);
    }
  };

  return (
    <MessagesContext.Provider value={{ messages, loadMessages, sendMessage }}>
      {children}
    </MessagesContext.Provider>
  );
}; 