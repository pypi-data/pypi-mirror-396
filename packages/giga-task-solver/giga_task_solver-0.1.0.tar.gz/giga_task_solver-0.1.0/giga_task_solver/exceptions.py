class GigaChatError(Exception):
    """Базовая ошибка клиента GigaChat."""


class GigaChatAuthError(GigaChatError):
    """Отсутствует или неверный API-ключ."""


class GigaChatAPIError(GigaChatError):
    """Ошибка ответа API GigaChat."""
