"""
Analyze router — retrieves real data from PostgreSQL and passes to AI.
"""

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from database.schemas import AnalyzeRequest, AnalyzeResponse
from services.analyze_service import AnalyzeService

router = APIRouter()


@router.post("/analyze")
def analyze_query(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """Analyse a query using real complaint, weather, and resource data."""
    start = time.perf_counter()
    result = AnalyzeService.analyze_query(db, request.query)
    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return {
        "success": True,
        "message": "Analysis complete",
        "data": result.model_dump(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed,
    }


@router.post("/chat")
def chat(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """Simple chat endpoint for the AI command center using Gemini."""
    start = time.perf_counter()
    query = request.query

    # ── Attempt Gemini Response ──────────────────────────────────────
    from ai.services import AIService
    model = AIService._get_model()
    response_text = ""
    if model:
        try:
            prompt = (
                "You are CityPilot AI, a smart city operations chatbot. "
                f"Respond to the following message from a city administrator: '{query}'. "
                "Keep your response concise, professional, and helpful."
            )
            response = model.generate_content(prompt)
            response_text = response.text.strip()
        except Exception:
            pass

    if not response_text:
        response_text = f"AI acknowledges: {query}. Please use the main analyze endpoint for deep structural insights."

    # ── Save to Chat History ─────────────────────────────────────────
    from database.models import ChatHistory
    try:
        chat_record = ChatHistory(
            query=query,
            response=response_text,
        )
        db.add(chat_record)
        db.commit()
    except Exception as e:
        db.rollback()

    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return {
        "success": True,
        "message": "Chat response complete",
        "data": {"response": response_text},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed,
    }
