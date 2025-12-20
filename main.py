#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Точка входа для Telegram-бота проверки текстов.
"""

import os
import sys
from pathlib import Path

# Добавляем src в путь импорта
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv

from src.bot import SpellCheckBot


def main():
    """Главная функция запуска бота."""
    # Загружаем переменные окружения
    load_dotenv()

    # Получаем конфигурацию
    bot_token = os.getenv('BOT_TOKEN')
    config_file = os.getenv('CONFIG_FILE', 'config/bot_config.json')

    # Google Sheets (опционально)
    google_credentials = os.getenv('GOOGLE_CREDENTIALS_PATH')
    google_spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')

    if not bot_token:
        print("❌ Ошибка: BOT_TOKEN не найден в .env файле")
        sys.exit(1)

    if not os.path.exists(config_file):
        print(f"❌ Ошибка: Конфиг файл {config_file} не найден")
        sys.exit(1)

    # Создаем и запускаем бота
    bot = SpellCheckBot(
        bot_token,
        config_file,
        google_credentials_path=google_credentials,
        google_spreadsheet_id=google_spreadsheet_id
    )
    bot.run()


if __name__ == '__main__':
    main()
