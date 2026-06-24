from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.config import settings


def _build_demo_tools() -> types.Tool:
    return types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="update_form_field",
                description=(
                    "Persist one document field ONLY after the patient explicitly confirmed the value. "
                    "Never call before confirmation. Use exact field_id from schema. "
                    "Encode value as JSON string. The UI updates in real time."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "field_id": types.Schema(
                            type=types.Type.STRING,
                            description="Schema field id",
                        ),
                        "value": types.Schema(
                            type=types.Type.STRING,
                            description="JSON-encoded field value",
                        ),
                    },
                    required=["field_id", "value"],
                ),
            ),
            types.FunctionDeclaration(
                name="complete_demo",
                description=(
                    "Call ONLY after you have ALREADY spoken the mandatory closing thank-you "
                    "message aloud, asked if the patient has more questions, and they have "
                    "no further questions. All required fields should be filled. "
                    "After calling this, do not speak or continue the conversation."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "honorific": types.Schema(
                            type=types.Type.STRING,
                            description=(
                                "Patient honorific: Anh, Chị, Cô, Chú, Bác, Ông, Bà, anh chị, or anh/chị [Name], etc."
                            ),
                        ),
                        "summary": types.Schema(
                            type=types.Type.STRING,
                            description="Brief summary of what was completed",
                        ),
                    },
                    required=["honorific"],
                ),
            ),
        ]
    )


def create_live_ephemeral_token(system_instruction: str, demo_id: str) -> dict:
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
        "tools": [_build_demo_tools()],
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
