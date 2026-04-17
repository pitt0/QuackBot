import telegram

from quack.core.registrations.repo import check_registrations

from .keyboard import build_keyboard
from .manager import SessionManager
from .presenter import format_payment_message

payments = SessionManager()


async def pay_command_callback(update: telegram.Update, _) -> None:
    assert update.message is not None  # noqa: S101
    assert update.message.from_user is not None  # noqa: S101

    users = check_registrations(update.message.chat_id)
    if not users:
        await update.message.reply_text("You can use /register @user1 @user2 to register those users for this chat")
        return

    keyboard = build_keyboard(update.message.chat_id, [(u, 1) for u in users], first_phase=True)
    msg = await update.message.reply_text(
        format_payment_message(dict.fromkeys(users, 0)),
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    payments.create_session(update.message.chat_id, msg.id, update.message.from_user.name, users)
