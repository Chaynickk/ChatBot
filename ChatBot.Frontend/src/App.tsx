// import React from 'react';
import { ChatScreen } from './components/ChatScreen';
import { UserProvider } from './components/UserContext';
import { ChatsProvider } from './components/ChatsContext';
import { MessagesProvider } from './components/MessagesContext';
import { API_BASE_URL } from './services/api';
import { useEffect, useState } from 'react';
import { apiService, UserResponse } from './services/api';

console.log('API_URL:', API_BASE_URL);

function App() {
  const [isTelegramWebApp, setIsTelegramWebApp] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [timerWidth, setTimerWidth] = useState(100);

  useEffect(() => {
    // Проверяем, запущено ли приложение в Telegram Mini App
    const webApp = window.Telegram?.WebApp;
    const isTelegram = webApp !== undefined && webApp.initData !== undefined;
    setIsTelegramWebApp(isTelegram);

    if (!isTelegram) {
      window.location.href = 'https://t.me/chatlux_bot?startapp=start';
      return;
    }

    const initData = webApp.initData;
    if (!initData) {
      setNotification({ type: 'error', message: 'Не удалось получить данные пользователя из Telegram.' });
      return;
    }

    const processUser = async () => {
      try {
        // Пробуем получить пользователя по initData
        const user: UserResponse | undefined | null = await apiService.getUserByInitData(initData);
        if (user !== undefined && user !== null && (user.telegram_id || user.id)) {
          const userKey = user.telegram_id ? user.telegram_id.toString() : user.id!.toString();
          localStorage.setItem('userId', userKey);
          let userInfo = '';
          if (user.full_name) userInfo = `: ${user.full_name}`;
          else if (user.username) userInfo = `: @${user.username}`;
          setNotification({ type: 'success', message: `Авторизация успешна${userInfo}` });
        } else {
          setNotification({ type: 'error', message: 'Ошибка авторизации: пользователь не найден.' });
        }
      } catch (err: any) {
        if (err.status === 404) {
          // Если не найден — регистрируем
          try {
            const newUser: UserResponse | undefined | null = await apiService.registerUserByInitData(initData);
            if (newUser !== undefined && newUser !== null && (newUser.telegram_id || newUser.id)) {
              const userKey = newUser.telegram_id ? newUser.telegram_id.toString() : newUser.id!.toString();
              localStorage.setItem('userId', userKey);
              setNotification({ type: 'success', message: 'Регистрация успешна' });
            } else {
              setNotification({ type: 'error', message: 'Ошибка регистрации: пользователь не создан.' });
            }
          } catch (regErr: any) {
            setNotification({ type: 'error', message: 'Ошибка при регистрации пользователя.' });
          }
        } else {
          setNotification({ type: 'error', message: 'Ошибка при обращении к серверу.' });
        }
      }
    };
    processUser();
  }, []);

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
    <UserProvider>
      <ChatsProvider>
        <MessagesProvider>
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
        </MessagesProvider>
      </ChatsProvider>
    </UserProvider>
  );
}

export default App;
