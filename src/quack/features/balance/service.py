from collections import defaultdict

from .repo import fetch_balance
from .types import TBalance


def get_balance(group_id: int) -> TBalance:
    balance = fetch_balance(group_id)
    creditors = []
    debtors = []

    for user, bal in balance:
        if bal > 0:
            creditors.append([user, bal])
        elif bal < 0:
            debtors.append([user, -bal])

    # sort biggest first (your "lesser side" logic emerges from this)
    creditors.sort(key=lambda x: -x[1])
    debtors.sort(key=lambda x: -x[1])

    i = j = 0
    result: TBalance = defaultdict(lambda: defaultdict(int))

    while i < len(creditors) and j < len(debtors):
        c_user, c_amt = creditors[i]
        d_user, d_amt = debtors[j]

        # settle the smaller side
        amount = min(c_amt, d_amt)

        result[d_user][c_user] += amount

        creditors[i][1] -= amount
        debtors[j][1] -= amount

        if creditors[i][1] == 0:
            i += 1
        if debtors[j][1] == 0:
            j += 1

    return result
