from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from google import genai
from google.genai import errors as genai_errors

from app.config import settings


def create_live_ephemeral_token(system_instruction: str) -> dict:
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY is not configured on the server",
        )

    now = datetime.now(timezone.utc)
    model = settings.gemini_live_model

    live_config = {
        "response_modalities": ["AUDIO"],
        "system_instruction": system_instruction,
        "speech_config": {
            "voice_config": {
                "prebuilt_voice_config": {"voice_name": "Aoede"},
            }
        },
        "input_audio_transcription": {},
        "output_audio_transcription": {},
    }

    client = genai.Client(
        api_key=settings.gemini_api_key,
        http_options={"api_version": "v1alpha"},
    )

    try:
        token = client.auth_tokens.create(
            config={
                "uses": 1,
                "expire_time": (now + timedelta(minutes=30)).isoformat(),
                "new_session_expire_time": (now + timedelta(minutes=2)).isoformat(),
                "live_connect_constraints": {
                    "model": model,
                    "config": live_config,
                },
                "http_options": {"api_version": "v1alpha"},
            }
        )
    except genai_errors.ClientError as exc:
        message = str(exc)
        if "suspended" in message.lower():
            detail = "Gemini API key bị suspend. Tạo key mới tại https://aistudio.google.com/apikey"
        elif "PERMISSION_DENIED" in message:
            detail = "Gemini API key không có quyền. Kiểm tra key và bật Generative Language API."
        else:
            detail = f"Gemini API error: {message}"
        raise HTTPException(status_code=502, detail=detail) from exc

    return {
        "token": token.name,
        "model": model,
        "expires_at": (now + timedelta(minutes=30)).isoformat(),
    }
