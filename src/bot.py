"""Главный модуль Telegram-бота для проверки текстов."""

import os
from datetime import datetime
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes
)

from .text_checker import TextChecker
from .utils.config_loader import ConfigLoader


class SpellCheckBot:
    """Telegram-бот для проверки орфографии и грамматики."""

    def __init__(
        self,
        token: str,
        config_path: str
    ):
        """
        Инициализация бота.

        Args:
            token: Токен Telegram-бота
            config_path: Путь к файлу конфигурации
        """
        self.token = token
        self.config_loader = ConfigLoader(config_path)
        self.text_checker = TextChecker(self.config_loader)
        self.application: Optional[Application] = None

    async def handle_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Обработчик входящих сообщений.

        Args:
            update: Объект обновления от Telegram
            context: Контекст обработчика
        """
        if not update.message or not update.message.text:
            return

        text = update.message.text

        # Проверяем, это сообщение от райтера
        if not self.text_checker.validate_message(text):
            return

        # Логируем обработку
        username = (
            update.message.from_user.username
            or update.message.from_user.id
        )
        timestamp = datetime.now().strftime('%H:%M:%S')

        print(f"\n{'=' * 50}")
        print(
            f"[{timestamp}] Проверяю сообщение от {username}"
        )

        # Выполняем проверку
        response = self.text_checker.check_text(text)

        # Отправляем ответ только если есть результат
        if response:
            await update.message.reply_text(
                response,
                reply_to_message_id=update.message.message_id,
                parse_mode='Markdown'
            )

            print(f"[{timestamp}] Отправлен ответ")

        print(f"{'=' * 50}\n")

    async def error_handler(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Обработчик ошибок бота.

        Args:
            update: Объект обновления от Telegram
            context: Контекст обработчика
        """
        print(f"Произошла ошибка: {context.error}")

    def run(self) -> None:
        """Запускает бота."""
        config = self.config_loader.get()

        print("🚀 Запуск бота для проверки текстов")
        print(
            "📝 Проверка: орфография + кастомные правила "
            "+ пробелы"
        )
        print(
            f"📏 Минимальная длина текста: "
            f"{config.get('settings', {}).get('min_text_length', 50)} "
            f"символов\n"
        )

        # Создаем приложение
        self.application = (
            Application.builder().token(self.token).build()
        )

        # Добавляем обработчики
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_message
            )
        )
        self.application.add_error_handler(self.error_handler)

        print("✅ Бот запущен и готов к работе!")
        print("⏹️  Нажмите Ctrl+C для остановки\n")

        # Запускаем бота
        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES
        )
