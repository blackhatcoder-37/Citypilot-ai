"""
Upload router — secure file upload with path traversal prevention.
"""

import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from config import get_settings
from database.database import get_db
from database.models import KnowledgeDocument
from repositories.knowledge_repository import KnowledgeRepository

router = APIRouter()
settings = get_settings()


def _validate_filename(filename: str) -> str:
    """Validate and sanitise the filename. Raises HTTPException on invalid input."""
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    # Strip path components (prevents path traversal)
    safe_name = Path(filename).name

    if safe_name != filename.replace("\\", "/").split("/")[-1]:
        raise HTTPException(status_code=400, detail="Invalid filename — path traversal detected.")

    # Check for dangerous patterns
    if ".." in safe_name or safe_name.startswith("."):
        raise HTTPException(status_code=400, detail="Invalid filename.")

    # Check extension
    suffix = Path(safe_name).suffix.lower()
    if suffix not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{suffix}' not allowed. Accepted: {', '.join(sorted(settings.ALLOWED_EXTENSIONS))}",
        )

    return safe_name


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Securely upload a document.
    - Validates filename and extension
    - Generates a UUID-based stored filename
    - Prevents path traversal
    - Records metadata in knowledge_documents table
    """
    start = time.perf_counter()

    # 1. Validate filename
    original_filename = _validate_filename(file.filename or "unknown")

    # 2. Check file size
    contents = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # 3. Generate UUID filename
    suffix = Path(original_filename).suffix.lower()
    stored_filename = f"{uuid.uuid4().hex}{suffix}"

    # 4. Ensure upload directory exists (use pathlib)
    upload_dir = Path(settings.UPLOAD_DIR).resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 5. Write file (ensure path stays inside upload_dir)
    file_path = (upload_dir / stored_filename).resolve()
    if not str(file_path).startswith(str(upload_dir)):
        raise HTTPException(status_code=400, detail="Invalid file path.")

    file_path.write_bytes(contents)

    # 6. Record in database
    doc = KnowledgeDocument(
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_type=suffix.lstrip("."),
        file_size_bytes=len(contents),
        file_path=str(file_path),
        status="Uploaded",
        is_embedded=False,
    )
    KnowledgeRepository.create(db, doc)

    # ── Parse, Chunk, and Embed for RAG ─────────────────────────────
    from services.rag_service import RAGService
    RAGService.process_and_embed_document(db, doc.id)

    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return {
        "success": True,
        "message": f"File '{original_filename}' uploaded successfully",
        "data": {
            "id": doc.id,
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "file_type": suffix.lstrip("."),
            "file_size_bytes": len(contents),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed,
    }


@router.get("/upload/documents")
def get_all_documents(db: Session = Depends(get_db)):
    """Retrieve all uploaded knowledge documents."""
    start = time.perf_counter()
    docs = KnowledgeRepository.get_all(db)
    elapsed = round((time.perf_counter() - start) * 1000, 2)
    return {
        "success": True,
        "message": f"Retrieved {len(docs)} documents",
        "data": [
            {
                "id": doc.id,
                "original_filename": doc.original_filename,
                "stored_filename": doc.stored_filename,
                "file_type": doc.file_type,
                "file_size_bytes": doc.file_size_bytes,
                "upload_date": doc.upload_date.isoformat() if doc.upload_date else None,
                "status": doc.status,
                "is_embedded": doc.is_embedded
            }
            for doc in docs
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed
    }


@router.delete("/upload/documents/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """Delete a document, its database record, and its physical file."""
    start = time.perf_counter()
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Delete physical file
    try:
        if doc.file_path:
            p = Path(doc.file_path)
            if p.exists():
                p.unlink()
    except Exception as e:
        logger.error(f"Failed to delete physical file {doc.file_path}: {e}")

    # Delete from DB
    try:
        db.delete(doc)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database deletion failed: {e}")

    elapsed = round((time.perf_counter() - start) * 1000, 2)
    return {
        "success": True,
        "message": f"Document '{doc.original_filename}' deleted successfully",
        "data": {"id": doc_id},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed
    }
