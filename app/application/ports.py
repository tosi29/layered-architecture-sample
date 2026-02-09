from __future__ import annotations

from typing import Protocol

from .models import ChatSession, Feedback


class SessionRepository(Protocol):
    def get(self, session_id: str) -> ChatSession | None:
        ...

    def save(self, session: ChatSession) -> None:
        ...


class FeedbackRepository(Protocol):
    def save(self, feedback: Feedback) -> None:
        ...
