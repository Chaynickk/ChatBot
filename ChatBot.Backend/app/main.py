from app.routes import user, project, folder, chat, message, memory, custom_prompt, delete, chat_settings, project_settings
from app.models.user import Base
from app.db.database import engine
from contextlib import asynccontextmanager
from fastapi import FastAPI, Security
from app.auth.security import api_key_header
from app.models.message import Message
import os
import telebot
import threading
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

# Создаем экземпляр бота
bot = telebot.TeleBot(BOT_TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_command(message):
    # Создаем кнопку для открытия веб-приложения
    markup = telebot.types.InlineKeyboardMarkup()
    web_app = telebot.types.WebAppInfo(url="https://chatlux.ru")
    markup.add(telebot.types.InlineKeyboardButton(text="Открыть веб-приложение", web_app=web_app))
    
    bot.reply_to(
        message,
        "Привет! Я ваш AI ассистент. Нажмите кнопку ниже, чтобы открыть веб-приложение.",
        reply_markup=markup
    )

# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_message(message):
    # Создаем кнопку для открытия веб-приложения
    markup = telebot.types.InlineKeyboardMarkup()
    web_app = telebot.types.WebAppInfo(url="https://chatlux.ru")
    markup.add(telebot.types.InlineKeyboardButton(text="Открыть веб-приложение", web_app=web_app))
    
    bot.reply_to(
        message,
        "Для использования полного функционала, пожалуйста, используйте веб-приложение.",
        reply_markup=markup
    )

# Функция для запуска бота в отдельном потоке
def run_bot():
    bot.infinity_polling()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем таблицы в базе данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True  # Поток завершится вместе с основной программой
    bot_thread.start()
    
    yield

app = FastAPI(lifespan=lifespan)

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники (или укажи конкретные, если нужно)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(project.router)
app.include_router(folder.router)
app.include_router(chat.router)
app.include_router(message.router)
app.include_router(memory.router)
app.include_router(custom_prompt.router)
app.include_router(delete.router)
app.include_router(chat_settings.router)
app.include_router(project_settings.router)

@app.get("/ping")
def ping():
    return {"message": "pong"}

