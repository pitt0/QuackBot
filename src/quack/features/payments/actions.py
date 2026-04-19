from __future__ import annotations

from typing import TYPE_CHECKING

from .presenter import build_keyboard, format_payment_message
from .repo import persist_purchase

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from telegram import CallbackQuery

    from .manager import SessionManager
    from .session import PaymentSession


type ActionCallback = Callable[[SessionManager, PaymentSession, CallbackQuery, str | None], Coroutine[None, None, None]]
type Responses = dict[str, ActionCallback]


async def toggle_user(_, session: PaymentSession, query: CallbackQuery, user: str | None) -> None:
    if user is not None:
        session.toggle_user(user)

    keyboard = build_keyboard(session.chat_id, session.p_users(), first_phase=len(session.steps) == 0)
    await query.edit_message_reply_markup(reply_markup=keyboard)


async def undo_step(_m, session: PaymentSession, query: CallbackQuery, _=None) -> None:
    session.undo()

    text = format_payment_message(session.expenses(), label=session.label or "Active")
    keyboard = build_keyboard(session.chat_id, session.p_users(), first_phase=len(session.steps) == 0)
    await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=keyboard)


async def set_label_flag(_m, session: PaymentSession, query: CallbackQuery, _=None) -> None:
    message = await query.get_bot().send_message(text="Send a message with the new label", chat_id=session.chat_id)
    session.listen_label(message.id)


async def confirm_payment(manager: SessionManager, session: PaymentSession, query: CallbackQuery, _=None) -> None:
    persist_purchase(session.requested_by, session.expenses(), session.label)

    text = format_payment_message(session.expenses(), label=session.label or "Done")
    await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=None)

    manager.delete(session.id)


async def cancel_payment(manager: SessionManager, session: PaymentSession, query: CallbackQuery, _=None) -> None:
    text = "Purchase Cancelled"
    await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=None)

    manager.delete(session.id)


ACTION_RESPONSES: Responses = {
    "toggle": toggle_user,
    "undo": undo_step,
    "label": set_label_flag,
    "confirm": confirm_payment,
    "cancel": cancel_payment,
}
