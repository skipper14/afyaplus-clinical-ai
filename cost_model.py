from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

import pandas as pd


@dataclass(frozen=True)
class ModelPrice:
    input_per_1k: float
    output_per_1k: float


MODEL_PRICING: Dict[str, ModelPrice] = {
    "gpt-4o-mini": ModelPrice(input_per_1k=0.15, output_per_1k=0.60),
    "gpt-4o": ModelPrice(input_per_1k=2.50, output_per_1k=10.00),
}


def cost_per_request(input_tokens: int, output_tokens: int, model_name: str) -> float:
    """Return the USD cost of a single inference request."""
    price = MODEL_PRICING[model_name]
    input_cost = (input_tokens / 1000.0) * price.input_per_1k
    output_cost = (output_tokens / 1000.0) * price.output_per_1k
    return round(float(input_cost + output_cost), 6)


def project_30_day_spend(
    daily_request_volume: int,
    model_split: Dict[str, float],
    avg_input_tokens: Dict[str, int],
    avg_output_tokens: Dict[str, int],
) -> pd.DataFrame:
    """Project daily and monthly spend using a fixed 75/25 routing split."""
    rows = []
    total_days = 30
    for day in range(1, total_days + 1):
        for model_name, share in model_split.items():
            requests = daily_request_volume * share
            input_tokens = avg_input_tokens[model_name]
            output_tokens = avg_output_tokens[model_name]
            per_request = cost_per_request(input_tokens, output_tokens, model_name)
            daily_cost = requests * per_request
            rows.append({
                "day": day,
                "model": model_name,
                "daily_request_volume": requests,
                "avg_input_tokens": input_tokens,
                "avg_output_tokens": output_tokens,
                "cost_per_request": per_request,
                "daily_cost_usd": round(float(daily_cost), 4),
            })
    df = pd.DataFrame(rows)
    monthly = (
        df.groupby("model", as_index=False)["daily_cost_usd"]
        .sum()
        .rename(columns={"daily_cost_usd": "monthly_cost_usd"})
    )
    return df, monthly


def structural_savings_analysis() -> pd.DataFrame:
    """Estimate savings from routing to the cheapest model that still meets quality gates."""
    data = [
        {"feature": "symptom_triage", "mini_cost": 0.0025, "gpt4o_cost": 0.0185, "mini_quality": 4.2, "gpt4o_quality": 4.5, "routes_to_mini": True},
        {"feature": "medication_guidance", "mini_cost": 0.0031, "gpt4o_cost": 0.0210, "mini_quality": 4.0, "gpt4o_quality": 4.6, "routes_to_mini": True},
        {"feature": "appointment_routing", "mini_cost": 0.0018, "gpt4o_cost": 0.0150, "mini_quality": 4.1, "gpt4o_quality": 4.4, "routes_to_mini": True},
    ]
    rows = []
    for feature in data:
        savings = feature["gpt4o_cost"] - feature["mini_cost"]
        rows.append(
            {
                "feature": feature["feature"],
                "mini_cost_per_request": feature["mini_cost"],
                "gpt4o_cost_per_request": feature["gpt4o_cost"],
                "savings_per_request": round(float(savings), 5),
                "quality_gap": round(float(feature["gpt4o_quality"] - feature["mini_quality"]), 4),
                "recommended_model": "gpt-4o-mini",
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    model_split = {"gpt-4o-mini": 0.75, "gpt-4o": 0.25}
    avg_input = {"gpt-4o-mini": 850, "gpt-4o": 1200}
    avg_output = {"gpt-4o-mini": 180, "gpt-4o": 260}
    daily, monthly = project_30_day_spend(2000, model_split, avg_input, avg_output)
    print(daily.head())
    print(monthly)
