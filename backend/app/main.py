"""Main FastAPI application"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import settings
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
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="POC Manager API",
    description="Multi-tenant POC management application",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
