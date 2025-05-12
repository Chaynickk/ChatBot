-- === Таблица пользователей ===
CREATE TABLE users (
    telegram_id BIGINT PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    is_plus BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    custom_prompt TEXT
);


-- === Таблица проектов (workspace) ===
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    system_prompt TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === Таблица папок внутри проектов ===
CREATE TABLE folders (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === Таблица моделей (LLM) ===
CREATE TABLE models (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    provider TEXT NOT NULL,
    display_name TEXT NOT NULL,
    is_public BOOLEAN DEFAULT TRUE,
    plus_only BOOLEAN DEFAULT FALSE
);

-- === Таблица чатов ===
CREATE TABLE chats (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    folder_id INTEGER REFERENCES folders(id) ON DELETE SET NULL,
    title TEXT,
    model_id INTEGER REFERENCES models(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parent_chat_id INTEGER REFERENCES chats(id) ON DELETE SET NULL,
    parent_message_id INTEGER REFERENCES messages(id) ON DELETE SET NULL
);


-- === Таблица сообщений в чатах ===
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER REFERENCES chats(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES messages(id) ON DELETE SET NULL,
    role TEXT CHECK (role IN ('user', 'assistant', 'system')) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === Таблица подписок (для Plus) ===
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    status TEXT CHECK (status IN ('active', 'expired', 'cancelled')) NOT NULL
);

-- === Таблица экспортов чатов ===
CREATE TABLE exports (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER REFERENCES chats(id) ON DELETE CASCADE,
    export_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- === Долгосрочная память ===
CREATE TABLE memories (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);