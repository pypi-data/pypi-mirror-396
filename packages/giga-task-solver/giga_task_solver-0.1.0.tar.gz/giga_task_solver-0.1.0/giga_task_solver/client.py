import os
import requests
from .exceptions import GigaChatAuthError, GigaChatAPIError

API_URL = "https://giga.chat/api/v1/chat/completions"
DEFAULT_MODEL = "giga-chat"


def solve(task_text: str, model: str = DEFAULT_MODEL, timeout: int = 60) -> str:
    api_key = os.getenv("GIGACHAT_API_KEY")
    if not api_key:
        raise GigaChatAuthError(
            "Не задан API-ключ. Установите переменную окружения GIGACHAT_API_KEY"
        )

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": task_text}]
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
        raise GigaChatAPIError(f"Ошибка сети: {exc}") from exc

    if response.status_code == 401:
        raise GigaChatAuthError("Неверный API-ключ GigaChat")

    if not response.ok:
        raise GigaChatAPIError(
            f"Ошибка API GigaChat: {response.status_code} — {response.text}"
        )

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise GigaChatAPIError("Неожиданный формат ответа API") from exc
