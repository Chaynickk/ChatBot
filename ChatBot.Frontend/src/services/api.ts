const API_BASE_URL = 'http://localhost:5000';

export interface ChatResponse {
    response: string;
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
    }
}; 