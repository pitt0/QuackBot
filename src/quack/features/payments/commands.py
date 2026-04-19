from __future__ import annotations

from typing import TYPE_CHECKING

from quack.core.registrations.repo import check_registrations

from .actions import ACTION_RESPONSES
from .listeners import register_prices, set_label
from .manager import SessionManager
from .presenter import build_keyboard, format_payment_message

if TYPE_CHECKING:
    import telegram


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


async def answer_button(update: telegram.Update, _) -> None:
    query = update.callback_query
    assert query is not None  # noqa: S101
    await query.answer()

    assert query.data is not None  # noqa: S101
    action, session_id, *user = query.data.split(":")

    session = payments.get(session_id)
    if not session:
        return

    callback = ACTION_RESPONSES[action]
    await callback(payments, session, query, user[0] if user else None)


async def register_updates(update: telegram.Update, _) -> None:
    assert update.message is not None  # noqa: S101

    session = payments.get(str(update.message.chat_id))
    if session is None:
        return

    if session.is_listening():
        await set_label(session, update.message)
    else:
        await register_prices(session, update.message)
