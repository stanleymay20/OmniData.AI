from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import seaborn as sns
from ..core.auth import get_current_user
from ..core.config import settings

router = APIRouter()

class ReportRequest(BaseModel):
    dataset_name: str
    forecast_goal: str
    include_charts: bool = True
    include_insights: bool = True

def generate_chart(data, title):
    """Generate a matplotlib chart and return it as bytes"""
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    # TODO: Implement actual chart generation based on data
    plt.title(title)
    plt.tight_layout()
    
    # Save to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

def create_report(data: dict, request: ReportRequest) -> bytes:
    """Create a PDF report with the given data"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph(f"ScrollIntel Report: {request.dataset_name}", title_style))
    story.append(Spacer(1, 12))
    
    # Overview
    story.append(Paragraph("Overview", styles['Heading2']))
    story.append(Paragraph(
        f"This report analyzes the dataset '{request.dataset_name}' with the goal of {request.forecast_goal}.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    # Charts
    if request.include_charts:
        story.append(Paragraph("Visual Analysis", styles['Heading2']))
        chart = generate_chart(data, "Data Trends")
        story.append(Image(chart, width=6*inch, height=4*inch))
        story.append(Spacer(1, 12))
    
    # Insights
    if request.include_insights:
        story.append(Paragraph("Key Insights", styles['Heading2']))
        insights = [
            "The data shows a strong upward trend in the last quarter",
            "Key indicators suggest continued growth in the next period",
            "Market conditions are favorable for the forecasted outcomes"
        ]
        for insight in insights:
            story.append(Paragraph(f"• {insight}", styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Forecast
    story.append(Paragraph("Forecast", styles['Heading2']))
    forecast_data = [
        ["Timeframe", "Prediction", "Confidence"],
        ["Short-term", "Positive growth", "85%"],
        ["Medium-term", "Stable expansion", "75%"],
        ["Long-term", "Sustained success", "65%"]
    ]
    table = Table(forecast_data, colWidths=[2*inch, 3*inch, 2*inch])
    table.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    story.append(table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

@router.post("/report/generate")
async def generate_report(
    request: ReportRequest,
    current_user = Depends(get_current_user)
):
    """Generate a PDF report for the given dataset and forecast goal"""
    try:
        # TODO: Fetch actual data from database
        data = {
            "trends": [1, 2, 3, 4, 5],
            "forecast": [6, 7, 8, 9, 10]
        }
        
        # Generate PDF
        pdf_bytes = create_report(data, request)
        
        # Save to temporary file
        temp_file = f"reports/{current_user.id}_{request.dataset_name}.pdf"
        with open(temp_file, "wb") as f:
            f.write(pdf_bytes)
        
        return FileResponse(
            temp_file,
            media_type="application/pdf",
            filename=f"scrollintel_report_{request.dataset_name}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 