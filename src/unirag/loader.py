from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from unirag.config import settings


def load_pdf_documents(pdf_dir: str | None = None) -> List[Document]:
    base = Path(pdf_dir or settings.pdf_dir)
    pdf_paths = sorted(base.glob("*.pdf"))
    docs: List[Document] = []

    for pdf_path in pdf_paths:
        reader = PdfReader(str(pdf_path))
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if not text.strip():
                continue

            docs.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": pdf_path.name,
                        "source_path": str(pdf_path),
                        "page": i,
                    },
                )
            )
    return docs


def chunk_documents(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunked = splitter.split_documents(docs)
    for idx, doc in enumerate(chunked):
        doc.metadata["chunk_id"] = f"chunk_{idx:05d}"
    return chunked
