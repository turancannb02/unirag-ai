import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "")

    embeddings_provider: str = os.getenv("EMBEDDINGS_PROVIDER", "hf")
    embeddings_model: str = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    retrieval_k: int = int(os.getenv("RETRIEVAL_K", "6"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "900"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))

    pdf_dir: str = os.getenv("PDF_DIR", "data/raw_pdfs")
    vectorstore_dir: str = os.getenv("VECTORSTORE_DIR", "data/processed/vectorstore")


settings = Settings()
