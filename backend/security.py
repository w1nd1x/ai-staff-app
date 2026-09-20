import json
import time
import hmac
import hashlib
from fastapi import Header
from urllib.parse import parse_qsl
from fastapi import HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from backend.database.models import get_user, add_user


class TelegramUser(BaseModel):
    id: int
    first_name: str
    username: str | None = None
    is_premium: bool | None = None
    has_autopilot: bool | None = None

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


MAX_INIT_DATA_AGE = 86400 # 24 часа
DEV_MODE = True

async def get_current_user(authorization: str | None = Header(None)):


    if DEV_MODE:
        dev_id = 12345678
        dev_username = 'test_dev'

        db_user = get_user(dev_id)
        if not db_user:
            add_user(tg_id=dev_id, username=dev_username)

        return TelegramUser(
            id=dev_id,
            first_name='DevUser',
            username=dev_username,
        )


    if not authorization:
        raise HTTPException(
            status_code = 401,
            detail = 'Missing Authorization Header',
        )
#Парсинг initData
    init_data = authorization.replace("Bearer ", "").strip()
    parse_data = parse_qsl(init_data, keep_blank_values=True)
    data_dict = dict(parse_data)

    extract_hash = data_dict.get('hash')
    if not extract_hash:
        raise HTTPException(
            status_code = 401,
            detail = 'в initData отсуствует параметр hash')

#Сортировка без hash для проверки
    filtered_data = sorted([(k, v) for k, v in parse_data if k != 'hash'])
    data_check_string = '\n'.join(f'{k}={v}' for k, v in filtered_data)

#Формирование хеша
    secret_key = hmac.new(
        key=b'WebAppData',
        msg=BOT_TOKEN.encode("utf-8"),
        digestmod=hashlib.sha256
    ).digest()


    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, extract_hash):
        raise HTTPException(
            status_code=401,
            detail='Недействительный HMAC hash. Данные подделаны!'
        )

# 7. Проверка устаревания данных (Защита от Replay Attacks)
    auth_date = data_dict.get('auth_date')
    if not auth_date or (time.time() - int(auth_date)) > MAX_INIT_DATA_AGE:
        raise HTTPException(
            status_code=401,
            detail="Срок действия авторизации истек. Перезапустите Mini App."
        )

    # 8. Распаковка JSON с данными пользователя
    user_raw = data_dict.get('user')
    if not user_raw:
        raise HTTPException(
            status_code=400,
            detail="В initData отсутствуют данные пользователя"
        )

    user_json = json.loads(user_raw)
    tg_id = user_json.get("id")
    username = user_json.get("username", "без_ника")
    first_name = user_json.get("first_name", "Пользователь")

    # 9. Проверяем / создаем пользователя в БД и подтягиваем статус подписки
    db_user = get_user(tg_id)
    if not db_user:
        add_user(tg_id=tg_id, username=username)
        db_user = get_user(tg_id)

    return TelegramUser(
        id=tg_id,
        first_name=first_name,
        username=username,
        is_premium=db_user["is_premium"] if db_user else False,
        has_autopilot=db_user["has_autopilot"] if db_user else False
    )

