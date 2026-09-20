import requests

try:
    print("Получаем список моделей с OpenRouter...")
    response = requests.get("https://openrouter.ai/api/v1/models")
    response.raise_for_status()
    all_models = response.json().get("data", [])

    # Фильтруем только те модели, у которых в названии есть ":free"
    free_models = [m["id"] for m in all_models if m["id"].endswith(":free")]

    print(f"\n✅ Найдено {len(free_models)} бесплатных моделей прямо сейчас:")
    for model in free_models:  # покажем первые 10 для экономии места
        print(f" - {model}")

except Exception as e:
    print(f"❌ Ошибка подключения: {e}")