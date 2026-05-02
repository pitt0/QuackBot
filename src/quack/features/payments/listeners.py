from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .presenter import build_keyboard, format_payment_message

if TYPE_CHECKING:
    from telegram import Message

    from .session import PaymentSession


async def set_label(session: PaymentSession, message: Message) -> None:
    assert message.text is not None  # noqa: S101

    session.set_label(message.text)

    bot = message.get_bot()

    await bot.edit_message_text(
        text=format_payment_message(session.expenses(), session.label or "Active"),
        parse_mode="HTML",
        reply_markup=build_keyboard(session.chat_id, session.p_users()),
        chat_id=session.chat_id,
        message_id=session.message_id,
    )

    # await bot.delete_message(chat_id=session.chat_id, message_id=message.id)
    # await bot.delete_message(chat_id=session.chat_id, message_id=session.get_listener_message())


async def register_prices(session: PaymentSession, message: Message) -> None:
    assert message.text is not None  # noqa: S101

    if message.from_user is None or message.from_user.name != session.requested_by:
        return

    prices = re.findall(r"\d+(?:\.\d+)?", message.text)
    if not prices:
        return

    prices = [float(p) for p in prices]

    session.add_prices(prices)

    text = format_payment_message(session.expenses(), session.label or "Active")
    keyboard = build_keyboard(session.chat_id, session.p_users())

    await message.get_bot().edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard,
        chat_id=session.chat_id,
        message_id=session.message_id,
    )
