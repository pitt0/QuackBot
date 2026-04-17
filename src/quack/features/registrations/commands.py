import telegram
from telegram.ext import ContextTypes

from .repo import register_users


async def registration_command_callback(update: telegram.Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message is not None  # noqa: S101

    if not ctx.args:
        await update.message.reply_text("Usage: /register @user1 @user2")
        return

    users = set(ctx.args)
    registrations = register_users(update.message.chat_id, users)
    users_txt = "\n".join(f" • {u}" for u in registrations)
    await update.message.reply_text(f"👥 <h1>Users registered for this chat:<h1>\n\n{users_txt}")
