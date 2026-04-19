import telegram


async def start_callback(update: telegram.Update, _) -> None:
    if update.message is None:
        return

    await update.message.reply_text("🏠 Roommate Pay Bot\n\nCommands:\n/register user1 user2\n/purchase\n/balance\n/expenses")
