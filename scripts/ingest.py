#!/usr/bin/env python3
from pathlib import Path
import sys, os

# Add src directory to sys.path so that unirag package can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from unirag.config import settings
from unirag.loader import chunk_documents, load_pdf_documents
from unirag.vectorstore import build_vectorstore


def main() -> None:
    pdf_dir = Path(settings.pdf_dir)
    if not pdf_dir.exists():
        raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")

    docs = load_pdf_documents(str(pdf_dir))
    if not docs:
        raise RuntimeError("No readable PDF text found. Add PDFs to data/raw_pdfs.")

    chunks = chunk_documents(docs)
    build_vectorstore(chunks)

    print(f"Loaded pages: {len(docs)}")
    print(f"Created chunks: {len(chunks)}")
    print(f"Saved index to: {settings.vectorstore_dir}")


if __name__ == "__main__":
    main()
