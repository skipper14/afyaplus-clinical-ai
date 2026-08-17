from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


MONTHLY_TRAFFIC_SIZE = 400


def simulate_month(month_index: int, baseline: pd.DataFrame | None = None) -> pd.DataFrame:
    rng = np.random.default_rng(42 + month_index)
    n = MONTHLY_TRAFFIC_SIZE
    channels = ["USSD", "Mobile App", "Web Portal"]
    model_choices = ["gpt-4o-mini", "gpt-4o"]
    months = ["Month 1", "Month 2", "Month 3"]

    if baseline is None:
        baseline = pd.DataFrame({
            "question_id": [f"Q{idx:03d}" for idx in range(1, n + 1)],
            "channel": rng.choice(channels, size=n),
            "model_used": rng.choice(model_choices, size=n, p=[0.8, 0.2]),
            "input_token_length": rng.normal(850, 120, size=n),
            "output_token_length": rng.normal(140, 35, size=n),
            "latency_ms": rng.normal(1050, 150, size=n),
            "rouge_l": rng.uniform(0.55, 0.82, size=n),
            "bleu": rng.uniform(0.42, 0.74, size=n),
            "token_f1": rng.uniform(0.52, 0.78, size=n),
            "judge_overall": rng.uniform(3.5, 4.8, size=n),
        })

    shift = 1 + month_index * 0.12
    input_token_length = baseline["input_token_length"].to_numpy() * (1 + month_index * 0.18) + rng.normal(0, 50, size=n)
    latency_ms = baseline["latency_ms"].to_numpy() * (1 + month_index * 0.16) + rng.normal(0, 60, size=n)
    rouge_l = baseline["rouge_l"].to_numpy() - month_index * 0.04 + rng.normal(0, 0.03, size=n)
    bleu = baseline["bleu"].to_numpy() - month_index * 0.03 + rng.normal(0, 0.02, size=n)
    token_f1 = baseline["token_f1"].to_numpy() - month_index * 0.05 + rng.normal(0, 0.02, size=n)
    judge_overall = baseline["judge_overall"].to_numpy() - month_index * 0.2 + rng.normal(0, 0.15, size=n)

    month_df = pd.DataFrame(
        {
            "question_id": [f"{months[month_index]}-Q{idx:03d}" for idx in range(1, n + 1)],
            "channel": rng.choice(channels, size=n),
            "model_used": rng.choice(model_choices, size=n, p=[0.8, 0.2]),
            "input_token_length": np.clip(input_token_length, 400, None),
            "output_token_length": np.clip(baseline["output_token_length"].to_numpy() * (1 + month_index * 0.08), 40, None),
            "latency_ms": np.clip(latency_ms, 350, None),
            "rouge_l": np.clip(rouge_l, 0.2, 0.95),
            "bleu": np.clip(bleu, 0.1, 0.9),
            "token_f1": np.clip(token_f1, 0.2, 0.95),
            "judge_overall": np.clip(judge_overall, 1.0, 5.0),
        }
    )
    month_df["month"] = months[month_index]
    return month_df


def build_monthly_dataset() -> list[pd.DataFrame]:
    baseline = simulate_month(0)
    return [simulate_month(i, baseline=baseline) for i in range(3)]


def main() -> None:
    output_dir = Path(__file__).resolve().parent
    monthly_frames = build_monthly_dataset()
    for idx, frame in enumerate(monthly_frames, start=1):
        frame.to_csv(output_dir / f"month{idx}_traffic.csv", index=False)
    print(f"Saved monthly drift datasets to {output_dir}")


if __name__ == "__main__":
    main()
