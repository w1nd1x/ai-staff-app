from pydantic import BaseModel
from typing import List, Dict


# Описываем структуру одного поля ввода для фронтенда
class FormField(BaseModel):
    id: str  # Например, 'niche'
    label: str  # Например, 'Ваша ниша'
    type: str  # 'input', 'textarea' или 'select'
    placeholder: str  # Подсказка внутри поля
    options: List[str] = []  # Варианты выбора для 'select'


# Описываем структуру ИИ-сотрудника
class Specialist(BaseModel):
    id: str
    title: str
    icon: str  # Эмодзи для меню
    description: str  # Описание обязанностей
    fields: List[FormField]  # Список полей формы
    system_prompt: str  # Скрытый системный промпт


# Наша база данных штата сотрудников
AI_STAFF: Dict[str, Specialist] = {

    # 1. КОПИРАЙТЕР
    "copywriter": Specialist(
        id="copywriter",
        title="ИИ-Копирайтер",
        icon="✍️",
        description="Пишет вовлекающие посты для соцсетей без воды и штампов.",
        fields=[
            FormField(id="niche", label="Ниша бизнеса", type="input", placeholder="Например: Салон красоты"),
            FormField(id="topic", label="О чем пост / Какой инфоповод", type="textarea",
                      placeholder="Например: Скидка 30% на массаж до пятницы"),
            FormField(id="target", label="Целевая аудитория", type="input", placeholder="Например: Девушки 25-35 лет"),
            FormField(id="wishes", label="Особые пожелания (Стиль)", type="input",
                      placeholder="Например: Писать дружелюбно")
        ],
        system_prompt=(
            "Ты — опытный коммерческий копирайтер. Напиши вовлекающий пост для бизнеса. "
            "Правила: без штампов, разделяй на абзацы, используй списки, в конце добавь понятный призыв к действию. "
            "Контекст: Ниша: {niche}, Тема: {topic}, ЦА: {target}, Пожелания: {wishes}."
        )
    ),

    # 2. СЦЕНАРИСТ REELS
    "scenarist": Specialist(
        id="scenarist",
        title="ИИ-Сценарист Reels",
        icon="🎬",
        description="Генерирует вирусные сценарии коротких видео в виде таблицы.",
        fields=[
            FormField(id="niche", label="Ниша бизнеса / Блога", type="input",
                      placeholder="Например: Школа английского"),
            FormField(id="topic", label="Тема ролика", type="input",
                      placeholder="Например: 3 ошибки новичка в разговоре"),
            FormField(id="goal", label="Главная цель ролика", type="select", placeholder="Выбери цель",
                      options=["Набрать подписчиков", "Продать продукт", "Поднять вовлеченность"]),
            FormField(id="wishes", label="Особые пожелания", type="input",
                      placeholder="Например: Добавь юмора и динамики")
        ],
        system_prompt=(
            "Ты — топовый сценарист вертикальных видео (Reels/Shorts). Твоя цель — придумать вирусный сценарий. "
            "Обязательно сделай мощный 'хук' в первые 3 секунды. "
            "Выдай результат СТРОГФО в виде Markdown-таблицы из 3-х колонок: Кадр/Тайминг | Что в кадре (Визуал) | Что говорить (Голос). "
            "Контекст: Ниша: {niche}, Тема: {topic}, Цель: {goal}, Стиль: {wishes}."
        )
    ),

    # 3. МЕНЕДЖЕР ПО ПРОДАЖАМ
    "salesman": Specialist(
        id="salesman",
        title="ИИ-Продажник",
        icon="🤝",
        description="Помогает отвечать на сложные сообщения клиентов и закрывать сделки.",
        fields=[
            FormField(id="product", label="Что ты продаешь и за сколько", type="input",
                      placeholder="Например: Курс по похудению за 15 000 руб"),
            FormField(id="client_text", label="Что конкретно написал клиент", type="textarea",
                      placeholder="Вставь текст сообщения (например: 'Для меня это дорого')"),
            FormField(id="goal", label="Какая цель твоего ответа", type="select", placeholder="Выбери цель",
                      options=["Отработать 'Дорого'", "Вывести на созвон", "Предложить рассрочку", "Напомнить о себе"]),
            FormField(id="wishes", label="Особые пожелания", type="input",
                      placeholder="Например: Писать очень вежливо, без давления")
        ],
        system_prompt=(
            "Ты — хладнокровный и эмпатичный топ-менеджер по продажам. Твоя задача — спасти сделку в переписке. "
            "Правила: покажи ценность продукта, не извиняйся за цену, пиши коротко (2-3 абзаца) и обязательно заканчивай легким открытым вопросом. "
            "Выдай СТРОГО 2 варианта ответа: Вариант 1 (Мягкий, через заботу) и Вариант 2 (Прямой, коммерческий). "
            "Контекст: Продукт: {product}, Сообщение клиента: {client_text}, Твоя цель: {goal}, Пожелания: {wishes}."
        )
    )
}


