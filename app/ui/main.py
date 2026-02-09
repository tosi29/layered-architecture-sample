from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.application.models import Feedback
from app.application.services import ChatService
from app.infrastructure.s3_repository import build_repositories_from_env


app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    sessions_repo, feedback_repo = build_repositories_from_env()
    service = ChatService(sessions_repo, feedback_repo)
    session = service.get_or_create_session(session_id)

    response = TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "session": session,
        },
    )
    if request.cookies.get("session_id") != session_id:
        response.set_cookie("session_id", session_id, httponly=True)
    return response


@app.post("/chat")
def chat(request: Request, message: str = Form(...)) -> JSONResponse:
    session_id = request.cookies.get("session_id")
    if not session_id:
        return JSONResponse({"error": "missing session"}, status_code=400)

    sessions_repo, feedback_repo = build_repositories_from_env()
    service = ChatService(sessions_repo, feedback_repo)
    session = service.handle_message(session_id, message)

    return JSONResponse({"messages": [m.model_dump(mode="json") for m in session.messages]})


@app.post("/feedback")
def feedback(
    request: Request,
    rating: int = Form(...),
    comment: str | None = Form(None),
) -> JSONResponse:
    session_id = request.cookies.get("session_id")
    if not session_id:
        return JSONResponse({"error": "missing session"}, status_code=400)

    sessions_repo, feedback_repo = build_repositories_from_env()
    service = ChatService(sessions_repo, feedback_repo)
    service.save_feedback(Feedback(session_id=session_id, rating=rating, comment=comment))
    return JSONResponse({"ok": True})


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "bucket": os.environ.get("AWS_S3_BUCKET")}
