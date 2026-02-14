"""Product schemas"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class ProductBase(BaseModel):
    """Base product schema"""

    name: str


class ProductCreate(ProductBase):
    """Schema for creating a product"""

    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product"""

    name: Optional[str] = None


class Product(ProductBase):
    """Schema for product response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    created_at: datetime
    updated_at: Optional[datetime]


class ProductWithUsage(Product):
    """Schema for product with usage information"""

    poc_count: int
    poc_titles: List[str] = []
