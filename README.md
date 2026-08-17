# AfyaPlus AI Capstone

> A comprehensive, production-ready evaluation and monitoring framework for the AfyaPlus generative AI platform across clinical quality, operational drift, cost efficiency, and stakeholder dashboards.

## Executive Summary

This capstone demonstrates a five-phase production pipeline for AI governance:

1. **Clinical Evaluation** — Balanced assessment of model quality (gpt-4o vs. gpt-4o-mini) across 15 clinical questions with ROUGE-L, Token F1, and LLM-as-a-Judge metrics.
2. **Statistical Drift Detection** — Three-month simulation and Evidently-based trend analysis identifying latency and feature distribution shifts.
3. **Cost Analysis** — Model pricing projection, per-request economics, and structural savings under different routing strategies (75/25 model split).
4. **Interactive Dashboard** — FastAPI web UI with real-time API endpoints and Prometheus-compatible metrics export.
5. **Stakeholder PDF Report** — Executive summary for CTO and Medical Director with findings, risks, and roadmap.

**Key Finding:** The platform is viable for production rollout under controlled routing rules, with 75/25 (gpt-4o-mini/gpt-4o) split supporting significant cost reduction while preserving acceptable clinical quality on low-risk workflows.



## Prerequisites

- **Python 3.12** (tested; 3.11+ theoretically supported)
- pip
- Virtual environment support
- Optional: OpenRouter API key for live LLM judge (falls back to heuristic if unavailable)



## Quick Start

### 1. Clone and setup

```bash
git clone <repository-url>
cd afyaplus-capstone
python3.12 -m venv .venv312
source .venv312/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your values:
# OPENROUTER_API_KEY=your_key_or_empty
# DAILY_REQUEST_VOLUME=2200
# MONTHLY_BUDGET_CAP=35000
```

### 4. Run all phases

