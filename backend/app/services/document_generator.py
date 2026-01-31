"""Document generation service"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import markdown
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.poc import POC


class DocumentGenerator:
    """POC document generator"""
    
    def __init__(self, db: Session, poc: POC):
        self.db = db
        self.poc = poc
    
    def generate_pdf(self, output_path: str):
        """Generate PDF document"""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=30,
        )
        story.append(Paragraph(self.poc.title, title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # POC Details
        details_data = [
            ['Customer:', self.poc.customer_company_name],
            ['Status:', self.poc.status.value],
            ['Start Date:', str(self.poc.start_date) if self.poc.start_date else 'N/A'],
            ['End Date:', str(self.poc.end_date) if self.poc.end_date else 'N/A'],
            ['Success Score:', f"{self.poc.overall_success_score}/100" if self.poc.overall_success_score else 'N/A'],
        ]
        
        details_table = Table(details_data, colWidths=[2 * inch, 4 * inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Description
        if self.poc.description:
            story.append(Paragraph("Description", styles['Heading2']))
            story.append(Paragraph(self.poc.description, styles['BodyText']))
            story.append(Spacer(1, 0.2 * inch))
        
        # Success Criteria
        if self.poc.success_criteria:
            story.append(Paragraph("Success Criteria", styles['Heading2']))
            criteria_data = [['Criteria', 'Target', 'Achieved', 'Met']]
            for criteria in self.poc.success_criteria:
                criteria_data.append([
                    criteria.title,
                    criteria.target_value or 'N/A',
                    criteria.achieved_value or 'N/A',
                    'Yes' if criteria.is_met else 'No'
                ])
            
            criteria_table = Table(criteria_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 0.8 * inch])
            criteria_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            story.append(criteria_table)
            story.append(Spacer(1, 0.2 * inch))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def generate_word(self, output_path: str):
        """Generate Word document"""
        doc = Document()
        
        # Title
        title = doc.add_heading(self.poc.title, 0)
        title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        # POC Details
        doc.add_heading('POC Details', level=1)
        table = doc.add_table(rows=5, cols=2)
        table.style = 'Light Grid Accent 1'
        
        details = [
            ('Customer', self.poc.customer_company_name),
            ('Status', self.poc.status.value),
            ('Start Date', str(self.poc.start_date) if self.poc.start_date else 'N/A'),
            ('End Date', str(self.poc.end_date) if self.poc.end_date else 'N/A'),
            ('Success Score', f"{self.poc.overall_success_score}/100" if self.poc.overall_success_score else 'N/A'),
        ]
        
        for i, (label, value) in enumerate(details):
            table.rows[i].cells[0].text = label
            table.rows[i].cells[1].text = value
        
        # Description
        if self.poc.description:
            doc.add_heading('Description', level=1)
            doc.add_paragraph(self.poc.description)
        
        # Success Criteria
        if self.poc.success_criteria:
            doc.add_heading('Success Criteria', level=1)
            criteria_table = doc.add_table(rows=len(self.poc.success_criteria) + 1, cols=4)
            criteria_table.style = 'Light Grid Accent 1'
            
            # Header
            headers = ['Criteria', 'Target', 'Achieved', 'Met']
            for i, header in enumerate(headers):
                criteria_table.rows[0].cells[i].text = header
            
            # Data
            for i, criteria in enumerate(self.poc.success_criteria, 1):
                criteria_table.rows[i].cells[0].text = criteria.title
                criteria_table.rows[i].cells[1].text = criteria.target_value or 'N/A'
                criteria_table.rows[i].cells[2].text = criteria.achieved_value or 'N/A'
                criteria_table.rows[i].cells[3].text = 'Yes' if criteria.is_met else 'No'
        
        # Tasks
        if self.poc.poc_tasks:
            doc.add_heading('Tasks', level=1)
            for task in self.poc.poc_tasks:
                doc.add_heading(task.title, level=2)
                if task.description:
                    doc.add_paragraph(task.description)
                doc.add_paragraph(f"Status: {task.status.value}")
                if task.success_level:
                    doc.add_paragraph(f"Success Level: {task.success_level}/100")
        
        # Save
        doc.save(output_path)
        return output_path
    
    def generate_markdown(self, output_path: str):
        """Generate Markdown document"""
        md_content = []
        
        # Title
        md_content.append(f"# {self.poc.title}\n")
        
        # POC Details
        md_content.append("## POC Details\n")
        md_content.append(f"- **Customer:** {self.poc.customer_company_name}")
        md_content.append(f"- **Status:** {self.poc.status.value}")
        md_content.append(f"- **Start Date:** {self.poc.start_date or 'N/A'}")
        md_content.append(f"- **End Date:** {self.poc.end_date or 'N/A'}")
        if self.poc.overall_success_score:
            md_content.append(f"- **Success Score:** {self.poc.overall_success_score}/100")
        md_content.append("")
        
        # Description
        if self.poc.description:
            md_content.append("## Description\n")
            md_content.append(self.poc.description)
            md_content.append("")
        
        # Success Criteria
        if self.poc.success_criteria:
            md_content.append("## Success Criteria\n")
            md_content.append("| Criteria | Target | Achieved | Met |")
            md_content.append("|----------|--------|----------|-----|")
            for criteria in self.poc.success_criteria:
                met = "✅" if criteria.is_met else "❌"
                md_content.append(
                    f"| {criteria.title} | {criteria.target_value or 'N/A'} | "
                    f"{criteria.achieved_value or 'N/A'} | {met} |"
                )
            md_content.append("")
        
        # Tasks
        if self.poc.poc_tasks:
            md_content.append("## Tasks\n")
            for task in self.poc.poc_tasks:
                md_content.append(f"### {task.title}\n")
                if task.description:
                    md_content.append(task.description)
                md_content.append(f"\n**Status:** {task.status.value}")
                if task.success_level:
                    md_content.append(f"**Success Level:** {task.success_level}/100")
                md_content.append("")
        
        # Resources
        if self.poc.resources:
            md_content.append("## Resources\n")
            for resource in self.poc.resources:
                md_content.append(f"### {resource.title}\n")
                if resource.description:
                    md_content.append(resource.description)
                md_content.append(f"\n**Type:** {resource.resource_type.value}\n")
                md_content.append(resource.content)
                md_content.append("")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))
        
        return output_path
