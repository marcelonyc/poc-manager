"""POC schemas"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from app.models.poc import POCStatus


class POCBase(BaseModel):
    """Base POC schema"""

    title: str
    description: Optional[str] = None
    customer_company_name: str
    executive_summary: Optional[str] = None
    objectives: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class POCCreate(POCBase):
    """Schema for creating a POC"""

    product_ids: Optional[List[int]] = []


class POCUpdate(BaseModel):
    """Schema for updating a POC"""

    title: Optional[str] = None
    description: Optional[str] = None
    customer_company_name: Optional[str] = None
    customer_logo_url: Optional[str] = None
    executive_summary: Optional[str] = None
    objectives: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[POCStatus] = None
    overall_success_score: Optional[int] = None
    product_ids: Optional[List[int]] = None


class POCParticipantAdd(BaseModel):
    """Schema for adding a participant to a POC"""

    user_id: Optional[int] = None
    email: Optional[str] = None  # For inviting new users
    full_name: Optional[str] = None
    is_sales_engineer: bool = False
    is_customer: bool = False


class POC(POCBase):
    """Schema for POC response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    created_by: int
    customer_logo_url: Optional[str]
    executive_summary: Optional[str]
    objectives: Optional[str]
    status: POCStatus
    overall_success_score: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]


class SimpleProduct(BaseModel):
    """Simplified product schema for POC responses"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class POCDetail(POC):
    """Schema for detailed POC response with related data"""

    participants: List[dict] = []
    products: List[SimpleProduct] = []
    success_criteria_count: int = 0
    tasks_count: int = 0
    task_groups_count: int = 0
