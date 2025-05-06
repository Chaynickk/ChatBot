from typing import List, Dict

def messages_to_prompt(messages: List[Dict[str, str]]) -> str:
    """
    Преобразует список сообщений в форматированный промпт для модели.
    
    Args:
        messages: Список сообщений в формате [{"role": str, "content": str}, ...]
        
    Returns:
        str: Отформатированный промпт для модели
    """
    role_format = {
        "system": "[ИНСТРУКЦИЯ]\n{content}\n\n",
        "user": "User: {content}\n",
        "assistant": "Assistant: {content}\n"
    }

    prompt = ""
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "").strip()
        if role in role_format:
            prompt += role_format[role].format(content=content)
    prompt += "Assistant:"  # чтобы модель продолжила
    return prompt 