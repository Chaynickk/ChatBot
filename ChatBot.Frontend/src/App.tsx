// import React from 'react';
import { ChatScreen } from './components/ChatScreen';
import { UserProvider, useUser } from './components/UserContext';
import { ChatsProvider, useChats } from './components/ChatsContext';
import { MessagesProvider } from './components/MessagesContext';
import { API_BASE_URL } from './services/api';
import { useEffect, useState } from 'react';

console.log('API_URL:', API_BASE_URL);

// Основной компонент App
export const App: React.FC = () => {
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [timerWidth, setTimerWidth] = useState(100);

  // Таймер для уведомления
  useEffect(() => {
    if (notification) {
      setTimerWidth(100);
      const start = Date.now();
      const duration = 5000;
      let frame: number;
      const animate = () => {
        const elapsed = Date.now() - start;
        const percent = Math.max(0, 100 - (elapsed / duration) * 100);
        setTimerWidth(percent);
        if (elapsed < duration) {
          frame = requestAnimationFrame(animate);
        } else {
          setNotification(null);
        }
      };
      frame = requestAnimationFrame(animate);
      return () => cancelAnimationFrame(frame);
    }
  }, [notification]);

  const handleNotification = (notification: { type: 'success' | 'error'; message: string } | null) => {
    setNotification(notification);
    if (notification) {
      setTimeout(() => setNotification(null), 2000); // Уменьшаем время до 2 секунд
    }
  };

  // Функция для загрузки чатов
  const loadChats = () => {
    const chats = useChats();
    if (chats.loadChats) {
      chats.loadChats();
    }
  };

  return (
    <UserProvider onNotification={handleNotification} onChatsLoad={loadChats}>
      <ChatsProvider onNotification={handleNotification}>
        <MessagesProvider>
          <AppContent notification={notification} timerWidth={timerWidth} />
        </MessagesProvider>
      </ChatsProvider>
    </UserProvider>
  );
};

// Создаем отдельный компонент для инициализации
interface AppContentProps {
  notification: { type: 'success' | 'error'; message: string } | null;
  timerWidth: number;
}

const AppContent: React.FC<AppContentProps> = ({ notification, timerWidth }) => {
  const [isTelegramWebApp, setIsTelegramWebApp] = useState(false);
  const { login } = useUser();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Проверяем, запущено ли приложение в Telegram Mini App
    const webApp = window.Telegram?.WebApp;
    const isTelegram = webApp !== undefined && webApp.initData !== undefined;
    setIsTelegramWebApp(isTelegram);

    if (!isTelegram) {
      window.location.href = 'https://t.me/chatlux_bot?startapp=start';
      return;
    }

    // Сохраняем InitData и выполняем авторизацию только один раз
    if (!isInitialized && webApp.initData) {
      setIsInitialized(true);
      localStorage.setItem('initData', webApp.initData);
      login(webApp.initData).catch(error => {
        console.error('Ошибка при авторизации:', error);
      });
    }
  }, [login, isInitialized]);

  if (!isTelegramWebApp) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h1>ChatLUX</h1>
        <p>Это приложение доступно только через Telegram Mini App.</p>
        <p>Перенаправление на бота...</p>
      </div>
    );
  }

  return (
    <div>
      <h1>ChatLUX</h1>
      {notification && (
        <div style={{
          position: 'fixed',
          top: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          background: notification.type === 'success' ? '#23242a' : '#e74c3c',
          color: 'white',
          padding: '14px 28px 18px 22px',
          borderRadius: '10px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          minWidth: 220,
          fontSize: 18,
          fontWeight: 500,
          flexDirection: 'column',
        }}>
          <div style={{display: 'flex', alignItems: 'center', gap: 10}}>
            {notification.type === 'success' && (
              <span style={{fontSize: 22, color: '#fff', background: '#2ecc40', borderRadius: '50%', width: 28, height: 28, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                <svg width="18" height="18" viewBox="0 0 20 20" fill="none"><path d="M5 10.5L9 14.5L15 7.5" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              </span>
            )}
            <span>{notification.message}</span>
          </div>
          <div style={{width: '100%', height: 4, background: 'rgba(255,255,255,0.18)', borderRadius: 2, marginTop: 8, overflow: 'hidden'}}>
            <div style={{height: '100%', width: `${timerWidth}%`, background: notification.type === 'success' ? '#2ecc40' : '#fff', borderRadius: 2, transition: 'width 0.1s linear'}} />
          </div>
        </div>
      )}
      <ChatScreen />
    </div>
  );
};
