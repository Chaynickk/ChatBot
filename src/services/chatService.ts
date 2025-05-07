import { BACKEND_URL } from '../config';

interface ChatCreate {
  user_id: number;
  project_id?: number;
  folder_id?: number;
  title?: string;
  model_id?: number;
  parent_chat_id?: number;
  parent_message_id?: number;
}

interface ChatOut extends ChatCreate {
  id: number;
  created_at: string;
}

interface MessageCreate {
  chat_id: number;
  content: string;
  role: "user" | "assistant" | "system";
  parent_id?: number;
}

interface MessageOut {
  id: number;
  chat_id: number;
  content: string;
  role: string;
  parent_id?: number;
  created_at: string;
}

class ChatService {
  private static instance: ChatService;
  private isBackendAvailable: boolean = false;
  private currentChatId: number | null = null;

  private constructor() {
    // Проверяем доступность бэкенда при инициализации
    this.checkBackendAvailability();
  }

  public static getInstance(): ChatService {
    if (!ChatService.instance) {
      ChatService.instance = new ChatService();
    }
    return ChatService.instance;
  }

  private async checkBackendAvailability(): Promise<void> {
    try {
      const response = await fetch(`${BACKEND_URL}/ping`);
      this.isBackendAvailable = response.ok;
    } catch (error) {
      this.isBackendAvailable = false;
      console.warn('Backend is not available, using fallback mode');
    }
  }

  private generateFallbackChatId(): number {
    return Date.now();
  }

  private generateFallbackMessageId(): number {
    return Date.now() + Math.floor(Math.random() * 1000);
  }

  async createChat(telegramId: number, title?: string): Promise<ChatOut> {
    if (!this.isBackendAvailable) {
      // Заглушка для оффлайн режима
      const fallbackChat: ChatOut = {
        id: this.generateFallbackChatId(),
        user_id: telegramId,
        title: title || 'Новый чат',
        created_at: new Date().toISOString()
      };
      this.currentChatId = fallbackChat.id;
      return fallbackChat;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/chats/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: telegramId,
          title: title || 'Новый чат'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const chat = await response.json();
      this.currentChatId = chat.id;
      return chat;
    } catch (error) {
      console.error('Error creating chat:', error);
      throw error;
    }
  }

  async sendMessage(message: string, telegramId: number): Promise<AsyncGenerator<MessageOut, void, unknown>> {
    if (!this.currentChatId) {
      // Если чат еще не создан, создаем его
      await this.createChat(telegramId);
    }

    if (!this.isBackendAvailable) {
      // Заглушка для оффлайн режима
      return this.generateFallbackResponse(message);
    }

    try {
      const response = await fetch(`${BACKEND_URL}/messages/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chat_id: this.currentChatId,
          content: message,
          role: "user"
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return this.handleStreamingResponse(response);
    } catch (error) {
      console.error('Error sending message:', error);
      return this.generateFallbackResponse(message);
    }
  }

  private async *handleStreamingResponse(response: Response): AsyncGenerator<MessageOut, void, unknown> {
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No reader available');
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = new TextDecoder().decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          yield data.data;
        }
      }
    }
  }

  private async *generateFallbackResponse(message: string): AsyncGenerator<MessageOut, void, unknown> {
    // Заглушка для оффлайн режима
    const fallbackMessage: MessageOut = {
      id: this.generateFallbackMessageId(),
      chat_id: this.currentChatId!,
      content: "Извините, сервер временно недоступен. Попробуйте позже.",
      role: "assistant",
      created_at: new Date().toISOString()
    };

    yield fallbackMessage;
  }
}

export const chatService = ChatService.getInstance(); 