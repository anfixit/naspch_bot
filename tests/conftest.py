"""Общие фикстуры для тестов."""

import pytest
import os
import sys

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def sample_config():
    """Базовая конфигурация для тестов."""
    return {
        "checks": {
            "spelling": True,
            "custom_rules": True,
            "spaces": True
        },
        "ignore_words": ["эксплойт", "хайп", "инста"],
        "custom_rules": [
            {
                "wrong": "Гига чат",
                "correct": "Гигачат",
                "case_sensitive": False
            }
        ],
        "space_checks": {
            "multiple_spaces": True,
            "space_before_punctuation": True,
            "no_space_after_punctuation": True
        },
        "response": {
            "show_suggestions_count": 3,
            "show_emoji": True
        },
        "settings": {
            "min_text_length": 50
        }
    }


@pytest.fixture
def sample_text_with_errors():
    """Пример текста с ошибками."""
    return """ТГ-канал (ауд 100К): t.me/testchannel

Новый продукт  появился в магазинах.Он стоит 
1000 рублей ,а работает через Гига чат.
Есть ошыбка в слове."""
