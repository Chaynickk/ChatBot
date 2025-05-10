// import React from 'react';
import { ChatScreen } from './components/ChatScreen';
import { UserProvider } from './components/UserContext';
import { ChatsProvider } from './components/ChatsContext';
import { MessagesProvider } from './components/MessagesContext';
import { API_BASE_URL } from './services/api';
import { useEffect, useState } from 'react';
import { apiService } from './services/api';

console.log('API_URL:', API_BASE_URL);

function App() {
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    const initUser = async () => {
      const initData = apiService.getInitData();
      if (initData.user?.id) {
        const telegramId = initData.user.id;
        try {
          const userData = await apiService.createUser(telegramId);
          const newUserId = userData.id.toString();
          localStorage.setItem('userId', newUserId);
          setUserId(newUserId);
        } catch (error) {
          console.error('Ошибка при инициализации пользователя:', error);
        }
      }
    };
    initUser();
  }, []);

  return (
    <UserProvider>
      <ChatsProvider>
        <MessagesProvider>
          <div>
            <h1>Telegram Mini App</h1>
            {userId && <p>User ID: {userId}</p>}
            <ChatScreen />
          </div>
        </MessagesProvider>
      </ChatsProvider>
    </UserProvider>
  );
}

export default App;
