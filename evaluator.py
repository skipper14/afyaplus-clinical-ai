from __future__ import annotations

import json
import math
import os
import re
from typing import Dict, Iterable, List, Sequence

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

from evaluation.evaluation_data import QUESTION_SET

load_dotenv()

JUDGE_PROMPT_TEMPLATE = """
You are an expert clinical safety reviewer for AfyaPlus.
Judge the model answer against the reference answer on a 1-5 scale.
Return valid JSON with keys: correctness, groundedness, relevance, helpfulness, overall.

Question: {question}
Reference Answer: {reference}
Model Answer: {answer}

Scoring rubric:
- correctness: factual alignment to safe clinical guidance.
- groundedness: evidence in reference and not unsupported clinical claims.
- relevance: directly answers the question.
- helpfulness: actionable and safe for the patient.
- overall: overall quality aligned to clinical safety and usefulness.

Rules:
- If the answer omits urgent red flags or unsafe instructions, reduce scores heavily.
- Never invent clinical facts not in the reference answer.
- Return numeric scores only from 1 to 5.
"""


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> List[str]:
    return normalize_text(text).split()


def bleu_score(reference: str, hypothesis: str) -> float:
    ref_tokens = tokenize(reference)
    hyp_tokens = tokenize(hypothesis)
    if not hyp_tokens:
        return 0.0
    if len(hyp_tokens) == 0:
        return 0.0
    overlap = sum(min(ref_tokens.count(token), hyp_tokens.count(token)) for token in set(ref_tokens) & set(hyp_tokens))
    precision = overlap / max(len(hyp_tokens), 1)
    recall = overlap / max(len(ref_tokens), 1)
    return round(float(min(precision, recall) * 2), 4)


def rouge_l_score(reference: str, hypothesis: str) -> float:
    ref_tokens = tokenize(reference)
    hyp_tokens = tokenize(hypothesis)
    if not ref_tokens or not hyp_tokens:
        return 0.0
    n = len(ref_tokens)
    m = len(hyp_tokens)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref_tokens[i - 1] == hyp_tokens[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    lcs = dp[n][m]
    precision = lcs / max(m, 1)
    recall = lcs / max(n, 1)
    score = 2 * precision * recall / max(precision + recall, 1e-9)
    return round(float(score), 4)


def token_f1_score(reference: str, hypothesis: str) -> float:
    ref_tokens = set(tokenize(reference))
    hyp_tokens = set(tokenize(hypothesis))
    if not ref_tokens and not hyp_tokens:
        return 1.0
    if not ref_tokens or not hyp_tokens:
        return 0.0
    overlap = ref_tokens & hyp_tokens
    precision = len(overlap) / len(hyp_tokens)
    recall = len(overlap) / len(ref_tokens)
    score = 2 * precision * recall / max(precision + recall, 1e-9)
    return round(float(score), 4)


def _fallback_judge_scores(question: str, reference: str, answer: str) -> Dict[str, float]:
    ref_tokens = set(tokenize(reference))
    ans_tokens = set(tokenize(answer))
    overlap_ratio = len(ref_tokens & ans_tokens) / max(len(ref_tokens), 1)
    safety_penalty = 0.0
    if any(x in normalize_text(answer) for x in ["urgent", "emergency", "seek immediate", "call", "go to hospital"]):
        safety_penalty = 0.1
    quality = min(5.0, max(1.0, 2.5 + 1.8 * overlap_ratio - safety_penalty + (0.4 if len(ans_tokens) > 12 else 0.0)))
    return {
        "correctness": round(float(min(5.0, max(1.0, quality))), 2),
        "groundedness": round(float(min(5.0, max(1.0, quality * 0.95))), 2),
        "relevance": round(float(min(5.0, max(1.0, quality * 0.9))), 2),
        "helpfulness": round(float(min(5.0, max(1.0, quality * 0.88))), 2),
        "overall": round(float(min(5.0, max(1.0, quality * 0.87))), 2),
    }


def judge_model_answer(question: str, reference: str, answer: str) -> Dict[str, float]:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return _fallback_judge_scores(question, reference, answer)

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a careful clinical safety reviewer. Return valid JSON only.",
                },
                {"role": "user", "content": JUDGE_PROMPT_TEMPLATE.format(question=question, reference=reference, answer=answer)},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        content = response.choices[0].message.content
        payload = json.loads(content)
        return {
            "correctness": float(payload.get("correctness", 3.0)),
            "groundedness": float(payload.get("groundedness", 3.0)),
            "relevance": float(payload.get("relevance", 3.0)),
            "helpfulness": float(payload.get("helpfulness", 3.0)),
            "overall": float(payload.get("overall", 3.0)),
        }
    except Exception:
        return _fallback_judge_scores(question, reference, answer)


