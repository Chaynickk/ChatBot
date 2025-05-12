const API_BASE_URL = 'https://variables-ata-reserve-those.trycloudflare.com/api';

export interface SendMessageRequest {
    chat_id: number;
    content: string;
    role: string;
    parent_id: number;
}

export type MessageStreamEvent = any; // Заменить на точный тип, если он определён

export const apiService = {
    async sendMessageToBackend(
        body: SendMessageRequest,
        onEvent: (event: MessageStreamEvent) => void
    ) {
        const baseUrl = API_BASE_URL.replace(/\/$/, "");
        const url = `${baseUrl}/messages/`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                chat_id: body.chat_id,
                content: body.content,
                role: body.role
            }),
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
}; 