import logging
import os

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from quack.bot import (
    alias_command_callback,
    balance_command_callback,
    buttons,
    label_listener,
    pay_command_callback,
    price_listener,
    registration_command_callback,
)
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
    # app.add_handler(history_handler)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, price_listener))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, label_listener))

    app.add_handler(CallbackQueryHandler(buttons))

    app.run_polling()
