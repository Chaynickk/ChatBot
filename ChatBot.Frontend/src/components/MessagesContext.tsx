import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { useChats } from './ChatsContext';
import { useUser } from './UserContext';
import { apiService, API_BASE_URL, checkServerAvailability } from '../services/api';

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
      const res = await fetch(`${API_BASE_URL}/messages/?chat_id=${activeChatId}`);
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

    // Добавляем сообщение с пульсирующей точкой
    setMessages(prev => [
      ...prev,
      {
        id: tempBotMsgId,
        role: 'assistant',
        content: '',
        isThinking: true,
        created_at: new Date().toISOString(),
      }
    ]);

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
        const errorMessage = e instanceof Error ? e.message : 'Неизвестная ошибка при создании чата';
        setMessages(prev => [
          ...prev.filter(msg => msg.id !== tempBotMsgId), // Удаляем сообщение с пульсирующей точкой
          {
            role: 'assistant',
            content: `Ошибка создания чата: ${errorMessage}. Пожалуйста, убедитесь, что вы авторизованы в Telegram.`,
            created_at: new Date().toISOString(),
            id: tempUserId + 2
          }
        ]);
        return;
      }
    }

    if (!chatId) {
      setMessages(prev => [
        ...prev.filter(msg => msg.id !== tempBotMsgId), // Удаляем сообщение с пульсирующей точкой
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

    try {
      // Проверяем доступность сервера
      const isServerAvailable = await checkServerAvailability();
      if (!isServerAvailable) {
        throw new Error('Сервер недоступен. Пожалуйста, проверьте подключение к интернету.');
      }

      const requestBody = {
        chat_id: Number(chatId),
        content: content
      };

      console.log('Отправка запроса на:', `${API_BASE_URL}/messages/`);
      console.log('Данные запроса:', requestBody);
      
      const response = await fetch(`${API_BASE_URL}/messages/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Telegram ${user?.telegram_id}`
        },
        body: JSON.stringify(requestBody)
      });
      
      console.log('Статус ответа:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Ошибка ответа сервера:', {
          status: response.status,
          statusText: response.statusText,
          errorText,
          requestBody
        });
        throw new Error(`Ошибка сервера: ${response.status} ${response.statusText} - ${errorText}`);
      }
      
      if (!response.body) throw new Error('Нет потока данных');
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let botText = '';
      let firstChunk = true;
      let done = false;
      
      // Добавляем отладочное сообщение
      setMessages(prev => [
        ...prev,
        {
          id: tempBotMsgId + 1,
          role: 'system',
          content: 'Начало получения ответа...',
          created_at: new Date().toISOString(),
        }
      ]);
      
      while (!done) {
        const { value, done: streamDone } = await reader.read();
        done = streamDone;
        const chunk = decoder.decode(value || new Uint8Array(), { stream: true });
        
        // Добавляем отладочное сообщение о получении чанка
        setMessages(prev => [
          ...prev,
          {
            id: Date.now(),
            role: 'system',
            content: `Получен чанк: ${chunk}`,
            created_at: new Date().toISOString(),
          }
        ]);
        
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.trim()) {
            try {
              const json = JSON.parse(line);
              
              // Добавляем отладочное сообщение о распарсенном JSON
              setMessages(prev => [
                ...prev,
                {
                  id: Date.now(),
                  role: 'system',
                  content: `Распарсенный JSON: ${JSON.stringify(json)}`,
                  created_at: new Date().toISOString(),
                }
              ]);
              
              if (json.response) {
                if (firstChunk) {
                  botText = json.response;
                  // Добавляем отладочное сообщение о первом чанке
                  setMessages(prev => [
                    ...prev,
                    {
                      id: Date.now(),
                      role: 'system',
                      content: 'Первый чанк получен, создаем новое сообщение',
                      created_at: new Date().toISOString(),
                    }
                  ]);
                  
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
                  botText += json.response;
                  // Добавляем отладочное сообщение о последующих чанках
                  setMessages(prev => [
                    ...prev,
                    {
                      id: Date.now(),
                      role: 'system',
                      content: `Добавлен чанк к сообщению: ${json.response}`,
                      created_at: new Date().toISOString(),
                    }
                  ]);
                  
                  setMessages(prev =>
                    prev.map(msg =>
                      msg.id === tempBotMsgId
                        ? { ...msg, content: botText, isThinking: false }
                        : msg
                    )
                  );
                }
              } else {
                // Добавляем сообщение о чанке без поля response
                setMessages(prev => [
                  ...prev,
                  {
                    id: Date.now(),
                    role: 'system',
                    content: `Получен чанк без поля response: ${JSON.stringify(json)}`,
                    created_at: new Date().toISOString(),
                  }
                ]);
              }
            } catch (e) {
              setMessages(prev => [
                ...prev,
                {
                  id: Date.now(),
                  role: 'system',
                  content: `Ошибка парсинга JSON: ${line}`,
                  created_at: new Date().toISOString(),
                }
              ]);
            }
          }
        }
      }
      
      // Финальное обновление сообщения
      setMessages(prev => {
        const updated = prev.map(msg =>
          msg.id === tempBotMsgId
            ? { ...msg, content: botText, isThinking: false }
            : msg
        );
        
        // Добавляем сообщение о завершении
        if (botText) {
          updated.push({
            id: Date.now(),
            role: 'system',
            content: 'Ответ получен полностью',
            created_at: new Date().toISOString(),
          });
        }
        
        return updated;
      });
    } catch (e) {
      console.error('Полная ошибка при отправке сообщения:', e);
      const errorMessage = e instanceof Error ? e.message : 'Неизвестная ошибка';
      setMessages(prev => [
        ...prev.filter(msg => msg.id !== tempBotMsgId),
        {
          role: 'assistant',
          content: `Извините, произошла ошибка при отправке сообщения: ${errorMessage}. Пожалуйста, попробуйте еще раз.`,
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