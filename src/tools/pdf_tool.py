from crewai.tools import BaseTool
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
                               PageBreak, KeepTogether, Image, Flowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from src.utils.logger import logger
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, ClassVar
import json

class EnhancedPDFReportTool(BaseTool):
    """Professional PDF report generator with advanced formatting and charts"""
    
    name: str = "Enhanced PDF Report Generator Tool"
    description: str = """
    Creates comprehensive, professional PDF reports with advanced formatting.
    
    Input: Analysis content (summary text) and optional filename
    Features: Executive summary, charts, tables, professional styling
    Output: Path to generated PDF report
    """
    
    def _setup_custom_styles(self):
        """Setup custom styles for professional report formatting"""
        styles = getSampleStyleSheet()
        
        # Store styles in a dictionary to avoid Pydantic field conflicts
        style_dict = {}
        
        # Title style
        style_dict['title'] = ParagraphStyle(
            'ReportTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            spaceBefore=20,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        # Executive summary style
        style_dict['executive'] = ParagraphStyle(
            'ExecutiveSummary',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            spaceBefore=12,
            textColor=colors.black,
            leftIndent=20,
            rightIndent=20,
            firstLineIndent=0,
            alignment=TA_JUSTIFY
        )
        
        # Section header style
        style_dict['section_header'] = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=18,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.darkblue,
            borderPadding=2
        )
        
        # Subsection style
        style_dict['subsection'] = ParagraphStyle(
            'SubSection',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold'
        )
        
        # Body text style
        style_dict['body'] = ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            spaceBefore=6,
            alignment=TA_JUSTIFY,
            firstLineIndent=20
        )
        
        # Quote style
        style_dict['quote'] = ParagraphStyle(
            'Quote',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            spaceBefore=8,
            leftIndent=30,
            rightIndent=30,
            fontName='Helvetica-Oblique',
            textColor=colors.darkgrey
        )
        
        return style_dict

    def _generate_filename(self, query: str = "") -> str:
        """Generate filename based on query and timestamp"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if query:
            # Clean query for filename
            safe_query = re.sub(r'[^\w\s-]', '', query.replace(' ', '_'))[:20]
            return f"Competitor_Analysis_{safe_query}_{timestamp}.pdf"
        return f"Competitor_Analysis_{timestamp}.pdf"

    def _extract_structured_data(self, content: str) -> Dict[str, Any]:
        """Extract structured data from analysis content for better formatting"""
        
        # Initialize structured data
        structured = {
            'executive_summary': '',
            'key_findings': [],
            'competitors': [],
            'market_insights': [],
            'recommendations': [],
            'raw_content': content
        }
        
        try:
            # Extract executive summary (look for Executive Summary section)
            summary_patterns = [
                r'(?:### Executive Summary|## Executive Summary|Executive Summary)[:\s]*\n\n([^#]+?)(?=\n\n#{1,3}|\n\n[A-Z]|\Z)',
                r'(?:executive summary|summary)[:\s]*([^\.]+(?:\.[^\.]+){0,5}\.)',
                r'^([^#\n]+(?:\.[^\.]+){0,3}\.)'  # First substantial sentences
            ]
            
            summary_found = False
            for pattern in summary_patterns:
                summary_match = re.search(pattern, content, re.IGNORECASE | re.DOTALL | re.MULTILINE)
                if summary_match and len(summary_match.group(1).strip()) > 50:
                    structured['executive_summary'] = summary_match.group(1).strip()
                    summary_found = True
                    break
            
            if not summary_found:
                # Use first substantial paragraph as summary
                sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20][:4]
                structured['executive_summary'] = '. '.join(sentences) + '.' if sentences else content[:400] + '...'

            # Extract key findings more comprehensively
            findings_patterns = [
                r'(?:### Key Insights|## Key Insights|Key Insights|### Key Findings|## Key Findings|Key Findings)[:\s]*\n\n([^#]+?)(?=\n\n#{1,3}|\Z)',
                r'(?:key findings?|findings?|insights?|takeaways?)[:\s]*([^\.]+(?:\.[^\.]+)*\.)',
            ]
            
            for pattern in findings_patterns:
                findings_match = re.search(pattern, content, re.IGNORECASE | re.DOTALL | re.MULTILINE)
                if findings_match:
                    findings_text = findings_match.group(1)
                    # Split on bullet points, asterisks, or line breaks with bullets
                    findings = []
                    for line in findings_text.split('\n'):
                        line = line.strip()
                        if line.startswith('*') or line.startswith('•') or line.startswith('-'):
                            finding = line.lstrip('*•- ').strip()
                            if len(finding) > 10:
                                findings.append(finding)
                    
                    if findings:
                        structured['key_findings'] = findings[:6]  # Top 6 findings
                        break

            # Extract company/competitor names more accurately
            company_patterns = [
                r'\*\*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]*)*(?:\s+(?:Inc|Corp|LLC|Ltd|Group|Motors|Motor|Company))?)\*\*',  # Bold company names
                r'\b(Tesla|BYD|Volkswagen|General Motors|Hyundai|Ford|Rivian|Lucid|Mercedes-Benz|BMW|Audi|Porsche|Kia|Genesis|Chevrolet|Cadillac)\b',  # Known EV companies
                r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]*)+)(?=:|\s+[-–])',  # Company names followed by colon or dash
            ]
            
            competitors_found = set()
            for pattern in company_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    
                    # Clean up and validate company name
                    match = match.strip()
                    if (3 <= len(match) <= 50 and  # Reasonable length
                        match not in ['The', 'This', 'That', 'With', 'From', 'Market', 'Analysis', 'Report'] and  # Not common words
                        not match.lower().startswith('http') and  # Not URLs
                        re.search(r'[A-Za-z]', match)):  # Contains letters
                        competitors_found.add(match.title())
            
            structured['competitors'] = list(competitors_found)[:10]  # Top 10 competitors
            
            # Extract recommendations more accurately
            rec_patterns = [
                r'(?:### Strategic Recommendations|## Strategic Recommendations|Strategic Recommendations|### Recommendations|## Recommendations|Recommendations)[:\s]*\n\n([^#]+?)(?=\n\n#{1,3}|\Z)',
                r'(?:recommend|suggestion|should|advice|strategy)[s]?[:\s]*([^\.]+\.(?:[^\.]+\.){0,2})',
            ]
            
            for pattern in rec_patterns:
                rec_matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL | re.MULTILINE)
                if rec_matches:
                    if isinstance(rec_matches[0], str) and len(rec_matches[0]) > 100:
                        # Extract recommendations from a section
                        rec_text = rec_matches[0]
                        recommendations = []
                        for line in rec_text.split('\n'):
                            line = line.strip()
                            if line.startswith('*') or line.startswith('•') or line.startswith('-'):
                                rec = line.lstrip('*•- ').strip()
                                if len(rec) > 15:
                                    recommendations.append(rec)
                        
                        if recommendations:
                            structured['recommendations'] = recommendations[:5]
                            break
                    else:
                        # Individual recommendation sentences
                        recommendations = [rec.strip() for rec in rec_matches if len(rec.strip()) > 15]
                        if recommendations:
                            structured['recommendations'] = recommendations[:5]
                            break
            
        except Exception as e:
            logger.warning(f"Failed to extract structured data: {e}")
        
        return structured

    def _create_title_page(self, story: list, query: str = "Competitor Analysis"):
        """Create professional title page"""
        
        # Main title
        title = Paragraph(f"{query.title()}", self.title_style)
        
        # Subtitle
        subtitle = Paragraph("Competitive Intelligence Report", 
                           ParagraphStyle('subtitle', parent=self.styles['Heading2'],
                                        fontSize=18, textColor=colors.darkgreen,
                                        alignment=TA_CENTER, spaceAfter=20))
        
        # Report metadata box
        current_date = datetime.now().strftime("%B %d, %Y")
        metadata = f"""
        <para alignment="center" backColor="lightsteelblue" borderColor="darkblue" borderWidth="2" borderPadding="15">
        <b>Report Details</b><br/>
        Generated: {current_date}<br/>
        Analysis Type: Competitive Intelligence<br/>
        AI Model: Gemini 2.0 Flash Experimental<br/>
        Report Version: 2.0 Enhanced
        </para>
        """
        
        metadata_para = Paragraph(metadata, ParagraphStyle('metadata', parent=self.styles['Normal'], fontSize=12))
        
        # Add elements to story
        story.extend([
            Spacer(1, 1.5*inch),
            title,
            Spacer(1, 0.5*inch),
            subtitle,
            Spacer(1, 1*inch),
            metadata_para,
            Spacer(1, 1.5*inch)
        ])
        
        story.append(PageBreak())

    def _create_executive_summary(self, story: list, structured_data: Dict[str, Any]):
        """Create executive summary section"""
        
        # Section title
        story.append(Paragraph("Executive Summary", self.section_style))
        story.append(Spacer(1, 15))
        
        # Summary content
        summary = structured_data.get('executive_summary', 'No executive summary available.')
        story.append(Paragraph(summary, self.exec_summary_style))
        story.append(Spacer(1, 20))
        
        # Key metrics if available
        if structured_data.get('competitors'):
            metrics_data = [
                ["Metric", "Value"],
                ["Competitors Analyzed", str(len(structured_data['competitors']))],
                ["Key Findings", str(len(structured_data.get('key_findings', [])))],
                ["Recommendations", str(len(structured_data.get('recommendations', [])))],
                ["Analysis Date", datetime.now().strftime("%Y-%m-%d")]
            ]
            
            metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightsteelblue),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.darkblue),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(Paragraph("Report Metrics", self.subsection_style))
            story.append(metrics_table)
            story.append(Spacer(1, 20))

    def _create_competitors_section(self, story: list, structured_data: Dict[str, Any]):
        """Create competitors overview section"""
        
        story.append(Paragraph("Competitor Landscape", self.section_style))
        story.append(Spacer(1, 15))
        
        competitors = structured_data.get('competitors', [])
        
        if competitors:
            # Create competitor table
            comp_data = [["#", "Company Name", "Category"]]
            for i, comp in enumerate(competitors, 1):
                # Simple categorization based on common patterns
                category = "Technology" if any(word in comp.lower() for word in ['ai', 'tech', 'data', 'cloud']) else "General"
                comp_data.append([str(i), comp, category])
            
            comp_table = Table(comp_data, colWidths=[0.5*inch, 3*inch, 2*inch])
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.darkgreen),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(comp_table)
        else:
            story.append(Paragraph("No specific competitors identified in the analysis.", self.body_style))
        
        story.append(Spacer(1, 20))

    def _create_findings_section(self, story: list, structured_data: Dict[str, Any]):
        """Create key findings section"""
        
        story.append(Paragraph("Key Findings & Insights", self.section_style))
        story.append(Spacer(1, 15))
        
        findings = structured_data.get('key_findings', [])
        
        if findings:
            for i, finding in enumerate(findings, 1):
                bullet_text = f"• {finding}"
                story.append(Paragraph(bullet_text, self.findings_style))
        else:
            # Extract insights from raw content
            story.append(Paragraph(structured_data.get('raw_content', '')[:1000] + "...", self.body_style))
        
        story.append(Spacer(1, 20))

    def _create_recommendations_section(self, story: list, structured_data: Dict[str, Any]):
        """Create recommendations section"""
        
        story.append(Paragraph("Strategic Recommendations", self.section_style))
        story.append(Spacer(1, 15))
        
        recommendations = structured_data.get('recommendations', [])
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                rec_text = f"{i}. {rec}"
                story.append(Paragraph(rec_text, self.body_style))
                story.append(Spacer(1, 8))
        else:
            default_recs = [
                "Conduct deeper analysis of identified competitors' pricing strategies",
                "Monitor competitor product launches and feature updates regularly",
                "Analyze customer feedback and reviews for competitive positioning insights",
                "Develop differentiation strategies based on identified market gaps"
            ]
            
            for i, rec in enumerate(default_recs, 1):
                rec_text = f"{i}. {rec}"
                story.append(Paragraph(rec_text, self.body_style))
                story.append(Spacer(1, 8))
        
        story.append(Spacer(1, 20))

    def _create_detailed_analysis(self, story: list, structured_data: Dict[str, Any]):
        """Create detailed analysis section"""
        
        story.append(Paragraph("Detailed Analysis", self.section_style))
        story.append(Spacer(1, 15))
        
        # Split content into manageable paragraphs
        content = structured_data.get('raw_content', '')
        paragraphs = content.split('\n')
        
        for paragraph in paragraphs:
            if paragraph.strip() and len(paragraph.strip()) > 50:
                story.append(Paragraph(paragraph.strip(), self.body_style))
                story.append(Spacer(1, 10))

    def _generate_filename(self, query: str = "") -> str:
        """Generate appropriate filename based on query"""
        
        # Clean the query for filename
        clean_query = re.sub(r'[^\w\s-]', '', query).strip()
        clean_query = re.sub(r'[-\s]+', '_', clean_query)
        
        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Generate filename
        if clean_query:
            filename = f"{clean_query}_Competitor_Analysis_{timestamp}.pdf"
        else:
            filename = f"Competitor_Analysis_Report_{timestamp}.pdf"
        
        return filename

    def _run(self, summary: str, filename: Optional[str] = None, query: str = "") -> str:
        """
        Generate enhanced professional PDF report
        
        Args:
            summary: Analysis content to include in report
            filename: Optional custom filename
            query: Original query for context
            
        Returns:
            Path to generated PDF file
        """
        try:
            # Setup styles
            styles = self._setup_custom_styles()
                
            # Generate filename if not provided
            if not filename:
                filename = self._generate_filename(query)
            
            # Ensure PDF extension
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            logger.info(f"Generating enhanced PDF report: {filename}")
            
            # Create document with professional margins
            doc = SimpleDocTemplate(
                filename, 
                pagesize=letter,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch,
                leftMargin=0.75*inch,
                rightMargin=0.75*inch,
                title="Competitor Analysis Report",
                author="AI Competitor Research Agent"
            )
            
            # Extract structured data from summary
            structured_data = self._extract_structured_data(summary)
            
            # Build story elements
            story = []
            
            # Create a simple PDF structure for testing
            story.append(Paragraph(f"Competitor Analysis Report: {query or 'General Analysis'}", styles['title']))
            story.append(Spacer(1, 12))
            
            # Add executive summary
            story.append(Paragraph("Executive Summary", styles['section_header']))
            story.append(Paragraph(structured_data.get('executive_summary', 'Analysis summary not available.'), styles['body']))
            story.append(Spacer(1, 12))
            
            # Add key findings
            story.append(Paragraph("Key Findings", styles['section_header']))
            for finding in structured_data.get('key_findings', ['No key findings identified.']):
                story.append(Paragraph(f"• {finding}", styles['body']))
            story.append(Spacer(1, 12))
            
            # Add competitors section
            story.append(Paragraph("Identified Competitors", styles['section_header']))
            if structured_data.get('competitors'):
                for competitor in structured_data['competitors'][:5]:  # Limit to 5
                    story.append(Paragraph(f"• {competitor}", styles['body']))
            else:
                story.append(Paragraph("No specific competitors identified in the analysis.", styles['body']))
            story.append(Spacer(1, 12))
            
            # Add recommendations
            story.append(Paragraph("Recommendations", styles['section_header']))
            for rec in structured_data.get('recommendations', ['Further analysis recommended.']):
                story.append(Paragraph(f"• {rec}", styles['body']))
            
            # Add complete analysis content instead of just preview
            story.append(PageBreak())
            story.append(Paragraph("Detailed Analysis", styles['section_header']))
            raw_content = structured_data.get('raw_content', summary)
            
            # Process the full content with proper markdown-style formatting
            if raw_content:
                # Split on multiple newlines for section breaks
                sections = raw_content.split('\n\n')
                for section in sections:
                    if section.strip():
                        # Check if it's a header (starts with ### or ##)
                        if section.strip().startswith('###'):
                            header_text = section.strip().replace('###', '').strip()
                            story.append(Paragraph(header_text, styles['subsection']))
                        elif section.strip().startswith('##'):
                            header_text = section.strip().replace('##', '').strip()
                            story.append(Paragraph(header_text, styles['section_header']))
                        elif section.strip().startswith('#'):
                            header_text = section.strip().replace('#', '').strip()
                            story.append(Paragraph(header_text, styles['title']))
                        else:
                            # Regular content - preserve bullet points and formatting
                            lines = section.split('\n')
                            for line in lines:
                                if line.strip():
                                    if line.strip().startswith('*') or line.strip().startswith('-'):
                                        # Bullet point
                                        bullet_text = line.strip().replace('*', '•').replace('-', '•')
                                        story.append(Paragraph(bullet_text, styles['body']))
                                    else:
                                        story.append(Paragraph(line.strip(), styles['body']))
            
            # Build PDF
            doc.build(story)
            
            # Get absolute path
            abs_path = os.path.abspath(filename)
            
            # Log success with file info
            if os.path.exists(abs_path):
                file_size = os.path.getsize(abs_path) / 1024  # Size in KB
                logger.info(f"Enhanced PDF report generated successfully: {abs_path} ({file_size:.1f} KB)")
            
            return abs_path
            
        except Exception as e:
            error_msg = f"Enhanced PDF generation failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return f"Error: {error_msg}"

# Alias for backwards compatibility
PDFReportTool = EnhancedPDFReportTool