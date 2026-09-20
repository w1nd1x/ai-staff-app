import sqlite3

from anyio.to_interpreter import current_default_interpreter_limiter



# Путь к файлу базы данных, он появится в корне проекта
DB_PATH = "database.db"


def init_db():
    """Инициализация БД: создаем таблицу пользователей, если её еще нет"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Создаем таблицу пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            tg_id INTEGER PRIMARY KEY,
            username TEXT,
            is_premium BOOLEAN DEFAULT 0,
            has_autopilot BOOLEAN DEFAULT 0,
            limits INTEGER DEFAULT 5
        )
    ''')

    conn.commit()
    conn.close()
    print("Бизнес-логика: База данных успешно инициализирована!")


def add_user(tg_id: int, username: str):
    """Добавляет нового юзера в базу, если его там еще нет"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # INSERT OR IGNORE значит: если юзер с таким tg_id уже есть, ничего не делаем
    cursor.execute(
        "INSERT OR IGNORE INTO users (tg_id, username) VALUES (?, ?)",
        (tg_id, username)
    )

    conn.commit()
    conn.close()


def get_user(tg_id: int) -> dict:
    """Получает всё инфо о юзере по его Telegram ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT tg_id, username, is_premium, has_autopilot, limits FROM users WHERE tg_id = ?", (tg_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "tg_id": row[0],
            "username": row[1],
            "is_premium": bool(row[2]),  # Конвертируем 0/1 из базы в True/False
            "has_autopilot": bool(row[3]),# Конвертируем 0/1 из базы в True/False
            "limits": int(row[4])
        }
    return None


def update_payment_status(tg_id: int, field: str, status: bool):
    """Включает пользователю доступ (is_premium или has_autopilot) после оплаты"""
    if field not in ["is_premium", "has_autopilot"]:
        return  # Защита от дурака, чтобы не обновили несуществующее поле

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Меняем статус (True превратится в 1, False в 0)
    cursor.execute(f"UPDATE users SET {field} = ? WHERE tg_id = ?", (int(status), tg_id))

    conn.commit()
    conn.close()

def check_limits(tg_id: int,) -> bool:
    if tg_id == 12345678:
        return True

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT limits FROM users WHERE tg_id = ?", (tg_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0] > 0:
        return True
    return False

def decrease_limit(tg_id: int) -> bool:
    if tg_id == 12345678:
        return  # Не списываем лимиты у разработчика

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET limits = limits - 1 WHERE tg_id = ?",(tg_id,))
    conn.commit()
    conn.close()

def reset_all_users_limits(default_limit: int = 5):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('UPDATE  users SET limits = ?', (default_limit,))

    conn.commit()
    conn.close()
    print('Бизнес-логика: Лимиты всех пользователей успешно обновлены')