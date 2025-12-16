class DeepSeekError(Exception):
    """Базовая ошибка клиента DeepSeek."""


class DeepSeekAuthError(DeepSeekError):
    """Отсутствует или неверный API-ключ."""


class DeepSeekAPIError(DeepSeekError):
    """Ошибка ответа API DeepSeek."""
