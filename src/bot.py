"""Главный модуль Telegram-бота для проверки текстов."""

from datetime import datetime
from typing import Optional

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
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

        # Постоянная клавиатура с кнопками
        self.keyboard = ReplyKeyboardMarkup(
            [
                [KeyboardButton("🔄 Обновить правила")],
                [
                    KeyboardButton("📊 Статус"),
                    KeyboardButton("ℹ️ Помощь"),
                ],
            ],
            resize_keyboard=True,
        )

    def _get_rules_info(self) -> tuple:
        """Получает информацию о правилах."""
        config = self.config_loader.get()
        custom_rules_count = len(config.get("custom_rules", []))
        channel_rules_count = len(
            config.get("channel_rules", {})
        )
        return custom_rules_count, channel_rules_count

    async def handle_start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Обработчик команды /start.

        Args:
            update: Объект обновления от Telegram
            context: Контекст обработчика
        """
        if not update.message:
            return

        custom_rules, channel_rules = self._get_rules_info()

        await update.message.reply_text(
            "👋 **Привет! Я бот для проверки текстов.**\n\n"
            "📝 **Что я проверяю:**\n"
            "• Орфографию\n"
            "• Кастомные правила написания\n"
            "• Пробелы\n"
            "• Правила каналов\n\n"
            f"📊 **Загружено правил:**\n"
            f"📌 Кастомных: {custom_rules}\n"
            f"📢 Каналов: {channel_rules}\n\n"
            "⚠️ **ВАЖНО:** После изменения правил в "
            "Google Sheets нажмите кнопку "
            "**'🔄 Обновить правила'**!\n\n"
            "💡 Отправь сообщение с ссылкой на канал "
            "для проверки.",
            reply_markup=self.keyboard,
            parse_mode="Markdown",
        )

    async def handle_reload_button(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Обработчик кнопки обновления правил.

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
            f"[{timestamp}] Кнопка 'Обновить правила' "
            f"от {username}"
        )

        # Перезагружаем конфигурацию
        self.config_loader.reload()
        self.text_checker._init_components()

        # Подсчитываем правила
        custom_rules, channel_rules = self._get_rules_info()

        response = (
            "✅ **Правила успешно обновлены!**\n\n"
            f"📌 Кастомных правил: {custom_rules}\n"
            f"📢 Правил каналов: {channel_rules}\n\n"
            "Теперь можно проверять тексты с новыми правилами!"
        )

        await update.message.reply_text(
            response,
            reply_markup=self.keyboard,
            parse_mode="Markdown",
        )

        print(
            f"[{timestamp}] Правила обновлены: "
            f"{custom_rules} кастомных, "
            f"{channel_rules} каналов"
        )

    async def handle_status(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Показывает текущий статус бота."""
        if not update.message:
            return

        custom_rules, channel_rules = self._get_rules_info()

        await update.message.reply_text(
            "📊 **Статус бота:**\n\n"
            f"📌 Кастомных правил: {custom_rules}\n"
            f"📢 Правил каналов: {channel_rules}\n\n"
            "✅ Бот работает нормально!",
            reply_markup=self.keyboard,
            parse_mode="Markdown",
        )

    async def handle_help(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Показывает помощь по использованию бота."""
        if not update.message:
            return

        await update.message.reply_text(
            "ℹ️ **Как пользоваться ботом:**\n\n"
            "1️⃣ Отправь текст с ссылкой на канал в "
            "первой строке\n"
            "   Пример:\n"
            "   `ТГ-канал Тест: t.me/test`\n"
            "   `Текст для проверки...`\n\n"
            "2️⃣ Бот найдет все ошибки и предложит "
            "исправления\n\n"
            "3️⃣ Если добавил новые правила в Google Sheets, "
            "нажми **'🔄 Обновить правила'**\n\n"
            "📝 **Правила редактируются здесь:**\n"
            "[Google Sheets]"
            "(https://docs.google.com/spreadsheets/d/"
            "1tB2z-_i6KvY3S9Bqko5eNjscB55oYeqHW78nfYUsxfw)\n\n"
            "⚠️ **После изменений в таблице ОБЯЗАТЕЛЬНО "
            "нажми '🔄 Обновить правила'!**",
            reply_markup=self.keyboard,
            parse_mode="Markdown",
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

        # Проверяем кнопки меню
        if text == "🔄 Обновить правила":
            await self.handle_reload_button(update, context)
            return
        elif text == "📊 Статус":
            await self.handle_status(update, context)
            return
        elif text == "ℹ️ Помощь":
            await self.handle_help(update, context)
            return

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
            # Добавляем напоминание об обновлении правил
            footer = (
                "\n\n💡 _Если правила в Google Sheets изменились, "
                "нажми '🔄 Обновить правила'_"
            )
            full_response = response + footer

            await update.message.reply_text(
                full_response,
                reply_to_message_id=update.message.message_id,
                reply_markup=self.keyboard,
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
            CommandHandler("start", self.handle_start)
        )
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, self.handle_message
            )
        )
        self.application.add_error_handler(self.error_handler)

        print("✅ Бот запущен и готов к работе!")
        print("💡 Постоянное меню с кнопками активно")
        print("⏹️  Нажмите Ctrl+C для остановки\n")

        # Запускаем бота
        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES
        )
