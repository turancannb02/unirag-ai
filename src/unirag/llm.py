from typing import List

from langchain_core.documents import Document
from langchain_ollama import ChatOllama

from unirag.config import settings


SYSTEM_PROMPT = """You are a university administrative assistant.
Answer only using the provided context.
If the answer is uncertain or missing from context, say so clearly and suggest contacting the relevant office.
Always include practical next steps for the student.
Do not provide legal advice.
"""


def _format_context(docs: List[Document]) -> str:
    parts = []
    for d in docs:
        source = d.metadata.get("source", "unknown")
        page = d.metadata.get("page", "?")
        chunk_id = d.metadata.get("chunk_id", "na")
        parts.append(f"[source={source} page={page} chunk={chunk_id}]\n{d.page_content}")
    return "\n\n".join(parts)


def _fallback_extractive_answer(question: str, docs: List[Document]) -> str:
    if not docs:
        return (
            "I could not find supporting information in the indexed university documents. "
            "Please contact Student Services for confirmation."
        )

    bullets = []
    for d in docs[:3]:
        snippet = " ".join(d.page_content.split())[:280]
        bullets.append(f"- {snippet}...")

    return (
        f"Based on the indexed documents, here are the most relevant points for: '{question}'\n"
        + "\n".join(bullets)
        + "\nNext step: verify details with the cited official office/page before taking action."
    )


def generate_answer(question: str, docs: List[Document]) -> str:
    provider = settings.llm_provider.lower()

    if provider == "ollama":
        # Use Ollama LLM
        llm = ChatOllama(model=settings.llm_model, base_url=settings.ollama_base_url, temperature=0)
        context = _format_context(docs)
        user_prompt = (
            f"Question:\n{question}\n\n"
            f"Context:\n{context}\n\n"
            "Return a concise answer in bullet points and include concrete next steps."
        )
        response = llm.invoke([
            ("system", SYSTEM_PROMPT),
            ("user", user_prompt),
        ])
        return response.content

    # Fallback to extractive mode for unknown providers
    return _fallback_extractive_answer(question, docs)
