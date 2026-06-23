from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import settings
from app.demo_prompts import DEMO_PROMPTS, get_demo_instruction
from app.gemini_live import create_live_ephemeral_token

app = FastAPI(title="VN Clinic AI Voice API", version="1.0.0")

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LiveTokenRequest(BaseModel):
    demo_id: str = Field(..., pattern=r"^0[1-8]$")
    language: str = "vi"


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "vnclinic-voice-api",
        "gemini_configured": bool(settings.gemini_api_key),
        "demos": list(DEMO_PROMPTS.keys()),
    }


@app.post("/api/demo/live-token")
def demo_live_token(payload: LiveTokenRequest):
    try:
        instruction = get_demo_instruction(payload.demo_id, payload.language)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return create_live_ephemeral_token(instruction)
