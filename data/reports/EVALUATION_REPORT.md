# UniAdmin-AI Pilot Evaluation Report

## 1. Scope and Requirements Analysis

### Objective
Design and evaluate a pilot RAG assistant for University of Potsdam students and administrators. The system answers questions about enrollment, deadlines, compliance, and administrative procedures based on indexed official documents.

### Target users
- **Primary**: Current and prospective students (degree-seeking, parallel degree, doctoral candidates)
- **Secondary**: University administrative staff seeking quick reference to policies

### Main admin intents covered
- Semester re-registration deadlines and procedures
- Application and enrollment requirements
- Tuition payment processes and bank details
- PULS portal access and functionality
- Exam registration and grade management
- Transcript and certificate requests
- GDPR and AI Act compliance information

### Non-functional requirements
| Requirement | Status | Notes |
|-------------|--------|-------|
| Trust | Met | System includes disclaimer on every response |
| Citation | Met | Every answer cites source documents with page numbers |
| Response safety | Met | Defers to official offices for binding decisions |
| No hallucination | Met | Answers grounded in retrieved documents |

---

## 2. Data Sources

### List of indexed documents

| Title | URL/File | Date Accessed |
|-------|----------|---------------|
| EU AI Act (Regulation 2024/1689) | OJ_L_202401689_EN_TXT.pdf | During ingestion |
| EU GDPR | eu_gdpr.pdf | During ingestion |
| LDA Brandenburg AI Guidance | lda_brandenburg_ai.pdf | During ingestion |
| University Re-registration | up_re_registration.pdf | During ingestion |
| Application & Enrollment Deadlines | up_application_enrollment_deadlines.pdf | During ingestion |
| Important Dates | up_important_dates.pdf | During ingestion |
| PULS Portal Guide | up_puls_portal.pdf | During ingestion |
| UP Account/Login | up_account_login.pdf | During ingestion |

### Coverage by category
- **Compliance (AI Act, GDPR, LDA)**: Full EU regulations and Brandenburg authority guidance
- **Enrollment/Deadlines**: Complete re-registration procedures, parallel degree requirements
- **Portal Support**: PULS functionality, account activation, password reset
- **Exam/Transcript**: Registration procedures, grade viewing, certificate requests

### Known limitations
- Tables in PDFs may not extract perfectly (text-only extraction)
- Scanned PDFs would require OCR (not currently implemented)
- Documents reflect state at ingestion time; policies may change

---

## 3. System Architecture

### Ingestion pipeline
1. PDFs loaded from `data/raw_pdfs/` using `pypdf`
2. Text extracted per page with metadata (source file, page number)
3. Documents chunked using `RecursiveCharacterTextSplitter` (900 chars, 150 overlap)
4. Chunks embedded with `mxbai-embed-large` via Ollama
5. Vector store saved to `data/processed/vectorstore/`

### Chunking and indexing
- **Chunk size**: 900 characters
- **Overlap**: 150 characters
- **Separators**: `["\n\n", "\n", ". ", " ", ""]`
- Each chunk assigned unique `chunk_id` (e.g., `chunk_02354`)

### Retrieval and answer generation
1. User question embedded with same model
2. Top-k (k=6) chunks retrieved via similarity search
3. Retrieved context + question passed to LLM (`nemotron-3-nano:30b-cloud`)
4. LLM generates answer with citations

### Citation mechanism
- Deduplication by (source, page, chunk_id) tuple
- Format: `filename.pdf#pN (chunk_id)`
- Example: `up_re_registration.pdf#p2 (chunk_02361)`

---

## 4. Evaluation Design

### Benchmark size
- **100 questions** across 10 categories

### Category distribution
| Category | Questions |
|----------|-----------|
| semester_deadlines | 10 |
| enrollment | 10 |
| tuition_payment | 10 |
| portal_login_support | 10 |
| exam_registration | 10 |
| transcript_requests | 10 |
| compliance_gdpr | 10 |
| compliance_ai_act | 10 |
| compliance_lda | 5 |
| cross_document | 15 |

### Rubric dimensions (0-2 each, max 8 total)
| Dimension | 0 | 1 | 2 |
|-----------|---|---|---|
| Correctness | Wrong/misleading | Partially correct | Fully accurate |
| Completeness | Missing key info | Some details missing | Complete answer |
| Compliance | No disclaimer/unsafe | Partial compliance | Full compliance + escalation |
| Citation Quality | Missing/wrong | Partial | Accurate, relevant |

### Human evaluation process
- All 100 answers manually scored
- Scores recorded in `predictions_scored.csv`
- Notes field captures reasoning for low scores

---

## 5. Results

