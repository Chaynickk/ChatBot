const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

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
        const response = await fetch(`${API_BASE_URL}/chat/stream?message=${encodeURIComponent(message)}`);
        
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
        const response = await fetch(`${API_BASE_URL}/messages/messages/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
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
    }
}; 