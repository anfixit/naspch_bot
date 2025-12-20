"""Проверка по кастомным правилам написания."""

import re
from typing import Any, Dict, List

from .base_checker import BaseChecker


class CustomRulesChecker(BaseChecker):
    """Проверка текста по кастомным правилам написания."""

    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация проверки кастомных правил.

        Args:
            config: Конфигурация с custom_rules
        """
        super().__init__(config)
        self.custom_rules = config.get("custom_rules", [])

    def check(self, text: str) -> List[Dict[str, Any]]:
        """
        Проверяет текст по кастомным правилам.

        Args:
            text: Текст для проверки

        Returns:
            Список найденных несоответствий правилам
        """
        errors = []

        for rule in self.custom_rules:
            wrong = rule.get("wrong", "")
            correct = rule.get("correct", "")
            case_sensitive = rule.get("case_sensitive", False)

            if not wrong or not correct:
                continue

            pattern = re.escape(wrong)
            flags = 0 if case_sensitive else re.IGNORECASE

            for match in re.finditer(pattern, text, flags):
                errors.append(
                    {
                        "type": "custom",
                        "word": match.group(),
                        "suggestion": correct,
                        "message": "Неправильное написание",
                    }
                )

        return errors

    def is_enabled(self) -> bool:
        """Проверяет, включена ли проверка кастомных правил."""
        return self.config.get("checks", {}).get("custom_rules", True)
