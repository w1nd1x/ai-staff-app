import os
from openai import OpenAI
from backend.config.specialists import AI_STAFF
from dotenv import load_dotenv
from backend.database.models import decrease_limit

load_dotenv()



client = OpenAI(base_url="https://api.deepseek.com",
                api_key=os.getenv("DEEP_SEEK",)
                )

def generate_ai_content(specialist_id: str, user_data: dict, user_id: int):
    specialist = AI_STAFF.get(specialist_id)
    if not specialist:
        raise ValueError(f'Специалист с данным ID не найден')

    template = specialist.system_prompt
    full_prompt = template.format(**user_data)

    try:

        response = client.chat.completions.create(#type: ignore
            model='deepseek-chat',
            messages=[
                {"role": 'system', 'content': full_prompt},
                {"role": 'user', 'content': "Сгенерируй результат строго по инструкции выше"},
                ],
            temperature=0.7,
            stream=True)


        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

        #По окончаю генерации текста, вычитаем лимиты у пользователя
        decrease_limit(user_id)

    #Пробрасываем ошибку дальше
    except Exception as e:
        raise(e)

async def refine_ai_content(specialist_id: str, original_text: str, user_feedback: str, user_id: int):
    specialist = AI_STAFF.get(specialist_id)
    if not specialist:
        raise ValueError(f'Специалст с ID {specialist_id} не найден')
    clear_system_promt = (
        f"{specialist.system_prompt}\n\n"
        "СТРОГОЕ ПРАВИЛО ФОРМАТА:\n"
        "Выдавай ТОЛЬКО финальный отредактированный текст. "
        "Категорически запрещено добавлять приветствия, прощания, вопросы и любые мета-комментарии "
        "(например: 'Вот поправленный вариант', 'Если что-то не нравится — напиши')."
    )
    messages = [
        {"role": 'system', 'content': clear_system_promt},
        {"role": "assistant", "content": original_text},
        {"role": "user", "content": f"Внеси следующие правки в текст выше: {user_feedback}"}
    ]
    try:
        response = client.chat.completions.create(#type: ignore
            model="deepseek-chat",
            messages=messages,
            temperature=0.3,  # Сниженная температура, чтобы ИИ точнее соблюдал инструкции правок
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

        # 6. Списываем лимит пользователя после успешной генерации
        await decrease_limit(user_id)

    except Exception as e:
        print(f"❌ Ошибка в refine_ai_content: {e}")
        raise e








