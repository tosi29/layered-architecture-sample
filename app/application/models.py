from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatSession(BaseModel):
    session_id: str
    messages: List[Message] = Field(default_factory=list)

    def add_user_message(self, content: str) -> None:
        self.messages.append(Message(role="user", content=content))

    def add_bot_message(self, content: str) -> None:
        self.messages.append(Message(role="assistant", content=content))


class Feedback(BaseModel):
    session_id: str
    rating: int
    comment: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
