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

        # Проверяем формат подписи
        signature_format = rules.get("signature_format", "")
        if signature_format:
            errors.extend(
                self._check_signature_format(
                    text, signature_format, channel_name
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
        match = re.search(r"ТГ-канал\s+([^\(]+)", first_line, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return ""

    def _check_signature_format(
        self, text: str, expected_format: str, channel_name: str
    ) -> List[Dict[str, Any]]:
        """
        Проверяет формат подписи канала.

        Args:
            text: Полный текст
            expected_format: Ожидаемый формат
            channel_name: Название канала

        Returns:
            Список ошибок формата
        """
        errors = []

        # Извлекаем подпись канала (@channel)
        signature_match = re.search(r"@\w+", text)

        if not signature_match:
            errors.append(
                {
                    "type": "channel_signature",
                    "message": f"Отсутствует подпись канала для {channel_name}",
                    "expected": expected_format,
                }
            )
            return errors

        signature = signature_match.group(0)
        signature_pos = signature_match.start()

        # Проверяем формат подписи
        if "перенос строки" in expected_format.lower():
            # Подпись должна быть на новой строке
            if signature_pos == 0 or text[signature_pos - 1] != "\n":
                errors.append(
                    {
                        "type": "channel_signature",
                        "message": (
                            f"Подпись {signature} должна быть "
                            f"через перенос строки"
                        ),
                        "expected": f"...текст\n{signature}",
                    }
                )

        elif "пробел" in expected_format.lower():
            # Подпись должна быть через пробел
            if signature_pos > 0 and text[signature_pos - 1] == "\n":
                errors.append(
                    {
                        "type": "channel_signature",
                        "message": (
                            f"Подпись {signature} должна быть "
                            f"через пробел, а не на новой строке"
                        ),
                        "expected": f"...текст {signature}",
                    }
                )

        return errors

    def is_enabled(self) -> bool:
        """Проверяет, включена ли проверка правил каналов."""
        return len(self.channel_rules) > 0
