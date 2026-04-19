import logging
import os

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from quack.features.balance.commands import balance_command_callback
from quack.features.payments.commands import answer_button, pay_command_callback, register_updates
from quack.features.registrations.commands import alias_command_callback, registration_command_callback
from quack.storage.db import init_db

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

log = logging.getLogger()

if __name__ == "__main__":
    init_db()

    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if TOKEN is None:
        raise ValueError

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("purchase", pay_command_callback))
    app.add_handler(CommandHandler("balance", balance_command_callback))
    app.add_handler(CommandHandler("register", registration_command_callback))
    app.add_handler(CommandHandler("alias", alias_command_callback))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, register_updates))

    app.add_handler(CallbackQueryHandler(answer_button))

    app.run_polling()
