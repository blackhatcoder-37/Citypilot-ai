"""
RAG service — handles document parsing (PDF, DOCX, CSV), chunking,
embedding generation via Gemini, vector storage in PostgreSQL, and semantic retrieval.
"""

import os
import csv
import logging
import math
from pathlib import Path
from sqlalchemy.orm import Session
from langchain_text_splitters import RecursiveCharacterTextSplitter
import google.generativeai as genai
from config import get_settings
from database.models import KnowledgeDocument, DocumentChunk

logger = logging.getLogger("citypilot.rag")


class RAGService:
    """Service to ingest, split, embed, store, and query documents."""

    @staticmethod
    def _get_embedding(text: str, is_query: bool = False) -> list[float]:
        """Generate embedding vector using Gemini Embedding model."""
        settings = get_settings()
        api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            logger.warning("GEMINI_API_KEY not configured. Cannot generate embeddings.")
            # Return a dummy vector of 768 dimensions
            return [0.0] * 768

        try:
            genai.configure(api_key=api_key)
            task_type = "retrieval_query" if is_query else "retrieval_document"
            result = genai.embed_content(
                model="models/gemini-embedding-2",
                content=text,
                task_type=task_type
            )
            return [float(x) for x in result.get("embedding", [0.0] * 768)]  # type: ignore
        except Exception as e:
            logger.error(f"Failed to generate embedding for text: {e}")
            return [0.0] * 768

    @staticmethod
    def extract_text(file_path: Path, file_type: str) -> str:
        """Extract plain text from PDF, DOCX, or CSV files."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        text_content = ""
        file_type = file_type.lower().strip(".")

        try:
            if file_type == "pdf":
                import pypdf
                reader = pypdf.PdfReader(file_path)
                pages_text = []
                for idx, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        pages_text.append(page_text)
                text_content = "\n".join(pages_text)

            elif file_type in ["docx", "doc"]:
                import docx
                doc = docx.Document(str(file_path))
                paragraphs = [p.text for p in doc.paragraphs if p.text]
                text_content = "\n".join(paragraphs)

            elif file_type == "csv":
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.reader(f)
                    lines = []
                    for row in reader:
                        if row:
                            lines.append(", ".join(row))
                    text_content = "\n".join(lines)

            else:
                # Fallback for plain text, markdown, json, etc.
                text_content = file_path.read_text(encoding="utf-8", errors="ignore")

        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            raise RuntimeError(f"Text extraction failed: {e}")

        return text_content

    @staticmethod
    def process_and_embed_document(db: Session, doc_id: int) -> bool:
        """Parse, chunk, embed, and store a document's content in the database."""
        doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
        if not doc:
            logger.error(f"Document with ID {doc_id} not found in database.")
            return False

        try:
            # 1. Update status
            doc.status = "Processing"  # type: ignore
            db.commit()

            # 2. Extract text
            file_path = Path(str(doc.file_path))
            text_content = RAGService.extract_text(file_path, str(doc.file_type))
            if not text_content.strip():
                logger.warning(f"Document {doc.original_filename} is empty.")
                doc.status = "Empty"  # type: ignore
                db.commit()
                return False

            # 3. Chunk using LangChain Character Splitter
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            chunks = splitter.split_text(text_content)
            logger.info(f"Split {doc.original_filename} into {len(chunks)} chunks.")

            # 4. Generate embeddings and save chunks
            db_chunks = []
            for idx, chunk_text in enumerate(chunks):
                if not chunk_text.strip():
                    continue
                embedding = RAGService._get_embedding(chunk_text, is_query=False)
                db_chunk = DocumentChunk(
                    document_id=doc.id,
                    content=chunk_text,
                    source_filename=doc.original_filename,
                    chunk_index=idx,
                    embedding=embedding
                )
                db_chunks.append(db_chunk)

            if db_chunks:
                db.add_all(db_chunks)
                doc.status = "Embedded"  # type: ignore
                doc.is_embedded = True  # type: ignore
                db.commit()
                logger.info(f"Successfully stored {len(db_chunks)} chunks for {doc.original_filename}.")
                return True
            else:
                doc.status = "Failed"  # type: ignore
                db.commit()
                return False

        except Exception as e:
            logger.error(f"Failed to process and embed document {doc_id}: {e}")
            db.rollback()
            try:
                doc.status = f"Error: {str(e)[:50]}"  # type: ignore
                db.commit()
            except Exception:
                pass
            return False

    @staticmethod
    def cosine_similarity(v1: list[float], v2: list[float]) -> float:
        """Calculate cosine similarity between two float vectors."""
        if len(v1) != len(v2):
            return 0.0
        dot_product = sum(x * y for x, y in zip(v1, v2))
        norm1 = math.sqrt(sum(x * x for x in v1))
        norm2 = math.sqrt(sum(x * x for x in v2))
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        return dot_product / (norm1 * norm2)

    @staticmethod
    def retrieve_relevant_chunks(db: Session, query: str, limit: int = 5) -> list[dict]:
        """Retrieve top N relevant document chunks matching the query using cosine similarity."""
        query_embedding = RAGService._get_embedding(query, is_query=True)
        
        # Fast query all chunks from the database
        chunks = db.query(DocumentChunk).all()
        if not chunks:
            return []

        scored_chunks = []
        for chunk in chunks:
            similarity = RAGService.cosine_similarity(query_embedding, chunk.embedding)  # type: ignore
            scored_chunks.append({
                "content": chunk.content,
                "source": chunk.source_filename,
                "chunk_index": chunk.chunk_index,
                "similarity": similarity
            })

        # Sort by similarity descending
        scored_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_chunks[:limit]
