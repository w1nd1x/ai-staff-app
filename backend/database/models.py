import aiosqlite

# Путь к файлу базы данных
DB_PATH = "database.db"


async def init_db():
    """Инициализация БД: создание таблицы и настройка под параллельные запросы."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Ускоряем базу и убираем ошибки 'database is locked' при частых запросах
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("PRAGMA busy_timeout = 5000;")

        # Создаем таблицу пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                tg_id INTEGER PRIMARY KEY,
                username TEXT,
                is_premium BOOLEAN DEFAULT 0,
                has_autopilot BOOLEAN DEFAULT 0,
                limits INTEGER DEFAULT 5
            )
        ''')

        await db.commit()
    print("Бизнес-логика: База данных успешно инициализирована (aiosqlite)!")


async def add_user(tg_id: int, username: str):
    """Добавляет нового юзера в базу, если его там еще нет."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (tg_id, username) VALUES (?, ?)",
            (tg_id, username)
        )
        await db.commit()


async def get_user(tg_id: int) -> dict | None:
    """Получает всё инфо о юзере по его Telegram ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT tg_id, username, is_premium, has_autopilot, limits FROM users WHERE tg_id = ?",
            (tg_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "tg_id": row["tg_id"],
                    "username": row["username"],
                    "is_premium": bool(row["is_premium"]),
                    "has_autopilot": bool(row["has_autopilot"]),
                    "limits": int(row["limits"])
                }
            return None


async def update_payment_status(tg_id: int, field: str, status: bool):
    """Включает пользователю доступ (is_premium или has_autopilot) после оплаты."""
    if field not in ["is_premium", "has_autopilot"]:
        return  # Защита от дурака

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {field} = ? WHERE tg_id = ?", (int(status), tg_id))
        await db.commit()


async def check_limits(tg_id: int) -> bool:
    """Проверяет наличие лимитов у пользователя."""
    if tg_id == 12345678:  # Исключение для разработчика
        return True

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT limits FROM users WHERE tg_id = ?", (tg_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0] > 0:
                return True
            return False


async def decrease_limit(tg_id: int):
    """Списывает 1 лимит у пользователя."""
    if tg_id == 12345678:  # Не списываем лимиты у разработчика
        return

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET limits = limits - 1 WHERE tg_id = ? AND limits > 0",
            (tg_id,)
        )
        await db.commit()


async def increase_limit(tg_id: int, count: int = 1):
    """Начисляет или возвращает (в except) лимиты пользователю."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET limits = limits + ? WHERE tg_id = ?",
            (count, tg_id)
        )
        await db.commit()


async def reset_all_users_limits(default_limit: int = 5):
    """Сбрасывает лимиты всем пользователям."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE users SET limits = ?', (default_limit,))
        await db.commit()
    print('Бизнес-логика: Лимиты всех пользователей успешно обновлены')