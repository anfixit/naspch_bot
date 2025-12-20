"""Главный класс для управления всеми проверками текста."""

from typing import Dict, List, Any
from .checkers.spelling_checker import SpellingChecker
from .checkers.custom_rules_checker import CustomRulesChecker
from .checkers.space_checker import SpaceChecker
from .utils.config_loader import ConfigLoader
from .utils.formatter import ErrorFormatter
from .utils.message_validator import MessageValidator


class TextChecker:
    """Управляет всеми проверками текста."""

    def __init__(self, config_loader: ConfigLoader):
        """
        Инициализация проверки текста.

        Args:
            config_loader: Загрузчик конфигурации
        """
        self.config_loader = config_loader
        self._init_components()

    def _init_components(self) -> None:
        """Инициализирует все компоненты."""
        config = self.config_loader.get()

        # Инициализация чекеров
        self.spelling_checker = SpellingChecker(config)
        self.custom_rules_checker = CustomRulesChecker(config)
        self.space_checker = SpaceChecker(config)

        # Инициализация утилит
        response_config = config.get('response', {})
        self.formatter = ErrorFormatter(response_config)

        min_length = config.get(
            'settings',
            {}
        ).get('min_text_length', 50)
        self.validator = MessageValidator(min_length)

    def reload_config(self) -> None:
        """Перезагружает конфигурацию и компоненты."""
        if self.config_loader.reload():
            self._init_components()

    def validate_message(self, text: str) -> bool:
        """
        Проверяет, является ли сообщение сообщением райтера.

        Args:
            text: Текст сообщения

        Returns:
            True если сообщение нужно проверять
        """
        is_valid, _ = self.validator.validate_and_extract(text)
        return is_valid

    def check_text(self, text: str) -> str:
        """
        Выполняет все проверки и форматирует результат.

        Args:
            text: Текст сообщения

        Returns:
            Отформатированное сообщение с ошибками
        """
        # Перезагружаем конфигурацию перед проверкой
        self.reload_config()

        # Валидация и извлечение текста
        is_valid, text_to_check = (
            self.validator.validate_and_extract(text)
        )

        if not is_valid or text_to_check is None:
            return ""

        # Выполняем все проверки
        errors = self._perform_checks(text_to_check)

        # Форматируем результат
        return self.formatter.format(errors)

    def _perform_checks(
        self,
        text: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Выполняет все включенные проверки.

        Args:
            text: Текст для проверки

        Returns:
            Словарь с результатами проверок
        """
        results = {
            'spelling': [],
            'custom': [],
            'spaces': []
        }

        # Кастомные правила (проверяем первыми)
        if self.custom_rules_checker.is_enabled():
            print("  → Проверка кастомных правил...")
            results['custom'] = (
                self.custom_rules_checker.check(text)
            )

        # Орфография
        if self.spelling_checker.is_enabled():
            print("  → Проверка орфографии...")
            results['spelling'] = (
                self.spelling_checker.check(text)
            )

        # Пробелы
        if self.space_checker.is_enabled():
            print("  → Проверка пробелов...")
            results['spaces'] = self.space_checker.check(text)

        return results
