from __future__ import annotations

from typing import TYPE_CHECKING

from .session import PaymentSession

if TYPE_CHECKING:
    from collections.abc import Iterable


class SessionManager:
    def __init__(self):
        self._sessions: dict[str, PaymentSession] = {}

    def create_session(self, chat_id: int, message_id: int, requested_by: str, users: Iterable[str]) -> PaymentSession:
        session = PaymentSession(chat_id, message_id, requested_by, users)
        self._sessions[str(chat_id)] = session
        return session

    def get(self, chat_id: str) -> PaymentSession | None:
        return self._sessions.get(chat_id)

    def delete(self, chat_id: str) -> None:
        if chat_id in self._sessions:
            del self._sessions[chat_id]
