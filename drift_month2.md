# Drift Report — Month 2

**Generated:** 2026-08-17 03:32 UTC

## Summary

| Metric | Baseline | Current | Change |
|--------|----------|---------|--------|
| Latency (ms) | 1029.8 | 1197.7 | 16.3% |
| Input Tokens | 844 | 997 | 18.1% |
| ROUGE-L | 0.682 | 0.641 | -6.0% |

## Alerts

**3 drift alert(s) detected:**

- 🔴 **input_token_length** (high): 844.4872 → 997.0208 (18.1% change)
- 🔴 **latency_ms** (high): 1029.796 → 1197.7268 (16.3% change)
- 🟡 **rouge_l** (medium): 0.6821 → 0.6413 (6.0% change)

---

**Note:** Full interactive reports available locally at `drift/evidently_month2.html`
