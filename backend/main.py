import asyncio
from fastapi import HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import HTMLResponse

from backend.ai import generate_ai_content, refine_ai_content
from fastapi.responses import FileResponse
from backend.config.specialists import AI_STAFF
from fastapi.responses import StreamingResponse
from backend.dependencies import check_user_limits, verify_admin_key
from backend.security import TelegramUser
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.database.models import init_db, reset_all_users_limits, get_all_users, increase_limit

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.bot import dp, bot  # Импортируйте вашего бота и диспетчер


#Обновляем лимиты пользователей

async def schedule_limits_reset():
    while True:
        await asyncio.sleep(7200)
        await reset_all_users_limits(default_limit=5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем polling бота в фоновой задаче при старте FastAPI
    asyncio.create_task(dp.start_polling(bot))
    yield

# 1. Объявляем асинхронный контекстный менеджер
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- БЛОК 1: СТАРТ СЕРВЕРА ---
    # Все, что написано ДО ключевого слова yield,
    # выполняется в момент запуска Uvicorn.
    await init_db()
    print("✅ База данных подключена и таблицы созданы!")

    # Запускаем фоновую задачу сброса лимитов
    task = asyncio.create_task(schedule_limits_reset())

    yield  # 👈 ТОЧКА ПЕРЕДАЧИ УПРАВЛЕНИЯ

    # --- БЛОК 2: ОСТАНОВКА СЕРВЕРА ---
    # Все, что написано ПОСЛЕ yield,
    # выполняется, когда ты нажимаешь Ctrl+C и выключаешь сервер.
    print("🛑 Сервер останавливается, закрываем ресурсы...")


# 2. Передаем наш lifespan в экземпляр FastAPI
app = FastAPI(lifespan=lifespan, title='AI Staff API')


# 1. Создаем сервер
# app = FastAPI(title="AI Staff API")


# 2. Разрешаем сайту подключаться к серверу (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Для рефакторинга ответа
class ReplayRequest(BaseModel):
    specialist_id: str
    original_text: str
    user_feedback: str

# 3. Наш трафарет для проверки данных от пользователя
class GenerationRequest(BaseModel):
    specialist_id: str
    inputs: dict

class AddLimitsRequest(BaseModel):
    tg_id: int
    limits: int


# 4. Главная страница (проверка, что сервер жив)
@app.get("/")
async def read_root():
    return FileResponse('frontend/index.html')


# 5. Окошко выдачи списка специалистов (GET)
@app.get("/specialists")
def get_specialists():
    result = {}
    for spec_id, spec in AI_STAFF.items():
        result[spec_id] = spec.model_dump()
    return result



# 6. Окошко приема данных для ИИ (POST)
@app.post("/generate")
async def generate_text(
        data: GenerationRequest,
        user: TelegramUser = Depends(check_user_limits)
        ):


    try:
        # 1. Вызываем твою функцию из models.py и передаем ей данные, которые прислал юзер
        ai_response = generate_ai_content(
            specialist_id=data.specialist_id,
            user_data=data.inputs,
            user_id = user.id
        )
        
        # 2. Если всё прошло успешно, возвращаем готовый ответ

        return StreamingResponse(ai_response, media_type="text/plain")

    except Exception as e:
            # 3. Если нейросеть выдаст ошибку (например, кончились деньги на OpenAI),
            # сервер не упадет, а вежливо сообщит об этом

        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации текста: {str(e)}"
            )

#Окошка для переделки исходного ответа от Нейросети
@app.post("/refine")
async def refine(
        data: ReplayRequest,
        user: TelegramUser = Depends(check_user_limits)
):
    try:
        ai_response = refine_ai_content(
            specialist_id=data.specialist_id,
            original_text=data.original_text,
            user_feedback=data.user_feedback,
            user_id=user.id
        )
        return StreamingResponse(ai_response, media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500,
            detail=f"Ошибка доработки текста: {str(e)}"
        )


@app.get("/admin", response_class=FileResponse)
async def get_admin_user():
    return FileResponse('frontend/admin.html')

@app.get("/api/admin/users")
async def get_admin_users(
        is_admin: bool = Depends(verify_admin_key)
):
    # return {"status": "ok", "message": "Доступ разрешен!"}
    users = await get_all_users()
    return {'users': users}

@app.post("/api/admin/add-limits")
async def add_limits_endpoint(
        data: AddLimitsRequest,
        is_admin: bool = Depends(verify_admin_key)):

        await increase_limit(data.tg_id, data.limits)
        users = await get_all_users()
        return {"status": "ok", "users": users}