import os
import requests
from .exceptions import DeepSeekAuthError, DeepSeekAPIError

API_URL = "https://api.deepseek.com/v1/chat/completions"
DEFAULT_MODEL = "deepseek-chat"


def solve(task_text: str, model: str = DEFAULT_MODEL, timeout: int = 60) -> str:
    """
    Отправляет текст задачи в DeepSeek и возвращает ответ модели.
    """

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise DeepSeekAuthError(
            "Не задан API-ключ. Установите переменную окружения DEEPSEEK_API_KEY"
        )

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": task_text}
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise DeepSeekAPIError(f"Ошибка сети: {exc}") from exc

    if response.status_code == 401:
        raise DeepSeekAuthError("Неверный API-ключ DeepSeek")

    if not response.ok:
        raise DeepSeekAPIError(
            f"Ошибка API DeepSeek: {response.status_code} — {response.text}"
        )

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise DeepSeekAPIError("Неожиданный формат ответа API") from exc
