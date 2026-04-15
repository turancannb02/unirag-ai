from pathlib import Path
from typing import List

from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from unirag.config import settings


def get_embeddings():
    provider = settings.embeddings_provider.lower()

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when EMBEDDINGS_PROVIDER=openai")
        kwargs = {"model": settings.embeddings_model, "api_key": settings.openai_api_key}
        if settings.openai_base_url:
            kwargs["base_url"] = settings.openai_base_url
        return OpenAIEmbeddings(**kwargs)

    return HuggingFaceEmbeddings(model_name=settings.embeddings_model)


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
