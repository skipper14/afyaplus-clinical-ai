# Drift Report — Month 3

**Generated:** 2026-08-17 03:32 UTC

## Summary

| Metric | Baseline | Current | Change |
|--------|----------|---------|--------|
| Latency (ms) | 1029.8 | 1368.3 | 32.9% |
| Input Tokens | 844 | 1151 | 36.3% |
| ROUGE-L | 0.682 | 0.601 | -11.9% |

## Alerts

**3 drift alert(s) detected:**

- 🔴 **input_token_length** (high): 844.4872 → 1150.7862 (36.3% change)
- 🔴 **latency_ms** (high): 1029.796 → 1368.3431 (32.9% change)
- 🟡 **rouge_l** (medium): 0.6821 → 0.6011 (11.9% change)

---

**Note:** Full interactive reports available locally at `drift/evidently_month3.html`
