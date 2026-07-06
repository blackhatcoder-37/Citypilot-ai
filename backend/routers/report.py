"""
Report router — generates real, downloadable PDF reports from PostgreSQL data and AI insights.
"""

import time
import os
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import Complaint, Weather, Resource, ChatHistory
from repositories.complaint_repository import ComplaintRepository
from repositories.weather_repository import WeatherRepository
from repositories.resource_repository import ResourceRepository
from services.analyze_service import AnalyzeService

router = APIRouter()


class ReportRequest(BaseModel):
    type: str


def _build_pdf(file_path: Path, title: str, analysis: dict, db: Session):
    """Generate a structured, professional PDF report using ReportLab."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Styles matching CityPilot AI Dark Theme
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#6366f1'), # Indigo
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#94a3b8'), # Slate
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0f172a'), # Slate-900
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#334155'), # Slate-700
        leading=14,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#475569'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    story = []

    # Title & Metadata Header
    story.append(Paragraph(f"CityPilot AI — {title}", title_style))
    story.append(Paragraph(
        f"Generated on: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} | "
        f"Database Backend: PostgreSQL | System Status: Operational",
        subtitle_style
    ))
    story.append(Spacer(1, 10))

    # Key Metrics Grid Table
    metrics_data = [
        [
            Paragraph("<b>Risk Score:</b>", body_style), 
            Paragraph(f"{analysis.get('risk_score', 0)} / 100", body_style),
            Paragraph("<b>Priority:</b>", body_style),
            Paragraph(f"{analysis.get('priority', 'MEDIUM')}", body_style)
        ],
        [
            Paragraph("<b>Confidence:</b>", body_style),
            Paragraph(f"{analysis.get('confidence', 'High')}", body_style),
            Paragraph("<b>Est. Cost / Savings:</b>", body_style),
            Paragraph(f"{analysis.get('estimated_cost')} / {analysis.get('estimated_savings')}", body_style)
        ]
    ]
    t = Table(metrics_data, colWidths=[100, 160, 100, 160])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Executive Summary Section
    story.append(Paragraph("Executive Summary", h1_style))
    story.append(Paragraph(analysis.get("executive_summary", "No summary available."), body_style))
    story.append(Spacer(1, 10))

    # Recommendation Section
    story.append(Paragraph("AI Recommendations & Tactical Response", h1_style))
    story.append(Paragraph(analysis.get("recommendation", "No recommendations available."), body_style))
    story.append(Spacer(1, 10))

    # Evidence Chunks Section
    story.append(Paragraph("Analysis Evidence & Correlation Chunks", h1_style))
    for e in analysis.get("evidence", []):
        story.append(Paragraph(f"• {e}", bullet_style))
    story.append(Spacer(1, 10))

    # Resource Allocation Section
    story.append(Paragraph("Required Resource Deployments", h1_style))
    for r in analysis.get("resources_needed", []):
        story.append(Paragraph(f"• {r}", bullet_style))
    story.append(Spacer(1, 10))

    # Sources analyzed
    sources = analysis.get("sources", [])
    if sources:
        story.append(Paragraph("Source Knowledge Documents Used", h1_style))
        story.append(Paragraph(", ".join(sources), body_style))

    doc.build(story)


@router.post("/report")
def generate_report(request: ReportRequest, db: Session = Depends(get_db)):
    """Generate a real PDF report and store it in downloads/reports/."""
    start = time.perf_counter()
    report_type = request.type

    # 1. Fetch live system context and run a brief analysis
    # We query the latest analyze query from history or generate a standard query
    last_chat = db.query(ChatHistory).order_by(ChatHistory.id.desc()).first()
    query = "What is the emergency risk assessment for today?"
    if last_chat:
        query = last_chat.query

    # Generate analysis
    analysis_res = AnalyzeService.analyze_query(db, query)
    analysis_dict = analysis_res.model_dump()

    # 2. Ensure download folder exists
    downloads_dir = Path("downloads/reports")
    downloads_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{report_type.lower().replace(' ', '_')}_{int(time.time())}.pdf"
    file_path = downloads_dir / filename

    # 3. Build the PDF document
    _build_pdf(file_path, report_type, analysis_dict, db)

    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return {
        "success": True,
        "message": f"Report '{report_type}' generated successfully",
        "data": {
            "status": "success",
            "report_type": report_type,
            "download_url": f"http://localhost:8000/downloads/reports/{filename}",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed,
    }


@router.get("/downloads/reports/{filename}")
def download_report_file(filename: str):
    """Serve a generated PDF report securely."""
    safe_name = Path(filename).name
    report_path = Path("downloads/reports") / safe_name
    
    if not report_path.exists():
        raise HTTPException(status_code=404, detail=f"Report file '{filename}' not found.")
        
    return FileResponse(
        path=str(report_path),
        media_type="application/pdf",
        filename=safe_name
    )
