"""Валидация сообщений перед проверкой."""

import re
from typing import Optional, Tuple


class MessageValidator:
    """Валидация и предобработка сообщений."""

    def __init__(self, min_text_length: int = 50):
        """
        Инициализация валидатора.

        Args:
            min_text_length: Минимальная длина текста
        """
        self.min_text_length = min_text_length

    def is_rayters_message(self, text: str) -> bool:
        """
        Проверяет формат сообщения райтера.

        Args:
            text: Текст сообщения

        Returns:
            True если сообщение от райтера
        """
        if not text:
            return False

        lines = text.split("\n", 1)
        if not lines:
            return False

        first_line = lines[0]
        # Ловим ЛЮБУЮ ссылку t.me/ (любые символы до пробела)
        return bool(re.search(r"t\.me/\S+", first_line))

    def extract_text_to_check(self, text: str) -> Optional[str]:
        """
        Извлекает текст для проверки (убирает первую строку).

        Args:
            text: Исходный текст сообщения

        Returns:
            Текст для проверки или None если текст слишком короткий
        """
        lines = text.split("\n", 1)

        if len(lines) > 1:
            text_to_check = lines[1]
        else:
            return None

        if len(text_to_check.strip()) < self.min_text_length:
            return None

        return text_to_check

    def validate_and_extract(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Валидирует сообщение и извлекает текст для проверки.

        Args:
            text: Исходный текст сообщения

        Returns:
            Кортеж (is_valid, text_to_check)
        """
        if not self.is_rayters_message(text):
            return False, None

        text_to_check = self.extract_text_to_check(text)
        if text_to_check is None:
            return False, None

        return True, text_to_check
