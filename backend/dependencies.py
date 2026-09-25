from fastapi import Depends, HTTPException, Header
from dotenv import load_dotenv
import os
from backend.security import get_current_user, TelegramUser
from backend.database.models import check_limits

load_dotenv()
ADMIN_SECRET = os.getenv('ADMIN_SECRET')

async def check_user_limits(user: TelegramUser = Depends(get_current_user)):

    has_limit = await check_limits(user.id)

    if not has_limit:
        raise HTTPException(
            status_code=403,
            detail="Лимит генераций исчерпан! Попробуйте завтра.",
        )
    return user

async def verify_admin_key(x_admin_key: str | None = Header(None)):
    if x_admin_key == ADMIN_SECRET:
        return True

    else:
        raise HTTPException(
            status_code=403,
            detail='Нету заголовка'
        )