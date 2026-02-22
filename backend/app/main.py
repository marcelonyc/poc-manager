"""Main FastAPI application"""

import warnings

# Suppress Pydantic V2 deprecation warnings triggered by third-party libs
warnings.filterwarnings(
    "ignore",
    message=r".*__fields__.*deprecated.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*model_fields.*deprecated.*",
    category=DeprecationWarning,
)

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastmcp import FastMCP
from app.config import settings
from app.database import setup_encryption
from app.routers import (
    auth,
    tenants,
    users,
    pocs,
    tasks,
    poc_components,
    invitations,
    products,
    poc_invitations,
    password_reset,
    demo_request,
    tenant_invitations,
    public_pocs,
    chat,
    encryption,
    api_keys,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize encryption for sensitive fields
setup_encryption()

app = FastAPI(
    title="POC Manager API",
    description="Multi-tenant POC management application",
    version="1.0.0",
)


# CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.cors_origins_list,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# Mount uploads directory for static file serving
upload_path = Path(settings.UPLOAD_DIR)
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(tenants.router)
app.include_router(users.router)
app.include_router(pocs.router)
app.include_router(public_pocs.router)
app.include_router(tasks.router)
app.include_router(poc_components.router)
app.include_router(invitations.router)
app.include_router(tenant_invitations.router)
app.include_router(products.router)
app.include_router(poc_invitations.router)
app.include_router(poc_invitations.public_router)
app.include_router(password_reset.router)
app.include_router(demo_request.router)
app.include_router(chat.router)
app.include_router(encryption.router)
app.include_router(api_keys.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "POC Manager API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# 1. Generate MCP server from your API
mcp = FastMCP.from_fastapi(app=app, name="POC Manager MCP")

# 2. Create the MCP's ASGI app
mcp_app = mcp.http_app(path="/mcp")
# CORS middleware
# mcp_app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.cors_origins_list,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# 3. Create a new FastAPI app that combines both sets of routes
combined_app = FastAPI(
    title="POC Manager API with MCP",
    routes=[
        *mcp_app.routes,  # MCP routes
        *app.routes,  # Original API routes
    ],
    lifespan=mcp_app.lifespan,
)

# Add CORS middleware to the combined app (this is the app actually served by uvicorn)
combined_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