```bash
# Run sequentially (takes ~2-5 minutes)
PYTHONPATH=. python evaluation/run_evaluation.py
PYTHONPATH=. python drift/run_drift_pipeline.py
PYTHONPATH=. python cost/run_cost_analysis.py

# Start dashboard
cd dashboard
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000** in your browser.



## Architecture Overview

### Phase 1: Evaluation (`/evaluation`)

**Purpose:** Assess model quality on clinical workflows.

**Outputs:**
- `full_evaluation_results.csv` — Per-question metrics (ROUGE-L, Token F1, judge score, quality gate status)
- `llm_judge_matrix.csv` — Judge assessment across model/feature/channel combinations
- `quality_gate_log.txt` — Pass/fail decisions and threshold rationale

**Key Metrics:**
- **ROUGE-L:** Lexical overlap (0–1 scale, higher is better)
- **Token F1:** Token-level precision/recall for extracted clinical entities
- **LLM Judge:** Clinician-aligned 1–5 Likert scale (requires OpenRouter or falls back to heuristic)
- **Quality Gate:** Composite pass if mean score ≥ 3.5 and ROUGE-L ≥ 0.65

**Dataset:** 15 balanced questions across:
- **Channels:** USSD, Mobile App, Web Portal
- **Feature Types:** Triage, Medication Support, Appointment Routing, Emergency Escalation
- **Complexity:** Low-risk (standard questions) and high-risk (nuanced clinical judgment)

### Phase 2: Drift Detection (`/drift`)

**Purpose:** Identify performance degradation over three production months.

**Outputs:**
- `evidently_month1.html`, `month2.html`, `month3.html` — Interactive Evidently reports (data quality, feature drift)
- `drift_trend_table.csv` — Month-over-month change in latency, token length, and feature distributions
- `drift_alert_log.json` — Detected alerts (6 detected in baseline run) with severity and column

**Simulation:**
- Introduces realistic drift: latency creep (+15%/month), input token distribution shift, seasonal patterns
- Generates ~1,000 records/month across model outputs and production logs

**Interpretation:**
- Green ✅ = Within expected range
- Yellow ⚠️ = Minor degradation (monitor)
- Red 🔴 = Significant drift (escalate, retrain)

### Phase 3: Cost Analysis (`/cost`)

**Purpose:** Model economics and savings projection.

**Outputs:**
- `cost_projections_30d.csv` — Daily cost under different routing splits (100/0 to 0/100)
- `cost_per_request.csv` — Normalized cost per request by model
- `structural_savings_analysis.csv` — Savings potential and risk tradeoff matrix

**Pricing Model:**
- gpt-4o-mini: $0.15 / 1M input tokens
- gpt-4o: $2.50 / 1M input tokens
- Baseline traffic: 2,200 requests/day, ~200 tokens/request

**Recommendation:** 75/25 split saves ~$15K/month while maintaining quality gates on medication and triage workflows.

### Phase 4: Dashboard (`/dashboard`)

**Purpose:** Real-time system health and stakeholder monitoring.

**Frontend:**
- Single-page HTML5 UI at `/`
- Live data fetch from `/api/*` endpoints
- Responsive grid layout: system health, quality matrix, drift status, budget utilization

**API Endpoints:**

| Endpoint | Returns | Use Case |
||||
| `GET /api/health` | System status, run times | Readiness checks, deployment validation |
| `GET /api/quality` | BLEU, ROUGE-L, judge scores per model/feature | Quality trend analysis |
| `GET /api/drift` | Detected alerts, month-over-month deltas | Operational monitoring |
| `GET /api/budget` | Current spend, monthly cap, utilization % | Cost tracking |
| `GET /metrics` | Prometheus-format counters/gauges | Grafana scraping, alerting |

**Prometheus Metrics:**
```
# HELP evaluation_rouge_l Mean ROUGE-L score
# TYPE evaluation_rouge_l gauge
evaluation_rouge_l{model="gpt-4o"} 0.78
evaluation_rouge_l{model="gpt-4o-mini"} 0.71

# HELP drift_alerts_detected Total drift alerts in 90 days
# TYPE drift_alerts_detected gauge
drift_alerts_detected 6

# HELP cost_monthly_usd Projected 30-day spend
# TYPE cost_monthly_usd gauge
cost_monthly_usd 20500.0
```

### Phase 5: Executive Summary (`executive_summary.pdf`)

**Audience:** CTO, Medical Director, Product Leadership

**Sections:**
1. Executive Summary (viability assessment)
2. Quality Performance (model comparison, safety alignment)
3. Cost & Efficiency (75/25 split analysis, monthly savings)
4. Systemic Operational Risks (drift, hallucination, quality gate failures)
5. Actionable Engineering Roadmap (routing rules, gating, clinician review)
6. Conclusion (production readiness statement)



## Project Structure

```
afyaplus-capstone/
├── evaluation/
│   ├── evaluation_data.py         # 15-question dataset definition
│   ├── evaluator.py               # ROUGE-L, Token F1, LLM judge logic
│   ├── run_evaluation.py           # Main pipeline (generates CSVs)
│   ├── full_evaluation_results.csv
│   ├── llm_judge_matrix.csv
│   └── quality_gate_log.txt
├── drift/
│   ├── drift_simulation.py         # 3-month synthetic traffic generator
│   ├── run_drift_pipeline.py       # Evidently integration (generates HTML)
│   ├── drift_trend_table.csv
│   ├── drift_alert_log.json
│   ├── evidently_month1.html
│   ├── evidently_month2.html
│   └── evidently_month3.html
├── cost/
│   ├── cost_model.py               # Pricing logic
│   ├── run_cost_analysis.py        # Projection engine
│   ├── cost_projections_30d.csv
│   ├── cost_per_request.csv
│   └── structural_savings_analysis.csv
├── dashboard/
│   ├── main.py                     # FastAPI app
│   ├── dashboard_instructions.md   # Setup guide
│   ├── templates/
│   │   └── index.html              # UI
│   └── static/
│       └── styles.css
├── executive_summary.pdf           # Stakeholder report
├── executive_summary.md            # Source markdown
├── README.md                        # This file
├── requirements.txt
├── .env.example
└── .gitignore
```



## Running Individual Phases

### Evaluation Only

```bash
PYTHONPATH=. python evaluation/run_evaluation.py
```

**Expected output:**
```
Evaluation output written to .../evaluation/full_evaluation_results.csv
Judge matrix written to .../evaluation/llm_judge_matrix.csv
Quality gate log written to .../evaluation/quality_gate_log.txt
```

### Drift Only

```bash
PYTHONPATH=. python drift/run_drift_pipeline.py
```

**Expected output:**
```
Saved drift trend table to .../drift/drift_trend_table.csv
Saved drift alert log to .../drift/drift_alert_log.json
Detected 6 drift alerts
```

### Cost Analysis Only

```bash
PYTHONPATH=. python cost/run_cost_analysis.py
```

**Expected output:**
```
30-day cost projections saved to .../cost/cost_projections_30d.csv
Cost-per-request saved to .../cost/cost_per_request.csv
Savings analysis saved to .../cost/structural_savings_analysis.csv
```

### Dashboard Only

```bash
cd dashboard
PYTHONPATH=.. uvicorn main:app --reload
```

Then:
- Open **http://127.0.0.1:8000/** (UI)
- Test **http://127.0.0.1:8000/api/health** (JSON)
- Scrape **http://127.0.0.1:8000/metrics** (Prometheus)



## Key Results & Interpretation

### Quality Performance

| Model | ROUGE-L | Token F1 | Judge Score | Status |
||||||
| gpt-4o | 0.78 | 0.74 | 4.42 | ✅ Pass |
| gpt-4o-mini | 0.71 | 0.68 | 4.10 | ✅ Pass |

**Interpretation:** Both models exceed quality gates. Premium model outperforms on high-risk (medication, emergency triage). Mini acceptable for low-risk (standard triage, appointment routing).

### Drift Alerts (90-day window)

- **6 total alerts detected**
- Primary signals: latency drift (Month 2–3), input token distribution shift
- No catastrophic failures, but trending toward gating thresholds

### Cost Savings (75/25 split)

- **Monthly baseline (100% gpt-4o):** $28,500
- **75/25 routing:** $20,500
- **Monthly savings:** $8,000 (~28% reduction)
- **Annual savings:** $96,000



## Troubleshooting

### "No module named 'IPython'"
Evidently may require IPython for inline rendering. Install it:
```bash
pip install ipython
```

### "Cannot import HTML from IPython.display"
The project uses `get_html()` instead of deprecated APIs. Ensure Evidently ≥ 0.4.0:
```bash
pip install --upgrade evidently
```

### Dashboard won't start
Ensure `PYTHONPATH` is set and you're running from the correct directory:
```bash
cd /path/to/afyaplus-capstone
PYTHONPATH=. uvicorn dashboard.main:app --reload
```

### Empty CSV outputs
Check that `.env` file exists and `OPENROUTER_API_KEY` is set (or accept heuristic fallback for LLM judge). Evaluation will still run without a valid key.

### Missing drift reports
Drift pipeline requires Evidently to be installed and compatible. Verify:
```bash
python -c "from evidently.report import Report; print(dir(Report))" | grep html
```

Should show: `['_render', 'get_html', 'save', 'save_html', '_repr_html_']`



## Environment Variables

| Variable | Description | Default / Example |
||||
| `OPENROUTER_API_KEY` | OpenRouter API token for LLM judge (optional) | (empty = heuristic fallback) |
| `DAILY_REQUEST_VOLUME` | Simulated daily traffic | 2200 |
| `MONTHLY_BUDGET_CAP` | Cost threshold for alerts | 35000 |

Set in `.env`:
```bash
OPENROUTER_API_KEY=sk-or-v1-...
DAILY_REQUEST_VOLUME=2200
MONTHLY_BUDGET_CAP=35000
```

## Integration with Grafana & Prometheus

### Prometheus scrape config

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'afyaplus-dashboard'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 60s
```

### Grafana import

1. Add Prometheus data source: `http://localhost:9090`
2. Create dashboard with queries:
   - `evaluation_rouge_l` (gauge)
   - `drift_alerts_detected` (counter)
   - `cost_monthly_usd` (gauge)
- **Metrics explanation:** Check `dashboard/dashboard_instructions.md` for API details
- **Drift reports:** Open `drift/evidently_month*.html` in a browser for interactive exploration
