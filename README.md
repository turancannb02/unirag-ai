# UniAdmin-AI

Administrative RAG case-study starter for student services queries.

This project lets you:
- index public university administrative PDFs,
- answer student questions with page-level citations,
- run a manual multi-dimensional evaluation rubric,
- generate report-ready summary outputs.

## 1) Setup (uv)

```bash
cp .env.example .env
uv sync
```

Optional: activate the local venv managed by `uv`.

```bash
source .venv/bin/activate
```

## 2) Add Source Documents

Put your downloaded/printed PDFs into:

```text
data/raw_pdfs/
```

Recommended categories:
- enrollment
- tuition/payment
- exam registration
- transcript requests
- semester deadlines
- portal/login support

## 3) Build the Vector Index

```bash
uv run python scripts/ingest.py
```

## 4) Run API

```bash
uv run uvicorn unirag.api:app --reload --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Ask:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"How do I re-register for next semester?"}'
```

## 5) Evaluation Workflow

### 5.1 Create benchmark template

```bash
uv run python scripts/make_benchmark_template.py
```

Edit `data/benchmarks/questions.csv` with your real 50/75/100 questions.

### 5.2 Generate model answers for manual review

```bash
uv run python scripts/evaluate.py \
  --input data/benchmarks/questions.csv \
  --output data/reports/predictions.csv
```

### 5.3 Manually score using your rubric

Fill columns in `data/reports/predictions.csv`:
- `correctness_0_2`
- `completeness_0_2`
- `compliance_0_2`
- `citation_quality_0_2`

Save as `data/reports/predictions_scored.csv`.

### 5.4 Compute summary

```bash
uv run python scripts/score_rubric.py \
  --input data/reports/predictions_scored.csv \
  --output data/reports/summary.md
```

## Rubric (0-2 each)

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Correctness | Wrong/hallucinated | Mostly correct, minor gap | Fully correct |
| Completeness | Unusable | Correct but missing steps | Complete + actionable next steps |
| Compliance | Risky/legal overreach | Vague safeguards | Policy-aligned, safe framing |
| Citations | None/wrong source | Source but weak precision | Exact document + page |

Max per question: `8` points.

## Notes

- If `OPENAI_API_KEY` is not set, the system falls back to an extractive mode.
- For CV wording, present this as a **case study on public documents**, not an official production deployment.
