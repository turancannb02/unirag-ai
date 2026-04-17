import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    # LLM provider and model
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")
    llm_model: str = os.getenv("LLM_MODEL", "nemotron-3-nano:30b-cloud")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # Embeddings provider and model
    embeddings_provider: str = os.getenv("EMBEDDINGS_PROVIDER", "ollama")
    embeddings_model: str = os.getenv("EMBEDDINGS_MODEL", "mxbai-embed-large")

    retrieval_k: int = int(os.getenv("RETRIEVAL_K", "6"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "900"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))

    pdf_dir: str = os.getenv("PDF_DIR", "data/raw_pdfs")
    vectorstore_dir: str = os.getenv("VECTORSTORE_DIR", "data/processed/vectorstore")


settings = Settings()
