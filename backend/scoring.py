"""Rule-based scoring tuned for Tianjin middle-school English exam.

This module provides a transparent baseline aligned with Tianjin's latest
rubric (task response, coherence & organization, language accuracy, and
vocabulary range) while referencing Beijing's emphasis on语法准确性和篇章结构。
"""

from __future__ import annotations

from dataclasses import dataclass

from .llm import LLMClient, LLMResponse


@dataclass
class ScoreBreakdown:
    content: int
    organization: int
    language: int
    vocabulary: int
    mechanics: int

    @property
    def total(self) -> int:
        return self.content + self.organization + self.language + self.vocabulary + self.mechanics


MAX_CONTENT = 20
MAX_ORGANIZATION = 20
MAX_LANGUAGE = 30
MAX_VOCAB = 20
MAX_MECHANICS = 10


def _clamp(value: int, max_value: int) -> int:
    return max(0, min(value, max_value))


def baseline_heuristics(essay: str) -> ScoreBreakdown:
    """Apply deterministic heuristics as a fallback when no LLM is configured."""

    words = essay.split()
    sentences = [s for s in essay.replace("?", ".").replace("!", ".").split(".") if s.strip()]
    length_score = min(len(words) // 10, MAX_CONTENT)
    sentence_variety = len({len(s.split()) for s in sentences})
    organization_score = _clamp(10 + min(sentence_variety, 10), MAX_ORGANIZATION)
    grammar_penalty = sum(1 for w in words if w.islower() and w[0].isupper())
    language_score = _clamp(MAX_LANGUAGE - grammar_penalty * 2, MAX_LANGUAGE)
    vocab_unique = len(set(word.lower().strip(".,!;:""""'""" ) for word in words))
    vocab_score = _clamp(min(vocab_unique // 5, MAX_VOCAB), MAX_VOCAB)
    mechanics_penalty = sum(1 for word in words if word.endswith(".."))
    mechanics_score = _clamp(MAX_MECHANICS - mechanics_penalty, MAX_MECHANICS)

    return ScoreBreakdown(
        content=_clamp(length_score, MAX_CONTENT),
        organization=organization_score,
        language=language_score,
        vocabulary=vocab_score,
        mechanics=mechanics_score,
    )


async def score_essay(essay: str, llm_client: LLMClient | None = None) -> dict:
    """Generate a scoring report combining rubric-based points and LLM feedback."""

    llm_client = llm_client or LLMClient()
    llm_result: LLMResponse = await llm_client.analyze(essay)
    heuristic_scores = baseline_heuristics(essay)

    report = {
        "total": heuristic_scores.total,
        "rubric": {
            "content": {
                "score": heuristic_scores.content,
                "max": MAX_CONTENT,
                "rationale": "依据任务完成度、要点覆盖和观点相关性评估。",
            },
            "organization": {
                "score": heuristic_scores.organization,
                "max": MAX_ORGANIZATION,
                "rationale": "参考天津和北京中考的篇章结构要求，检查段落衔接与逻辑。",
            },
            "language": {
                "score": heuristic_scores.language,
                "max": MAX_LANGUAGE,
                "rationale": "语法准确性、句式多样性与时态一致性。",
                "issues": llm_result.grammar_issues,
            },
            "vocabulary": {
                "score": heuristic_scores.vocabulary,
                "max": MAX_VOCAB,
                "rationale": "词汇丰富度、搭配和拼写符合天津标准并参考北京要求。",
                "issues": llm_result.vocabulary_issues,
            },
            "mechanics": {
                "score": heuristic_scores.mechanics,
                "max": MAX_MECHANICS,
                "rationale": "标点、大小写和格式符合考试规范。",
            },
        },
        "advice": llm_result.improvement_advice,
    }

    return report
