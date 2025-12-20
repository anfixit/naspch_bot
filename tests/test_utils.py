"""Тесты для утилит."""

import pytest
from src.utils.message_validator import MessageValidator
from src.utils.formatter import ErrorFormatter


class TestMessageValidator:
    """Тесты валидации сообщений."""

    def setup_method(self):
        """Подготовка к тестам."""
        self.validator = MessageValidator(min_text_length=50)

    def test_valid_rayters_message(self):
        """Тест валидного сообщения райтера."""
        text = "ТГ-канал: t.me/test\n" + "А" * 60
        is_valid = self.validator.is_rayters_message(text)
        
        assert is_valid is True

    def test_invalid_no_link(self):
        """Тест сообщения без ссылки."""
        text = "Обычное сообщение без ссылки"
        is_valid = self.validator.is_rayters_message(text)
        
        assert is_valid is False

    def test_extract_text(self):
        """Тест извлечения текста."""
        text = "ТГ-канал: t.me/test\n" + "Текст " * 20
        extracted = self.validator.extract_text_to_check(text)
        
        assert extracted is not None
        assert "ТГ-канал" not in extracted
        assert "Текст" in extracted

    def test_text_too_short(self):
        """Тест слишком короткого текста."""
        text = "ТГ-канал: t.me/test\nКороткий текст"
        extracted = self.validator.extract_text_to_check(text)
        
        assert extracted is None

    def test_validate_and_extract(self):
        """Тест полной валидации и извлечения."""
        text = "ТГ-канал: t.me/test\n" + "Длинный текст " * 10
        is_valid, extracted = (
            self.validator.validate_and_extract(text)
        )
        
        assert is_valid is True
        assert extracted is not None


class TestErrorFormatter:
    """Тесты форматирования ошибок."""

    def setup_method(self):
        """Подготовка к тестам."""
        config = {
            'show_emoji': True,
            'show_suggestions_count': 3
        }
        self.formatter = ErrorFormatter(config)

    def test_no_errors(self):
        """Тест форматирования без ошибок."""
        errors = {'spelling': [], 'custom': [], 'spaces': []}
        result = self.formatter.format(errors)
        
        assert "✅" in result
        assert "не найдено" in result

    def test_spelling_errors(self):
        """Тест форматирования орфографических ошибок."""
        errors = {
            'spelling': [
                {
                    'word': 'ошыбка',
                    'suggestions': ['ошибка', 'ошибки']
                }
            ],
            'custom': [],
            'spaces': []
        }
        result = self.formatter.format(errors)
        
        assert "ошыбка" in result
        assert "ошибка" in result
        assert "Орфография" in result

    def test_custom_errors(self):
        """Тест форматирования кастомных ошибок."""
        errors = {
            'spelling': [],
            'custom': [
                {
                    'word': 'Гига чат',
                    'suggestion': 'Гигачат'
                }
            ],
            'spaces': []
        }
        result = self.formatter.format(errors)
        
        assert "Гига чат" in result
        assert "Гигачат" in result
        assert "Неправильное написание" in result

    def test_space_errors(self):
        """Тест форматирования ошибок пробелов."""
        errors = {
            'spelling': [],
            'custom': [],
            'spaces': [
                {
                    'word': 'слово  слово',
                    'suggestion': 'слово слово',
                    'message': 'Лишние пробелы (2 подряд)'
                }
            ]
        }
        result = self.formatter.format(errors)
        
        assert "Пробелы" in result
        assert "Лишние пробелы" in result

    def test_no_emoji(self):
        """Тест без эмодзи."""
        config = {'show_emoji': False, 'show_suggestions_count': 3}
        formatter = ErrorFormatter(config)
        
        errors = {'spelling': [], 'custom': [], 'spaces': []}
        result = formatter.format(errors)
        
        assert "✅" not in result
        assert "не найдено" in result
