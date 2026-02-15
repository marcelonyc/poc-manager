"""POC router"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    UploadFile,
    File,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, timezone
import secrets
import os
import tempfile
import uuid
from pathlib import Path
from app.database import get_db
from app.models.user import User, UserRole
from app.models.poc import POC, POCStatus, POCParticipant
from app.models.poc_public_link import POCPublicLink
from app.models.product import Product
from app.models.poc_invitation import POCInvitation, POCInvitationStatus
from app.schemas.poc import (
    POCCreate,
    POCUpdate,
    POC as POCSchema,
    POCDetail,
    POCParticipantAdd,
)
from app.schemas.poc_public_link import (
    POCPublicLinkCreate,
    POCPublicLinkResponse,
    POCPublicLinkDetail,
)
from app.auth import (
    require_sales_engineer,
    get_current_user,
    get_current_tenant_id,
    check_tenant_access,
    require_tenant_admin,
)
from app.services.email import send_poc_invitation_email_with_tracking
from app.services.document_generator import DocumentGenerator
from app.utils.demo_limits import check_demo_poc_limit
from app.config import Settings

settings = Settings()

router = APIRouter(prefix="/pocs", tags=["POCs"])


@router.post(
    "/", response_model=POCSchema, status_code=status.HTTP_201_CREATED
)
def create_poc(
    poc_data: POCCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Create a new Proof of Concept (POC).

    Purpose: Initialize a new POC with basic information, timeline, and associated products.
    Creator automatically becomes a sales engineer participant.

    Args:
        poc_data: POCCreate with title, description, customer company, dates, and product IDs

    Returns:
        POCSchema with created POC in DRAFT status

    Requires: Sales Engineer or Administrator role

    Raises:
        403 Forbidden: Insufficient permissions
    """
    # Check demo limits
    check_demo_poc_limit(db, tenant_id, current_user.tenant)

    poc = POC(
        title=poc_data.title,
        description=poc_data.description,
        customer_company_name=poc_data.customer_company_name,
        start_date=poc_data.start_date,
        end_date=poc_data.end_date,
        tenant_id=tenant_id,
        created_by=current_user.id,
        status=POCStatus.DRAFT,
    )
    db.add(poc)
    db.flush()

    # Associate products
    if poc_data.product_ids:
        products = (
            db.query(Product)
            .filter(
                Product.id.in_(poc_data.product_ids),
                Product.tenant_id == tenant_id,
            )
            .all()
        )
        poc.products = products

    # Add creator as participant
    participant = POCParticipant(
        poc_id=poc.id,
        user_id=current_user.id,
        is_sales_engineer=True,
    )
    db.add(participant)
    db.commit()
    db.refresh(poc)

    return poc


