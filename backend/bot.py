import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
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

CHANNEL_ID = '@llinkiflexxer'
CHANNEL_LINK = 'https://t.me/llinkiflexxer'

async def is_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['administrator', 'creator', 'member']:
            return True
        else:
            return False

    except Exception as e:
        print(f'ошибка проверки подписи {e}')
        return False


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без_ника"
    if await is_subscribed(bot, user_id):

        # Записываем юзера в БД
        add_user(tg_id=user_id, username=username)

        # Ссылка-заглушка для Web App
        web_app_url = "https://bcb4d87a8d4201be-194-76-217-49.serveousercontent.com"
        welcome_text = (
            f"Здравствуйте, **{username}**! 👋\n\n"
            "Вы подключены к рабочей среде **NeuroStaff**.\n"
            "Делегируйте задачи виртуальным специалистам и оптимизируйте "
            "рабочие процессы прямо из Telegram.\n\n"
            "Для старта нажмите кнопку ниже 👇"
        )

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
            text=welcome_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться на канал", url=CHANNEL_LINK)],
            [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_sub")]])
        await message.answer(
            "⚠️ **Для доступа к ИИ-Штату подпишитесь на наш канал.**\n\n"
            "После подписки нажмите кнопку **«Я подписался»** ниже:",
            parse_mode="Markdown",
            reply_markup=kb
        )

@dp.callback_query(F.data == 'check_sub')
async def check_sub_handlers(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_name = call.from_user.username or 'без_ника'
    if await is_subscribed(bot, user_id):
        await call.message.delete()
        add_user(tg_id=user_id, username=user_name)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Открыть ИИ-Штат 🚀", web_app=WebAppInfo(url='https://bcb4d87a8d4201be-194-76-217-49.serveousercontent.com'))]
        ])
        await call.message.answer(
            f"Спасибо за подписку, {call.from_user.first_name}! 🎉\n Доступ открыт:",
            reply_markup=kb
        )

    else:
        # Покажем системное всплывающее окно
        await call.answer("❌ Подписка не найдена! Сначала подпишитесь.", show_alert=True)


# Главная функция запуска
async def main():
    init_db()
    await bot.delete_webhook(drop_pending_updates=True)  # <-- Очистит зависшую очередь
    print("Бизнес-логика: Бот успешно запущен и вышел на связь!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())