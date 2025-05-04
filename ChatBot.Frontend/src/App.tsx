import { useEffect } from 'react';

function App() {
  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    if (tg) {
      tg.ready(); // обязательно!
      console.log("initDataUnsafe", tg.initDataUnsafe);
    }
  }, []);  

  return (
    <div style={{ padding: 20 }}>
      <h1>Проверка Telegram WebApp</h1>
    </div>
  );
}

export default App;
