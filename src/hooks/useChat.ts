import { useState, useCallback } from 'react';
import { chatService } from '../services/chatService';

interface Message {
  id: number;
  content: string;
  role: string;
  created_at: string;
}

interface UseChatReturn {
  sendMessage: (message: string, telegramId: number) => Promise<void>;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (message: string, telegramId: number) => {
    setIsLoading(true);
    setError(null);

    try {
      // Получаем выбранную модель из localStorage
      const selectedModelId = Number(localStorage.getItem('selectedModelId')) || undefined;

      // Создаем сообщение пользователя
      const userMessage: Message = {
        id: Date.now(),
        content: message,
        role: 'user',
        created_at: new Date().toISOString()
      };

      // Добавляем сообщение пользователя в состояние
      setMessages(prev => [...prev, userMessage]);

      // Отправляем сообщение и получаем ответ
      const responseStream = await chatService.sendMessage(message, telegramId, selectedModelId);
      
      // Обрабатываем стриминг ответа
      let assistantMessage: Message | null = null;
      
      for await (const chunk of responseStream) {
        if (!assistantMessage) {
          // Создаем первое сообщение ассистента
          assistantMessage = {
            id: Date.now() + 1,
            content: chunk.content,
            role: 'assistant',
            created_at: new Date().toISOString()
          };
          setMessages(prev => [...prev, assistantMessage!]);
        } else {
          // Обновляем существующее сообщение ассистента
          setMessages(prev => {
            const lastMessage = prev[prev.length - 1];
            if (lastMessage.role === 'assistant') {
              return [
                ...prev.slice(0, -1),
                { ...lastMessage, content: chunk.content }
              ];
            }
            return prev;
          });
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка при отправке сообщения');
      console.error('Error in sendMessage:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    sendMessage,
    messages,
    isLoading,
    error
  };
} 