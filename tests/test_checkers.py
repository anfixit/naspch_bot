"""Тесты для модулей проверки."""

import pytest
from src.checkers.spelling_checker import SpellingChecker
from src.checkers.custom_rules_checker import CustomRulesChecker
from src.checkers.space_checker import SpaceChecker


class TestSpellingChecker:
    """Тесты проверки орфографии."""

    def setup_method(self):
        """Подготовка к тестам."""
        config = {
            'ignore_words': ['эксплойт', 'хайп'],
            'checks': {'spelling': True}
        }
        self.checker = SpellingChecker(config)

    def test_find_spelling_error(self):
        """Тест поиска орфографической ошибки."""
        text = "Это ошыбка в слове"
        errors = self.checker.check(text)
        
        assert len(errors) > 0
        assert errors[0]['type'] == 'spelling'
        assert errors[0]['word'] == 'ошыбка'

    def test_ignore_words(self):
        """Тест игнорирования слов."""
        text = "Это эксплойт и хайп"
        errors = self.checker.check(text)
        
        assert len(errors) == 0

    def test_correct_text(self):
        """Тест корректного текста."""
        text = "Это правильный текст без ошибок"
        errors = self.checker.check(text)
        
        assert len(errors) == 0


class TestCustomRulesChecker:
    """Тесты проверки кастомных правил."""

    def setup_method(self):
        """Подготовка к тестам."""
        config = {
            'custom_rules': [
                {
                    'wrong': 'Гига чат',
                    'correct': 'Гигачат',
                    'case_sensitive': False
                },
                {
                    'wrong': 'Chat GPT',
                    'correct': 'ChatGPT',
                    'case_sensitive': False
                }
            ],
            'checks': {'custom_rules': True}
        }
        self.checker = CustomRulesChecker(config)

    def test_find_custom_error(self):
        """Тест поиска кастомной ошибки."""
        text = "Работает через Гига чат"
        errors = self.checker.check(text)
        
        assert len(errors) == 1
        assert errors[0]['type'] == 'custom'
        assert errors[0]['suggestion'] == 'Гигачат'

    def test_case_insensitive(self):
        """Тест регистронезависимости."""
        text = "Работает через ГИГА ЧАТ"
        errors = self.checker.check(text)
        
        assert len(errors) == 1

    def test_multiple_rules(self):
        """Тест нескольких правил."""
        text = "Гига чат и Chat GPT"
        errors = self.checker.check(text)
        
        assert len(errors) == 2


class TestSpaceChecker:
    """Тесты проверки пробелов."""

    def setup_method(self):
        """Подготовка к тестам."""
        config = {
            'space_checks': {
                'multiple_spaces': True,
                'space_before_punctuation': True,
                'no_space_after_punctuation': True
            },
            'checks': {'spaces': True}
        }
        self.checker = SpaceChecker(config)

    def test_multiple_spaces(self):
        """Тест множественных пробелов."""
        text = "Слово  слово"
        errors = self.checker.check(text)
        
        assert len(errors) == 1
        assert 'Лишние пробелы' in errors[0]['message']

    def test_space_before_punctuation(self):
        """Тест пробела перед пунктуацией."""
        text = "Слово ,слово"
        errors = self.checker.check(text)
        
        assert len(errors) >= 1
        found = any('Пробел перед' in e['message'] for e in errors)
        assert found

    def test_no_space_after_punctuation(self):
        """Тест отсутствия пробела после пунктуации."""
        text = "Слово,слово"
        errors = self.checker.check(text)
        
        assert len(errors) == 1
        assert 'Нет пробела после' in errors[0]['message']

    def test_correct_spacing(self):
        """Тест корректных пробелов."""
        text = "Правильный текст, без ошибок."
        errors = self.checker.check(text)
        
        assert len(errors) == 0
