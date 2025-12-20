"""Главный модуль Telegram-бота для проверки текстов."""

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

    async def handle_reload(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Обработчик команды /reload для перезагрузки правил.

        Args:
            update: Объект обновления от Telegram
            context: Контекст обработчика
        """
        if not update.message:
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
        custom_rules_count = len(config.get("custom_rules", []))
        channel_rules_count = len(
            config.get("channel_rules", {})
        )

        response = (
            "🔄 **Правила перезагружены из Google Sheets!**\n\n"
            f"📌 Кастомных правил: {custom_rules_count}\n"
            f"📢 Правил каналов: {channel_rules_count}"
        )

        await update.message.reply_text(
            response, parse_mode="Markdown"
        )

        print(
            f"[{timestamp}] Правила перезагружены: "
            f"{custom_rules_count} кастомных, "
            f"{channel_rules_count} каналов"
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
            f"символов\n"
        )

        # Создаем приложение
        self.application = (
            Application.builder().token(self.token).build()
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
        print("💡 Команды:")
        print("   /reload - перезагрузить правила из Google Sheets")
        print("⏹️  Нажмите Ctrl+C для остановки\n")

        # Запускаем бота
        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES
        )
