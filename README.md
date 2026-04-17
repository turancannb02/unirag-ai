# UniAdmin-AI

<p align="center">
  <img src="https://img.shields.io/badge/Language-Python-blue?style=plastic&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Framework-LangChain-0EA5E9?style=plastic" alt="LangChain">
  <img src="https://img.shields.io/badge/Vector%20Store-FAISS-111827?style=plastic" alt="FAISS">
  <img src="https://img.shields.io/badge/API-FastAPI-009688?style=plastic&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Embeddings-Ollama-222222?style=plastic" alt="Ollama">
  <img src="https://img.shields.io/badge/Package%20Manager-uv-4B5563?style=plastic" alt="uv">
</p>

A RAG-based administrative assistant for university student services, built and evaluated as a pilot for higher-education deployment.

Answers student and staff questions about enrollment, deadlines, GDPR, and EU AI Act compliance with page-level citations and zero hallucinations across a 100-question benchmark.

---

## Evaluation Results

Evaluated on **100 questions across 10 administrative categories** using a 4-dimension rubric (max 8 points per question).

| Metric | Result |
|--------|--------|
| Overall score | **789 / 800 (98.6%)** |
| Perfect answers (8/8) | **94 / 100 (94%)** |
| Hallucinations detected | **0** |
| Average score per question | **7.89 / 8.00** |

### Category-level performance

| Category | Score | % |
|----------|-------|---|
| compliance_ai_act | 8.00 / 8 | 100% |
| compliance_gdpr | 8.00 / 8 | 100% |
| compliance_lda | 8.00 / 8 | 100% |
| enrollment | 8.00 / 8 | 100% |
| exam_registration | 8.00 / 8 | 100% |
| portal_login_support | 8.00 / 8 | 100% |
| transcript_requests | 8.00 / 8 | 100% |
| tuition_payment | 8.00 / 8 | 100% |
| cross_document | 7.67 / 8 | 95.8% |
| semester_deadlines | 7.40 / 8 | 92.5% |

The only failures were in `semester_deadlines` and `cross_document`, where source documents lacked explicit dates. The model correctly hedged and directed users to official offices rather than hallucinating.

---

## What This Is

UniAdmin-AI is a local-first RAG pipeline built to explore how retrieval-augmented generation performs on official university administrative documents: enrollment procedures, payment processes, GDPR policies, and EU AI Act compliance guidance.

Every component is built explicitly: chunking strategy, embedding model selection, retrieval configuration, citation grounding, compliance framing, and evaluation rubric design.

**Indexed document categories:**
- EU AI Act (Regulation 2024/1689) and EU GDPR
- LDA Brandenburg AI guidance
- University re-registration and enrollment deadlines
- PULS portal guide and account/login documentation
- Important dates and exam procedures

---

## Architecture

```
data/raw_pdfs/
    ↓
pypdf text extraction (page-level metadata)
    ↓
RecursiveCharacterTextSplitter (900 chars, 150 overlap)
    ↓
mxbai-embed-large embeddings via Ollama
    ↓
FAISS vector index
    ↓
user question → similarity search (top-k=6)
    ↓
context assembly + prompt construction
    ↓
LLM (nemotron-mini via Ollama)
    ↓
answer with page-level citations + compliance disclaimer
```

---

## Project Structure

```text
unirag-ai/
├── src/unirag/
│   ├── rag.py           # Core RAG chain
│   ├── vectorstore.py   # FAISS index management
│   ├── loader.py        # PDF loading and chunking
│   ├── llm.py           # LLM backend (Ollama)
│   ├── api.py           # FastAPI endpoints
│   ├── schemas.py       # Request/response models
│   └── config.py        # Configuration
├── scripts/
│   ├── ingest.py                  # Build vector index from PDFs
│   ├── evaluate.py                # Generate model answers for benchmark
│   ├── score_rubric.py            # Compute summary statistics
│   └── make_benchmark_template.py # Create benchmark CSV template
├── data/
│   ├── benchmarks/questions.csv   # 100-question benchmark
│   ├── raw_pdfs/                  # Source documents (not tracked)
│   └── reports/                   # Evaluation outputs
└── pyproject.toml
```

