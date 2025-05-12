// Удаляю prompt и sessionStorage
// const sessionBackendUrl = sessionStorage.getItem('backendUrl');
// if (!sessionBackendUrl) {
//   const backendUrl = prompt('Введите адрес бэкенда:', import.meta.env.VITE_API_URL || 'http://localhost:5000');
//   if (backendUrl) {
//     sessionStorage.setItem('backendUrl', backendUrl);
//   }
// }

// Заменяю загрузку из env на жёсткую константу
export const API_BASE_URL = 'https://albert-engineers-vegas-per.trycloudflare.com';

console.log('API_BASE_URL (api.ts):', API_BASE_URL);

// Функция для проверки доступности сервера
export const checkServerAvailability = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/ping`);
        return response.ok;
    } catch (error) {
        console.error('Ошибка при проверке доступности сервера:', error);
        return false;
    }
};

export interface ChatResponse {
    response: string;
}

export interface SendMessageRequest {
    chat_id: number;
    content: string;
    role: string;
    parent_id: number;
}

export type MessageStreamEvent =
    | { type: 'user_message'; data: any }
    | { type: 'chunk'; data: string }
    | { type: 'assistant_message'; data: any };

export interface ProjectResponse {
    id: number;
    name: string;
    user_id: number;
    created_at: string;
    updated_at: string;
}

export interface UserResponse {
    id?: number;
    telegram_id: string;
    username?: string;
    full_name?: string;
    is_plus?: boolean;
    created_at?: string;
    updated_at?: string;
    custom_prompt?: string;
}

export const apiService = {
    async sendToGigaChat(message: string): Promise<ChatResponse> {
        const response = await fetch(`${API_BASE_URL}/gigachat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });

        if (!response.ok) {
            throw new Error('Ошибка при отправке сообщения');
        }

        return response.json();
    },

    async sendToYandexGPT(message: string): Promise<ReadableStream> {
        const response = await fetch(`${API_BASE_URL}/chat/stream?message=${encodeURIComponent(message)}`, {
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        if (!response.ok) {
            throw new Error('Ошибка при отправке сообщения');
        }

        return response.body!;
    },

    async sendToGPT4oMini(message: string): Promise<ChatResponse> {
        const response = await fetch(`${API_BASE_URL}/gpt4omini`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });

        if (!response.ok) {
            throw new Error('Ошибка при отправке сообщения');
        }

        return response.json();
    },

    async sendMessageToBackend(
        body: SendMessageRequest,
        onEvent: (event: MessageStreamEvent) => void
    ) {
        const formData = new FormData();
        formData.append('chat_id', String(body.chat_id));
        formData.append('content', body.content);
        // role и parent_id не добавляем

        const response = await fetch(`${API_BASE_URL}/messages/`, {
            method: 'POST',
            body: formData,
        });
        if (!response.body) throw new Error('Нет потока данных');
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            let lines = buffer.split(/\r?\n\n/);
            buffer = lines.pop() || '';
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const json = JSON.parse(line.slice(6));
                        onEvent(json);
                    } catch (e) {
                        // ignore parse errors
                    }
                }
            }
        }
    },

    async createProject(name: string, user_id: number = 0): Promise<ProjectResponse> {
        const url = `${API_BASE_URL}/api/projects/`;
        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name, user_id }),
            });
            
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                console.error('Ошибка при создании проекта:', errorData);
                throw new Error(`Ошибка при создании проекта: ${res.status} ${res.statusText}`);
            }
            
            const data = await res.json();
            console.log('Проект успешно создан:', data);
            return data;
        } catch (error) {
            console.error('Ошибка при создании проекта:', error);
            throw error;
        }
    },

    async createChat({
        user_id,
        project_id,
        folder_id = null,
        title = 'Новый чат',
        model_id = 1,
        parent_chat_id = null,
        parent_message_id = null
    }: {
        user_id: number,
        project_id?: number,
        folder_id?: number | null,
        title?: string,
        model_id?: number,
        parent_chat_id?: number | null,
        parent_message_id?: number | null
    }) {
        const url = `${API_BASE_URL}/api/chats/`;
        const body = {
            user_id,
            project_id,
            folder_id,
            title,
            model_id,
            parent_chat_id,
            parent_message_id
        };
        console.log('Создание чата, тело запроса:', body);
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Telegram ${user_id}`
            },
            body: JSON.stringify(body),
        });
        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            console.error('Ошибка при создании чата:', errorData);
            throw new Error(`Ошибка при создании чата: ${res.status} ${res.statusText}`);
        }
        const data = await res.json();
        console.log('Чат успешно создан:', data);
        return data.id;
    },

    async createUser(telegram_id: string): Promise<UserResponse> {
        const url = `${API_BASE_URL}/users/users/`;
        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ telegram_id }),
            });
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                console.error('Ошибка при создании пользователя:', errorData);
                throw new Error(`Ошибка при создании пользователя: ${res.status} ${res.statusText}`);
            }
            const data = await res.json();
            console.log('Пользователь успешно создан:', data);
            return data;
        } catch (error) {
            console.error('Ошибка при создании пользователя:', error);
            throw error;
        }
    },

    getInitData(): { user?: { id: string } } {
        const urlParams = new URLSearchParams(window.location.search);
        const initData = urlParams.get('initData');
        if (!initData) return {};
        try {
            const data = JSON.parse(decodeURIComponent(initData));
            return data;
        } catch (e) {
            console.error('Ошибка при парсинге InitData:', e);
            return {};
        }
    },

    async getUserByInitData(initData: string): Promise<UserResponse> {
        const url = `${API_BASE_URL}/users/users/?init_data=${encodeURIComponent(initData)}`;
        console.log('Отправка запроса авторизации:', url);
        const res = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        console.log('Ответ сервера:', res.status, res.statusText);
        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            console.error('Ошибка авторизации:', errorData);
            throw res;
        }
        const data = await res.json();
        console.log('Успешный ответ:', data);
        return data;
    },

    async registerUserByInitData(initData: string): Promise<UserResponse> {
        const url = `${API_BASE_URL}/users/users/?init_data=${encodeURIComponent(initData)}`;
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (!res.ok) {
            throw res;
        }
        return res.json();
    },

    async getLastChatIdByTelegramId(telegram_id: number): Promise<number | null> {
        const res = await fetch(`${API_BASE_URL}/api/chats/?telegram_id=${telegram_id}`);
        if (!res.ok) return null;
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
            return data[data.length - 1].id;
        }
        return null;
    }
}; 