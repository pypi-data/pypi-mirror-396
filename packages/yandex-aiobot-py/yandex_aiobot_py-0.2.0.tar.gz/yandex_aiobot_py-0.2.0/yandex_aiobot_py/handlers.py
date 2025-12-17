from typing import Callable, Dict, Optional


class BaseHandler:
    """Базовый класс обработчика (можно расширять при необходимости)."""

    def __init__(self):
        pass


class MemoryStepHandler(BaseHandler):
    """
    Хранит обработчики для пользователей в памяти.
    Позволяет регистрировать, получать и удалять обработчики по user_login.
    Как использовать:
    handler_store = MemoryStepHandler()

    # Регистрация
    handler_store.register_handler("user@example.com", some_callback_function)

    # Получение
    callback = handler_store.get_handler("user@example.com")
    if callback:
        await callback(message)

    # Удаление
    handler_store.delete_handler("user@example.com")
    """

    def __init__(self):
        super().__init__()
        self.handlers: Dict[str, Callable] = {}

    def register_handler(self, user_login: str, callback: Callable) -> None:
        """Регистрирует обработчик для пользователя."""
        self.handlers[user_login] = callback

    def delete_handler(self, user_login: str) -> None:
        """Удаляет обработчик пользователя, если он существует."""
        self.handlers.pop(user_login, None)

    def get_handler(self, user_login: str) -> Optional[Callable]:
        """Возвращает обработчик для пользователя или None, если не найден."""
        return self.handlers.get(user_login)

    def get_all_handlers(self) -> Dict[str, Callable]:
        """Возвращает словарь всех обработчиков."""
        return self.handlers.copy()
