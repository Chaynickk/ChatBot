import React from 'react';
import { ChatScreen } from './components/ChatScreen';
import { UserProvider } from './components/UserContext';
import { ChatsProvider } from './components/ChatsContext';
import { MessagesProvider } from './components/MessagesContext';
import { BackendUrlPrompt } from './components/BackendUrlPrompt';

function App() {
  return (
    <>
      <BackendUrlPrompt />
      <UserProvider>
        <ChatsProvider>
          <MessagesProvider>
            <ChatScreen />
          </MessagesProvider>
        </ChatsProvider>
      </UserProvider>
    </>
  );
}

export default App;
