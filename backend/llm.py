"""Utility for calling an OpenAI-compatible LLM endpoint."""

from __future__ import annotations

import httpx
from pydantic import BaseModel

from .config import settings


class LLMResponse(BaseModel):
    """Simplified LLM response payload for scoring and feedback."""

    grammar_issues: list[str]
    vocabulary_issues: list[str]
    improvement_advice: str


class LLMClient:
    """Client that wraps an OpenAI-compatible chat completion endpoint."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.llm_api_key
        self.base_url = base_url or settings.llm_base_url.rstrip("/")
        self.model = model or settings.llm_model

    async def analyze(self, essay: str) -> LLMResponse:
        """Call the LLM to obtain grammar/vocabulary feedback and improvement advice."""

        if not self.api_key:
            # When no API key is provided, return a deterministic placeholder response.
            return LLMResponse(
                grammar_issues=["缺少 API KEY，返回本地占位语法检查结果。"],
                vocabulary_issues=["缺少 API KEY，返回本地占位词汇检查结果。"],
                improvement_advice="请配置 LLM_API_KEY 以获得高质量的教师视角反馈。",
            )

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是一名天津中考阅卷英语特级教师，结合天津新课标评分细则并参考北京中考评分体系，"
                        "逐条指出作文中的语法和词汇问题，并提供提升建议。"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "请分析下面的英文作文，列出语法错误、词汇错误，并给出改进建议。"
                        "请用中文回答并保持条理清晰。\n\n作文：\n" + essay
                    ),
                },
            ],
            "temperature": 0.2,
        }

        async with httpx.AsyncClient(base_url=self.base_url, timeout=30) as client:
            response = await client.post("/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]

        # 简单解析，假设大模型按照约定返回三个板块
        grammar_issues: list[str] = []
        vocabulary_issues: list[str] = []
        improvement_advice = ""
        current = None
        for line in content.splitlines():
            normalized = line.strip(" -：:：")
            if not normalized:
                continue
            if normalized.startswith("语法"):
                current = "grammar"
                continue
            if normalized.startswith("词汇") or normalized.startswith("用词"):
                current = "vocab"
                continue
            if normalized.startswith("建议"):
                current = "advice"
                continue
            if current == "grammar":
                grammar_issues.append(normalized)
            elif current == "vocab":
                vocabulary_issues.append(normalized)
            elif current == "advice":
                improvement_advice += normalized + "\n"

        return LLMResponse(
            grammar_issues=grammar_issues or ["模型未返回具体语法问题。"],
            vocabulary_issues=vocabulary_issues or ["模型未返回具体词汇问题。"],
            improvement_advice=improvement_advice.strip() or "模型未返回改进建议。",
        )
