from collections import defaultdict

from quack.storage.payments import fetch_history


def get_debts() -> dict[str, dict[str, int]]:
    history = fetch_history()
    balance = defaultdict(lambda: defaultdict(int))

    final: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    # compute net balances
    for creditor_tag, *_, debtor_tag, debt_amount in history:
        balance[creditor_tag][debtor_tag] += debt_amount
        balance[debtor_tag][creditor_tag] -= debt_amount

    # normalize
    for debtor in balance:
        for creditor, amount in balance[debtor].items():
            if amount > 0:
                final[debtor][creditor] = amount

    return final
