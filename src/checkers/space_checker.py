"""Проверка лишних пробелов и пробелов вокруг пунктуации."""

import re
from typing import Any, Dict, List

from .base_checker import BaseChecker


class SpaceChecker(BaseChecker):
    """Проверка пробелов в тексте."""

    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация проверки пробелов.

        Args:
            config: Конфигурация с space_checks
        """
        super().__init__(config)
        self.space_checks = config.get("space_checks", {})

    def check(self, text: str) -> List[Dict[str, Any]]:
        """
        Проверяет пробелы в тексте.

        Args:
            text: Текст для проверки

        Returns:
            Список проблем с пробелами
        """
        errors = []

        if self.space_checks.get("multiple_spaces", True):
            errors.extend(self._check_multiple_spaces(text))

        if self.space_checks.get("space_before_punctuation", True):
            errors.extend(self._check_space_before_punct(text))

        if self.space_checks.get("no_space_after_punctuation", True):
            errors.extend(self._check_no_space_after_punct(text))

        return errors

    def _check_multiple_spaces(self, text: str) -> List[Dict[str, Any]]:
        """Проверяет множественные пробелы."""
        errors = []
        pattern = r"(\S+)( {2,})(\S+)"

        for match in re.finditer(pattern, text):
            spaces_count = len(match.group(2))
            context = match.group(0)
            suggestion = f"{match.group(1)} {match.group(3)}"

            errors.append(
                {
                    "type": "space",
                    "word": context,
                    "suggestion": suggestion,
                    "message": f"Лишние пробелы ({spaces_count} подряд)",
                }
            )

        return errors

    def _check_space_before_punct(self, text: str) -> List[Dict[str, Any]]:
        """Проверяет пробелы перед знаками препинания."""
        errors = []
        pattern = r"(\S+)( +)([,.!?;:])"

        for match in re.finditer(pattern, text):
            context = match.group(0)
            suggestion = f"{match.group(1)}{match.group(3)}"

            errors.append(
                {
                    "type": "space",
                    "word": context,
                    "suggestion": suggestion,
                    "message": f'Пробел перед "{match.group(3)}"',
                }
            )

        return errors

    def _check_no_space_after_punct(self, text: str) -> List[Dict[str, Any]]:
        """Проверяет отсутствие пробела после знаков препинания."""
        errors = []
        pattern = r"(\S+)([,.!?;:])([а-яА-ЯёЁa-zA-Z]\S*)"

        for match in re.finditer(pattern, text):
            context = match.group(0)
            suggestion = f"{match.group(1)}{match.group(2)} {match.group(3)}"

            errors.append(
                {
                    "type": "space",
                    "word": context,
                    "suggestion": suggestion,
                    "message": f'Нет пробела после "{match.group(2)}"',
                }
            )

        return errors

    def is_enabled(self) -> bool:
        """Проверяет, включена ли проверка пробелов."""
        return self.config.get("checks", {}).get("spaces", True)