@router.get("/", response_model=List[POCSchema])
def list_pocs(
    skip: int = 0,
    limit: int = 100,
    status: POCStatus = None,
    customer_name: str = None,
    user_name: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    List POCs with optional filtering.

    Returns a paginated list of Proof-of-Concept engagements. Results are
    automatically scoped to the caller's tenant. Customers only see POCs
    they participate in. Supports filtering by status, customer company name,
    and participant name.

    Route: GET /pocs/?skip=0&limit=100&status=&customer_name=&user_name=

    Query parameters:
        skip (int, default 0): Number of records to skip for pagination.
        limit (int, default 100): Maximum number of records to return.
        status (str, optional): Filter by POC status — one of "draft", "active", "completed", "archived".
        customer_name (str, optional): Case-insensitive partial match on customer company name.
        user_name (str, optional): Case-insensitive partial match on participant full name.

    Returns:
        List of POC objects, each containing:
            - id (int): Unique POC identifier.
            - title (str): POC title.
            - description (str | null): POC description.
            - tenant_id (int): Owning tenant ID.
            - created_by (int): User ID of the creator.
            - customer_company_name (str | null): Customer organization name.
            - status (str): Current POC status.
            - start_date (date | null): Planned start date.
            - end_date (date | null): Planned end date.
            - overall_success_score (float | null): Aggregate success metric.
            - created_at (datetime): Creation timestamp.
            - updated_at (datetime | null): Last modification timestamp.

    Errors:
        401 Unauthorized: Missing or invalid authentication token.
    """
    query = db.query(POC)

    # Filter by tenant for non-platform admins
    if current_user.role != UserRole.PLATFORM_ADMIN:
        query = query.filter(POC.tenant_id == tenant_id)

    # Filter by status
    if status:
        query = query.filter(POC.status == status)

    # Filter by customer company name
    if customer_name:
        query = query.filter(
            POC.customer_company_name.ilike(f"%{customer_name}%")
        )

    # Filter by participant user name
    if user_name:
        query = (
            query.join(POCParticipant)
            .join(User)
            .filter(User.full_name.ilike(f"%{user_name}%"))
        )

    # Customers only see POCs they're participating in
    if current_user.role == UserRole.CUSTOMER:
        if not user_name:  # Avoid joining twice
            query = query.join(POCParticipant)
        query = query.filter(POCParticipant.user_id == current_user.id)

    pocs = query.offset(skip).limit(limit).all()
    return pocs


@router.get("/{poc_id}", response_model=POCDetail)
def get_poc(
    poc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed POC information including participants and entity counts.

    Retrieves comprehensive details for a single POC, including participant
    list, and counts of success criteria, tasks, and task groups. Access is
    granted to tenant members and POC participants.

    Route: GET /pocs/{poc_id}

    Path parameters:
        poc_id (int): The unique identifier of the POC.

    Returns:
        POC detail object containing:
            - id (int): Unique POC identifier.
            - title (str): POC title.
            - description (str | null): POC description.
            - tenant_id (int): Owning tenant ID.
            - created_by (int): Creator user ID.
            - customer_company_name (str | null): Customer organization name.
            - customer_logo_url (str | null): URL to customer logo.
            - executive_summary (str | null): Executive summary text.
            - objectives (str | null): POC objectives.
            - start_date (date | null): Planned start date.
            - end_date (date | null): Planned end date.
            - status (str): Current status — "draft", "active", "completed", or "archived".
            - overall_success_score (float | null): Aggregate success metric.
            - created_at (datetime): Creation timestamp.
            - updated_at (datetime | null): Last modification timestamp.
            - participants (list): Each with user_id, is_sales_engineer, is_customer.
            - success_criteria_count (int): Number of success criteria.
            - tasks_count (int): Number of POC tasks.
            - task_groups_count (int): Number of POC task groups.

    Errors:
        404 Not Found: POC does not exist.
        403 Forbidden: Caller lacks tenant access and is not a POC participant.
        401 Unauthorized: Missing or invalid authentication token.
    """
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POC not found",
        )

    # Check access
    if not check_tenant_access(current_user, poc.tenant_id):
        # Check if user is a participant
        participant = (
            db.query(POCParticipant)
            .filter(
                POCParticipant.poc_id == poc_id,
                POCParticipant.user_id == current_user.id,
            )
            .first()
        )
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    # Build detailed response
    participants = (
        db.query(POCParticipant).filter(POCParticipant.poc_id == poc_id).all()
    )

    return {
        **poc.__dict__,
        "participants": [
            {
                "user_id": p.user_id,
                "is_sales_engineer": p.is_sales_engineer,
                "is_customer": p.is_customer,
            }
            for p in participants
        ],
        "success_criteria_count": len(poc.success_criteria),
        "tasks_count": len(poc.poc_tasks),
        "task_groups_count": len(poc.poc_task_groups),
    }