### Overall score
- **Total**: 789 / 800 points
- **Percentage**: 98.6% of maximum
- **Average per question**: 7.89 / 8.00

### Average per answer by score
| Score | Count | Percentage |
|-------|-------|------------|
| 8/8 (perfect) | 94 | 94% |
| 7/8 | 3 | 3% |
| 6/8 | 1 | 1% |
| 5/8 | 2 | 2% |

### Category-level performance
| Category | Avg Score | Max | Percentage |
|----------|-----------|-----|------------|
| compliance_ai_act | 8.00 | 8 | 100% |
| compliance_gdpr | 8.00 | 8 | 100% |
| compliance_lda | 8.00 | 8 | 100% |
| enrollment | 8.00 | 8 | 100% |
| exam_registration | 8.00 | 8 | 100% |
| portal_login_support | 8.00 | 8 | 100% |
| transcript_requests | 8.00 | 8 | 100% |
| tuition_payment | 8.00 | 8 | 100% |
| cross_document | 7.67 | 8 | 95.8% |
| semester_deadlines | 7.40 | 8 | 92.5% |

### Distribution of low-scoring answers
- **5/8 (2 instances)**: Q006, Q007 - Lecture period dates not explicitly stated in sources, model hedged correctly but lacked specificity
- **6/8 (1 instance)**: Q086: Cross-document compliance question; answer correctly framed but citations lacked page-level precision across AI Act and GDPR sources.
- **7/8 (3 instances)**: Minor completeness or citation gaps

---

## 6. Error Analysis

### Hallucinations
- **None detected**. Model consistently hedged when information was unavailable (e.g., Q006, Q007 lecture dates)

### Missing policy details
- Q006/Q007: Source documents did not contain explicit lecture period start/end dates; model correctly directed users to official calendar

### Citation failures
- No complete failures observed
- Low-scoring answers had relevant but non-specific citations

### Format extraction failures
- No structured data extraction was required for this benchmark
- All questions were answered with prose responses

---

## 7. Risk and Compliance Considerations

### GDPR-oriented controls
- System processes no user PII during inference
- No conversation logging implemented (pilot system)
- Data minimization: only question text used for retrieval

### AI limitations and human escalation rules
- **Disclaimer on every response**: "This assistant is for informational support based on indexed public documents. For legally binding decisions, contact the relevant university office."
- Consistently directs users to:
  - Student Administration Center for enrollment issues
  - ZIM Helpdesk for technical/account problems
  - Examination offices for grade concerns
  - Data protection officer for GDPR requests

Under EU AI Act Annex III, AI systems used in education that influence access to educational opportunities may be classified as high-risk. This pilot is scoped as a research/informational tool and does not make autonomous decisions affecting student enrollment or assessment.

---

## 8. Interoperability and Pilot Next Steps

### API endpoints
Current implementation is a Python library (`src/unirag/rag.py`). For production:
```python
# Proposed REST endpoint
POST /api/v1/ask
{
  "question": "string"
}
Response:
{
  "answer": "string",
  "citations": [{"source": "string", "page": int, "chunk_id": "string"}],
  "disclaimer": "string"
}
```

### Proposed integration with university systems
| System | Integration Type | Status |
|--------|-----------------|--------|
| PULS | Deep link to portal | Implemented (URLs in answers) |
| UP Account | Account activation flow | Documented in answers |
| LDA Brandenburg | Complaint pathway | Referenced for GDPR issues |
| EUR-Lex | AI Act full text | Referenced for legal reference |

### Infrastructure requirements for production deployment
A production deployment within UP infrastructure would require a document refresh pipeline triggered by official website updates, authentication integration with UP accounts to scope responses by user role (student vs. staff), and a PULS API connection to surface live enrollment status alongside static document answers. A data protection impact assessment (DPIA) under GDPR Article 35 would be required before processing student queries in a live environment, given the potential high-risk classification of educational AI systems under EU AI Act Annex III.

### Improvement backlog
| Priority | Item | Rationale |
|----------|------|-----------|
| High | Add OCR for scanned PDFs | Future-proof for non-text PDFs |
| Medium | Table extraction | Some documents contain tabular data |
| Medium | Freshness checking | Alert when documents are outdated |
| Low | Multi-language support | International student accessibility |
| Low | Conversation memory | Enable follow-up questions |

---

## Appendix: Evaluation Data Files

| File | Description |
|------|-------------|
| `data/benchmarks/questions.csv` | 100 benchmark questions with reference answers |
| `data/reports/predictions.csv` | Raw model outputs |
| `data/reports/predictions_scored.csv` | Scored results with notes |
| `data/reports/summary.md` | Quick summary statistics |

---
