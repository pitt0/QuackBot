from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence


class PaymentInput(TypedDict):
    users: Sequence[str]
    prices: list[int]


class PaymentSession:
    def __init__(self, chat_id: int, message_id: int, requested_by: str, users: Iterable[str]) -> None:
        self.chat_id = chat_id
        self.message_id = message_id
        self.requested_by = requested_by
        self.users = users

        self.label: str | None = None

        self.payers = set(users)

        self.steps: list[PaymentInput] = []

    def toggle_user(self, user: str) -> None:
        if user in self.payers:
            self.payers.remove(user)
        else:
            self.payers.add(user)

    def p_users(self) -> list[tuple[str, int]]:
        return [(u, 1 if u in self.payers else 0) for u in self.users]

    def add_prices(self, prices: list[float]) -> None:
        # NOTE: store price in cents so that floating point math does not trouble us
        self.steps.append({"users": tuple(self.payers), "prices": [int(p * 100) for p in prices]})

    def set_label(self, label: str) -> None:
        self.label = label

    def undo(self) -> None:
        self.steps.pop()

    def expenses(self) -> dict[str, int]:
        totals: dict[str, int] = defaultdict(int)

        for step in self.steps:
            for user in step["users"]:
                totals[user] += int(sum(step["prices"]) / len(step["users"]))

        return totals

    def total(self) -> float:
        return sum(sum(s["prices"]) for s in self.steps)
