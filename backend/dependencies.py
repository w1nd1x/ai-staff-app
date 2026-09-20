from fastapi import Depends, HTTPException
from starlette import status

from backend.security import get_current_user, TelegramUser
from backend.database.models import check_limits

async def check_user_limits(user: TelegramUser = Depends(get_current_user)):

    has_limit = check_limits(user.id)

    if not has_limit:
        raise HTTPException(
            status_code=403,
            detail="Лимит генераций исчерпан! Попробуйте завтра.",
        )
    return user