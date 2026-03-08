from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_keyboard(chat_id: int, users: list[tuple[str, int]], *, first_phase: bool = False) -> InlineKeyboardMarkup:
    buttons = [[], []]

    for user, present in users:
        mark = "✅" if present else "❌"

        buttons[0].append(InlineKeyboardButton(f"{mark} {user}", callback_data=f"toggle:{chat_id}:{user}"))

    buttons[1] = [InlineKeyboardButton("✅ Confirm & Split", callback_data=f"confirm:{chat_id}")]
    if first_phase:
        buttons[1].append(InlineKeyboardButton("❌ Cancel Session", callback_data=f"cancel:{chat_id}"))
    else:
        buttons[1].append(InlineKeyboardButton("↩️ Undo", callback_data=f"undo:{chat_id}"))

    return InlineKeyboardMarkup(buttons)
