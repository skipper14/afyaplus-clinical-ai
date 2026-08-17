from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.evaluation_data import QUESTION_SET
from evaluation.evaluator import evaluate_dataset, quality_gate_status, summarize_by_model_feature

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR


def main() -> None:
    results = evaluate_dataset(model_names=("gpt-4o-mini", "gpt-4o"))
    results_path = OUTPUT_DIR / "full_evaluation_results.csv"
    report_path = OUTPUT_DIR / "llm_judge_matrix.csv"
    gate_path = OUTPUT_DIR / "quality_gate_log.txt"

    results.to_csv(results_path, index=False)

    summary_df = summarize_by_model_feature(results)
    summary_df.to_csv(report_path, index=False)

    gate_status = quality_gate_status(results)
    with gate_path.open("w", encoding="utf-8") as f:
        f.write("AfyaPlus Clinical Quality Gate Log\n")
        f.write("================================\n\n")
        for model_name in ("gpt-4o-mini", "gpt-4o"):
            status = gate_status.get(model_name, {})
            f.write(f"Model: {model_name}\n")
            f.write(f"  ROUGE-L threshold pass: {status.get('rouge_l_pass', False)}\n")
            f.write(f"  Judge overall threshold pass: {status.get('judge_overall_pass', False)}\n")
            f.write(f"  Overall gate pass: {status.get('overall_pass', False)}\n\n")

    summary_rows = []
    for model_name, model_df in results.groupby("model"):
        summary_rows.append(
            {
                "model": model_name,
                "mean_bleu": round(float(model_df["bleu"].mean()), 4),
                "mean_rouge_l": round(float(model_df["rouge_l"].mean()), 4),
                "mean_token_f1": round(float(model_df["token_f1"].mean()), 4),
                "mean_judge_overall": round(float(model_df["judge_overall"].mean()), 4),
                "mean_judge_correctness": round(float(model_df["judge_correctness"].mean()), 4),
            }
        )
    summary_df = pd.DataFrame(summary_rows)
    with results_path.open("a", encoding="utf-8") as f:
        f.write("\n")
        f.write("model,mean_bleu,mean_rouge_l,mean_token_f1,mean_judge_overall,mean_judge_correctness\n")
        for row in summary_rows:
            f.write(
                f"{row['model']},{row['mean_bleu']},{row['mean_rouge_l']},{row['mean_token_f1']},{row['mean_judge_overall']},{row['mean_judge_correctness']}\n"
            )

    print(f"Evaluation output written to {results_path}")
    print(f"Judge matrix written to {report_path}")
    print(f"Quality gate log written to {gate_path}")


if __name__ == "__main__":
    main()
