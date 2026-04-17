def format_payment_message(expenses: dict[str, int], label: str = "Active") -> str:
    total = round(sum(e for e in expenses.values()) / 1000, 2)
    users = "\n\n".join(f" • {u} — €{round(e / 1000, 2)} ✅" for u, e in expenses.items())
    return f"""
🛒 <b>New Purchase:</b> {label}

💰 <b>Total Spend:</b> €{total}

👥 <b>Participants</b>

{users}

    """
