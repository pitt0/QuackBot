import re

import telegram
from telegram.ext import ContextTypes

from quack.payments.debts import get_debts
from quack.payments.keyboard import build_keyboard
from quack.payments.manager import SessionManager
from quack.registration.services import persist_users_tags
from quack.storage.payments import persist_purchase
from quack.storage.registrations import check_registrations, persist_alias, register_users

session_manager = SessionManager()


def format_payment_message(expenses: dict[str, int], label: str = "Active") -> str:
    total = round(sum(e for e in expenses.values()) / 1000, 2)
    users = "\n\n".join(f" • {u} — €{round(e / 1000, 2)} ✅" for u, e in expenses.items())
    return f"""
🛒 <b>New Purchase:</b> {label}

💰 <b>Total Spend:</b> €{total}

👥 <b>Participants</b>

{users}

    """


async def start_callback(update: telegram.Update, _) -> None:
    if update.message is None:
        return

    await update.message.reply_text("🏠 Roommate Pay Bot\n\nCommands:\n/purchase user1 user2\n/balance\n/expenses")


async def pay_command_callback(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message is not None  # noqa: S101
    assert update.message.from_user is not None  # noqa: S101

    users = set(context.args or []) or check_registrations(update.message.chat_id)
    if not users:
        await update.message.reply_text(
            "Usage: /purchase user1 user2\n\nYou can use /register to automate users recognitions in this channel",
        )
        return

    alias_miss = persist_users_tags(users)
    if alias_miss is not None:
        await update.message.reply_text(
            f"There is no user with alias {alias_miss}\n\nYou can register an alias with /alias @<user tag> <user alias>",
        )
        return

    keyboard = build_keyboard(update.message.chat_id, [(u, 1) for u in users], first_phase=True)
    msg = await update.message.reply_text(
        format_payment_message(dict.fromkeys(users, 0)),
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    session_manager.create_session(update.message.chat_id, msg.id, update.message.from_user.name, users)


async def registration_command_callback(update: telegram.Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message is not None  # noqa: S101

    if not ctx.args:
        await update.message.reply_text("Usage: /register @user1 @user2")
        return

    users = set(ctx.args)
    registrations = register_users(update.message.chat_id, users)
    users_txt = "\n".join(f" • {u}" for u in registrations)
    await update.message.reply_text(f"👥 <h1>Users registered for this chat:<h1>\n\n{users_txt}")


async def alias_command_callback(update: telegram.Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message is not None  # noqa: S101

    if not ctx.args:
        await update.message.reply_text("Usage: /alias @<user tag> <user alias>")
        return

    tag, *alias = ctx.args
    persist_alias(tag, " ".join(alias))

    await update.message.reply_text("Alias registration complete")


async def balance_command_callback(update: telegram.Update, _) -> None:
    assert update.message is not None  # noqa: S101
    debts = get_debts()
    form = "\n\n".join(
        f"{creditor} owes:\n" + "\n".join(f" • €{round(amount / 1000, 2)} ➡️ {debtor}" for debtor, amount in debtors.items())
        for creditor, debtors in debts.items()
    )

    balance_msg = f"⚖️ <b>Current Balances</b>\n\n{form}"
    await update.message.reply_text(text=balance_msg, parse_mode="HTML")


async def buttons(update: telegram.Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    assert query is not None  # noqa: S101
    await query.answer()

    assert query.data is not None  # noqa: S101
    action, session_id, *rest = query.data.split(":")

    session = session_manager.get(session_id)
    if not session:
        return

    if action == "label":
        message = await ctx.bot.send_message(text="Send a message with the new label", chat_id=session.chat_id)
        session.listen_label(message.id)
        return

    if action == "toggle":
        user = rest[0]
        session.toggle_user(user)

        await query.edit_message_reply_markup(
            reply_markup=build_keyboard(session.chat_id, session.p_users(), first_phase=len(session.steps) == 0),
        )
        return

    if action == "undo":
        session.undo()
        await ctx.bot.edit_message_text(
            text=format_payment_message(session.expenses(), label=session.label or "Active"),
            chat_id=session.chat_id,
            message_id=session.message_id,
            parse_mode="HTML",
            reply_markup=build_keyboard(session.chat_id, session.p_users(), first_phase=len(session.steps) == 0),
        )
        return

    if action == "confirm":
        persist_purchase(session.requested_by, session.expenses(), session.label)
        text = format_payment_message(session.expenses(), label=session.label or "Done")

    else:  # NOTE: action = "cancel"
        text = "Purchase Cancelled"

    await ctx.bot.edit_message_text(
        text=text,
        chat_id=session.chat_id,
        message_id=session.message_id,
        parse_mode="HTML",
        reply_markup=None,
    )
    session_manager.delete(session_id)
    return


async def label_listener(update: telegram.Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    assert message is not None  # noqa: S101
    assert message.text is not None  # noqa: S101

    session = session_manager.get(str(message.chat_id))
    if not session or not session.payers:
        return

    if message.from_user is None or message.from_user.name != session.requested_by:
        return

    if session.is_listening():
        session.set_label(message.text)

    await ctx.bot.edit_message_text(
        text=format_payment_message(session.expenses(), session.label or "Active"),
        parse_mode="HTML",
        reply_markup=build_keyboard(session.chat_id, session.p_users()),
        chat_id=session.chat_id,
        message_id=session.message_id,
    )

    await ctx.bot.delete_message(chat_id=session.chat_id, message_id=message.id)
    await ctx.bot.delete_message(chat_id=session.chat_id, message_id=session.get_listener_message())


async def price_listener(update: telegram.Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    assert message is not None  # noqa: S101
    assert message.text is not None  # noqa: S101

    session = session_manager.get(str(message.chat_id))
    if not session or not session.payers or session.is_listening():
        return

    if message.from_user is None or message.from_user.name != session.requested_by:
        return

    prices = re.findall(r"\d+(?:\.\d+)?", message.text)
    if not prices:
        return

    prices = [float(p) for p in prices]

    session.add_prices(prices)

    await ctx.bot.edit_message_text(
        text=format_payment_message(session.expenses(), session.label or "Active"),
        parse_mode="HTML",
        reply_markup=build_keyboard(session.chat_id, session.p_users()),
        chat_id=session.chat_id,
        message_id=session.message_id,
    )