@router.put("/{poc_id}", response_model=POCSchema)
def update_poc(
    poc_id: int,
    poc_data: POCUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Update POC information.

    Purpose: Modify POC details including title, description, dates, status, and associated products.

    Args:
        poc_id (int): POC identifier
        poc_data: POCUpdate with fields to modify

    Returns:
        Updated POCSchema

    Requires: Sales Engineer or Administrator

    Raises:
        404 Not Found: POC not found
        403 Forbidden: Access denied
    """
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POC not found",
        )

    # Check access
    if not check_tenant_access(current_user, poc.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Update fields
    update_data = poc_data.model_dump(exclude_unset=True)

    # Handle product_ids separately
    if "product_ids" in update_data:
        product_ids = update_data.pop("product_ids")
        if product_ids is not None:
            products = (
                db.query(Product)
                .filter(
                    Product.id.in_(product_ids),
                    Product.tenant_id == tenant_id,
                )
                .all()
            )
            poc.products = products

    # Update remaining fields
    for field, value in update_data.items():
        setattr(poc, field, value)

    db.commit()
    db.refresh(poc)
    return poc


@router.post("/{poc_id}/participants")
async def add_participant(
    poc_id: int,
    participant_data: POCParticipantAdd,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
):
    """
    Add a participant to a POC.

    Purpose: Add existing user as participant or invite new user with automatic email notification.
    Supports both internal team members and external customers.

    Args:
        poc_id (int): POC identifier
        participant_data: POCParticipantAdd with either user_id or email+full_name for invitation

    Returns:
        Dict with success message and invitation details (if new invitation)

    Requires: Sales Engineer role

    Raises:
        404 Not Found: POC or user not found
        400 Bad Request: User already participant or pending invitation exists
    """
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POC not found",
        )

    # Check access
    if not check_tenant_access(current_user, poc.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Handle existing user or invitation
    if participant_data.user_id:
        user = (
            db.query(User).filter(User.id == participant_data.user_id).first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        user_id = user.id
    else:
        # Send invitation email
        if not participant_data.email or not participant_data.full_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and full_name are required for invitations",
            )

        # Check if user already exists with this email
        existing_user = (
            db.query(User).filter(User.email == participant_data.email).first()
        )
        if existing_user:
            # Check if already a participant
            existing_participant = (
                db.query(POCParticipant)
                .filter(
                    POCParticipant.poc_id == poc_id,
                    POCParticipant.user_id == existing_user.id,
                )
                .first()
            )
            if existing_participant:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is already a participant",
                )

        # Check for existing pending invitation (for both new and existing users)
        existing_invitation = (
            db.query(POCInvitation)
            .filter(
                POCInvitation.poc_id == poc_id,
                POCInvitation.email == participant_data.email,
                POCInvitation.status == POCInvitationStatus.PENDING,
            )
            .first()
        )

        if existing_invitation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pending invitation already exists for this email",
            )

        # Create invitation for both new and existing users
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        invitation = POCInvitation(
            poc_id=poc_id,
            email=participant_data.email,
            full_name=participant_data.full_name,
            token=token,
            status=POCInvitationStatus.PENDING,
            invited_by=current_user.id,
            is_customer=participant_data.is_customer,
            expires_at=expires_at,
            email_sent=False,
            resend_count=0,
        )

        db.add(invitation)
        db.commit()
        db.refresh(invitation)

        # Send invitation email in background
        background_tasks.add_task(
            send_poc_invitation_email_with_tracking,
            invitation_id=invitation.id,
            recipient=participant_data.email,
            full_name=participant_data.full_name,
            poc_title=poc.title,
            token=token,
            invited_by_name=current_user.full_name,
            personal_message=None,
            tenant=poc.tenant,
        )

        return {
            "message": "Invitation sent successfully",
            "invitation_id": invitation.id,
            "expires_at": invitation.expires_at,
        }

    # Check if already participant
    existing = (
        db.query(POCParticipant)
        .filter(
            POCParticipant.poc_id == poc_id, POCParticipant.user_id == user_id
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a participant",
        )

    # Add participant
    participant = POCParticipant(
        poc_id=poc_id,
        user_id=user_id,
        is_sales_engineer=participant_data.is_sales_engineer,
        is_customer=participant_data.is_customer,
    )
    db.add(participant)
    db.commit()

    return {"message": "Participant added successfully"}


@router.delete("/{poc_id}/participants/{user_id}")
def remove_participant(
    poc_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
):
    """
    Remove a participant from a POC.

    Purpose: Unassign user's participation in a POC, revoking their access.

    Args:
        poc_id (int): POC identifier
        user_id (int): User to remove

    Returns:
        Dict with success message

    Requires: Sales Engineer role

    Raises:
        404 Not Found: POC or participant not found
        403 Forbidden: Access denied
    """
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POC not found",
        )

    # Check access
    if not check_tenant_access(current_user, poc.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    participant = (
        db.query(POCParticipant)
        .filter(
            POCParticipant.poc_id == poc_id, POCParticipant.user_id == user_id
        )
        .first()
    )

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found",
        )

    db.delete(participant)
    db.commit()

    return {"message": "Participant removed successfully"}


@router.get("/stats/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Get tenant dashboard statistics.

    Returns aggregate metrics for the caller's tenant, useful for populating
    dashboard widgets. Counts POCs by status and breaks down team composition.

    Route: GET /pocs/stats/dashboard

    Returns:
        Dict containing:
            - active_pocs (int): Count of POCs with status "active".
            - completed_pocs (int): Count of POCs with status "completed".
            - in_progress_pocs (int): Count of POCs with status "draft" or "active".
            - team_members (int): Non-customer users in the tenant.
            - customers (int): Users with "customer" role in the tenant.

    Errors:
        401 Unauthorized: Missing or invalid authentication token.
    """
    # Filter by tenant
    query_base = db.query(POC).filter(POC.tenant_id == tenant_id)

    # Count POCs by status
    active_pocs = query_base.filter(POC.status == POCStatus.ACTIVE).count()
    completed_pocs = query_base.filter(
        POC.status == POCStatus.COMPLETED
    ).count()
    in_progress_pocs = query_base.filter(
        POC.status.in_([POCStatus.DRAFT, POCStatus.ACTIVE])
    ).count()

    # Count team members (users in same tenant excluding customers)
    team_members = (
        db.query(User)
        .filter(
            User.tenant_id == tenant_id,
            User.role != UserRole.CUSTOMER,
        )
        .count()
    )

    # Count customers (users with customer role in same tenant)
    customers = (
        db.query(User)
        .filter(
            User.tenant_id == tenant_id,
            User.role == UserRole.CUSTOMER,
        )
        .count()
    )

    return {
        "active_pocs": active_pocs,
        "completed_pocs": completed_pocs,
        "in_progress_pocs": in_progress_pocs,
        "team_members": team_members,
        "customers": customers,
    }


@router.delete("/{poc_id}")
def archive_poc(
    poc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
):
    """
    Archive a POC.

    Purpose: Mark POC as archived to hide from active lists while preserving data.

    Args:
        poc_id (int): POC identifier

    Returns:
        Dict with success message

    Requires: Sales Engineer role

    Raises:
        404 Not Found: POC not found
        403 Forbidden: Access denied
    """
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POC not found",
        )

    # Check access
    if not check_tenant_access(current_user, poc.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    poc.status = POCStatus.ARCHIVED
    db.commit()

    return {"message": "POC archived successfully"}


@router.get("/{poc_id}/generate-document")
def generate_poc_document(
    poc_id: int,
    format: str = "pdf",  # pdf or markdown
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate and download a POC document as PDF or Markdown.

    Exports the full POC including tasks, success criteria, resources, and
    participants into a downloadable document. Both vendor team members and
    customer participants can generate documents.

    Route: GET /pocs/{poc_id}/generate-document?format=pdf

    Path parameters:
        poc_id (int): The unique identifier of the POC to export.

    Query parameters:
        format (str, default "pdf"): Output format — "pdf" or "markdown".

    Returns:
        FileResponse: Binary file download with Content-Disposition attachment header.
            - PDF: application/pdf media type.
            - Markdown: text/markdown media type.

    Errors:
        404 Not Found: POC does not exist.
        403 Forbidden: Caller is not a tenant member or POC participant.
        400 Bad Request: Invalid format value (must be "pdf" or "markdown").
        401 Unauthorized: Missing or invalid authentication token.
    """
    # Get POC with all relationships
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="POC not found"
        )

    # Check access - allow both vendors and customers to generate documents
    if not check_tenant_access(current_user, poc.tenant_id):
        # Check if user is a customer participant
        is_participant = (
            db.query(POCParticipant)
            .filter(
                POCParticipant.poc_id == poc_id,
                POCParticipant.user_id == current_user.id,
            )
            .first()
        )

        if not is_participant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

    # Validate format
    if format not in ["pdf", "markdown"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Must be 'pdf' or 'markdown'",
        )

    # Generate document
    generator = DocumentGenerator(db, poc)

    # Create temp file
    temp_dir = tempfile.gettempdir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(
        c for c in poc.title if c.isalnum() or c in (" ", "-", "_")
    ).strip()

    if format == "pdf":
        filename = f"{safe_title}_{timestamp}.pdf"
        output_path = os.path.join(temp_dir, filename)
        generator.generate_pdf(output_path)
        media_type = "application/pdf"
    else:  # markdown
        filename = f"{safe_title}_{timestamp}.md"
        output_path = os.path.join(temp_dir, filename)
        generator.generate_markdown(output_path)
        media_type = "text/markdown"

    return FileResponse(
        path=output_path,
        media_type=media_type,
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/{poc_id}/logo")
async def upload_poc_logo(
    poc_id: int,
    logo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Upload customer logo image for POC.

    Purpose: Store customer company logo for display in POC materials. Replaces existing logo.
    Supported formats: JPEG, PNG, GIF, WebP (max 2MB).

    Args:
        poc_id (int): POC identifier
        logo: Image file upload

    Returns:
        Dict with message and logo_url

    Requires: Sales Engineer role

    Raises:
        404 Not Found: POC not found
        400 Bad Request: Invalid format or file too large
        403 Forbidden: Access denied
    """
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POC not found",
        )

    # Check tenant access
    if (
        current_user.role not in [UserRole.PLATFORM_ADMIN]
        and tenant_id != poc.tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Validate file type
    allowed_types = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
    ]
    if logo.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: JPEG, PNG, GIF, WebP",
        )

    # Validate file size (max 2MB for logo)
    content = await logo.read()
    if len(content) > 2 * 1024 * 1024:  # 2MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size: 2MB",
        )

    # Create uploads directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR) / "poc_logos"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_ext = logo.filename.split(".")[-1] if "." in logo.filename else "png"
    filename = f"poc_{poc.id}_{uuid.uuid4().hex[:8]}.{file_ext}"
    file_path = upload_dir / filename

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    # Delete old logo if exists
    if poc.customer_logo_url:
        old_path = Path(settings.UPLOAD_DIR) / poc.customer_logo_url.lstrip(
            "/"
        )
        if old_path.exists():
            old_path.unlink()

    # Update POC logo URL
    poc.customer_logo_url = f"/uploads/poc_logos/{filename}"
    db.commit()

    return {
        "message": "Customer logo uploaded successfully",
        "logo_url": poc.customer_logo_url,
    }


