from collections import defaultdict

from .repo import fetch_history
from .types import TBalance


def get_balance(group_id: int) -> TBalance:
    history = fetch_history(group_id)
    balance = defaultdict(lambda: defaultdict(int))

    debts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    # compute net balances
    for creditor_tag, *_, debtor_tag, debt_amount in history:
        balance[creditor_tag][debtor_tag] += debt_amount
        balance[debtor_tag][creditor_tag] -= debt_amount

    # normalize
    for creditor in balance:
        for debtor, amount in balance[creditor].items():
            if amount > 0:
                debts[debtor][creditor] = amount

    # resolve circular balance
    capacity = min(c for debs in balance.values() for c in debs.values())
    if capacity > 0:
        pass

    return debts
