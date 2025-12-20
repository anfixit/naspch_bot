"""Форматирование ответов бота с найденными ошибками."""

from typing import Dict, List, Any


class ErrorFormatter:
    """Форматирует ошибки в читаемый вид для отправки."""

    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация форматтера.

        Args:
            config: Конфигурация response
        """
        self.show_emoji = config.get("show_emoji", True)
        self.max_suggestions = config.get("show_suggestions_count", 3)

    def format(self, errors: Dict[str, List[Dict]]) -> str:
        """
        Форматирует все ошибки в читаемый текст.

        Args:
            errors: Словарь с ошибками по типам

        Returns:
            Отформатированное сообщение
        """
        spelling = errors.get("spelling", [])
        custom = errors.get("custom", [])
        spaces = errors.get("spaces", [])

        total = len(spelling) + len(custom) + len(spaces)

        if total == 0:
            return self._format_no_errors()

        message = self._format_header(total)
        message += self._format_custom_errors(custom)
        message += self._format_spelling_errors(spelling)
        message += self._format_space_errors(spaces)

        return message

    def _format_no_errors(self) -> str:
        """Форматирует сообщение об отсутствии ошибок."""
        if self.show_emoji:
            return "✅ Ошибок не найдено!"
        return "Ошибок не найдено!"

    def _format_header(self, total: int) -> str:
        """Форматирует заголовок с количеством ошибок."""
        emoji = "❌" if self.show_emoji else ""
        return f"{emoji} Найдено ошибок: {total}\n\n"

    def _format_custom_errors(self, errors: List[Dict[str, Any]]) -> str:
        """Форматирует кастомные ошибки."""
        if not errors:
            return ""

        emoji = "📌 " if self.show_emoji else ""
        message = f"{emoji}**Неправильное написание:**\n"

        for i, error in enumerate(errors, 1):
            word = error.get("word", "")
            suggestion = error.get("suggestion", "")
            message += f"{i}. «{word}» → «{suggestion}»\n"

        return message + "\n"

    def _format_spelling_errors(self, errors: List[Dict[str, Any]]) -> str:
        """Форматирует орфографические ошибки."""
        if not errors:
            return ""

        emoji = "📝 " if self.show_emoji else ""
        message = f"{emoji}**Орфография:**\n"

        for i, error in enumerate(errors, 1):
            word = error.get("word", "")
            suggestions = error.get("suggestions", [])[: self.max_suggestions]

            if suggestions:
                suggestion_text = ", ".join(f"«{s}»" for s in suggestions)
                message += f"{i}. «{word}» → {suggestion_text}\n"
            else:
                message += f"{i}. «{word}» — нет вариантов\n"

        return message + "\n"

    def _format_space_errors(self, errors: List[Dict[str, Any]]) -> str:
        """Форматирует ошибки с пробелами."""
        if not errors:
            return ""

        emoji = "⎵ " if self.show_emoji else ""
        message = f"{emoji}**Пробелы:**\n"

        for i, error in enumerate(errors, 1):
            msg = error.get("message", "")
            word = error.get("word", "")
            suggestion = error.get("suggestion", "")

            message += f"{i}. {msg}: «{word}» → «{suggestion}»\n"

        return message
