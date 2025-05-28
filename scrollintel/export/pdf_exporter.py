"""
ScrollIntel PDF Exporter
Generates sacred flame reports in PDF format
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
import pytz
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging

from ..store.project_store import ProjectStore
from ..assistants.scroll_prophet import scroll_prophet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFExporter:
    def __init__(self, export_dir: Optional[str] = None):
        """Initialize PDF exporter with configuration."""
        self.export_dir = Path(export_dir or os.getenv("PDF_EXPORT_DIR", "./exports/pdf"))
        self.template_dir = Path(os.getenv("PDF_TEMPLATE_DIR", "./templates/pdf"))
        self.font_dir = Path(os.getenv("PDF_FONT_DIR", "./assets/fonts"))
        
        # Create directories if they don't exist
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.font_dir.mkdir(parents=True, exist_ok=True)
        
        # Register custom fonts
        self._register_fonts()
        
        # Initialize styles
        self.styles = self._create_styles()
        
        # Initialize project store
        self.project_store = ProjectStore()

    def _register_fonts(self):
        """Register custom fonts for the PDF."""
        try:
            # Register main font
            pdfmetrics.registerFont(TTFont(
                'ScrollFont',
                str(self.font_dir / 'scroll-font.ttf')
            ))
            # Register decorative font
            pdfmetrics.registerFont(TTFont(
                'ScrollDecorative',
                str(self.font_dir / 'scroll-decorative.ttf')
            ))
        except Exception as e:
            logger.warning(f"Failed to register custom fonts: {e}")
            # Fallback to default fonts
            pass

    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create custom paragraph styles for the PDF."""
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='ScrollTitle',
            fontName='ScrollDecorative',
            fontSize=24,
            alignment=1,  # Center
            spaceAfter=30,
            textColor=colors.HexColor('#B8860B')  # ScrollGold
        ))
        
        # Section header style
        styles.add(ParagraphStyle(
            name='ScrollHeader',
            fontName='ScrollFont',
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#8B4513')  # SaddleBrown
        ))
        
        # Body text style
        styles.add(ParagraphStyle(
            name='ScrollBody',
            fontName='ScrollFont',
            fontSize=12,
            spaceAfter=12,
            textColor=colors.black
        ))
        
        # Quote style
        styles.add(ParagraphStyle(
            name='ScrollQuote',
            fontName='ScrollDecorative',
            fontSize=14,
            alignment=1,  # Center
            spaceAfter=20,
            textColor=colors.HexColor('#8B4513')  # SaddleBrown
        ))
        
        return styles

    async def generate_report(self, session_id: str) -> str:
        """
        Generate a PDF report for a session.
        
        Args:
            session_id: ID of the session to generate report for
            
        Returns:
            str: Path to the generated PDF file
        """
        try:
            # Get session data
            session = self.project_store.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # Get AI insights if available
            insights = None
            try:
                insights = await scroll_prophet.get_insights({
                    "domain": session["domain"],
                    "data_type": session.get("metadata", {}).get("type", "Unknown"),
                    "metrics": session.get("interpretation", {}).get("metrics", {}).keys(),
                    "recent_activity": [{
                        "type": "interpretation",
                        "timestamp": session["timestamp"]
                    }]
                })
            except Exception as e:
                logger.warning(f"Failed to get AI insights: {e}")
            
            # Generate PDF
            filename = f"scroll_report_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = self.export_dir / filename
            
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build PDF content
            story = []
            
            # Title
            story.append(Paragraph("🔥 ScrollIntel Flame Report", self.styles["ScrollTitle"]))
            
            # Prophetic quote
            story.append(Paragraph(
                '"The flame reveals patterns unseen by man, illuminating the path to wisdom."',
                self.styles["ScrollQuote"]
            ))
            
            # Domain Insight
            story.append(Paragraph("Domain Insight", self.styles["ScrollHeader"]))
            story.append(Paragraph(
                f"<b>Domain:</b> {session['domain']}",
                self.styles["ScrollBody"]
            ))
            story.append(Paragraph(
                f"<b>Flame Caption:</b> {session['interpretation']['caption']}",
                self.styles["ScrollBody"]
            ))
            
            # Chart
            if session.get("chart_path"):
                img = Image(session["chart_path"], width=6*inch, height=4*inch)
                story.append(img)
            
            # Interpretation
            story.append(Paragraph("Interpretation", self.styles["ScrollHeader"]))
            for key, value in session["interpretation"].items():
                if key != "caption":
                    story.append(Paragraph(
                        f"<b>{key.title()}:</b> {value}",
                        self.styles["ScrollBody"]
                    ))
            
            # AI Insights
            if insights:
                story.append(Paragraph("ScrollProphet Insights", self.styles["ScrollHeader"]))
                
                # Key Insights
                story.append(Paragraph("Key Insights:", self.styles["ScrollBody"]))
                for insight in insights.get("key_insights", []):
                    story.append(Paragraph(f"• {insight}", self.styles["ScrollBody"]))
                
                # Analysis Areas
                story.append(Paragraph("Analysis Areas:", self.styles["ScrollBody"]))
                for area in insights.get("analysis_areas", []):
                    story.append(Paragraph(f"• {area}", self.styles["ScrollBody"]))
                
                # Action Items
                story.append(Paragraph("Action Items:", self.styles["ScrollBody"]))
                for action in insights.get("action_items", []):
                    story.append(Paragraph(f"• {action}", self.styles["ScrollBody"]))
            
            # Source Data
            story.append(Paragraph("Source Data", self.styles["ScrollHeader"]))
            if session.get("metadata"):
                metadata_table = Table([
                    [Paragraph("Source", self.styles["ScrollBody"]),
                     Paragraph(str(session["metadata"].get("source", "Unknown")), self.styles["ScrollBody"])],
                    [Paragraph("Timestamp", self.styles["ScrollBody"]),
                     Paragraph(session["timestamp"], self.styles["ScrollBody"])],
                    [Paragraph("Type", self.styles["ScrollBody"]),
                     Paragraph(str(session["metadata"].get("type", "Unknown")), self.styles["ScrollBody"])]
                ])
                metadata_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5DEB3')),  # Wheat
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'ScrollFont'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('TOPPADDING', (0, 0), (-1, -1), 12),
                ]))
                story.append(metadata_table)
            
            # Footer
            story.append(Spacer(1, 30))
            story.append(Paragraph(
                f"Generated on {datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}",
                self.styles["ScrollBody"]
            ))
            story.append(Paragraph(
                "ScrollIntel v2 - The Flame Interpreter",
                self.styles["ScrollBody"]
            ))
            
            # Build PDF
            doc.build(story)
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise

# Create global instance
pdf_exporter = PDFExporter() 