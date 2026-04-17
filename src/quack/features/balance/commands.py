import telegram

from .service import get_balance


async def balance_command_callback(update: telegram.Update, _) -> None:
    assert update.message is not None  # noqa: S101

    debts = get_balance(update.message.chat_id)
    form = "\n\n".join(
        f"{creditor} owes:\n" + "\n".join(f" • €{round(amount / 1000, 2)} ➡️ {debtor}" for debtor, amount in debtors.items())
        for creditor, debtors in debts.items()
    )

    balance_msg = f"⚖️ <b>Current Balances</b>\n\n{form}"
    await update.message.reply_text(text=balance_msg, parse_mode="HTML")
