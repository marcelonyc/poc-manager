"""Application configuration"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List
from app.utils.encryption import EncryptionManager


class Settings(BaseSettings):
    """Application settings"""

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "poc_user"
    DATABASE_URL: str = (
        "postgresql://postgres:postgres@localhost:5432/poc_manager"
    )
    DATABASE_TEST_URL: str = (
        "postgresql://postgres:postgres@localhost:5432/poc_manager_test"
    )

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Encryption for sensitive data
    ENCRYPTION_KEY: str = "your-encryption-key-change-in-production"
    ENCRYPTION_LEGACY_KEYS: str = (
        ""  # Comma-separated list of legacy keys for rotation
    )

    # Email
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@example.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:3001,http://localhost:5173"
    FRONTEND_URL: str = "http://localhost:3001"
    PLATFORM_ADMIN_EMAIL: str = "admin@example.com"

    # File Upload
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "uploads"

    # Platform Limits
    DEFAULT_TENANT_ADMIN_LIMIT: int = 5
    DEFAULT_ADMINISTRATOR_LIMIT: int = 10
    DEFAULT_SALES_ENGINEER_LIMIT: int = 50
    DEFAULT_ACCOUNT_EXECUTIVE_LIMIT: int = 50
    DEFAULT_CUSTOMER_LIMIT: int = 500

    # Integrations (Optional defaults)
    SLACK_DEFAULT_TOKEN: str = ""
    SLACK_DEFAULT_CHANNEL: str = ""

    # Slack App (slash-command integration)
    SLACK_BOT_TOKEN: str = ""
    SLACK_SIGNING_SECRET: str = ""
    SLACK_CLIENT_ID: str = ""
    SLACK_CLIENT_SECRET: str = ""
    JIRA_DEFAULT_URL: str = ""
    JIRA_DEFAULT_EMAIL: str = ""
    JIRA_DEFAULT_API_TOKEN: str = ""
    GITHUB_DEFAULT_TOKEN: str = ""
    VITE_API_URL: str = "/api"

    # AI Assistant (Ollama + LlamaIndex)
    OLLAMA_MODEL: str = "llama3.2"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    MCP_TOOLS: str = ""

    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def legacy_encryption_keys(self) -> List[str]:
        """Parse legacy encryption keys for key rotation"""
        if not self.ENCRYPTION_LEGACY_KEYS:
            return []
        return [
            key.strip()
            for key in self.ENCRYPTION_LEGACY_KEYS.split(",")
            if key.strip()
        ]

    def get_encryption_manager(self) -> EncryptionManager:
        """Get configured encryption manager instance"""
        return EncryptionManager(
            primary_key=self.ENCRYPTION_KEY,
            legacy_keys=self.legacy_encryption_keys,
        )


settings = Settings()
