"""Базовый класс для всех проверок текста."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseChecker(ABC):
    """Абстрактный базовый класс для проверок."""

    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация чекера.

        Args:
            config: Словарь с настройками для данного типа проверки
        """
        self.config = config

    @abstractmethod
    def check(self, text: str) -> List[Dict[str, Any]]:
        """
        Проверяет текст и возвращает список ошибок.

        Args:
            text: Текст для проверки

        Returns:
            Список словарей с найденными ошибками
        """
        pass

    def is_enabled(self) -> bool:
        """Проверяет, включен ли данный чекер в конфигурации."""
        return True
