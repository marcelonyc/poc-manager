"""Integration model"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.utils.encrypted_field import register_encrypted_field
import enum


class IntegrationType(str, enum.Enum):
    """Integration type enumeration"""

    SLACK = "slack"
    JIRA = "jira"
    GITHUB = "github"
    EMAIL = "email"


class TenantIntegration(Base):
    """Tenant-specific integration configuration"""

    __tablename__ = "tenant_integrations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    integration_type = Column(SQLEnum(IntegrationType), nullable=False)
    is_enabled = Column(Boolean, default=True)

    # Configuration stored as key-value pairs (could be JSON)
    # Slack: token, channel
    # Jira: url, email, api_token, project_key
    # GitHub: token, default_repo
    # Email: server, port, username, password, from_address
    config_data = Column(Text, nullable=True)  # JSON string

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="integrations")

    def __repr__(self):
        return f"<TenantIntegration {self.integration_type} for Tenant:{self.tenant_id}>"


# Register encrypted fields
register_encrypted_field(TenantIntegration, "config_data")
