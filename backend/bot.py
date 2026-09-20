import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Импортируем функции нашей базы данных
from database.models import init_db, add_user

# Загружаем переменные окружения из файла .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Инициализируем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без_ника"

    # Записываем юзера в БД
    add_user(tg_id=user_id, username=username)

    # Ссылка-заглушка для Web App
    web_app_url = "https://bcb4d87a8d4201be-194-76-217-49.serveousercontent.com"

    # Создаем кнопку Mini App
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Открыть ИИ-Штат 🚀",
                web_app=WebAppInfo(url=web_app_url)
            )
        ]
    ])

    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        f"Добро пожаловать в твой личный **ИИ-Штат сотрудников**.\n\n"
        f"Нажми на кнопку ниже, чтобы запустить приложение👇",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )



# Главная функция запуска
async def main():
    init_db()
    await bot.delete_webhook(drop_pending_updates=True)  # <-- Очистит зависшую очередь
    print("Бизнес-логика: Бот успешно запущен и вышел на связь!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())