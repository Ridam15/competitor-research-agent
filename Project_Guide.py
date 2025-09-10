#!/usr/bin/env python3
"""
Project Guide Generator for Competitor Research Agent
Creates a detailed PDF guide explaining the project's capabilities and usage
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os
from datetime import datetime

class ProjectGuideGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Custom styles with better formatting
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            spaceBefore=20,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.darkblue,
            borderPadding=8,
            backColor=colors.lightblue
        )
        
        self.subheading_style = ParagraphStyle(
            'CustomSubheading', 
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=15,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold',
            leftIndent=10
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            spaceBefore=6,
            textColor=colors.black,
            fontName='Helvetica',
            alignment=TA_JUSTIFY,
            leftIndent=10,
            rightIndent=10
        )
        
        self.code_style = ParagraphStyle(
            'Code',
            parent=self.styles['Normal'],
            fontName='Courier-Bold',
            fontSize=10,
            leftIndent=30,
            rightIndent=10,
            spaceBefore=4,
            spaceAfter=4,
            backColor=colors.lightgrey,
            borderColor=colors.grey,
            borderWidth=1,
            borderPadding=8
        )
        
        self.bullet_style = ParagraphStyle(
            'BulletStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=30,
            bulletIndent=20,
            spaceAfter=4
        )

    def create_title_page(self):
        """Create the title page with better formatting"""
        # Title section
        title = Paragraph("Competitor Research Agent", self.title_style)
        subtitle = Paragraph("AI-Powered Multi-Agent Business Intelligence System", 
                            ParagraphStyle('subtitle', 
                                         parent=self.styles['Heading2'],
                                         fontSize=16,
                                         textColor=colors.darkgreen,
                                         alignment=TA_CENTER,
                                         spaceAfter=10))
        subtitle2 = Paragraph("Complete Project Guide & Documentation", 
                             ParagraphStyle('subtitle2',
                                          parent=self.styles['Heading3'],
                                          fontSize=14,
                                          textColor=colors.blue,
                                          alignment=TA_CENTER,
                                          spaceAfter=20))
        
        # Key features box
        features_box = Paragraph("""
        <para alignment="center" backColor="lightblue" borderColor="darkblue" borderWidth="2" borderPadding="10">
        <b>Key Features:</b><br/>
        🤖 Multi-Agent AI Architecture • 🔍 Intelligent Web Scraping<br/>
        📊 Advanced Data Analysis • 📄 Professional PDF Reports<br/>
        ⚡ Automated Workflow • 🔧 Extensible Framework
        </para>
        """, ParagraphStyle('features', parent=self.styles['Normal'], fontSize=12))
        
        date = Paragraph(f"<para alignment='center'><i>Generated: {datetime.now().strftime('%B %d, %Y')}</i></para>", 
                        self.styles['Normal'])
        
        self.story.extend([
            Spacer(1, 1.5*inch),
            title,
            Spacer(1, 0.3*inch), 
            subtitle,
            Spacer(1, 0.2*inch),
            subtitle2,
            Spacer(1, 0.5*inch),
            features_box,
            Spacer(1, 1.5*inch),
            date
        ])
        
        self.story.append(PageBreak())

    def add_table_of_contents(self):
        """Add table of contents with better formatting"""
        toc_title = Paragraph("📋 Table of Contents", self.heading_style)
        self.story.append(toc_title)
        self.story.append(Spacer(1, 15))
        
        toc_data = [
            ["Section", "Page"],
            ["1. 📖 Project Overview", "3"],
            ["2. ⭐ Key Features & Capabilities", "4"],
            ["3. 🏗️ System Architecture", "5"],
            ["4. 🤖 Multi-Agent Workflow", "6"],
            ["5. 💻 Installation & Setup", "7"],
            ["6. 🚀 Usage Guide", "8"],
            ["7. 🔑 API Configuration", "9"],
            ["8. 🔧 Tool Capabilities", "10"],
            ["9. 📊 Output Examples", "12"],
            ["10. ⚙️ Advanced Configuration", "13"],
            ["11. 🔧 Troubleshooting", "14"],
            ["12. 📋 Technical Specifications", "15"]
        ]
        
        toc_table = Table(toc_data, colWidths=[4.5*inch, 1*inch])
        toc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightsteelblue),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.darkblue),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        self.story.append(toc_table)
        self.story.append(PageBreak())

    def add_overview(self):
        """Add project overview section with better formatting"""
        self.story.append(Paragraph("1. 📖 Project Overview", self.heading_style))
        
        overview_text = """
        The <b>Competitor Research Agent</b> is an advanced AI-powered multi-agent system designed to automate 
        competitive intelligence gathering and analysis. Built with the CrewAI framework and powered by 
        Google's Gemini 2.0 Flash Experimental model, it provides comprehensive market research capabilities 
        through intelligent web scraping, data analysis, and automated report generation.
        """
        
        self.story.append(Paragraph(overview_text, self.body_style))
        self.story.append(Spacer(1, 15))
        
        benefits_text = """
        <para backColor="lightyellow" borderColor="orange" borderWidth="1" borderPadding="10">
        <b>🎯 Key Benefits:</b><br/>
        • Transforms manual competitor research from <b>hours to minutes</b><br/>
        • Delivers professional PDF reports with <b>actionable insights</b><br/>
        • Uses latest AI technology for <b>intelligent analysis</b><br/>
        • Provides <b>comprehensive market intelligence</b> automatically
        </para>
        """
        
        self.story.append(Paragraph(benefits_text, self.body_style))
        self.story.append(Spacer(1, 20))

    def add_key_features(self):
        """Add key features section with improved formatting"""
        self.story.append(Paragraph("2. ⭐ Key Features & Capabilities", self.heading_style))
        
        features_data = [
            ["Feature", "Description", "Technology"],
            ["🔍 Intelligent Web Search", "Automated competitor discovery with AI-optimized queries", "DuckDuckGo API + AI"],
            ["🕷️ Advanced Web Scraping", "JavaScript execution and dynamic content handling", "Playwright Browser"],
            ["🤖 Multi-Agent Architecture", "Three specialized AI agents working in sequence", "CrewAI Framework"],
            ["🧠 AI-Powered Analysis", "Advanced data analysis and insight generation", "Gemini 2.0 Flash Exp"],
            ["📄 Professional Reports", "Automated PDF generation with tables and charts", "ReportLab Library"],
            ["⚡ Rate Limit Management", "Intelligent retry logic with exponential backoff", "Built-in Logic"],
            ["🔧 Extensible Tools", "Modular architecture for easy customization", "Python Classes"],
            ["📈 Comparative Analysis", "Automated competitor feature and pricing comparison", "AI Processing"],
        ]
        
        features_table = Table(features_data, colWidths=[1.8*inch, 2.7*inch, 1.5*inch])
        features_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightsteelblue),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.darkblue),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            # Alternating row colors
            ('BACKGROUND', (0, 2), (-1, 2), colors.aliceblue),
            ('BACKGROUND', (0, 4), (-1, 4), colors.aliceblue),
            ('BACKGROUND', (0, 6), (-1, 6), colors.aliceblue),
            ('BACKGROUND', (0, 8), (-1, 8), colors.aliceblue),
        ]))
        
        self.story.append(features_table)
        self.story.append(Spacer(1, 20))

    def add_architecture(self):
        """Add system architecture section"""
        self.story.append(Paragraph("3. System Architecture", self.heading_style))
        
        arch_text = """
        The system follows a modular, multi-agent architecture built on the CrewAI framework:
        """
        self.story.append(Paragraph(arch_text, self.styles['Normal']))
        
        arch_data = [
            ["Component", "Technology", "Purpose"],
            ["Multi-Agent Framework", "CrewAI", "Orchestrates agent collaboration and task sequencing"],
            ["Language Model", "Gemini 2.0 Flash Experimental", "Powers AI reasoning and content generation"],
            ["Web Search", "DuckDuckGo (ddgs)", "Performs competitor discovery searches"],
            ["Web Scraping", "Playwright", "Extracts detailed information from competitor websites"],
            ["Report Generation", "ReportLab", "Creates professional PDF reports"],
            ["Data Processing", "Pydantic", "Ensures data validation and type safety"],
            ["Logging & Monitoring", "Python Logging", "Tracks system performance and errors"],
            ["Configuration", "Environment Variables", "Manages API keys and settings securely"],
        ]
        
        arch_table = Table(arch_data, colWidths=[2*inch, 2*inch, 2.5*inch])
        arch_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.darkgreen),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        self.story.append(arch_table)
        self.story.append(Spacer(1, 12))

    def add_workflow(self):
        """Add multi-agent workflow section with better visualization"""
        self.story.append(Paragraph("4. 🤖 Multi-Agent Workflow", self.heading_style))
        
        # Add workflow description
        workflow_intro = """
        The system uses a sophisticated multi-agent architecture where three specialized AI agents 
        work together in a coordinated sequence to deliver comprehensive competitive intelligence.
        """
        self.story.append(Paragraph(workflow_intro, self.body_style))
        self.story.append(Spacer(1, 15))
        
        workflow_data = [
            ["Agent", "Primary Role", "Tools Used", "Output Delivered"],
            ["🔍 Researcher Agent", "• Competitor Discovery\n• Data Collection\n• Website Scraping", 
             "• SearchTool\n• ScrapeTool", "• Raw competitor data\n• Website content\n• Company information"],
            ["🧠 Analyzer Agent", "• Data Processing\n• Insight Generation\n• Competitive Analysis", 
             "• LLMSummarizerTool\n• Gemini 2.0 Flash", "• Structured insights\n• Market comparisons\n• Key findings"],
            ["📄 Reporter Agent", "• Report Generation\n• Professional Formatting\n• Output Creation", 
             "• PDFReportTool\n• ReportLab", "• Professional PDF\n• Executive summary\n• Actionable insights"],
        ]
        
        workflow_table = Table(workflow_data, colWidths=[1.3*inch, 2*inch, 1.5*inch, 1.7*inch])
        workflow_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.darkgreen),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        self.story.append(workflow_table)
        self.story.append(Spacer(1, 15))
        
        # Add process flow
        process_flow = """
        <para backColor="lightcyan" borderColor="darkcyan" borderWidth="1" borderPadding="10">
        <b>📊 Sequential Processing Flow:</b><br/>
        <b>Step 1:</b> Research Agent searches for competitors and scrapes their websites<br/>
        <b>Step 2:</b> Analyzer Agent processes the raw data and generates intelligent insights<br/>
        <b>Step 3:</b> Reporter Agent creates a professional PDF report with findings<br/><br/>
        Each agent includes built-in error handling, retry logic, and rate limit management.
        </para>
        """
        
        self.story.append(Paragraph(process_flow, self.body_style))
        self.story.append(Spacer(1, 20))

    def add_installation(self):
        """Add installation guide with step-by-step formatting"""
        self.story.append(Paragraph("5. 💻 Installation & Setup", self.heading_style))
        
        self.story.append(Paragraph("5.1 Prerequisites", self.subheading_style))
        
        prereq_data = [
            ["Requirement", "Version", "Purpose"],
            ["🐍 Python", "3.8+", "Core runtime environment"],
            ["📦 pip", "Latest", "Package management"],
            ["🔧 Git", "Latest", "Version control (optional)"],
            ["☁️ Google Cloud Account", "Active", "Gemini API access"],
            ["💾 Available Storage", "500MB+", "Dependencies and reports"],
        ]
        
        prereq_table = Table(prereq_data, colWidths=[2*inch, 1.5*inch, 3*inch])
        prereq_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkviolet),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.darkviolet),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        self.story.append(prereq_table)
        self.story.append(Spacer(1, 15))
        
        self.story.append(Paragraph("5.2 Step-by-Step Installation", self.subheading_style))
        
        install_steps = [
            ("Step 1: Clone Repository", [
                "git clone <repository-url>",
                "cd competitor-research-agent"
            ]),
            ("Step 2: Create Virtual Environment", [
                "python -m venv venv"
            ]),
            ("Step 3: Activate Environment", [
                "# On macOS/Linux:",
                "source venv/bin/activate",
                "# On Windows:",
                "venv\\Scripts\\activate"
            ]),
            ("Step 4: Install Dependencies", [
                "pip install -r requirements.txt"
            ]),
            ("Step 5: Setup Browser Support", [
                "playwright install"
            ]),
            ("Step 6: Configure API Keys", [
                "# Create .env file with your API keys",
                "GEMINI_API_KEY=your_key_here"
            ])
        ]
        
        for step_title, commands in install_steps:
            self.story.append(Paragraph(f"<b>{step_title}</b>", self.subheading_style))
            for command in commands:
                self.story.append(Paragraph(command, self.code_style))
            self.story.append(Spacer(1, 8))
        
        self.story.append(Spacer(1, 20))

    def add_usage_guide(self):
        """Add usage guide section with better formatting"""
        self.story.append(Paragraph("6. 🚀 Usage Guide", self.heading_style))
        
        self.story.append(Paragraph("6.1 Basic Usage", self.subheading_style))
        
        usage_intro = """
        The system is designed for easy command-line usage. Simply provide a query and let the AI agents 
        handle the rest. The system will automatically search, analyze, and generate a professional report.
        """
        self.story.append(Paragraph(usage_intro, self.body_style))
        self.story.append(Spacer(1, 10))
        
        basic_usage_data = [
            ["Command", "Description", "Expected Output"],
            ["python main.py", "Run with default AI competitors query", "General AI market analysis"],
            ["python main.py \"competitors to OpenAI\"", "Target specific company analysis", "OpenAI competitor analysis"],
            ["python main.py \"top fintech companies\"", "Industry-wide analysis", "Fintech market overview"],
            ["python main.py \"project management tools\"", "Product category analysis", "PM tools comparison"],
        ]
        
        usage_table = Table(basic_usage_data, colWidths=[2.5*inch, 2*inch, 2*inch])
        usage_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.papayawhip),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.darkorange),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        self.story.append(usage_table)
        self.story.append(Spacer(1, 15))
        
        self.story.append(Paragraph("6.2 Advanced Query Examples", self.subheading_style))
        
        advanced_examples = [
            ["Query Category", "Example Query", "Use Case"],
            ["🏢 Company Analysis", "competitors to Tesla automotive", "Automotive industry analysis"],
            ["🌍 Geographic Focus", "European SaaS companies 2024", "Regional market research"],
            ["💰 Investment Research", "unicorn fintech startups", "Investment opportunity analysis"],
            ["🔧 Technology Stack", "cloud infrastructure providers", "Technical platform comparison"],
            ["📈 Market Trends", "AI image generation tools", "Emerging technology trends"],
            ["🎯 Niche Markets", "B2B email marketing platforms", "Specific segment analysis"],
        ]
        
        advanced_table = Table(advanced_examples, colWidths=[1.5*inch, 2.5*inch, 2.5*inch])
        advanced_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkslategray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.darkslategray),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        self.story.append(advanced_table)
        self.story.append(Spacer(1, 20))

    def add_api_configuration(self):
        """Add API configuration section with better formatting"""
        self.story.append(Paragraph("7. 🔑 API Configuration", self.heading_style))
        
        config_intro = """
        The system requires Google Gemini API access for AI processing. Follow these steps to configure 
        your API credentials securely using environment variables.
        """
        self.story.append(Paragraph(config_intro, self.body_style))
        self.story.append(Spacer(1, 15))
        
        # API setup steps
        api_steps_data = [
            ["Step", "Action", "Details"],
            ["1", "Get Gemini API Key", "Visit Google AI Studio (makersuite.google.com)"],
            ["2", "Create Account", "Sign in with Google account"],
            ["3", "Generate Key", "Create new API key in dashboard"],
            ["4", "Create .env File", "Add GEMINI_API_KEY=your_key_here"],
            ["5", "Test Configuration", "Run python main.py to verify"],
        ]
        
        api_table = Table(api_steps_data, colWidths=[0.7*inch, 2*inch, 3.8*inch])
        api_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.mistyrose),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.darkred),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        self.story.append(api_table)
        self.story.append(Spacer(1, 15))
        
        # Rate limits info
        rate_limits = """
        <para backColor="lightgoldenrodyellow" borderColor="gold" borderWidth="1" borderPadding="10">
        <b>⚡ API Rate Limits & Management:</b><br/>
        • <b>Free Tier:</b> 15 requests per minute, 1500 per day<br/>
        • <b>Paid Tier:</b> Higher limits available with billing setup<br/>
        • <b>Built-in Handling:</b> Automatic retry logic with exponential backoff<br/>
        • <b>Error Recovery:</b> Graceful handling of rate limit exceeded errors
        </para>
        """
        
        self.story.append(Paragraph(rate_limits, self.body_style))
        self.story.append(Spacer(1, 20))

    def add_tool_capabilities(self):
        """Add tool capabilities section"""
        self.story.append(Paragraph("8. Tool Capabilities", self.heading_style))
        
        tools_data = [
            ["Tool Name", "Functionality", "Technical Details"],
            ["SearchTool", "Web search for competitor discovery", "• Uses DuckDuckGo API<br/>• Returns top 5 results<br/>• Extracts titles, URLs, snippets"],
            ["ScrapeTool", "Website content extraction", "• Playwright browser automation<br/>• JavaScript execution<br/>• Custom selector targeting"],
            ["LLMSummarizerTool", "AI-powered data analysis", "• Gemini 2.0 Flash Experimental<br/>• Intelligent summarization<br/>• Comparative analysis"],
            ["PDFReportTool", "Professional report generation", "• ReportLab framework<br/>• Styled tables and formatting<br/>• Customizable templates"],
        ]
        
        tools_table = Table(tools_data, colWidths=[1.5*inch, 2*inch, 3*inch])
        tools_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.purple),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        self.story.append(tools_table)
        self.story.append(Spacer(1, 12))
        
        customization_text = """
        <b>Tool Customization:</b>
        Each tool can be extended or modified for specific use cases:
        • Add new search engines to SearchTool
        • Implement custom scraping selectors for specific websites
        • Extend LLMSummarizerTool with domain-specific prompts
        • Customize PDF report templates and styling
        """
        
        self.story.append(Paragraph(customization_text, self.styles['Normal']))
        self.story.append(Spacer(1, 12))

    def add_output_examples(self):
        """Add output examples section"""
        self.story.append(Paragraph("9. Output Examples", self.heading_style))
        
        self.story.append(Paragraph("9.1 Console Output", self.subheading_style))
        
        console_output = [
            "2024-09-09 19:01:15,295 - INFO - Starting competitor research for: top AI competitors",
            "🚀 Crew: crew",
            "└── 📋 Task: Research competitors",
            "    ├── 🔧 Used Competitor Search Tool (1)",
            "    └── 🔧 Used Website Scraper Tool (1)", 
            "└── 📋 Task: Analyze data",
            "    └── 🔧 Used LLM Summarizer Tool (1)",
            "└── 📋 Task: Generate report", 
            "    └── 🔧 Used PDF Report Generator Tool (1)",
            "Final Output: AI_Infrastructure_Companies_Report.pdf"
        ]
        
        for output in console_output:
            self.story.append(Paragraph(output, self.code_style))
        
        self.story.append(Spacer(1, 12))
        
        self.story.append(Paragraph("9.2 PDF Report Structure", self.subheading_style))
        
        report_structure_text = """
        Generated PDF reports include:
        • Executive summary with key findings
        • Competitor comparison table with ratings and pricing
        • Detailed analysis of market positioning
        • Recommendations based on competitive landscape
        • Professional formatting with tables and charts
        """
        
        self.story.append(Paragraph(report_structure_text, self.styles['Normal']))
        self.story.append(Spacer(1, 12))

    def add_advanced_config(self):
        """Add advanced configuration section"""
        self.story.append(Paragraph("10. Advanced Configuration", self.heading_style))
        
        config_options = [
            ["Configuration", "Location", "Purpose"],
            ["Agent Parameters", "src/agents/*.py", "Modify agent behavior, timeouts, iterations"],
            ["Tool Settings", "src/tools/*.py", "Customize search results, scraping selectors"],
            ["Workflow Logic", "src/workflows/*.py", "Adjust task dependencies, retry logic"],
            ["Logging Level", "src/utils/logger.py", "Control verbosity of system logs"],
            ["Model Selection", "Agent configurations", "Switch between AI models (Gemini/Groq)"],
        ]
        
        config_table = Table(config_options, colWidths=[2*inch, 2*inch, 2.5*inch])
        config_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.mistyrose),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.darkred),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        self.story.append(config_table)
        self.story.append(Spacer(1, 12))

    def add_troubleshooting(self):
        """Add troubleshooting section"""
        self.story.append(Paragraph("11. Troubleshooting", self.heading_style))
        
        troubleshooting_data = [
            ["Issue", "Solution"],
            ["API Rate Limits", "• System includes automatic retry logic<br/>• Upgrade to paid API tier<br/>• Increase delay between requests"],
            ["Scraping Failures", "• Some websites block automated access<br/>• Check website robots.txt<br/>• Add custom selectors for specific sites"],
            ["Import Errors", "• Ensure all dependencies installed<br/>• Activate virtual environment<br/>• Run 'playwright install' for browser setup"],
            ["PDF Generation Issues", "• Check file permissions<br/>• Ensure output directory exists<br/>• Verify ReportLab installation"],
            ["Memory Issues", "• Reduce max_results in SearchTool<br/>• Limit concurrent scraping operations<br/>• Monitor system resources"],
        ]
        
        trouble_table = Table(troubleshooting_data, colWidths=[2*inch, 4.5*inch])
        trouble_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.red),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightpink),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.red),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        self.story.append(trouble_table)
        self.story.append(Spacer(1, 12))

    def add_technical_specs(self):
        """Add technical specifications"""
        self.story.append(Paragraph("12. Technical Specifications", self.heading_style))
        
        specs_data = [
            ["Component", "Specification", "Notes"],
            ["Python Version", "3.8+", "Recommended: 3.9 or higher"],
            ["Memory Usage", "~500MB", "Varies with concurrent operations"],
            ["Processing Time", "1-3 minutes", "Depends on query complexity"],
            ["API Calls", "5-15 per run", "Search + AI processing + scraping"],
            ["Output Size", "1-5MB PDF", "Varies with content volume"],
            ["Concurrent Limit", "3 agents", "Sequential processing by default"],
            ["Browser Support", "Chromium", "Playwright managed"],
            ["Network Dependency", "Internet required", "For search and API calls"],
        ]
        
        specs_table = Table(specs_data, colWidths=[2*inch, 2*inch, 2.5*inch])
        specs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightsteelblue),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.darkblue),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        self.story.append(specs_table)
        self.story.append(Spacer(1, 12))

    def generate_pdf(self, filename="Competitor_Research_Agent_Guide.pdf"):
        """Generate the complete PDF guide with improved formatting"""
        doc = SimpleDocTemplate(
            filename, 
            pagesize=letter, 
            topMargin=0.75*inch, 
            bottomMargin=0.75*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        
        # Build all sections
        self.create_title_page()
        self.add_table_of_contents()
        self.add_overview()
        self.add_key_features()
        self.add_architecture()
        self.add_workflow()
        self.add_installation()
        self.add_usage_guide()
        self.add_api_configuration()
        self.add_tool_capabilities()
        self.add_output_examples()
        self.add_advanced_config()
        self.add_troubleshooting()
        self.add_technical_specs()
        
        # Build the PDF
        doc.build(self.story)
        return os.path.abspath(filename)

if __name__ == "__main__":
    generator = ProjectGuideGenerator()
    pdf_path = generator.generate_pdf()
    print(f"Project guide generated: {pdf_path}")
