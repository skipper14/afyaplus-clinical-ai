from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from evidently import ColumnMapping
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset
except Exception:  # pragma: no cover
    ColumnMapping = None
    Report = None
    DataDriftPreset = None

from drift.drift_simulation import build_monthly_dataset

BASE_DIR = Path(__file__).resolve().parent


def build_drift_summary(monthly_frames: list[pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for idx, df in enumerate(monthly_frames, start=1):
        rows.append(
            {
                "month": f"Month {idx}",
                "mean_rouge_l": round(float(df["rouge_l"].mean()), 4),
                "mean_latency_ms": round(float(df["latency_ms"].mean()), 2),
                "mean_input_token_length": round(float(df["input_token_length"].mean()), 2),
            }
        )
    trend_df = pd.DataFrame(rows)
    trend_df.to_csv(BASE_DIR / "drift_trend_table.csv", index=False)
    return trend_df


def detect_alerts(monthly_frames: list[pd.DataFrame]) -> list[dict]:
    baseline = monthly_frames[0]
    alerts = []
    for month_idx in range(1, len(monthly_frames)):
        comparison = monthly_frames[month_idx]
        for metric in ["input_token_length", "latency_ms", "rouge_l"]:
            baseline_mean = float(baseline[metric].mean())
            current_mean = float(comparison[metric].mean())
            delta_pct = abs(current_mean - baseline_mean) / max(baseline_mean, 1e-9)
            if delta_pct > 0.08 or comparison[metric].mean() < baseline[metric].mean() * 0.95:
                alerts.append({
                    "month": f"Month {month_idx + 1}",
                    "metric": metric,
                    "baseline_mean": round(baseline_mean, 4),
                    "current_mean": round(current_mean, 4),
                    "delta_pct": round(delta_pct, 4),
                    "severity": "medium" if delta_pct < 0.15 else "high",
                    "rule": "mean shift > 8% vs baseline",
                })
    with (BASE_DIR / "drift_alert_log.json").open("w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)
    return alerts


def generate_evidently_reports(monthly_frames: list[pd.DataFrame]) -> None:
    baseline = monthly_frames[0]
    for month_idx in range(1, len(monthly_frames) + 1):
        current = monthly_frames[month_idx - 1]
        if Report is None:
            report_html = """<html><body><h1>Fallback Drift Summary</h1><p>Evidently is not installed in this environment; a deterministic summary was generated instead.</p></body></html>"""
        else:
            report = Report(metrics=[DataDriftPreset()])
            column_mapping = ColumnMapping(
                numerical_features=[
                    "input_token_length",
                    "output_token_length",
                    "latency_ms",
                    "rouge_l",
                    "bleu",
                    "token_f1",
                    "judge_overall",
                ],
                categorical_features=["channel", "model_used"],
            )
            report.run(reference_data=baseline, current_data=current, column_mapping=column_mapping)
            report_html = report.get_html()
        with (BASE_DIR / f"evidently_month{month_idx}.html").open("w", encoding="utf-8") as f:
            f.write(report_html)


def main() -> None:
    monthly_frames = build_monthly_dataset()
    build_drift_summary(monthly_frames)
    generate_evidently_reports(monthly_frames)
    alerts = detect_alerts(monthly_frames)
    print(f"Saved drift trend table to {BASE_DIR / 'drift_trend_table.csv'}")
    print(f"Saved drift alert log to {BASE_DIR / 'drift_alert_log.json'}")
    print(f"Detected {len(alerts)} drift alerts")


if __name__ == "__main__":
    main()
