from __future__ import annotations

from .models import ChatSession, Feedback
from .ports import FeedbackRepository, SessionRepository


class ChatService:
    def __init__(self, sessions: SessionRepository, feedback: FeedbackRepository) -> None:
        self._sessions = sessions
        self._feedback = feedback

    def get_or_create_session(self, session_id: str) -> ChatSession:
        session = self._sessions.get(session_id)
        if session is None:
            session = ChatSession(session_id=session_id)
            self._sessions.save(session)
        return session

    def handle_message(self, session_id: str, content: str) -> ChatSession:
        session = self.get_or_create_session(session_id)
        session.add_user_message(content)
        session.add_bot_message(self._generate_reply(content))
        self._sessions.save(session)
        return session

    def save_feedback(self, feedback: Feedback) -> None:
        self._feedback.save(feedback)

    @staticmethod
    def _generate_reply(content: str) -> str:
        # Placeholder reply. Replace with real model integration.
        return f"You said: {content}"
