import { ChatScreen } from './components/ChatScreen';
import { UserProvider } from './components/UserContext';
import { ChatsProvider } from './components/ChatsContext';
import { MessagesProvider } from './components/MessagesContext';

function App() {
  return (
    <UserProvider>
      <ChatsProvider>
        <MessagesProvider>
          <ChatScreen />
        </MessagesProvider>
      </ChatsProvider>
    </UserProvider>
  );
}

export default App;
