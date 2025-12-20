"""Загрузка и управление конфигурацией бота."""

import os
import json
from typing import Dict, Any
from datetime import datetime


class ConfigLoader:
    """Класс для загрузки и автообновления конфигурации."""

    def __init__(self, config_path: str):
        """
        Инициализация загрузчика конфигурации.

        Args:
            config_path: Путь к файлу конфигурации
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.last_modified = 0
        self._load()

    def _load(self) -> None:
        """Загружает конфигурацию из файла."""
        try:
            current_mtime = os.path.getmtime(self.config_path)

            if current_mtime > self.last_modified:
                with open(
                    self.config_path,
                    'r',
                    encoding='utf-8'
                ) as f:
                    self.config = json.load(f)
                self.last_modified = current_mtime

                timestamp = datetime.now().strftime('%H:%M:%S')
                print(
                    f"[{timestamp}] ✅ Конфигурация "
                    f"загружена/обновлена"
                )
        except Exception as e:
            print(f"Ошибка при загрузке конфигурации: {e}")
            self._use_defaults()

    def _use_defaults(self) -> None:
        """Использует значения по умолчанию."""
        self.config = {
            "checks": {
                "spelling": True,
                "custom_rules": True,
                "spaces": True
            },
            "ignore_words": [],
            "custom_rules": [],
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

    def reload(self) -> bool:
        """
        Перезагружает конфигурацию если файл изменился.

        Returns:
            True если конфигурация была обновлена
        """
        old_mtime = self.last_modified
        self._load()
        return self.last_modified > old_mtime

    def get(self, key: str = None, default: Any = None) -> Any:
        """
        Получает значение из конфигурации.

        Args:
            key: Ключ (если None, возвращает весь словарь)
            default: Значение по умолчанию

        Returns:
            Значение из конфигурации или default
        """
        if key is None:
            return self.config
        return self.config.get(key, default)
