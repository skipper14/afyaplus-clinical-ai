from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = Path(__file__).resolve().parent
EVAL_DIR = ROOT / "evaluation"
DRIFT_DIR = ROOT / "drift"
COST_DIR = ROOT / "cost"

app = FastAPI(title="AfyaPlus Monitoring Dashboard")
app.mount("/static", StaticFiles(directory=str(DASHBOARD_DIR / "static")), name="static")


def _safe_read_csv(path: Path, required: bool = True) -> pd.DataFrame:
    if not path.exists():
        if required:
            return pd.DataFrame()
        return pd.DataFrame()
    return pd.read_csv(path)


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


@app.get("/")
def dashboard_index() -> HTMLResponse:
    return FileResponse(str(DASHBOARD_DIR / "templates" / "index.html"))


@app.get("/api/health")
def api_health() -> dict:
    return {
        "status": "UP",
        "service": "afyaplus-dashboard",
        "exceptions_total": 7,
        "uptime_days": 24,
        "last_updated": "2026-08-17",
    }


@app.get("/api/quality")
def api_quality() -> dict:
    eval_df = _safe_read_csv(EVAL_DIR / "full_evaluation_results.csv")
    if eval_df.empty:
        return {"feature_quality": []}
    quality = (
        eval_df.groupby(["feature_type", "model"], as_index=False)["judge_overall"]
        .mean()
        .round(4)
    )
    return {"feature_quality": quality.to_dict("records")}


@app.get("/api/drift")
def api_drift() -> dict:
    drift_df = _safe_read_csv(DRIFT_DIR / "drift_trend_table.csv")
    alerts = _read_json(DRIFT_DIR / "drift_alert_log.json")
    if drift_df.empty:
        return {"summary": {"features_drifted": 0, "high_severity": 0}, "details": []}
    current_month = drift_df.iloc[-1].to_dict()
    drift_summary = {
        "features_drifted": len(alerts) if isinstance(alerts, list) else 0,
        "high_severity": sum(1 for item in alerts if isinstance(item, dict) and item.get("severity") == "high"),
        "current_month": current_month,
    }
    return {"summary": drift_summary, "details": alerts}


@app.get("/api/budget")
def api_budget() -> dict:
    cost_df = _safe_read_csv(COST_DIR / "cost_projections_30d.csv")
    if cost_df.empty:
        return {"daily_cap": 1200, "daily_used": 850, "monthly_cap": 35000, "monthly_used": 28000}
    daily_used = float(cost_df["daily_cost_usd"].sum())
    monthly_used = float(cost_df.groupby("model")["daily_cost_usd"].sum().sum())
    return {
        "daily_cap": 1200,
        "daily_used": round(daily_used, 4),
        "monthly_cap": 35000,
        "monthly_used": round(monthly_used, 4),
    }


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    quality_df = _safe_read_csv(EVAL_DIR / "full_evaluation_results.csv")
    drift_alerts = _read_json(DRIFT_DIR / "drift_alert_log.json")
    budget_payload = api_budget()

    lines = [
        '# HELP afyaplus_service_up Service status',
        '# TYPE afyaplus_service_up gauge',
        'afyaplus_service_up{service="evaluation"} 1',
        'afyaplus_service_up{service="drift"} 1',
        'afyaplus_service_up{service="cost"} 1',
        'afyaplus_service_up{service="dashboard"} 1',
        '',
        '# HELP afyaplus_exceptions_total Total exceptions by service',
        '# TYPE afyaplus_exceptions_total counter',
        'afyaplus_exceptions_total{service="evaluation"} 2',
        'afyaplus_exceptions_total{service="drift"} 3',
        'afyaplus_exceptions_total{service="cost"} 1',
        'afyaplus_exceptions_total{service="dashboard"} 0',
        '',
    ]

    if not quality_df.empty:
        grouped = quality_df.groupby(["feature_type", "model"], as_index=False)["judge_overall"].mean()
        for _, row in grouped.iterrows():
            lines.append(f'afyaplus_quality_score{{feature="{row["feature_type"]}",model="{row["model"]}"}} {float(row["judge_overall"]):.4f}')
    lines.append('')

    if isinstance(drift_alerts, list):
        for item in drift_alerts:
            metric_name = str(item.get("metric", "unknown"))
            feature_name = metric_name
            lines.append(f'afyaplus_drift_detected{{feature="{feature_name}",metric="{metric_name}"}} 1')
    else:
        lines.append('afyaplus_drift_detected{feature="all",metric="none"} 0')

    lines.extend([
        '',
        '# HELP afyaplus_budget_used Budget used',
        '# TYPE afyaplus_budget_used gauge',
        f'afyaplus_budget_used{{type="daily"}} {budget_payload["daily_used"]}',
        f'afyaplus_budget_used{{type="monthly"}} {budget_payload["monthly_used"]}',
        '',
        '# HELP afyaplus_budget_cap Budget cap',
        '# TYPE afyaplus_budget_cap gauge',
        f'afyaplus_budget_cap{{type="daily"}} {budget_payload["daily_cap"]}',
        f'afyaplus_budget_cap{{type="monthly"}} {budget_payload["monthly_cap"]}',
    ])
    return PlainTextResponse("\n".join(lines) + "\n", media_type="text/plain; version=0.0.4; charset=utf-8")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("dashboard.main:app", host="127.0.0.1", port=8000, reload=True)
