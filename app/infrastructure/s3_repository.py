from __future__ import annotations

import json
import os
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

from app.application.models import ChatSession, Feedback
from app.application.ports import FeedbackRepository, SessionRepository


class S3SessionRepository(SessionRepository):
    def __init__(self, bucket: str, prefix: str = "sessions") -> None:
        self._bucket = bucket
        self._prefix = prefix
        self._s3 = boto3.client("s3")

    def get(self, session_id: str) -> ChatSession | None:
        key = f"{self._prefix}/{session_id}.json"
        try:
            obj = self._s3.get_object(Bucket=self._bucket, Key=key)
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in {"NoSuchKey", "404"}:
                return None
            raise
        body = obj["Body"].read().decode("utf-8")
        payload = json.loads(body)
        return ChatSession.model_validate(payload)

    def save(self, session: ChatSession) -> None:
        key = f"{self._prefix}/{session.session_id}.json"
        payload = session.model_dump(mode="json")
        self._s3.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
        )


class S3FeedbackRepository(FeedbackRepository):
    def __init__(self, bucket: str, prefix: str = "feedback") -> None:
        self._bucket = bucket
        self._prefix = prefix
        self._s3 = boto3.client("s3")

    def save(self, feedback: Feedback) -> None:
        timestamp = datetime.utcnow().isoformat()
        key = f"{self._prefix}/{feedback.session_id}/{timestamp}.json"
        payload = feedback.model_dump(mode="json")
        self._s3.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
        )


def build_repositories_from_env() -> tuple[S3SessionRepository, S3FeedbackRepository]:
    bucket = os.environ.get("AWS_S3_BUCKET")
    if not bucket:
        raise RuntimeError("AWS_S3_BUCKET is required")
    return S3SessionRepository(bucket=bucket), S3FeedbackRepository(bucket=bucket)
