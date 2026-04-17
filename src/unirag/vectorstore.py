from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

from unirag.config import settings


def get_embeddings():
    provider = settings.embeddings_provider.lower()

    if provider == "ollama":
        return OllamaEmbeddings(model=settings.embeddings_model, base_url=settings.ollama_base_url)

    raise ValueError(f"Unsupported embeddings provider: {provider}")


def build_vectorstore(chunks: List[Document], persist_path: str | None = None) -> FAISS:
    path = Path(persist_path or settings.vectorstore_dir)
    path.mkdir(parents=True, exist_ok=True)

    embeddings = get_embeddings()
    store = FAISS.from_documents(chunks, embeddings)
    store.save_local(str(path))
    return store


def load_vectorstore(persist_path: str | None = None) -> FAISS:
    path = Path(persist_path or settings.vectorstore_dir)
    embeddings = get_embeddings()
    return FAISS.load_local(
        str(path),
        embeddings,
        allow_dangerous_deserialization=True,
    )
