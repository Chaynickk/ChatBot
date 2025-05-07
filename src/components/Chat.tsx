import React, { useState, useEffect, useRef } from 'react';
import { useChat } from '../hooks/useChat';

interface ChatProps {
  telegramId: number;
}

const suggestions = [
  "Расскажи о своих возможностях",
  "Как начать работу?",
  "Покажи примеры использования",
  "Какие модели ты поддерживаешь?"
];

export const Chat: React.FC<ChatProps> = ({ telegramId }) => {
  const [inputMessage, setInputMessage] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [selectedSuggestion, setSelectedSuggestion] = useState<number | null>(null);
  const { sendMessage, messages, isLoading, error } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Автопрокрутка к последнему сообщению
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Скрываем подсказки после первого сообщения
  useEffect(() => {
    if (messages.length > 0) {
      setShowSuggestions(false);
    }
  }, [messages.length]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    try {
      await sendMessage(inputMessage, telegramId);
      setInputMessage('');
      setSelectedSuggestion(null);
    } catch (err) {
      console.error('Error sending message:', err);
    }
  };

  const handleSuggestionClick = (suggestion: string, index: number) => {
    setInputMessage(suggestion);
    setSelectedSuggestion(index);
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Сообщения */}
      <div className="flex-1 overflow-y-auto">
        {/* Подсказки */}
        {showSuggestions && (
          <div className="transition-all duration-500 ease-in-out transform hover:scale-[1.02] p-4">
            <div className="text-center text-gray-500 mb-4 text-lg font-medium">
              Чем я могу помочь?
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion, index)}
                  className={`p-4 rounded-lg transition-all duration-300 text-left
                    ${selectedSuggestion === index 
                      ? 'bg-blue-50 border-2 border-blue-500 text-blue-700' 
                      : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                    }`}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Сообщения чата */}
        <div className="max-w-3xl mx-auto w-full">
          {messages.map((message, index) => (
            <div
              key={message.id}
              className={`group flex items-start gap-4 p-4 hover:bg-gray-50/50 transition-colors
                ${message.role === 'user' ? 'bg-white' : 'bg-gray-50/50'}`}
            >
              {/* Аватар */}
              <div className="w-8 h-8 rounded-full flex-shrink-0 overflow-hidden">
                {message.role === 'user' ? (
                  <div className="w-full h-full bg-blue-500 flex items-center justify-center text-white font-medium">
                    U
                  </div>
                ) : (
                  <div className="w-full h-full bg-green-500 flex items-center justify-center text-white font-medium">
                    AI
                  </div>
                )}
              </div>

              {/* Контент сообщения */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium text-sm">
                    {message.role === 'user' ? 'Вы' : 'Ассистент'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(message.created_at).toLocaleTimeString()}
                  </span>
                </div>
                <div className="prose prose-sm max-w-none">
                  <p className="whitespace-pre-wrap text-gray-800">
                    {message.content}
                  </p>
                </div>
              </div>
            </div>
          ))}

          {/* Индикатор загрузки */}
          {isLoading && (
            <div className="flex items-start gap-4 p-4 bg-gray-50/50">
              <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white font-medium flex-shrink-0">
                AI
              </div>
              <div className="flex-1">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          )}

          {/* Ошибка */}
          {error && (
            <div className="mx-4 my-2 p-3 bg-red-50 text-red-500 rounded-lg animate-shake">
              {error}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Форма отправки */}
      <div className="border-t bg-white">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Введите сообщение..."
              className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm transition-all duration-300 hover:shadow-md"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !inputMessage.trim()}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-sm hover:shadow-lg transform hover:scale-105"
            >
              Отправить
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}; 