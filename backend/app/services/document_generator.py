"""Document generation service"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import markdown
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.poc import POC, POCParticipant
from app.models.task import POCTask, POCTaskGroup, POCTaskAssignee
from app.models.comment import Comment
from app.models.resource import Resource
from pathlib import Path
import os


class DocumentGenerator:
    """POC document generator"""

    def __init__(self, db: Session, poc: POC):
        self.db = db
        self.poc = poc
        self.tenant = poc.tenant
        self.primary_color = colors.HexColor(
            self.tenant.primary_color
            if self.tenant and self.tenant.primary_color
            else "#0066cc"
        )
        self.secondary_color = colors.HexColor(
            self.tenant.secondary_color
            if self.tenant and self.tenant.secondary_color
            else "#333333"
        )

    def generate_pdf(self, output_path: str):
        """Generate PDF document"""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add customer logo if available
        if self.poc.customer_logo_url:
            logo_path = self._get_logo_path(self.poc.customer_logo_url)
            if logo_path and os.path.exists(logo_path):
                try:
                    # Add logo centered at top
                    logo = Image(
                        logo_path,
                        width=2 * inch,
                        height=2 * inch,
                        kind="proportional",
                    )
                    logo.hAlign = "CENTER"
                    story.append(logo)
                    story.append(Spacer(1, 0.1 * inch))
                except Exception:
                    pass  # Skip logo if there's an error loading it

        # Customer name centered below logo
        customer_style = ParagraphStyle(
            "CustomerName",
            parent=styles["Heading1"],
            fontSize=18,
            textColor=colors.HexColor("#333333"),
            alignment=TA_CENTER,
            spaceAfter=20,
        )
        story.append(Paragraph(self.poc.customer_company_name, customer_style))
        story.append(Spacer(1, 0.2 * inch))

        # Title
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=self.primary_color,
            spaceAfter=30,
        )
        story.append(Paragraph(self.poc.title, title_style))
        story.append(Spacer(1, 0.2 * inch))

        # POC Details
        details_data = [
            ["Customer:", self.poc.customer_company_name],
            ["Status:", self.poc.status.value],
            [
                "Start Date:",
                str(self.poc.start_date) if self.poc.start_date else "N/A",
            ],
            [
                "End Date:",
                str(self.poc.end_date) if self.poc.end_date else "N/A",
            ],
            [
                "Success Score:",
                (
                    f"{self.poc.overall_success_score}/100"
                    if self.poc.overall_success_score
                    else "N/A"
                ),
            ],
        ]

        details_table = Table(details_data, colWidths=[2 * inch, 4 * inch])
        details_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), self.primary_color),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
                    ("TEXTCOLOR", (1, 0), (1, -1), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                    ("GRID", (0, 0), (-1, -1), 1, self.secondary_color),
                ]
            )
        )
        story.append(details_table)
        story.append(Spacer(1, 0.3 * inch))

        # Description
        if self.poc.description:
            story.append(Paragraph("Description", styles["Heading2"]))
            story.append(Paragraph(self.poc.description, styles["BodyText"]))
            story.append(Spacer(1, 0.2 * inch))

        # Success Criteria
        if self.poc.success_criteria:
            story.append(Paragraph("Success Criteria", styles["Heading2"]))
            criteria_data = [["Criteria", "Target", "Achieved", "Met"]]
            for criteria in self.poc.success_criteria:
                criteria_data.append(
                    [
                        criteria.title,
                        criteria.target_value or "N/A",
                        criteria.achieved_value or "N/A",
                        "Yes" if criteria.is_met else "No",
                    ]
                )

            criteria_table = Table(
                criteria_data,
                colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 0.8 * inch],
            )
            criteria_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), self.primary_color),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        ("GRID", (0, 0), (-1, -1), 1, self.secondary_color),
                    ]
                )
            )
            story.append(criteria_table)
            story.append(Spacer(1, 0.2 * inch))

        # Executive Summary
        if self.poc.executive_summary:
            story.append(Paragraph("Executive Summary", styles["Heading2"]))
            story.append(
                Paragraph(self.poc.executive_summary, styles["BodyText"])
            )
            story.append(Spacer(1, 0.2 * inch))

        # Objectives
        if self.poc.objectives:
            story.append(Paragraph("Objectives", styles["Heading2"]))
            story.append(Paragraph(self.poc.objectives, styles["BodyText"]))
            story.append(Spacer(1, 0.2 * inch))

        # Products
        if self.poc.products:
            story.append(Paragraph("Products", styles["Heading2"]))
            for product in self.poc.products:
                story.append(
                    Paragraph(f"• {product.name}", styles["BodyText"])
                )
            story.append(Spacer(1, 0.2 * inch))

        # Individual Tasks
        individual_tasks = (
            self.db.query(POCTask)
            .filter(POCTask.poc_id == self.poc.id)
            .order_by(POCTask.sort_order)
            .all()
        )

        if individual_tasks:
            story.append(Paragraph("Individual Tasks", styles["Heading2"]))
            story.append(Spacer(1, 0.1 * inch))

            for task in individual_tasks:
                # Task title with status
                status_emoji = {
                    "not_started": "⚪",
                    "in_progress": "🔵",
                    "completed": "✅",
                    "blocked": "🔴",
                }
                emoji = status_emoji.get(task.status.value, "⚪")
                task_title = f"{emoji} {task.title} - {task.status.value.replace('_', ' ').title()}"

                task_style = ParagraphStyle(
                    "TaskTitle",
                    parent=styles["Heading3"],
                    textColor=self.secondary_color,
                )
                story.append(Paragraph(task_title, task_style))

                if task.description:
                    story.append(
                        Paragraph(task.description, styles["BodyText"])
                    )
                    story.append(Spacer(1, 0.1 * inch))

                # Assignees
                assignees = (
                    self.db.query(POCTaskAssignee)
                    .filter(POCTaskAssignee.poc_task_id == task.id)
                    .all()
                )

                if assignees:
                    assignee_text = "<b>Assigned to:</b><br/>"
                    for assignee in assignees:
                        if assignee.participant and assignee.participant.user:
                            name = (
                                assignee.participant.user.full_name
                                or assignee.participant.user.email
                            )
                            email = assignee.participant.user.email
                            assignee_text += f"👤 {name} ({email})<br/>"
                    story.append(Paragraph(assignee_text, styles["BodyText"]))
                    story.append(Spacer(1, 0.1 * inch))

                # Task Resources
                task_resources = (
                    self.db.query(Resource)
                    .filter(Resource.poc_task_id == task.id)
                    .all()
                )

                if task_resources:
                    story.append(
                        Paragraph("<b>Resources:</b>", styles["BodyText"])
                    )
                    for resource in task_resources:
                        res_text = f"• <b>{resource.title}</b> ({resource.resource_type.value})"
                        if resource.description:
                            res_text += f"<br/>  {resource.description}"
                        if resource.resource_type.value == "LINK":
                            res_text += f'<br/>  <a href="{resource.content}">{resource.content}</a>'
                        story.append(Paragraph(res_text, styles["BodyText"]))
                    story.append(Spacer(1, 0.1 * inch))

                # Latest Comments (5)
                comments = (
                    self.db.query(Comment)
                    .filter(Comment.poc_task_id == task.id)
                    .order_by(Comment.created_at.desc())
                    .limit(5)
                    .all()
                )

                if comments:
                    story.append(
                        Paragraph(
                            "<b>Latest Comments:</b>", styles["BodyText"]
                        )
                    )
                    for comment in reversed(comments):
                        author = (
                            comment.author.full_name or comment.author.email
                        )
                        date = comment.created_at.strftime("%Y-%m-%d %H:%M")
                        visibility = (
                            "🔒 Internal"
                            if comment.is_internal
                            else "👁️ Public"
                        )
                        comment_text = f"• <b>{author}</b> ({visibility}) - {date}<br/>  {comment.content}"
                        story.append(
                            Paragraph(comment_text, styles["BodyText"])
                        )
                    story.append(Spacer(1, 0.1 * inch))

                story.append(Spacer(1, 0.15 * inch))

        # Task Groups
        task_groups = (
            self.db.query(POCTaskGroup)
            .filter(POCTaskGroup.poc_id == self.poc.id)
            .order_by(POCTaskGroup.sort_order)
            .all()
        )

        if task_groups:
            story.append(Paragraph("Task Groups", styles["Heading2"]))
            story.append(Spacer(1, 0.1 * inch))

            for group in task_groups:
                # Group title with status
                status_val = (
                    group.status.value if group.status else "not_started"
                )
                status_emoji = {
                    "not_started": "⚪",
                    "in_progress": "🔵",
                    "completed": "✅",
                    "blocked": "🔴",
                }
                emoji = status_emoji.get(status_val, "⚪")
                group_title = f"📁 {group.title} - {emoji} {status_val.replace('_', ' ').title()}"

                group_style = ParagraphStyle(
                    "GroupTitle",
                    parent=styles["Heading3"],
                    textColor=self.primary_color,
                )
                story.append(Paragraph(group_title, group_style))

                if group.description:
                    story.append(
                        Paragraph(group.description, styles["BodyText"])
                    )
                    story.append(Spacer(1, 0.1 * inch))

                # Get tasks in this group
                if group.task_group_id:
                    from app.models.task import TaskGroup

                    template_group = (
                        self.db.query(TaskGroup)
                        .filter(TaskGroup.id == group.task_group_id)
                        .first()
                    )

                    if template_group and template_group.tasks:
                        template_task_ids = [
                            t.id for t in template_group.tasks
                        ]
                        group_tasks = (
                            self.db.query(POCTask)
                            .filter(
                                POCTask.poc_id == self.poc.id,
                                POCTask.task_id.in_(template_task_ids),
                            )
                            .order_by(POCTask.sort_order)
                            .all()
                        )

                        if group_tasks:
                            for task in group_tasks:
                                # Task title with status
                                emoji = status_emoji.get(
                                    task.status.value, "⚪"
                                )
                                task_title = f"  {emoji} {task.title} - {task.status.value.replace('_', ' ').title()}"

                                subtask_style = ParagraphStyle(
                                    "SubTaskTitle",
                                    parent=styles["Heading4"],
                                    textColor=self.secondary_color,
                                    leftIndent=20,
                                )
                                story.append(
                                    Paragraph(task_title, subtask_style)
                                )

                                if task.description:
                                    desc_style = ParagraphStyle(
                                        "SubTaskDesc",
                                        parent=styles["BodyText"],
                                        leftIndent=20,
                                    )
                                    story.append(
                                        Paragraph(task.description, desc_style)
                                    )

                                # Assignees
                                assignees = (
                                    self.db.query(POCTaskAssignee)
                                    .filter(
                                        POCTaskAssignee.poc_task_id == task.id
                                    )
                                    .all()
                                )

                                if assignees:
                                    assignee_names = []
                                    for assignee in assignees:
                                        if (
                                            assignee.participant
                                            and assignee.participant.user
                                        ):
                                            name = (
                                                assignee.participant.user.full_name
                                                or assignee.participant.user.email
                                            )
                                            assignee_names.append(f"👤 {name}")
                                    if assignee_names:
                                        assignee_style = ParagraphStyle(
                                            "AssigneeText",
                                            parent=styles["BodyText"],
                                            leftIndent=20,
                                        )
                                        story.append(
                                            Paragraph(
                                                f"<b>Assigned to:</b> {', '.join(assignee_names)}",
                                                assignee_style,
                                            )
                                        )

                                # Task Resources
                                task_resources = (
                                    self.db.query(Resource)
                                    .filter(Resource.poc_task_id == task.id)
                                    .all()
                                )

                                if task_resources:
                                    res_style = ParagraphStyle(
                                        "ResourceText",
                                        parent=styles["BodyText"],
                                        leftIndent=20,
                                    )
                                    story.append(
                                        Paragraph(
                                            "<b>Resources:</b>", res_style
                                        )
                                    )
                                    for resource in task_resources:
                                        res_text = f"  • {resource.title} ({resource.resource_type.value})"
                                        if (
                                            resource.resource_type.value
                                            == "LINK"
                                        ):
                                            res_text += f'<br/>    <a href="{resource.content}">{resource.content}</a>'
                                        story.append(
                                            Paragraph(res_text, res_style)
                                        )

                                # Latest Comments (5)
                                comments = (
                                    self.db.query(Comment)
                                    .filter(Comment.poc_task_id == task.id)
                                    .order_by(Comment.created_at.desc())
                                    .limit(5)
                                    .all()
                                )

                                if comments:
                                    comment_style = ParagraphStyle(
                                        "CommentText",
                                        parent=styles["BodyText"],
                                        leftIndent=20,
                                    )
                                    story.append(
                                        Paragraph(
                                            "<b>Latest Comments:</b>",
                                            comment_style,
                                        )
                                    )
                                    for comment in reversed(comments):
                                        author = (
                                            comment.author.full_name
                                            or comment.author.email
                                        )
                                        date = comment.created_at.strftime(
                                            "%Y-%m-%d %H:%M"
                                        )
                                        visibility = (
                                            "🔒"
                                            if comment.is_internal
                                            else "👁️"
                                        )
                                        comment_text = f"  {visibility} <b>{author}</b> ({date}): {comment.content}"
                                        story.append(
                                            Paragraph(
                                                comment_text, comment_style
                                            )
                                        )

                                story.append(Spacer(1, 0.1 * inch))

                story.append(Spacer(1, 0.15 * inch))

        # POC-level Resources
        poc_resources = (
            self.db.query(Resource)
            .filter(
                Resource.poc_id == self.poc.id, Resource.poc_task_id.is_(None)
            )
            .all()
        )

        if poc_resources:
            story.append(Paragraph("POC Resources", styles["Heading2"]))
            for resource in poc_resources:
                res_title_style = ParagraphStyle(
                    "ResourceTitle",
                    parent=styles["Heading3"],
                    textColor=self.secondary_color,
                )
                story.append(Paragraph(resource.title, res_title_style))
                story.append(
                    Paragraph(
                        f"<b>Type:</b> {resource.resource_type.value}",
                        styles["BodyText"],
                    )
                )
                if resource.description:
                    story.append(
                        Paragraph(resource.description, styles["BodyText"])
                    )
                if resource.resource_type.value == "LINK":
                    story.append(
                        Paragraph(
                            f'<b>Link:</b> <a href="{resource.content}">{resource.content}</a>',
                            styles["BodyText"],
                        )
                    )
                elif resource.content:
                    story.append(
                        Paragraph(resource.content, styles["BodyText"])
                    )
                story.append(Spacer(1, 0.1 * inch))

        # Participants
        participants = (
            self.db.query(POCParticipant)
            .filter(POCParticipant.poc_id == self.poc.id)
            .all()
        )

        if participants:
            story.append(Paragraph("Participants", styles["Heading2"]))
            participant_data = [["Name", "Email", "Role", "Joined"]]
            for participant in participants:
                if participant.user:
                    name = participant.user.full_name or participant.user.email
                    email = participant.user.email
                    role_parts = []
                    if participant.is_sales_engineer:
                        role_parts.append("Sales Engineer")
                    if participant.is_customer:
                        role_parts.append("Customer")
                    role = (
                        ", ".join(role_parts) if role_parts else "Participant"
                    )
                    joined = (
                        participant.joined_at.strftime("%Y-%m-%d")
                        if participant.joined_at
                        else "N/A"
                    )
                    participant_data.append([name, email, role, joined])

            participant_table = Table(
                participant_data,
                colWidths=[1.5 * inch, 2 * inch, 1.5 * inch, 1 * inch],
            )
            participant_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), self.primary_color),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        ("GRID", (0, 0), (-1, -1), 1, self.secondary_color),
                    ]
                )
            )
            story.append(participant_table)

        # Build PDF
        doc.build(story)
        return output_path

    def generate_word(self, output_path: str):
        """Generate Word document"""
        doc = Document()

        # Add customer logo if available
        if self.poc.customer_logo_url:
            logo_path = self._get_logo_path(self.poc.customer_logo_url)
            if logo_path and os.path.exists(logo_path):
                try:
                    # Add logo centered at top
                    logo_paragraph = doc.add_paragraph()
                    logo_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    run = logo_paragraph.add_run()
                    run.add_picture(logo_path, width=Inches(2))
                except Exception:
                    pass  # Skip logo if there's an error loading it

        # Customer name centered below logo
        customer_para = doc.add_paragraph()
        customer_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        customer_run = customer_para.add_run(self.poc.customer_company_name)
        customer_run.font.size = Pt(18)
        customer_run.font.bold = True
        customer_run.font.color.rgb = RGBColor(51, 51, 51)

        # Add spacing
        doc.add_paragraph()

        # Title
        title = doc.add_heading(self.poc.title, 0)
        title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # POC Details
        doc.add_heading("POC Details", level=1)
        table = doc.add_table(rows=5, cols=2)
        table.style = "Light Grid Accent 1"

        details = [
            ("Customer", self.poc.customer_company_name),
            ("Status", self.poc.status.value),
            (
                "Start Date",
                str(self.poc.start_date) if self.poc.start_date else "N/A",
            ),
            (
                "End Date",
                str(self.poc.end_date) if self.poc.end_date else "N/A",
            ),
            (
                "Success Score",
                (
                    f"{self.poc.overall_success_score}/100"
                    if self.poc.overall_success_score
                    else "N/A"
                ),
            ),
        ]

        for i, (label, value) in enumerate(details):
            table.rows[i].cells[0].text = label
            table.rows[i].cells[1].text = value

        # Description
        if self.poc.description:
            doc.add_heading("Description", level=1)
            doc.add_paragraph(self.poc.description)

        # Success Criteria
        if self.poc.success_criteria:
            doc.add_heading("Success Criteria", level=1)
            criteria_table = doc.add_table(
                rows=len(self.poc.success_criteria) + 1, cols=4
            )
            criteria_table.style = "Light Grid Accent 1"

            # Header
            headers = ["Criteria", "Target", "Achieved", "Met"]
            for i, header in enumerate(headers):
                criteria_table.rows[0].cells[i].text = header

            # Data
            for i, criteria in enumerate(self.poc.success_criteria, 1):
                criteria_table.rows[i].cells[0].text = criteria.title
                criteria_table.rows[i].cells[1].text = (
                    criteria.target_value or "N/A"
                )
                criteria_table.rows[i].cells[2].text = (
                    criteria.achieved_value or "N/A"
                )
                criteria_table.rows[i].cells[3].text = (
                    "Yes" if criteria.is_met else "No"
                )

        # Tasks
        if self.poc.poc_tasks:
            doc.add_heading("Tasks", level=1)
            for task in self.poc.poc_tasks:
                doc.add_heading(task.title, level=2)
                if task.description:
                    doc.add_paragraph(task.description)
                doc.add_paragraph(f"Status: {task.status.value}")
                if task.success_level:
                    doc.add_paragraph(
                        f"Success Level: {task.success_level}/100"
                    )

        # Save
        doc.save(output_path)
        return output_path

    def generate_markdown(self, output_path: str):
        """Generate Markdown document"""
        md_content = []

        # Get theme colors for styling
        primary_color = (
            self.tenant.primary_color
            if self.tenant and self.tenant.primary_color
            else "#0066cc"
        )
        secondary_color = (
            self.tenant.secondary_color
            if self.tenant and self.tenant.secondary_color
            else "#333333"
        )

        # Add customer logo if available
        if self.poc.customer_logo_url:
            # In markdown, we'll reference the logo with a centered HTML image tag
            md_content.append(f'<div align="center">')
            md_content.append(
                f'<img src="{self.poc.customer_logo_url}" alt="Customer Logo" width="200"/>'
            )
            md_content.append(f"</div>\n")

        # Customer name centered with theme color
        md_content.append(f'<div align="center">')
        md_content.append(
            f'<h2 style="color: {secondary_color};">{self.poc.customer_company_name}</h2>'
        )
        md_content.append(f"</div>\n")

        # Title with primary theme color
        md_content.append(
            f'<h1 style="color: {primary_color};">{self.poc.title}</h1>\n'
        )

        # POC Details
        md_content.append(
            f'<h2 style="color: {primary_color};">POC Details</h2>\n'
        )
        md_content.append(f"- **Customer:** {self.poc.customer_company_name}")
        md_content.append(f"- **Status:** {self.poc.status.value}")
        md_content.append(f"- **Start Date:** {self.poc.start_date or 'N/A'}")
        md_content.append(f"- **End Date:** {self.poc.end_date or 'N/A'}")
        if self.poc.overall_success_score:
            md_content.append(
                f"- **Success Score:** {self.poc.overall_success_score}/100"
            )
        md_content.append("")

        # Description
        if self.poc.description:
            md_content.append(
                f'<h2 style="color: {primary_color};">Description</h2>\n'
            )
            md_content.append(self.poc.description)
            md_content.append("")

        # Success Criteria
        if self.poc.success_criteria:
            md_content.append(
                f'<h2 style="color: {primary_color};">Success Criteria</h2>\n'
            )
            md_content.append("| Criteria | Target | Achieved | Met |")
            md_content.append("|----------|--------|----------|-----|")
            for criteria in self.poc.success_criteria:
                met = "✅" if criteria.is_met else "❌"
                md_content.append(
                    f"| {criteria.title} | {criteria.target_value or 'N/A'} | "
                    f"{criteria.achieved_value or 'N/A'} | {met} |"
                )
            md_content.append("")

        # Executive Summary
        if self.poc.executive_summary:
            md_content.append(
                f'<h2 style="color: {primary_color};">Executive Summary</h2>\n'
            )
            md_content.append(self.poc.executive_summary)
            md_content.append("")

        # Objectives
        if self.poc.objectives:
            md_content.append(
                f'<h2 style="color: {primary_color};">Objectives</h2>\n'
            )
            md_content.append(self.poc.objectives)
            md_content.append("")

        # Products
        if self.poc.products:
            md_content.append(
                f'<h2 style="color: {primary_color};">Products</h2>\n'
            )
            for product in self.poc.products:
                md_content.append(f"- **{product.name}**")
            md_content.append("")

        # Individual Tasks
        individual_tasks = (
            self.db.query(POCTask)
            .filter(POCTask.poc_id == self.poc.id)
            .order_by(POCTask.sort_order)
            .all()
        )

        if individual_tasks:
            md_content.append(
                f'<h2 style="color: {primary_color};">Individual Tasks</h2>\n'
            )
            for task in individual_tasks:
                status_emoji = {
                    "not_started": "⚪",
                    "in_progress": "🔵",
                    "completed": "✅",
                    "blocked": "🔴",
                }
                emoji = status_emoji.get(task.status.value, "⚪")

                md_content.append(f"### {task.title}\n")
                md_content.append(
                    f"**Status:** {emoji} {task.status.value.replace('_', ' ').title()}\n"
                )

                if task.description:
                    md_content.append(f"{task.description}\n")

                # Assignees
                assignees = (
                    self.db.query(POCTaskAssignee)
                    .filter(POCTaskAssignee.poc_task_id == task.id)
                    .all()
                )

                if assignees:
                    md_content.append("**Assigned to:**")
                    for assignee in assignees:
                        if assignee.participant and assignee.participant.user:
                            name = (
                                assignee.participant.user.full_name
                                or assignee.participant.user.email
                            )
                            md_content.append(
                                f"- 👤 {name} ({assignee.participant.user.email})"
                            )
                    md_content.append("")

                # Task Resources
                task_resources = (
                    self.db.query(Resource)
                    .filter(Resource.poc_task_id == task.id)
                    .all()
                )

                if task_resources:
                    md_content.append("**Resources:**")
                    for resource in task_resources:
                        md_content.append(
                            f"- **{resource.title}** ({resource.resource_type.value})"
                        )
                        if resource.description:
                            md_content.append(f"  - {resource.description}")
                        if resource.resource_type.value == "LINK":
                            md_content.append(f"  - Link: {resource.content}")
                    md_content.append("")

                # Latest Comments (5)
                comments = (
                    self.db.query(Comment)
                    .filter(Comment.poc_task_id == task.id)
                    .order_by(Comment.created_at.desc())
                    .limit(5)
                    .all()
                )

                if comments:
                    md_content.append("**Latest Comments:**")
                    for comment in reversed(comments):
                        author = (
                            comment.author.full_name or comment.author.email
                        )
                        date = comment.created_at.strftime("%Y-%m-%d %H:%M")
                        visibility = (
                            "🔒 Internal"
                            if comment.is_internal
                            else "👁️ Public"
                        )
                        md_content.append(
                            f"- **{author}** ({visibility}) - {date}"
                        )
                        md_content.append(f"  {comment.content}")
                    md_content.append("")

                md_content.append("---\n")

        # Task Groups
        task_groups = (
            self.db.query(POCTaskGroup)
            .filter(POCTaskGroup.poc_id == self.poc.id)
            .order_by(POCTaskGroup.sort_order)
            .all()
        )

        if task_groups:
            md_content.append(
                f'<h2 style="color: {primary_color};">Task Groups</h2>\n'
            )
            for group in task_groups:
                md_content.append(f"### 📁 {group.title}\n")

                status_emoji = {
                    "not_started": "⚪",
                    "in_progress": "🔵",
                    "completed": "✅",
                    "blocked": "🔴",
                }
                status_val = (
                    group.status.value if group.status else "not_started"
                )
                emoji = status_emoji.get(status_val, "⚪")
                md_content.append(
                    f"**Status:** {emoji} {status_val.replace('_', ' ').title()}\n"
                )

                if group.description:
                    md_content.append(f"{group.description}\n")

                # Get tasks in this group
                if group.task_group_id:
                    from app.models.task import TaskGroup

                    template_group = (
                        self.db.query(TaskGroup)
                        .filter(TaskGroup.id == group.task_group_id)
                        .first()
                    )

                    if template_group and template_group.tasks:
                        template_task_ids = [
                            t.id for t in template_group.tasks
                        ]
                        group_tasks = (
                            self.db.query(POCTask)
                            .filter(
                                POCTask.poc_id == self.poc.id,
                                POCTask.task_id.in_(template_task_ids),
                            )
                            .order_by(POCTask.sort_order)
                            .all()
                        )

                        if group_tasks:
                            md_content.append("**Tasks in this group:**\n")
                            for task in group_tasks:
                                emoji = status_emoji.get(
                                    task.status.value, "⚪"
                                )
                                md_content.append(
                                    f"#### {task.title} - {emoji} {task.status.value.replace('_', ' ').title()}\n"
                                )

                                if task.description:
                                    md_content.append(f"{task.description}\n")

                                # Assignees
                                assignees = (
                                    self.db.query(POCTaskAssignee)
                                    .filter(
                                        POCTaskAssignee.poc_task_id == task.id
                                    )
                                    .all()
                                )

                                if assignees:
                                    assignee_names = []
                                    for assignee in assignees:
                                        if (
                                            assignee.participant
                                            and assignee.participant.user
                                        ):
                                            name = (
                                                assignee.participant.user.full_name
                                                or assignee.participant.user.email
                                            )
                                            assignee_names.append(f"👤 {name}")
                                    if assignee_names:
                                        md_content.append(
                                            f"**Assigned to:** {', '.join(assignee_names)}\n"
                                        )

                                # Task Resources
                                task_resources = (
                                    self.db.query(Resource)
                                    .filter(Resource.poc_task_id == task.id)
                                    .all()
                                )

                                if task_resources:
                                    md_content.append("**Resources:**")
                                    for resource in task_resources:
                                        md_content.append(
                                            f"- {resource.title} ({resource.resource_type.value})"
                                        )
                                        if (
                                            resource.resource_type.value
                                            == "LINK"
                                        ):
                                            md_content.append(
                                                f"  Link: {resource.content}"
                                            )
                                    md_content.append("")

                                # Latest Comments (5)
                                comments = (
                                    self.db.query(Comment)
                                    .filter(Comment.poc_task_id == task.id)
                                    .order_by(Comment.created_at.desc())
                                    .limit(5)
                                    .all()
                                )

                                if comments:
                                    md_content.append("**Latest Comments:**")
                                    for comment in reversed(comments):
                                        author = (
                                            comment.author.full_name
                                            or comment.author.email
                                        )
                                        date = comment.created_at.strftime(
                                            "%Y-%m-%d %H:%M"
                                        )
                                        visibility = (
                                            "🔒"
                                            if comment.is_internal
                                            else "👁️"
                                        )
                                        md_content.append(
                                            f"- {visibility} **{author}** ({date}): {comment.content}"
                                        )
                                    md_content.append("")

                                md_content.append("")

                md_content.append("---\n")

        # POC-level Resources
        poc_resources = (
            self.db.query(Resource)
            .filter(
                Resource.poc_id == self.poc.id, Resource.poc_task_id.is_(None)
            )
            .all()
        )

        if poc_resources:
            md_content.append(
                f'<h2 style="color: {primary_color};">POC Resources</h2>\n'
            )
            for resource in poc_resources:
                md_content.append(f"### {resource.title}\n")
                md_content.append(
                    f"**Type:** {resource.resource_type.value}\n"
                )
                if resource.description:
                    md_content.append(f"{resource.description}\n")

                if resource.resource_type.value == "LINK":
                    md_content.append(f"**Link:** {resource.content}\n")
                elif resource.resource_type.value == "CODE":
                    md_content.append(f"```\n{resource.content}\n```\n")
                else:
                    md_content.append(f"{resource.content}\n")

                md_content.append("")

        # Participants
        participants = (
            self.db.query(POCParticipant)
            .filter(POCParticipant.poc_id == self.poc.id)
            .all()
        )

        if participants:
            md_content.append(
                f'<h2 style="color: {primary_color};">Participants</h2>\n'
            )
            md_content.append("| Name | Email | Role | Joined |")
            md_content.append("|------|-------|------|--------|")
            for participant in participants:
                if participant.user:
                    name = participant.user.full_name or participant.user.email
                    email = participant.user.email
                    role_parts = []
                    if participant.is_sales_engineer:
                        role_parts.append("Sales Engineer")
                    if participant.is_customer:
                        role_parts.append("Customer")
                    role = (
                        ", ".join(role_parts) if role_parts else "Participant"
                    )
                    joined = (
                        participant.joined_at.strftime("%Y-%m-%d")
                        if participant.joined_at
                        else "N/A"
                    )
                    md_content.append(
                        f"| {name} | {email} | {role} | {joined} |"
                    )
            md_content.append("")

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_content))

        return output_path

    def _get_logo_path(self, logo_url: str) -> Optional[str]:

        # Remove leading slash and build path from upload directory
        from app.config import Settings

        settings = Settings()
        relative_path = logo_url.lstrip("/")

        # Handle both /uploads/... and uploads/... formats
        if relative_path.startswith("uploads/"):
            relative_path = relative_path[8:]  # Remove 'uploads/' prefix

        logo_path = Path(settings.UPLOAD_DIR) / relative_path
        return str(logo_path) if logo_path.exists() else None
