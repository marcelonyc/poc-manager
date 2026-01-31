"""Products router"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.poc import POC, poc_products
from app.schemas.product import ProductCreate, ProductUpdate, Product as ProductSchema, ProductWithUsage
from app.auth import require_administrator, get_current_user, check_tenant_access

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator)
):
    """Create a new product (Tenant Admin or Administrator)"""
    # Check if product with same name already exists for this tenant
    existing = db.query(Product).filter(
        Product.tenant_id == current_user.tenant_id,
        Product.name == product_data.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists",
        )
    
    product = Product(
        name=product_data.name,
        tenant_id=current_user.tenant_id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/", response_model=List[ProductSchema])
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all products for the current tenant"""
    products = db.query(Product).filter(
        Product.tenant_id == current_user.tenant_id
    ).order_by(Product.name).all()
    return products


@router.get("/{product_id}", response_model=ProductWithUsage)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get product details with usage information"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    if not check_tenant_access(current_user, product.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    # Get POCs using this product
    pocs = db.query(POC).join(poc_products).filter(
        poc_products.c.product_id == product_id
    ).all()
    
    return {
        **product.__dict__,
        "poc_count": len(pocs),
        "poc_titles": [poc.title for poc in pocs]
    }


@router.put("/{product_id}", response_model=ProductSchema)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator)
):
    """Update a product name (Tenant Admin or Administrator)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    if not check_tenant_access(current_user, product.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    # Check if new name already exists for another product
    if product_data.name and product_data.name != product.name:
        existing = db.query(Product).filter(
            Product.tenant_id == current_user.tenant_id,
            Product.name == product_data.name,
            Product.id != product_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this name already exists",
            )
    
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator)
):
    """Delete a product (Tenant Admin or Administrator)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    if not check_tenant_access(current_user, product.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    # Check if product is used in any POCs
    pocs = db.query(POC).join(poc_products).filter(
        poc_products.c.product_id == product_id
    ).all()
    
    if pocs:
        poc_list = [{"id": poc.id, "title": poc.title} for poc in pocs]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Product is in use and cannot be deleted",
                "pocs": poc_list
            }
        )
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}
