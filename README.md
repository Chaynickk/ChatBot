Простите за грязь в файлах, мы боимся удалять так как что то может сломатся


# ChatBot Backend

## Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/Chaynickk/ChatBot.git
cd ChatBot/ChatBot.Backend
```

### 2. Создайте и активируйте виртуальное окружение

```bash
python -m venv venv
# Windows:
venv\\Scripts\\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Настройте переменные окружения

Создайте файл `.env` в папке `ChatBot.Backend` и заполните его, например:

```
TELEGRAM_BOT_TOKEN=ваш_токен_бота
DATABASE_URL=postgresql+asyncpg://postgres:пароль@localhost/ChatBot
```

### 5. Запустите PostgreSQL и создайте базу данных

Скрипт создания БД во пути ChatBot\ChatBot.Backend\app\db\init_db.sql
Скрипт быстрое добовление моделей ChatBot\ChatBot.Backend\app\db\insert_models.sql (будет использоватся тольок модель с id 1, неуспаели сдлетаь выбор, УБЕДИТЕСЬ ЧТО ЭТИ МОДЕЛИ СКАЧЕНЫ)

### 6. Запустите Ollama (если используете локальные LLM)

Убедитесь, что Ollama запущен и доступен по адресу http://localhost:11434  
(см. https://ollama.com/)

### 7. Запустите backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Проверьте работу

- Откройте http://localhost:8000/docs для Swagger UI.
- Проверьте `/ping` — должен вернуть `{"message": "pong"}`.

---

### 9. Настройте туннель для связи фронта и бэка (если требуется)

Если фронтенд и бэкенд находятся на разных машинах или нужен публичный доступ к API, создайте туннель (например, через ngrok или cloudflared):

```bash
ngrok http 8000
# или
cloudflared tunnel --url http://localhost:8000
```

Полученую сылку вставтьве в переменую API_BASE_URL в следующих файлах:

ChatBot.Frontend\src\services\api.ts
src\services\api.ts

## Требования

- Python 3.10+
- PostgreSQL
- Ollama (со скачеными моделями)
- Telegram Bot Token

## API роуты

### users
- **POST /users/users/** — Регистрация пользователя
- **GET /users/users/** — Получить пользователя по init_data
- **POST /users/users/sync_plus_status** — Синхронизация статуса Plus для всех пользователей
- **POST /users/users/give_plus** — Выдать Plus-подписку пользователю
- **PATCH /users/prompt** — Обновить custom prompt пользователя

### projects
- **POST /api/projects/** — Создать проект
- **GET /api/projects/** — Получить проекты пользователя
- **PATCH /api/projects/{project_id}/rename** — Переименовать проект
- **PATCH /projects/system-prompt** — Обновить системный prompt проекта

### folders
- **POST /folders/folders/** — Создать папку
- **PATCH /folders/{folder_id}/rename** — Переименовать папку

### chats
- **POST /api/chats/** — Создать чат
- **GET /api/chats/** — Получить чаты пользователя
- **PATCH /api/chats/{chat_id}/rename** — Переименовать чат
- **POST /api/chats/branch/** — Создать ветку чата (ответвление)
- **PATCH /api/chats/{chat_id}/set_model** — Установить модель для чата
- **PATCH /chats/settings** — Обновить настройки чата (проект, папка)

### messages
- **POST /messages/** — Отправить сообщение в чат
- **GET /messages/** — Получить сообщения чата
- **GET /messages/in_chat/** — Получить сообщения только из указанного чата

### memories
- **POST /memories/** — Создать запись в памяти пользователя
- **PUT /memories/{memory_id}** — Обновить запись в памяти пользователя

### delete
- **DELETE /delete/chats/{chat_id}** — Удалить чат
- **DELETE /delete/projects/{project_id}** — Удалить проект
- **DELETE /delete/folders/{folder_id}** — Удалить папку
- **DELETE /delete/memory/{memory_id}** — Удалить запись из памяти

### default
- **GET /ping** — Проверка работоспособности сервера (возвращает pong)

## Стек технологий

- **Python 3.10+** — основной язык разработки.
- **FastAPI** — современный асинхронный web-фреймворк для создания REST API.
- **SQLAlchemy** — ORM для работы с базой данных (используется асинхронный режим через asyncpg).
- **PostgreSQL** — основная реляционная база данных.
- **pyTelegramBotAPI** — библиотека для интеграции с Telegram Bot API.
- **Ollama** — сервер локальных LLM (Large Language Models) для генерации ответов.
- **aiohttp** — асинхронный HTTP-клиент для взаимодействия с Ollama.
- **APScheduler** — планировщик задач для периодических операций.
- **python-dotenv** — для работы с переменными окружения из .env файлов.
- **pydantic** — для валидации и сериализации данных (схемы запросов/ответов).
- **Starlette** — ASGI-фреймворк, на котором основан FastAPI (используется для CORS и middleware).
- **pandas**, **python-docx**, **openpyxl**, **pdfplumber** — для обработки и парсинга файлов (docx, xlsx, pdf, csv) при необходимости.



# ChatBot Backend

## ОБЯЗАТЕЛЬНО ВЫПОЛНИТЕ 9 ШАГ ЗАПУСКА БЭКЕНДА


## Предварительные требования
- Node.js (версия 16 или выше)
- npm (обычно устанавливается вместе с Node.js)

## Шаги по запуску

### 1. Установка зависимостей
```bash
# Перейдите в директорию frontend
cd ChatBot/ChatBot.Frontend

# Установите все зависимости из package.json
npm install
```

### 2. Сборка проекта
```bash
# Выполните сборку проекта
npm run build
```
После успешной сборки в директории `ChatBot\ChatBot.Frontend\dist` появятся следующие файлы:
- `index.html`
- `assets/` (директория со стилями, скриптами и другими ресурсами)

### 3. Деплой на хостинг
1. Скопируйте **все содержимое** директории `dist` на ваш хостинг
2. Убедитесь, что:
   - Все файлы из `assets/` загружены в соответствующую директорию на хостинге
   - `index.html` находится в корневой директории вашего сайта
   - На хостинге настроен сервер (например, nginx или Apache) для раздачи статических файлов

---

**Удачи с деплоем! Если возникнут вопросы или потребуется дополнительная помощь, дайте знать.**90
