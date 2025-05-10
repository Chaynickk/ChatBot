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
  const selectedModelId = Number(localStorage.getItem('selectedModelId')) || undefined;

  const loadMessages = async () => {
    if (!activeChatId) return;
    try {
      console.log('Загрузка сообщений для чата:', activeChatId);
      const res = await fetch(`/messages/messages/?chat_id=${activeChatId}`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data);
        console.log('Сообщения успешно загружены:', data);
      } else {
        const errText = await res.text();
        console.error(`Ошибка при загрузке сообщений: ${res.status} ${errText}`);
      }
    } catch (e) {
      console.error('Ошибка при загрузке сообщений:', e);
    }
  };

  const sendMessage = async (content: string) => {
    let chatId = activeChatId;
    if (!chatId) {
      console.log('Чат не выбран, создаём новый чат перед отправкой сообщения...');
      chatId = await createChat(undefined, undefined, selectedModelId);
      if (!chatId) {
        console.error('Не удалось создать чат, сообщение не отправлено');
        return;
      }
    }
    const userMsg: SendMessageRequest = {
      chat_id: chatId,
      content,
      role: 'user',
      parent_id: 0,
    };
    setMessages(prev => [...prev, { ...userMsg, pending: true, created_at: new Date().toISOString() }]);
    try {
      console.log('Отправка сообщения:', userMsg);
      await apiService.sendMessageToBackend(userMsg, (event: MessageStreamEvent) => {
        if (event.type === 'user_message') {
          setMessages(prev => prev.map((m, i) => i === prev.length - 1 ? { ...event.data, role: 'user' } : m));
          console.log('user_message event:', event.data);
        } else if (event.type === 'chunk') {
          setMessages(prev => {
            if (prev.length && prev[prev.length - 1].role === 'assistant') {
              return prev.map((m, i) => i === prev.length - 1 ? { ...m, content: (m.content || '') + event.data } : m);
            } else {
              return [...prev, { role: 'assistant', content: event.data, created_at: new Date().toISOString() }];
            }
          });
          // Можно логировать чанки, если нужно
        } else if (event.type === 'assistant_message') {
          setMessages(prev => prev.map((m, i) =>
            i === prev.length - 1 && m.role === 'assistant' ? { ...event.data, role: 'assistant' } : m
          ));
          console.log('assistant_message event:', event.data);
        }
      });
      console.log('Сообщение успешно отправлено');
    } catch (e) {
      console.error('Ошибка при отправке сообщения:', e);
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