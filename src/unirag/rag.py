from typing import Dict, List, Tuple

from langchain_core.documents import Document

from unirag.config import settings
from unirag.llm import generate_answer
from unirag.vectorstore import load_vectorstore


def _dedupe_citations(docs: List[Document]) -> List[Dict[str, str | int]]:
    seen: set[Tuple[str, int, str]] = set()
    out = []
    for d in docs:
        source = str(d.metadata.get("source", "unknown"))
        page = int(d.metadata.get("page", 0))
        chunk_id = str(d.metadata.get("chunk_id", "na"))
        key = (source, page, chunk_id)
        if key in seen:
            continue
        seen.add(key)
        out.append({"source": source, "page": page, "chunk_id": chunk_id})
    return out


class UniAdminRAG:
    def __init__(self):
        self.store = load_vectorstore()

    def ask(self, question: str) -> dict:
        retriever = self.store.as_retriever(search_kwargs={"k": settings.retrieval_k})
        docs = retriever.invoke(question)
        answer = generate_answer(question, docs)
        citations = _dedupe_citations(docs)
        disclaimer = (
            "This assistant is for informational support based on indexed public documents. "
            "For legally binding decisions, contact the relevant university office."
        )
        return {
            "answer": answer,
            "citations": citations,
            "disclaimer": disclaimer,
        }
