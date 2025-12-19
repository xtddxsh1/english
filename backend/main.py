from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .llm import LLMClient
from .scoring import score_essay

app = FastAPI(title="Tianjin English Essay Scorer", version="0.1.0")


class EssayRequest(BaseModel):
    essay: str = Field(..., description="学生英文作文全文")


class ScoreResponse(BaseModel):
    total: int
    rubric: dict
    advice: str


@app.post("/score", response_model=ScoreResponse)
async def score_endpoint(payload: EssayRequest):
    """Score an essay and return rubric-aligned feedback."""

    result = await score_essay(payload.essay, llm_client=LLMClient())
    return ScoreResponse(**result)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
