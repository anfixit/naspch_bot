"""Проверка правил для конкретных каналов."""

import re
from typing import Any, Dict, List

from .base_checker import BaseChecker


class ChannelRulesChecker(BaseChecker):
    """Проверка правил для конкретных телеграм-каналов."""

    def __init__(
        self,
        config: Dict[str, Any],
        channel_rules: Dict[str, Dict[str, Any]],
    ):
        """
        Инициализация проверки правил каналов.

        Args:
            config: Общая конфигурация
            channel_rules: Правила для конкретных каналов
        """
        super().__init__(config)
        self.channel_rules = channel_rules

    def check(
        self, text: str, channel_name: str = None
    ) -> List[Dict[str, Any]]:
        """
        Проверяет текст по правилам канала.

        Args:
            text: Полный текст сообщения
            channel_name: Название канала из первой строки

        Returns:
            Список найденных нарушений
        """
        if not channel_name:
            channel_name = self._extract_channel_name(text)

        if not channel_name:
            return []

        channel_key = channel_name.lower()
        if channel_key not in self.channel_rules:
            return []

        rules = self.channel_rules[channel_key]
        errors = []

        # Проверяем правило подписи
        signature_rule = rules.get("signature_format", "")
        if signature_rule:
            errors.extend(
                self._check_signature_rule(
                    text, signature_rule, channel_name
                )
            )

        return errors

    def _extract_channel_name(self, text: str) -> str:
        """
        Извлекает название канала из первой строки.

        Args:
            text: Полный текст сообщения

        Returns:
            Название канала или пустую строку
        """
        lines = text.split("\n", 1)
        if not lines:
            return ""

        first_line = lines[0]

        # Ищем название канала в формате "ТГ-канал Название"
        match = re.search(
            r"ТГ-канал\s+([^:]+)", first_line, re.IGNORECASE
        )
        if match:
            return match.group(1).strip()

        return ""

    def _check_signature_rule(
        self, text: str, expected_ending: str, channel_name: str
    ) -> List[Dict[str, Any]]:
        """
        Проверяет что текст заканчивается на нужную подпись.

        Args:
            text: Полный текст
            expected_ending: Ожидаемое окончание из таблицы
            channel_name: Название канала

        Returns:
            Список ошибок
        """
        errors = []

        # Убираем первую строку (заголовок с каналом)
        lines = text.split("\n", 1)
        if len(lines) < 2:
            return errors

        # Берем текст КАК ЕСТЬ из таблицы
        content = lines[1]

        # Проверяем что текст заканчивается на ожидаемую строку
        if not content.endswith(expected_ending):
            # Заменяем невидимые символы на видимые для отображения
            expected_display = expected_ending.replace("\n", "↵")

            errors.append(
                {
                    "type": "channel_signature",
                    "message": (
                        f"Неправильная подпись для канала "
                        f"{channel_name}"
                    ),
                    "expected": f"Ожидается: `{expected_display}`",
                }
            )

        return errors

    def is_enabled(self) -> bool:
        """Проверяет, включена ли проверка правил каналов."""
        return len(self.channel_rules) > 0
