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
        self._listening: bool = False
        self._listener_message_id: int | None = None

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
        if len(self.payers) == 0:
            return

        # NOTE: store price in thousandths to ensure maximum accuracy without errors
        self.steps.append({"users": tuple(self.payers), "prices": [int(p * 1000) for p in prices]})

    def listen_label(self, message_id: int) -> None:
        self._listening = True
        self._listener_message_id = message_id

    def is_listening(self) -> bool:
        return self._listening

    def get_listener_message(self) -> int:
        m_id = self._listener_message_id
        self._listener_message_id = None
        if not isinstance(m_id, int):
            raise TypeError
        return m_id

    def set_label(self, label: str) -> None:
        if self._listening:
            self.label = label
            self._listening = False

    def undo(self) -> None:
        self.steps.pop()

    def expenses(self) -> dict[str, int]:
        """Get the total value of expenses in the current session in thousandths of euros integer precision."""
        totals: dict[str, int] = defaultdict(int)

        for step in self.steps:
            for user in step["users"]:
                totals[user] += int(sum(step["prices"]) / len(step["users"]))

        return totals

    def total(self) -> float:
        return sum(sum(s["prices"]) for s in self.steps)
