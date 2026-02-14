"""Products router"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.poc import POC, poc_products
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    Product as ProductSchema,
    ProductWithUsage,
)
from app.auth import (
    require_administrator,
    get_current_user,
    get_current_tenant_id,
    check_tenant_access,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED
)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Create a new product for use in POCs.

    Purpose: Add a product/solution to tenant catalog that can be associated with POCs.

    Args:
        product_data: ProductCreate with name and description

    Returns:
        ProductSchema with created product

    Requires: Tenant Admin or Administrator

    Raises:
        400 Bad Request: Product name already exists
        403 Forbidden: Insufficient permissions
    """
    # Check if product with same name already exists for this tenant
    existing = (
        db.query(Product)
        .filter(
            Product.tenant_id == tenant_id, Product.name == product_data.name
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists",
        )

    product = Product(
        name=product_data.name,
        tenant_id=tenant_id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/", response_model=List[ProductSchema])
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    List all products in the tenant catalog.

    Returns the complete product catalog for the caller's tenant, sorted
    alphabetically by name. Products can be associated with POCs to track
    which solutions are being evaluated.

    Route: GET /products/

    Returns:
        List of product objects, each containing:
            - id (int): Unique product identifier.
            - name (str): Product name.
            - tenant_id (int): Owning tenant ID.
            - created_at (datetime): Creation timestamp.

    Errors:
        401 Unauthorized: Missing or invalid authentication token.
    """
    products = (
        db.query(Product)
        .filter(Product.tenant_id == tenant_id)
        .order_by(Product.name)
        .all()
    )
    return products


@router.get("/{product_id}", response_model=ProductWithUsage)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get product details with POC usage statistics.

    Retrieves a single product and includes which POCs reference it.
    Useful for understanding product adoption across POC engagements.

    Route: GET /products/{product_id}

    Path parameters:
        product_id (int): The unique identifier of the product.

    Returns:
        Product detail object containing:
            - id (int): Unique product identifier.
            - name (str): Product name.
            - tenant_id (int): Owning tenant ID.
            - created_at (datetime): Creation timestamp.
            - poc_count (int): Number of POCs using this product.
            - poc_titles (list[str]): Titles of POCs using this product.

    Errors:
        404 Not Found: Product does not exist.
        403 Forbidden: Caller does not belong to the product's tenant.
        401 Unauthorized: Missing or invalid authentication token.
    """
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
    pocs = (
        db.query(POC)
        .join(poc_products)
        .filter(poc_products.c.product_id == product_id)
        .all()
    )

    return {
        **product.__dict__,
        "poc_count": len(pocs),
        "poc_titles": [poc.title for poc in pocs],
    }


@router.put("/{product_id}", response_model=ProductSchema)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """
    Update product details.

    Purpose: Modify product name or description.

    Args:
        product_id (int): Product identifier
        product_data: ProductUpdate with fields to modify

    Returns:
        Updated ProductSchema

    Requires: Administrator role

    Raises:
        404 Not Found: Product not found
        400 Bad Request: New name already exists
        403 Forbidden: Insufficient permissions
    """
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
        existing = (
            db.query(Product)
            .filter(
                Product.tenant_id == tenant_id,
                Product.name == product_data.name,
                Product.id != product_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this name already exists",
            )

    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_administrator),
):
    """
    Delete a product from catalog.

    Purpose: Remove a product. Only possible if no POCs use it.

    Args:
        product_id (int): Product identifier

    Returns:
        Dict with success message

    Requires: Administrator role

    Raises:
        404 Not Found: Product not found
        400 Bad Request: Product is in use by POCs
        403 Forbidden: Insufficient permissions
    """

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
    pocs = (
        db.query(POC)
        .join(poc_products)
        .filter(poc_products.c.product_id == product_id)
        .all()
    )

    if pocs:
        poc_list = [{"id": poc.id, "title": poc.title} for poc in pocs]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Product is in use and cannot be deleted",
                "pocs": poc_list,
            },
        )

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}