@router.delete("/{poc_id}/logo")
def delete_poc_logo(
    poc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_engineer),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Delete customer logo from POC.

    Purpose: Remove customer logo image associated with POC.

    Args:
        poc_id (int): POC identifier

    Returns:
        Dict with success message

    Requires: Sales Engineer role

    Raises:
        404 Not Found: POC or logo not found
        403 Forbidden: Access denied
    """
    poc = db.query(POC).filter(POC.id == poc_id).first()
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POC not found",
        )

    # Check tenant access
    if (
        current_user.role not in [UserRole.PLATFORM_ADMIN]
        and tenant_id != poc.tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    if not poc.customer_logo_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No logo found",
        )

    # Delete file
    file_path = Path(settings.UPLOAD_DIR) / poc.customer_logo_url.lstrip("/")
    if file_path.exists():
        file_path.unlink()

    # Clear logo URL
    poc.customer_logo_url = None
    db.commit()

    return {"message": "Customer logo deleted successfully"}


# ============ PUBLIC LINK ENDPOINTS ============


@router.post(
    "/{poc_id}/public-link",
    response_model=POCPublicLinkDetail,
    status_code=status.HTTP_201_CREATED,
)
def create_public_link(
    poc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Create a public shareable link for a POC.

    Purpose: Generate a unique public link allowing unauthenticated access to POC content
    (tasks, success criteria, resources, guest comments) without account creation.

    Args:
        poc_id (int): POC identifier

    Returns:
        POCPublicLinkDetail with access_token and access_url

    Requires: Tenant Admin role

    Raises:
        404 Not Found: POC not found
        400 Bad Request: Public link already exists
        403 Forbidden: Access denied
    """
    # Check if POC exists and belongs to the tenant
    poc = (
        db.query(POC)
        .filter(POC.id == poc_id, POC.tenant_id == tenant_id)
        .first()
    )
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POC not found",
        )

    # Check if a link already exists for this POC
    existing_link = (
        db.query(POCPublicLink)
        .filter(
            POCPublicLink.poc_id == poc_id,
            POCPublicLink.tenant_id == tenant_id,
            POCPublicLink.is_deleted == False,
        )
        .first()
    )

    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A public link already exists for this POC. Delete it first to create a new one.",
        )

    # Create new public link
    public_link = POCPublicLink(
        poc_id=poc_id,
        tenant_id=tenant_id,
        created_by=current_user.id,
        access_token=POCPublicLink.generate_token(),
    )

    db.add(public_link)
    db.commit()
    db.refresh(public_link)

    # Return with access URL
    access_url = f"{settings.FRONTEND_URL}/share/{public_link.access_token}"

    return POCPublicLinkDetail(
        id=public_link.id,
        poc_id=public_link.poc_id,
        access_token=public_link.access_token,
        access_url=access_url,
        created_at=public_link.created_at,
        created_by=public_link.created_by,
    )


