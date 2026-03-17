from collections import defaultdict

from quack.storage.payments import fetch_history

type TBalance = dict[str, dict[str, int]]


def longest_cycles(graph: TBalance) -> list[list[str]]:
    creditors_set = set(graph.keys())
    debtors_set = {d for debts in graph.values() for d in debts}

    nodes = creditors_set & debtors_set

    best_paths = []

    def dfs(start: str, node: str, visited: set, path: list):
        nonlocal best_paths

        visited.add(node)
        path.append(node)

        for nxt in graph.get(node, {}):
            if nxt == start and len(path) > 1:
                best_paths.append([*path, start])

            elif nxt not in visited:
                dfs(start, nxt, visited, path)

        path.pop()
        visited.remove(node)

    for n in nodes:
        dfs(n, n, set(), [])

    return best_paths


def resolve_circular(balances: TBalance) -> TBalance:
    cycles = longest_cycles(balances)
    for cycle in cycles:
        name = next(iter(cycle))

    return balances


def get_debts() -> TBalance:
    history = fetch_history()
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
