import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { useChats } from './ChatsContext';
import { useUser } from './UserContext';
import { apiService, API_BASE_URL } from '../services/api';

interface Message {
  id?: number;
  role: string;
  content: string;
  created_at?: string;
  isThinking?: boolean;
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
  const { activeChatId } = useChats();
  const { user } = useUser();
  const [messages, setMessages] = useState<Message[]>([]);
  const selectedModelId = Number(localStorage.getItem('selectedModelId')) || undefined;

  useEffect(() => {
    if (activeChatId) {
      loadMessages();
    } else {
      setMessages([]);
    }
  }, [activeChatId]);

  const loadMessages = async () => {
    if (!activeChatId) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/messages/?chat_id=${activeChatId}`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data);
      } else {
        const errText = await res.text();
        console.error(`Ошибка при загрузке сообщений: ${res.status} ${errText}`);
      }
    } catch (e) {
      console.error('Ошибка при загрузке сообщений:', e);
    }
  };

  const sendMessage = async (content: string) => {
    const tempUserId = Date.now();
    const userMessage = {
      id: tempUserId,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);

    let chatId = activeChatId;
    if (!chatId) {
      try {
        if (!user?.telegram_id) {
          throw new Error('Пользователь не авторизован');
        }
        const title = 'Новый чат';
        const model_id = selectedModelId || 1;
        chatId = await apiService.createChat({ 
          user_id: Number(user.telegram_id),
          title, 
          model_id 
        });
      } catch (e) {
        console.error('Ошибка создания чата:', e);
        setMessages(prev => [
          ...prev,
          {
            role: 'assistant',
            content: `Ошибка создания чата. Пожалуйста, убедитесь, что вы авторизованы в Telegram.`,
            created_at: new Date().toISOString(),
            id: tempUserId + 2
          }
        ]);
        return;
      }
    }

    const formData = new FormData();
    formData.append('chat_id', String(chatId));
    formData.append('content', content);

    try {
      const response = await fetch(`${API_BASE_URL}/messages/`, {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Telegram ${user?.telegram_id}`
        }
      });
      if (!response.ok) {
        throw new Error('Ошибка при отправке сообщения');
      }
      await loadMessages();
    } catch (e) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Извините, произошла ошибка при отправке сообщения. Пожалуйста, попробуйте еще раз.',
          created_at: new Date().toISOString(),
          id: tempUserId + 4
        }
      ]);
    }
  };

  return (
    <MessagesContext.Provider value={{ messages, loadMessages, sendMessage }}>
      {children}
    </MessagesContext.Provider>
  );
}; 