from fastapi import FastAPI, HTTPException

from unirag.rag import UniAdminRAG
from unirag.schemas import AskRequest, AskResponse

app = FastAPI(title="UniAdmin-AI API", version="0.1.0")
rag_engine: UniAdminRAG | None = None


@app.on_event("startup")
def startup_event() -> None:
    global rag_engine
    try:
        rag_engine = UniAdminRAG()
    except Exception:
        rag_engine = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "index_loaded": rag_engine is not None}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    if rag_engine is None:
        raise HTTPException(status_code=500, detail="Vector index not loaded. Run ingestion first.")

    result = rag_engine.ask(req.question)
    return AskResponse(**result)