@router.get("/{poc_id}/public-link", response_model=POCPublicLinkDetail)
def get_public_link(
    poc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Get the public sharing link for a POC.

    Retrieves the existing public link that allows unauthenticated external
    parties to view POC details. The link must have been created previously
    via POST. Only non-deleted links are returned.

    Route: GET /pocs/{poc_id}/public-link

    Path parameters:
        poc_id (int): The unique identifier of the POC.

    Returns:
        Public link detail object containing:
            - id (int): Unique public link identifier.
            - poc_id (int): Associated POC identifier.
            - access_token (str): Token used in the public URL.
            - access_url (str): Full shareable URL (e.g. https://app.example.com/share/{token}).
            - created_at (datetime): When the link was created.
            - created_by (int): User ID who created the link.

    Errors:
        404 Not Found: POC does not exist in this tenant, or no active public link exists.
        403 Forbidden: Caller is not a Tenant Admin.
        401 Unauthorized: Missing or invalid authentication token.
    """
    # Check if POC exists and belongs to the tenant
    poc = (
        db.query(POC)
        .filter(POC.id == poc_id, POC.tenant_id == tenant_id)
        .first()
    )
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POC not found",
        )

    # Get the public link
    public_link = (
        db.query(POCPublicLink)
        .filter(
            POCPublicLink.poc_id == poc_id,
            POCPublicLink.tenant_id == tenant_id,
            POCPublicLink.is_deleted == False,
        )
        .first()
    )

    if not public_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No public link exists for this POC",
        )

    # Return with access URL
    access_url = f"{settings.FRONTEND_URL}/share/{public_link.access_token}"

    return POCPublicLinkDetail(
        id=public_link.id,
        poc_id=public_link.poc_id,
        access_token=public_link.access_token,
        access_url=access_url,
        created_at=public_link.created_at,
        created_by=public_link.created_by,
    )


@router.delete("/{poc_id}/public-link", status_code=status.HTTP_204_NO_CONTENT)
def delete_public_link(
    poc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tenant_admin),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Delete the public link for a POC.

    Purpose: Revoke public access to POC by deleting the shareable link.

    Args:
        poc_id (int): POC identifier

    Returns:
        None (204 No Content)

    Requires: Tenant Admin role

    Raises:
        404 Not Found: POC or public link not found
        403 Forbidden: Access denied
    """

    # Check if POC exists and belongs to the tenant
    poc = (
        db.query(POC)
        .filter(POC.id == poc_id, POC.tenant_id == tenant_id)
        .first()
    )
    if not poc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POC not found",
        )

    # Get the public link
    public_link = (
        db.query(POCPublicLink)
        .filter(
            POCPublicLink.poc_id == poc_id,
            POCPublicLink.tenant_id == tenant_id,
            POCPublicLink.is_deleted == False,
        )
        .first()
    )

    if not public_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No public link exists for this POC",
        )

    # Soft delete the link
    public_link.is_deleted = True
    public_link.deleted_at = datetime.now(timezone.utc)
    db.commit()

    return None
