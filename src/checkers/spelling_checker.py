"""Проверка орфографии через Яндекс.Спеллер."""

import requests
from typing import List, Dict, Any
from .base_checker import BaseChecker


class SpellingChecker(BaseChecker):
    """Проверка орфографии через Яндекс.Спеллер API."""

    YANDEX_SPELLER_URL = (
        "https://speller.yandex.net/services/"
        "spellservice.json/checkText"
    )

    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация проверки орфографии.

        Args:
            config: Конфигурация с ignore_words
        """
        super().__init__(config)
        self.ignore_words = [
            w.lower() for w in config.get('ignore_words', [])
        ]

    def check(self, text: str) -> List[Dict[str, Any]]:
        """
        Проверяет орфографию в тексте.

        Args:
            text: Текст для проверки

        Returns:
            Список орфографических ошибок
        """
        try:
            params = {
                'text': text,
                'lang': 'ru',
                'options': 0
            }

            response = requests.get(
                self.YANDEX_SPELLER_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            errors = response.json()
            return self._format_errors(errors)

        except Exception as e:
            print(f"Ошибка при проверке орфографии: {e}")
            return []

    def _format_errors(
        self,
        errors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Форматирует ошибки в единый формат.

        Args:
            errors: Список ошибок от Яндекс.Спеллер

        Returns:
            Отформатированный список ошибок
        """
        formatted = []
        for error in errors:
            word = error.get('word', '')
            if word.lower() not in self.ignore_words:
                formatted.append({
                    'type': 'spelling',
                    'word': word,
                    'suggestions': error.get('s', []),
                    'message': 'Орфографическая ошибка'
                })
        return formatted

    def is_enabled(self) -> bool:
        """Проверяет, включена ли проверка орфографии."""
        return self.config.get('checks', {}).get('spelling', True)
