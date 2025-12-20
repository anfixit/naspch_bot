"""Загрузка и управление конфигурацией бота."""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional


class ConfigLoader:
    """Класс для загрузки и автообновления конфигурации."""

    def __init__(
        self, config_path: str, google_sheets_loader: Optional[Any] = None
    ):
        """
        Инициализация загрузчика конфигурации.

        Args:
            config_path: Путь к файлу конфигурации
            google_sheets_loader: Загрузчик Google Sheets (опционально)
        """
        self.config_path = config_path
        self.google_sheets_loader = google_sheets_loader
        self.config: Dict[str, Any] = {}
        self.last_modified = 0
        self._load()

    def _load(self) -> None:
        """Загружает конфигурацию из файла."""
        try:
            current_mtime = os.path.getmtime(self.config_path)

            if current_mtime > self.last_modified:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                self.last_modified = current_mtime

                timestamp = datetime.now().strftime("%H:%M:%S")
                print(
                    f"[{timestamp}] ✅ Конфигурация " f"загружена/обновлена"
                )

                # Загружаем правила из Google Sheets
                self._load_from_google_sheets()

        except Exception as e:
            print(f"Ошибка при загрузке конфигурации: {e}")
            self._use_defaults()

    def _load_from_google_sheets(self) -> None:
        """Загружает правила из Google Sheets если доступно."""
        if not self.google_sheets_loader:
            return

        if not self.google_sheets_loader.is_available():
            return

        # Загружаем кастомные правила
        custom_rules = self.google_sheets_loader.load_custom_rules()
        if custom_rules:
            self.config["custom_rules"] = custom_rules

        # Загружаем правила каналов
        channel_rules = self.google_sheets_loader.load_channel_rules()
        if channel_rules:
            self.config["channel_rules"] = channel_rules

    def _use_defaults(self) -> None:
        """Использует значения по умолчанию."""
        self.config = {
            "checks": {
                "spelling": True,
                "custom_rules": True,
                "spaces": True,
                "channel_rules": True,
            },
            "ignore_words": [],
            "custom_rules": [],
            "channel_rules": {},
            "space_checks": {
                "multiple_spaces": True,
                "space_before_punctuation": True,
                "no_space_after_punctuation": True,
            },
            "response": {"show_suggestions_count": 3, "show_emoji": True},
            "settings": {"min_text_length": 50},
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
