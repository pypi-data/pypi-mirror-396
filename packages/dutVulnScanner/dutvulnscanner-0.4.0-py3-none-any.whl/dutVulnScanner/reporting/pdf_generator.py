"""Professional PDF report generation for vulnerability scans."""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """
    Generate professional PDF reports from vulnerability scan results.
    
    Creates multi-section reports with:
    - Cover page with scan metadata
    - Executive summary (AI-generated)
    - Statistics dashboard
    - Detailed vulnerability findings
    - Technical details
    """
    
    # Color scheme
    COLORS = {
        "critical": colors.HexColor("#d32f2f"),
        "high": colors.HexColor("#f57c00"),
        "medium": colors.HexColor("#fbc02d"),
        "low": colors.HexColor("#0288d1"),
        "info": colors.HexColor("#5e35b1"),
        "primary": colors.HexColor("#1976d2"),
        "secondary": colors.HexColor("#424242"),
        "success": colors.HexColor("#388e3c"),
    }
    
    def __init__(self, page_size=letter):
        """
        Initialize PDF generator.
        
        Args:
            page_size: Page size (default: letter, can use A4)
        """
        self.page_size = page_size
        self.styles = getSampleStyleSheet()
        self._register_vietnamese_fonts()
        self._setup_custom_styles()
    
    def _register_vietnamese_fonts(self):
        """Register Vietnamese-compatible Unicode fonts."""
        import os
        
        # Try fonts in order of Vietnamese support quality
        font_candidates = [
            # Noto Sans - best Vietnamese support
            ('/usr/share/fonts/opentype/noto/NotoSans-Regular.ttf', 'NotoSans',
             '/usr/share/fonts/opentype/noto/NotoSans-Bold.ttf', 'NotoSans-Bold'),
            # Liberation Sans - good Vietnamese support
            ('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', 'LiberationSans',
             '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 'LiberationSans-Bold'),
            # DejaVu Sans - decent but may have issues with some combining marks
            ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'DejaVuSans',
             '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold'),
        ]
        
        for regular_path, base_name, bold_path, bold_name in font_candidates:
            try:
                if os.path.exists(regular_path) and os.path.exists(bold_path):
                    pdfmetrics.registerFont(TTFont(base_name, regular_path))
                    pdfmetrics.registerFont(TTFont(bold_name, bold_path))
                    
                    self.base_font = base_name
                    self.bold_font = bold_name
                    logger.info(f"Successfully registered {base_name} fonts for Vietnamese support")
                    return
            except Exception as e:
                logger.debug(f"Could not register {base_name}: {e}")
                continue
        
        # Fallback to built-in fonts
        logger.warning("Could not register Vietnamese fonts, falling back to Helvetica")
        self.base_font = 'Helvetica'
        self.bold_font = 'Helvetica-Bold'

    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.COLORS["primary"],
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName=self.bold_font
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.COLORS["primary"],
            spaceAfter=12,
            spaceBefore=12,
            fontName=self.bold_font
        ))
        
        # Subsection header
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=self.COLORS["secondary"],
            spaceAfter=8,
            spaceBefore=8,
            fontName=self.bold_font
        ))
        
        # AI summary style
        self.styles.add(ParagraphStyle(
            name='AIText',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=self.COLORS["secondary"],
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            leading=14,
            fontName=self.base_font
        ))
    
    def generate_report(
        self,
        output_path: Path,
        scan_results: Dict[str, Any],
        ai_summary: Optional[Dict[str, Any]] = None
    ):
        """
        Generate complete PDF report.
        
        Args:
            output_path: Path to save PDF file
            scan_results: Scan results dictionary
            ai_summary: Optional AI-generated summary
        """
        logger.info(f"Generating PDF report: {output_path}")
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=self.page_size,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        
        # Build content
        story = []
        
        # 1. Cover page
        story.extend(self._build_cover_page(scan_results))
        story.append(PageBreak())
        
        # 2. Executive summary (if AI summary available)
        if ai_summary:
            story.extend(self._build_executive_summary(ai_summary))
            story.append(PageBreak())
        
        # 2.5. Attack suggestions (if available)
        attack_suggestions = scan_results.get("attack_suggestions")
        if attack_suggestions:
            story.extend(self._build_attack_suggestions_section(attack_suggestions))
            story.append(PageBreak())
        
        # 2.6. Defense suggestions (if available)
        defense_suggestions = scan_results.get("defense_suggestions")
        if defense_suggestions:
            story.extend(self._build_defense_suggestions_section(defense_suggestions))
            story.append(PageBreak())
        
        # 3. Statistics overview
        story.extend(self._build_statistics_section(scan_results))
        story.append(Spacer(1, 0.3*inch))
        
        # 4. Detailed findings
        story.extend(self._build_findings_section(scan_results))
        
        # 5. Technical details
        story.append(PageBreak())
        story.extend(self._build_technical_details(scan_results))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        logger.info(f"PDF report generated successfully: {output_path}")
    
    def _build_cover_page(self, scan_results: Dict[str, Any]) -> List:
        """Build cover page elements."""
        elements = []
        
        # Spacer from top
        elements.append(Spacer(1, 2*inch))
        
        # Title
        title = Paragraph("Báo Cáo Quét Lỗ Hổng Bảo Mật", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))
        
        # Scan information table
        scan_info = [
            ["Mục tiêu:", scan_results.get("target", "N/A")],
            ["Mã quét:", scan_results.get("scan_id", "N/A")],
            ["Hồ sơ:", scan_results.get("profile", "N/A")],
            ["Ngày:", scan_results.get("start_time", "N/A")],
            ["Thời gian:", f"{scan_results.get('duration', 0):.2f} giây"],
            ["Trạng thái:", scan_results.get("status", "N/A").upper()],
        ]
        
        table = Table(scan_info, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), self.bold_font, 11),
            ('FONT', (1, 0), (1, -1), self.base_font, 11),
            ('TEXTCOLOR', (0, 0), (0, -1), self.COLORS["secondary"]),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 1*inch))
        
        # Total vulnerabilities (highlighted)
        stats = scan_results.get("statistics", {})
        total_vulns = stats.get("total", 0)
        
        primary_color = self.COLORS["primary"].hexval()[2:]
        vuln_text = f"<para align=center><font size=18 color='#{primary_color}'>" + \
                   f"<b>{total_vulns}</b> Lỗ Hổng Được Phát Hiện</font></para>"
        elements.append(Paragraph(vuln_text, self.styles['BodyText']))
        
        return elements
    
    def _build_executive_summary(self, ai_summary: Dict[str, Any]) -> List:
        """Build executive summary section from AI analysis."""
        elements = []
        
        elements.append(Paragraph("Tóm Tắt Tổng Quan", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add AI-generated sections
        sections = [
            ("Tổng Quan", ai_summary.get("executive_summary", "")),
            ("Đánh Giá Rủi Ro", ai_summary.get("risk_assessment", "")),
            ("Khuyến Nghị Ưu Tiên", ai_summary.get("prioritized_recommendations", "")),
            ("Phân Tích Kỹ Thuật", ai_summary.get("technical_insights", "")),
        ]
        
        for section_title, content in sections:
            if content:
                elements.append(Paragraph(section_title, self.styles['SubsectionHeader']))
                
                # Format content (handle markdown-like formatting)
                content_paragraphs = content.split('\n\n')
                for para in content_paragraphs:
                    if para.strip():
                        # Simple cleanup - just remove markdown symbols for now
                        # More sophisticated parsing would require a markdown library
                        para = para.replace('**', '').replace('*', '')
                        elements.append(Paragraph(para, self.styles['AIText']))
                
                elements.append(Spacer(1, 0.15*inch))
        
        # Add attribution
        model_used = ai_summary.get("model_used", "AI")
        attribution = f"<i>Phân tích được tạo bởi {model_used}</i>"
        elements.append(Paragraph(attribution, self.styles['Italic']))
        
        return elements
    
    def _build_statistics_section(self, scan_results: Dict[str, Any]) -> List:
        """Build statistics overview section."""
        elements = []
        
        elements.append(Paragraph("Thống Kê Lỗ Hổng", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.15*inch))
        
        stats = scan_results.get("statistics", {})
        by_severity = stats.get("by_severity", {})
        
        # Severity breakdown table
        severity_order = ["critical", "high", "medium", "low", "info"]
        severity_data = [["Mức Độ", "Số Lượng", "Tỷ Lệ"]]
        
        total = stats.get("total", 0)
        for severity in severity_order:
            count = by_severity.get(severity, 0)
            percentage = (count / total * 100) if total > 0 else 0
            severity_data.append([
                severity.upper(),
                str(count),
                f"{percentage:.1f}%"
            ])
        
        severity_table = Table(severity_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        
        # Style table with color-coded severity
        table_style = [
            ('FONT', (0, 0), (-1, 0), self.bold_font, 11),
            ('FONT', (0, 1), (-1, -1), self.base_font, 10),
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS["primary"]),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]
        
        # Color-code severity rows
        for idx, severity in enumerate(severity_order, start=1):
            if severity in self.COLORS:
                table_style.append(('TEXTCOLOR', (0, idx), (0, idx), self.COLORS[severity]))
                table_style.append(('FONT', (0, idx), (0, idx), self.bold_font, 10))
        
        severity_table.setStyle(TableStyle(table_style))
        elements.append(severity_table)
        
        # Tools used
        elements.append(Spacer(1, 0.2*inch))
        tools_used = ", ".join(scan_results.get("tools_used", []))
        tools_text = f"<b>Công Cụ Quét:</b> {tools_used}"
        elements.append(Paragraph(tools_text, self.styles['BodyText']))
        
        return elements
    
    def _build_findings_section(self, scan_results: Dict[str, Any]) -> List:
        """Build detailed findings section."""
        elements = []
        
        elements.append(Paragraph("Chi Tiết Phát Hiện", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.15*inch))
        
        vulnerabilities = scan_results.get("vulnerabilities", [])
        
        if not vulnerabilities:
            elements.append(Paragraph(
                "Không phát hiện lỗ hổng nào.",
                self.styles['BodyText']
            ))
            return elements
        
        # Group by severity for better organization
        by_severity = {}
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "info")
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(vuln)
        
        # Display in severity order
        severity_order = ["critical", "high", "medium", "low", "info"]
        
        for severity in severity_order:
            if severity not in by_severity:
                continue
            
            vulns = by_severity[severity]
            
            # Severity header
            severity_map = {
                "critical": "NGHIÊM TRỌNG",
                "high": "CAO",
                "medium": "TRUNG BÌNH",
                "low": "THẤP",
                "info": "THÔNG TIN"
            }
            severity_vi = severity_map.get(severity, severity.upper())
            severity_header = f"Mức Độ {severity_vi} ({len(vulns)})"
            elements.append(Paragraph(severity_header, self.styles['SubsectionHeader']))
            elements.append(Spacer(1, 0.1*inch))
            
            # Create table for each vulnerability
            for vuln in vulns:
                vuln_elements = self._create_vulnerability_item(vuln, severity)
                elements.extend(vuln_elements)
                elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def _create_vulnerability_item(self, vuln: Dict[str, Any], severity: str) -> List:
        """Create elements for a single vulnerability."""
        elements = []
        
        # Vulnerability data
        vuln_data = [
            ["Mã:", vuln.get("id", "N/A")],
            ["Tiêu đề:", vuln.get("title", "N/A")],
            ["Host:", vuln.get("host", "N/A")],
            ["Phát hiện bởi:", vuln.get("detected_by", "N/A")],
            ["Mô tả:", vuln.get("description", "Không có mô tả")],
        ]
        
        # Add evidence if available
        evidence = vuln.get("evidence", {})
        if evidence:
            tech = evidence.get("technology", "")
            version = evidence.get("version", "")
            if tech:
                vuln_data.append(["Công nghệ:", f"{tech} {version}".strip()])
        
        # Add remediation
        remediation = vuln.get("remediation", "")
        if remediation:
            vuln_data.append(["Giải pháp:", remediation])
        
        # Create table
        table = Table(vuln_data, colWidths=[1.5*inch, 5*inch])
        
        color = self.COLORS.get(severity, colors.grey)
        
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), self.bold_font, 9),
            ('FONT', (1, 0), (1, -1), self.base_font, 9),
            ('TEXTCOLOR', (0, 0), (0, -1), self.COLORS["secondary"]),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LINEBELOW', (0, 0), (-1, 0), 1, color),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f5f5f5")),
        ]))
        
        elements.append(KeepTogether(table))
        
        return elements
    
    def _build_attack_suggestions_section(self, attack_data: Dict[str, Any]) -> List:
        """Build attack/exploitation suggestions section."""
        from xml.sax.saxutils import escape
        elements = []
        
        # Section header with warning
        elements.append(Paragraph("⚠️ Đề Xuất Tấn Công / Exploitation", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Warning box
        warning_style = ParagraphStyle(
            name='WarningText',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor("#d32f2f"),
            spaceAfter=10,
            fontName=self.bold_font
        )
        
        warning_text = attack_data.get("warning", "⚠️ CHỈ SỬ DỤNG KHI CÓ SỰ CHO PHÉP BẰNG VĂN BẢN")
        elements.append(Paragraph(escape(warning_text), warning_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Attack scenarios content
        attack_text = attack_data.get("attack_scenarios", "")
        if attack_text:
            # Split by lines and add as paragraphs
            for line in attack_text.split('\n'):
                if line.strip():
                    # Escape HTML entities to prevent parsing errors with XSS payloads
                    para_text = line.replace('```', '').replace('**', '')
                    para_text = escape(para_text)
                    
                    try:
                        elements.append(Paragraph(para_text, self.styles['AIText']))
                    except Exception as e:
                        # If paragraph fails, use plain text
                        logger.warning(f"Failed to add paragraph, using plain text: {str(e)}")
                        from reportlab.platypus import Preformatted
                        elements.append(Preformatted(para_text, self.styles['Code']))
            
            elements.append(Spacer(1, 0.15*inch))
        
        # Add attribution
        model_used = attack_data.get("model_used", "AI")
        attribution = f"<i>Generated by {escape(model_used)}</i>"
        elements.append(Paragraph(attribution, self.styles['Italic']))
        
        return elements
    
    def _build_defense_suggestions_section(self, defense_data: Dict[str, Any]) -> List:
        """Build defense/remediation suggestions section."""
        from xml.sax.saxutils import escape
        elements = []
        
        # Section header
        elements.append(Paragraph("🛡️ Đề Xuất Phòng Thủ / Khắc Phục", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.15*inch))
        
        # Defense content
        defense_text = defense_data.get("remediation_steps", "")
        if defense_text:
            # Split by lines and add as paragraphs
            for line in defense_text.split('\n'):
                if line.strip():
                    # Escape HTML entities to prevent parsing errors
                    para_text = line.replace('```', '').replace('**', '')
                    para_text = escape(para_text)
                    
                    try:
                        elements.append(Paragraph(para_text, self.styles['AIText']))
                    except Exception as e:
                        # If paragraph fails, use plain text
                        logger.warning(f"Failed to add paragraph, using plain text: {str(e)}")
                        from reportlab.platypus import Preformatted
                        elements.append(Preformatted(para_text, self.styles['Code']))
            
            elements.append(Spacer(1, 0.15*inch))
        
        # Add attribution
        model_used = defense_data.get("model_used", "AI")
        attribution = f"<i>Generated by {escape(model_used)}</i>"
        elements.append(Paragraph(attribution, self.styles['Italic']))
        
        return elements

    
    def _build_technical_details(self, scan_results: Dict[str, Any]) -> List:
        """Build technical details section."""
        elements = []
        
        elements.append(Paragraph("Chi Tiết Kỹ Thuật", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.15*inch))
        
        # Scan metadata
        metadata = [
            ["Mã quét:", scan_results.get("scan_id", "N/A")],
            ["Mục tiêu:", scan_results.get("target", "N/A")],
            ["Hồ sơ:", scan_results.get("profile", "N/A")],
            ["Trình chạy:", scan_results.get("runner_type", "N/A")],
            ["Thời gian bắt đầu:", scan_results.get("start_time", "N/A")],
            ["Thời gian kết thúc:", scan_results.get("end_time", "N/A")],
            ["Thời gian thực hiện:", f"{scan_results.get('duration', 0):.2f} giây"],
            ["Trạng thái:", scan_results.get("status", "N/A")],
            ["Thư mục kết quả:", scan_results.get("output_directory", "N/A")],
        ]
        
        table = Table(metadata, colWidths=[2*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), self.bold_font, 9),
            ('FONT', (1, 0), (1, -1), self.base_font, 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _add_header_footer(self, canvas_obj, doc):
        """Add header and footer to pages."""
        canvas_obj.saveState()
        
        # Footer
        footer_text = f"Báo Cáo Quét Lỗ Hổng DUT | Tạo lúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        canvas_obj.setFont(self.base_font, 8)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawCentredString(
            self.page_size[0] / 2,
            0.5 * inch,
            footer_text
        )
        
        # Page number
        canvas_obj.drawRightString(
            self.page_size[0] - 0.75 * inch,
            0.5 * inch,
            f"Trang {doc.page}"
        )
        
        canvas_obj.restoreState()


def create_pdf_report(
    output_path: Path,
    scan_results: Dict[str, Any],
    ai_summary: Optional[Dict[str, Any]] = None
):
    """
    Convenience function to create PDF report.
    
    Args:
        output_path: Path to save PDF
        scan_results: Scan results dictionary
        ai_summary: Optional AI analysis summary
    """
    generator = PDFReportGenerator()
    generator.generate_report(output_path, scan_results, ai_summary)
