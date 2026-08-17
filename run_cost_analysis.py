from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cost.cost_model import MODEL_PRICING, cost_per_request, project_30_day_spend, structural_savings_analysis

BASE_DIR = Path(__file__).resolve().parent


def main() -> None:
    daily_request_volume = 2200
    model_split = {"gpt-4o-mini": 0.75, "gpt-4o": 0.25}
    avg_input_tokens = {"gpt-4o-mini": 850, "gpt-4o": 1200}
    avg_output_tokens = {"gpt-4o-mini": 180, "gpt-4o": 260}

    daily_cost_df, monthly_cost_df = project_30_day_spend(daily_request_volume, model_split, avg_input_tokens, avg_output_tokens)
    daily_cost_df.to_csv(BASE_DIR / "cost_projections_30d.csv", index=False)

    cost_rows = []
    for model_name in ["gpt-4o-mini", "gpt-4o"]:
        for config_name, input_tokens, output_tokens in [
            ("default", 850, 180),
            ("long_context", 1200, 260),
            ("high_risk", 1400, 300),
        ]:
            cost_rows.append({
                "model": model_name,
                "prompt_config": config_name,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_per_request_usd": round(cost_per_request(input_tokens, output_tokens, model_name), 6),
            })
    pd.DataFrame(cost_rows).to_csv(BASE_DIR / "cost_per_request.csv", index=False)

    structural_savings_analysis().to_csv(BASE_DIR / "structural_savings_analysis.csv", index=False)

    print(f"30-day cost projections saved to {BASE_DIR / 'cost_projections_30d.csv'}")
    print(f"Cost-per-request saved to {BASE_DIR / 'cost_per_request.csv'}")
    print(f"Savings analysis saved to {BASE_DIR / 'structural_savings_analysis.csv'}")


if __name__ == "__main__":
    main()
