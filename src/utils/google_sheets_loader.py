"""Загрузка правил из Google Sheets."""

import os
from typing import Any, Dict, List

import gspread
from google.oauth2.service_account import Credentials


class GoogleSheetsLoader:
    """Класс для загрузки правил из Google Sheets."""

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    ]

    def __init__(self, credentials_path: str, spreadsheet_id: str):
        """
        Инициализация загрузчика Google Sheets.

        Args:
            credentials_path: Путь к JSON файлу с credentials
            spreadsheet_id: ID Google Spreadsheet
        """
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        self._connect()

    def _connect(self) -> None:
        """Подключается к Google Sheets API."""
        try:
            if not os.path.exists(self.credentials_path):
                print(
                    f"⚠️  Google Sheets credentials не найдены: "
                    f"{self.credentials_path}"
                )
                return

            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.SCOPES,
            )
            self.client = gspread.authorize(creds)
            print("✅ Подключено к Google Sheets")
        except Exception as e:
            print(f"❌ Ошибка подключения к Google Sheets: {e}")
            self.client = None

    def load_custom_rules(self) -> List[Dict[str, Any]]:
        """
        Загружает кастомные правила написания (Лист 1).

        Returns:
            Список словарей с правилами
        """
        if not self.client:
            return []

        try:
            sheet = self.client.open_by_key(self.spreadsheet_id)
            worksheet = sheet.get_worksheet(0)

            values = worksheet.get_all_values()[1:]

            rules: List[Dict[str, Any]] = []
            for row in values:
                if len(row) >= 2 and row[0] and row[1]:
                    rules.append(
                        {
                            "wrong": row[0].strip(),
                            "correct": row[1].strip(),
                            "case_sensitive": False,
                        }
                    )

            print(
                f"📋 Загружено {len(rules)} кастомных правил "
                f"из Google Sheets"
            )
            return rules

        except Exception as e:
            print(
                f"❌ Ошибка загрузки кастомных правил "
                f"из Google Sheets: {e}"
            )
            return []

    def load_channel_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        Загружает правила для конкретных каналов (Лист 2).

        Returns:
            Словарь {название_канала: {правила}}
        """
        if not self.client:
            return {}

        try:
            sheet = self.client.open_by_key(self.spreadsheet_id)
            worksheet = sheet.get_worksheet(1)

            values = worksheet.get_all_values()[1:]

            channel_rules: Dict[str, Dict[str, Any]] = {}
            for row in values:
                if len(row) >= 2 and row[0] and row[1]:
                    channel_name = row[0].strip().lower()
                    rules_text = row[1].strip()

                    # Заменяем NEWLINE на реальный перенос строки
                    rules_text = rules_text.replace("NEWLINE", "\n")

                    channel_rules[channel_name] = {
                        "signature_format": rules_text,
                    }

            print(
                f"📋 Загружено правил для "
                f"{len(channel_rules)} каналов из Google Sheets"
            )
            return channel_rules

        except Exception as e:
            print(
                f"❌ Ошибка загрузки правил каналов "
                f"из Google Sheets: {e}"
            )
            return {}

    def is_available(self) -> bool:
        """
        Проверяет доступность Google Sheets.

        Returns:
            True если подключение активно
        """
        return self.client is not None
```

**Изменение:** строка 115 - добавлена замена `NEWLINE` на `\n`.

Теперь в Google Sheets пиши:
```
NEWLINE @filmkenner