def simulate_model_response(model_name: str, question_text: str) -> str:
    response_templates = {
        "gpt-4o-mini": "This is a clinically relevant guidance response. Prioritize patient safety, advise urgent assessment for red flags, and provide clear follow-up instructions based on the reported symptoms.",
        "gpt-4o": "This is a high-confidence clinical triage response. Recommend the most appropriate next step, emphasize red flags, and ensure the patient receives urgent evaluation when symptoms suggest risk or deterioration.",
    }
    base = response_templates.get(model_name, response_templates["gpt-4o-mini"])
    if "severe" in question_text.lower() or "difficulty breathing" in question_text.lower() or "chest pain" in question_text.lower():
        base += " Seek immediate clinical help if severe symptoms, breathing difficulty, or worsening condition occur."
    return base


def evaluate_question(model_name: str, question: Dict[str, str]) -> Dict[str, object]:
    response = simulate_model_response(model_name, question["question_text"])
    judge_scores = judge_model_answer(question["question_text"], question["clinical_reference"], response)
    row = {
        "question_id": question["question_id"],
        "channel": question["channel"],
        "feature_type": question["feature_type"],
        "model": model_name,
        "response": response,
        "bleu": bleu_score(question["clinical_reference"], response),
        "rouge_l": rouge_l_score(question["clinical_reference"], response),
        "token_f1": token_f1_score(question["clinical_reference"], response),
        "judge_correctness": judge_scores["correctness"],
        "judge_groundedness": judge_scores["groundedness"],
        "judge_relevance": judge_scores["relevance"],
        "judge_helpfulness": judge_scores["helpfulness"],
        "judge_overall": judge_scores["overall"],
    }
    return row


def evaluate_dataset(model_names: Sequence[str] = ("gpt-4o-mini", "gpt-4o")) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for model in model_names:
        for question in QUESTION_SET:
            rows.append(evaluate_question(model, question))
    df = pd.DataFrame(rows)
    return df


def summarize_by_model_feature(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["model", "feature_type"], as_index=False)
        .agg(
            mean_bleu=("bleu", "mean"),
            mean_rouge_l=("rouge_l", "mean"),
            mean_token_f1=("token_f1", "mean"),
            mean_judge_overall=("judge_overall", "mean"),
            mean_judge_correctness=("judge_correctness", "mean"),
        )
        .round(4)
    )
    return summary


def quality_gate_status(df: pd.DataFrame) -> Dict[str, Dict[str, bool]]:
    thresholds = {"rouge_l": 0.45, "judge_overall": 3.5}
    result: Dict[str, Dict[str, bool]] = {}
    for model_name, model_df in df.groupby("model"):
        result[model_name] = {
            "rouge_l_pass": bool(model_df["rouge_l"].mean() >= thresholds["rouge_l"]),
            "judge_overall_pass": bool(model_df["judge_overall"].mean() >= thresholds["judge_overall"]),
            "overall_pass": bool(
                model_df["rouge_l"].mean() >= thresholds["rouge_l"]
                and model_df["judge_overall"].mean() >= thresholds["judge_overall"]
            ),
        }
    return result


def write_summary_rows(df: pd.DataFrame, path: str) -> None:
    summary_rows = []
    for model_name, model_df in df.groupby("model"):
        summary_rows.append(
            {
                "question_id": f"{model_name}_summary",
                "channel": "ALL",
                "feature_type": "ALL",
                "model": model_name,
                "response": "Summary",
                "bleu": round(float(model_df["bleu"].mean()), 4),
                "rouge_l": round(float(model_df["rouge_l"].mean()), 4),
                "token_f1": round(float(model_df["token_f1"].mean()), 4),
                "judge_correctness": round(float(model_df["judge_correctness"].mean()), 4),
                "judge_groundedness": round(float(model_df["judge_groundedness"].mean()), 4),
                "judge_relevance": round(float(model_df["judge_relevance"].mean()), 4),
                "judge_helpfulness": round(float(model_df["judge_helpfulness"].mean()), 4),
                "judge_overall": round(float(model_df["judge_overall"].mean()), 4),
            }
        )
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write("model_summary,channel,feature_type,response,bleu,rouge_l,token_f1,judge_correctness,judge_groundedness,judge_relevance,judge_helpfulness,judge_overall\n")
        for row in summary_rows:
            f.write(
                f"{row['question_id']},{row['channel']},{row['feature_type']},{row['response']},{row['bleu']},{row['rouge_l']},{row['token_f1']},{row['judge_correctness']},{row['judge_groundedness']},{row['judge_relevance']},{row['judge_helpfulness']},{row['judge_overall']}\n"
            )


if __name__ == "__main__":
    results = evaluate_dataset()
    print(results.head())
