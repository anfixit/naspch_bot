"""Главный модуль Telegram-бота для проверки текстов."""

import asyncio
from datetime import datetime
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .text_checker import TextChecker
from .utils.config_loader import ConfigLoader
from .utils.google_sheets_loader import GoogleSheetsLoader


class SpellCheckBot:
    """Telegram-бот для проверки орфографии и грамматики."""

    def __init__(
        self,
        token: str,
        config_path: str,
        google_credentials_path: str = None,
        google_spreadsheet_id: str = None,
    ):
        """
        Инициализация бота.

        Args:
            token: Токен Telegram-бота
            config_path: Путь к файлу конфигурации
            google_credentials_path: Путь к credentials Google Sheets
            google_spreadsheet_id: ID таблицы Google Sheets
        """
        self.token = token

        # Инициализация Google Sheets (опционально)
        self.google_loader = None
        if google_credentials_path and google_spreadsheet_id:
            self.google_loader = GoogleSheetsLoader(
                google_credentials_path, google_spreadsheet_id
            )

        self.config_loader = ConfigLoader(
            config_path, google_sheets_loader=self.google_loader
        )
        self.text_checker = TextChecker(self.config_loader)
        self.application: Optional[Application] = None
        self._reload_task = None

    async def auto_reload_rules(self) -> None:
        """Автоматически перезагружает правила каждые 3 часа."""
        while True:
            await asyncio.sleep(10800)  # 3 часа
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(
                f"[{timestamp}] 🔄 Автообновление правил "
                f"из Google Sheets..."
            )

            self.config_loader.reload()
            self.text_checker._init_components()

            config = self.config_loader.get()
            custom_count = len(config.get("custom_rules", []))
            channel_count = len(config.get("channel_rules", {}))

            print(
                f"[{timestamp}] ✅ Правила обновлены: "
                f"{custom_count} кастомных, "
                f"{channel_count} каналов"
            )

    async def handle_reload(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Обработчик команды /reload (скрытая, только в ЛС).

        Args:
            update: Объект обновления от Telegram
            context: Контекст обработчика
        """
        if not update.message:
            return

        # Игнорируем команды в группах
        if update.message.chat.type != "private":
            return

        username = (
            update.message.from_user.username
            or update.message.from_user.id
        )
        timestamp = datetime.now().strftime("%H:%M:%S")

        print(
            f"[{timestamp}] Команда /reload от {username}"
        )

        # Перезагружаем конфигурацию
        self.config_loader.reload()
        self.text_checker._init_components()

        # Подсчитываем правила
        config = self.config_loader.get()
        custom_count = len(config.get("custom_rules", []))
        channel_count = len(config.get("channel_rules", {}))

        response = (
            "✅ Правила обновлены!\n\n"
            f"📌 Кастомных: {custom_count}\n"
            f"📢 Каналов: {channel_count}"
        )

        await update.message.reply_text(response)

        print(
            f"[{timestamp}] Правила обновлены: "
            f"{custom_count} кастомных, "
            f"{channel_count} каналов"
        )

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
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
        timestamp = datetime.now().strftime("%H:%M:%S")

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
                parse_mode="Markdown",
            )

            print(f"[{timestamp}] Отправлен ответ")

        print(f"{'=' * 50}\n")

    async def error_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Обработчик ошибок бота.

        Args:
            update: Объект обновления от Telegram
            context: Контекст обработчика
        """
        print(f"Произошла ошибка: {context.error}")

    async def post_init(
        self, application: Application
    ) -> None:
        """
        Запускается после инициализации приложения.

        Args:
            application: Приложение бота
        """
        # Запускаем автоматическое обновление правил
        # Сохраняем ссылку на задачу, чтобы избежать garbage collection
        self._reload_task = asyncio.create_task(self.auto_reload_rules())

    def run(self) -> None:
        """Запускает бота."""
        config = self.config_loader.get()

        print("🚀 Запуск бота для проверки текстов")
        print(
            "📝 Проверка: орфография + кастомные правила "
            "+ пробелы + правила каналов"
        )
        print(
            f"📏 Минимальная длина текста: "
            f"{config.get('settings', {}).get('min_text_length', 50)} "
            f"символов"
        )
        print("🔄 Автообновление правил: каждые 3 часа")
        print("")

        # Создаем приложение
        self.application = (
            Application.builder()
            .token(self.token)
            .post_init(self.post_init)
            .build()
        )

        # Добавляем обработчики
        self.application.add_handler(
            CommandHandler("reload", self.handle_reload)
        )
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, self.handle_message
            )
        )
        self.application.add_error_handler(self.error_handler)

        print("✅ Бот запущен и готов к работе!")
        print("💡 Скрытая команда /reload (только в ЛС)")
        print("⏹️  Нажмите Ctrl+C для остановки\n")

        # Запускаем бота
        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES
        )
