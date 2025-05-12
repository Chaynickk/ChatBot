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
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
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
    console.log('Загрузка сообщений для чата:', activeChatId);
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
    const tempBotMsgId = tempUserId + 1;
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
        if (!chatId) throw new Error('Не удалось создать новый чат');
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

    if (!chatId) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Ошибка: не удалось получить chat_id для отправки сообщения.',
          created_at: new Date().toISOString(),
          id: tempUserId + 5
        }
      ]);
      return;
    }

    console.log('Отправка сообщения:', { chatId, content });

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
      if (!response.body) throw new Error('Нет потока данных');
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let botText = '';
      let firstChunk = true;
      let done = false;
      while (!done) {
        const { value, done: streamDone } = await reader.read();
        done = streamDone;
        const chunk = decoder.decode(value || new Uint8Array(), { stream: true });
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.startsWith('data:')) {
            try {
              const json = JSON.parse(line.slice(5));
              if (json.type === 'chunk' && json.data) {
                if (firstChunk) {
                  // Удаляем точку (isThinking) и создаём новое сообщение ассистента с первым текстом
                  botText += json.data;
                  setMessages(prev => [
                    ...prev.filter(msg => msg.id !== tempBotMsgId),
                    {
                      id: tempBotMsgId,
                      role: 'assistant',
                      content: botText,
                      isThinking: false,
                      created_at: new Date().toISOString(),
                    }
                  ]);
                  firstChunk = false;
                } else {
                  botText += json.data;
                  setMessages(prev =>
                    prev.map(msg =>
                      msg.id === tempBotMsgId
                        ? { ...msg, content: botText }
                        : msg
                    )
                  );
                }
              }
              if (json.type === 'assistant_message' && json.data) {
                // Финальное сообщение ассистента (можно обновить, если нужно)
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === tempBotMsgId
                      ? { ...msg, content: json.data.content, isThinking: false }
                      : msg
                  )
                );
              }
            } catch (e) {
              // ignore parse errors
            }
          }
        }
      }
      // На всякий случай убираем isThinking
      setMessages(prev =>
        prev.map(msg =>
          msg.id === tempBotMsgId
            ? { ...msg, isThinking: false }
            : msg
        )
      );
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
    <MessagesContext.Provider value={{ messages, loadMessages, sendMessage, setMessages }}>
      {children}
    </MessagesContext.Provider>
  );
}; 