---

## Quickstart

### 1. Setup

```bash
git clone https://github.com/turancannb02/unirag-ai
cd unirag-ai
cp .env.example .env
uv sync
```

Requires Ollama running locally with models pulled:

```bash
ollama pull mxbai-embed-large
ollama pull nemotron-mini
```

### 2. Add source documents

Place PDFs into `data/raw_pdfs/`. See [Data Sources](#data-sources) for the document list used in the pilot evaluation.

### 3. Build the vector index

```bash
uv run python scripts/ingest.py
```

### 4. Run the API

```bash
uv run uvicorn unirag.api:app --reload --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Ask a question:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question": "How do I re-register for next semester?"}'
```

Response format:

```json
{
  "answer": "To re-register for the next semester...",
  "citations": [
    {"source": "up_re_registration.pdf", "page": 2, "chunk_id": "chunk_02361"}
  ],
  "disclaimer": "This assistant is for informational support based on indexed public documents. For legally binding decisions, contact the relevant university office."
}
```

---

## Evaluation Workflow

### 1. Create benchmark template

```bash
uv run python scripts/make_benchmark_template.py
```

Edit `data/benchmarks/questions.csv` with your questions and reference answers.

### 2. Generate model answers

```bash
uv run python scripts/evaluate.py \
  --input data/benchmarks/questions.csv \
  --output data/reports/predictions.csv
```

### 3. Score manually using the rubric

Fill in `data/reports/predictions.csv`:

| Column | Range | Meaning |
|--------|-------|---------|
| `correctness_0_2` | 0-2 | Factual accuracy |
| `completeness_0_2` | 0-2 | Coverage of key information |
| `compliance_0_2` | 0-2 | Appropriate disclaimers and escalation |
| `citation_quality_0_2` | 0-2 | Source accuracy and page precision |

Save as `data/reports/predictions_scored.csv`.

### 4. Compute summary

```bash
uv run python scripts/score_rubric.py \
  --input data/reports/predictions_scored.csv \
  --output data/reports/summary.md
```

---

## Compliance and Safety

Every response includes a disclaimer:

> *"This assistant is for informational support based on indexed public documents. For legally binding decisions, contact the relevant university office."*

Under EU AI Act Annex III, AI systems used in education that influence access to educational opportunities may be classified as high-risk. This system is scoped as a research/informational tool and does not make autonomous decisions affecting student enrollment or assessment.

**GDPR-oriented controls:**
- No user PII processed during inference
- No conversation logging (pilot system)
- Data minimisation: only question text used for retrieval

---

## Data Sources

PDFs are not tracked in this repository. The pilot evaluation used the following public documents:

| Document | Source |
|----------|--------|
| EU AI Act (Regulation 2024/1689) | EUR-Lex |
| EU GDPR | EUR-Lex |
| LDA Brandenburg AI Guidance | lda.brandenburg.de |
| University of Potsdam re-registration | uni-potsdam.de |
| Application & enrollment deadlines | uni-potsdam.de |
| PULS portal guide | uni-potsdam.de |
| UP account/login documentation | uni-potsdam.de |
| Important dates | uni-potsdam.de |

---

## What I Learned

- Citation grounding with page-level metadata is essential for trust in administrative contexts. Users need to be able to verify answers themselves.
- Chunk size of 900 chars with 150 overlap outperformed smaller chunks on multi-sentence policy questions.
- Compliance framing (disclaimers and escalation paths) is as important as answer quality for institutional deployment.
- Cross-document queries (e.g. GDPR and AI Act together) are the hardest failure mode. Hybrid retrieval helps but context window management matters.
- A structured evaluation rubric reveals failure modes that perplexity or RAGAS alone would miss.

