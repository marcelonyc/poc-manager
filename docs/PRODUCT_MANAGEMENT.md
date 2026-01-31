# Product Management Feature

## Overview
The Product Management feature allows tenants to maintain a reference catalog of products that can be associated with POCs. This enables better organization and reporting on which products are being evaluated in which POCs.

## Features Implemented

### Backend (✅ Complete)

1. **Database Schema**
   - `products` table: Stores product names per tenant
   - `poc_products` table: Many-to-many association between POCs and Products
   - Foreign key constraints with CASCADE deletes on the association table
   - Tenant isolation: Each product belongs to a single tenant

2. **API Endpoints** (`/products/`)
   - `POST /` - Create a new product (tenant_admin only)
     - Validates duplicate product names within the tenant
   - `GET /` - List all products for the current user's tenant
     - Returns products ordered by name
   - `GET /{id}` - Get product details with usage information
     - Returns: `poc_count` (number of POCs using this product)
     - Returns: `poc_titles` (array of POC titles using this product)
   - `PUT /{id}` - Update/rename a product (tenant_admin only)
     - Validates that new name doesn't conflict with existing products
     - Excludes the current product from duplicate check
   - `DELETE /{id}` - Delete a product (tenant_admin only)
     - Blocks deletion if product is used in any POC
     - Returns error with list of POCs using the product:
       ```json
       {
         "detail": {
           "message": "Cannot delete product. It is used in N POC(s)",
           "pocs": [
             {"id": 1, "title": "POC Title 1"},
             {"id": 2, "title": "POC Title 2"}
           ]
         }
       }
       ```

3. **POC Integration**
   - POC creation accepts `product_ids` array
   - POC update accepts `product_ids` array to change product associations
   - POC detail response includes associated products
   - Product associations are managed through SQLAlchemy relationships

### Frontend (✅ Complete)

1. **Products Page** (`/products`)
   - Accessible only to Tenant Admins
   - Product list with creation date
   - Add/Edit product form
   - Rename confirmation dialog
     - Prompts user to enter new name
     - Confirms before applying rename
   - Delete confirmation with usage protection
     - Shows warning if product is in use
     - Displays scrollable list of POCs using the product
     - Allows deletion only if product is not in use
   - Toast notifications for all operations

2. **Navigation**
   - "Products" link added to navigation menu (visible to tenant_admins only)
   - Route registered in App.tsx

3. **Future Integration (Pending POC Form Implementation)**
   - POC creation form: Multi-select dropdown for product selection
   - POC edit form: Update product associations
   - POC detail view: Display associated products

## Database Schema

### products table
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    tenant_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    UNIQUE(tenant_id, name)  -- Ensures unique product names per tenant
);
```

### poc_products table (Association Table)
```sql
CREATE TABLE poc_products (
    id SERIAL PRIMARY KEY,
    poc_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (poc_id) REFERENCES pocs(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE(poc_id, product_id)  -- Prevents duplicate associations
);
```

## User Permissions

### Tenant Admin
- Create new products
- Rename products (with confirmation)
- Delete products (only if not in use)
- View all tenant products

### Sales Engineers / Administrators
- View product list when creating/editing POCs
- Associate multiple products with POCs
- Cannot manage the product catalog

### Customers
- No access to product management
- May see associated products when viewing POCs (future)

## Business Rules

1. **Product Names**
   - Must be unique within a tenant
   - Cannot be empty
   - Can be renamed at any time (with confirmation)

2. **Product Deletion**
   - Cannot delete if used in any POC
   - System returns list of affected POCs
   - No cascade delete of POCs (protection)

3. **POC Associations**
   - POCs can have zero or more products
   - Products can be associated with multiple POCs
   - Associations persist through POC lifecycle

4. **Tenant Isolation**
   - Products are tenant-specific
   - Cannot associate products from other tenants
   - Product lists filtered by current user's tenant

## API Examples

### Create Product
```bash
POST /products/
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Enterprise Platform"
}
```

### Get Product with Usage
```bash
GET /products/5
Authorization: Bearer <token>

Response:
{
  "id": 5,
  "name": "Enterprise Platform",
  "tenant_id": 1,
  "created_at": "2024-01-30T22:15:00",
  "poc_count": 3,
  "poc_titles": [
    "Acme Corp POC",
    "Beta Industries Evaluation",
    "Gamma Solutions Trial"
  ]
}
```

### Rename Product
```bash
PUT /products/5
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Enterprise Platform v2"
}
```

### Delete Product (with usage)
```bash
DELETE /products/5
Authorization: Bearer <token>

Response (400):
{
  "detail": {
    "message": "Cannot delete product. It is used in 3 POC(s)",
    "pocs": [
      {"id": 1, "title": "Acme Corp POC"},
      {"id": 2, "title": "Beta Industries Evaluation"},
      {"id": 3, "title": "Gamma Solutions Trial"}
    ]
  }
}
```

### Associate Products with POC
```bash
POST /pocs/
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "New POC",
  "description": "Testing products",
  "customer_company_name": "Test Corp",
  "product_ids": [1, 3, 5]
}
```

## Testing

### Manual Testing Steps

1. **Create Products**
   - Login as tenant_admin
   - Navigate to /products
   - Create several test products
   - Verify unique name validation

2. **Rename Product**
   - Click "Rename" on a product
   - Enter new name in confirmation dialog
   - Verify product is renamed
   - Try duplicate name - should fail

3. **Delete Unused Product**
   - Create a product
   - Don't associate with any POC
   - Delete it - should succeed

4. **Delete In-Use Product**
   - Create POCs with product associations (manual DB insert or API)
   - Try to delete the product
   - Verify error modal shows POC list
   - Verify product is NOT deleted

5. **POC-Product Association**
   - Create POC with product_ids
   - Verify association in database
   - Update POC with different product_ids
   - Verify associations updated

### Database Queries for Testing

```sql
-- Check products
SELECT * FROM products WHERE tenant_id = 1;

-- Check POC-product associations
SELECT p.title, pr.name 
FROM pocs p
JOIN poc_products pp ON p.id = pp.poc_id
JOIN products pr ON pp.product_id = pr.id
WHERE p.tenant_id = 1;

-- Check product usage count
SELECT pr.id, pr.name, COUNT(pp.poc_id) as poc_count
FROM products pr
LEFT JOIN poc_products pp ON pr.id = pp.product_id
WHERE pr.tenant_id = 1
GROUP BY pr.id, pr.name;
```

## Files Changed/Added

### Backend
- `backend/app/models/product.py` - NEW
- `backend/app/models/poc.py` - Updated with poc_products table and relationship
- `backend/app/models/tenant.py` - Added products relationship
- `backend/app/schemas/product.py` - NEW
- `backend/app/schemas/poc.py` - Added product_ids and SimpleProduct schema
- `backend/app/routers/products.py` - NEW
- `backend/app/routers/pocs.py` - Updated create/update to handle product associations
- `backend/app/main.py` - Registered products router
- `backend/alembic/versions/20260130_2213-0b30068ce592_add_products_and_poc_products.py` - NEW migration

### Frontend
- `frontend/src/pages/Products.tsx` - NEW (complete product management UI)
- `frontend/src/App.tsx` - Added products route
- `frontend/src/components/Layout.tsx` - Added Products navigation link

## Future Enhancements

1. **POC Forms** (Pending)
   - Implement POC creation form with product multi-select
   - Implement POC edit form with product management
   - Display products in POC detail view

2. **Reporting** (Future)
   - Dashboard widget: Products by usage
   - Product success metrics
   - POC outcomes by product

3. **Advanced Features** (Future)
   - Product categories/tags
   - Product descriptions and metadata
   - Version tracking for products
   - Product lifecycle management

## Migration

The database migration `20260130_2213-0b30068ce592_add_products_and_poc_products.py` has been applied.

To rollback:
```bash
docker compose exec backend alembic downgrade -1
```

To re-apply:
```bash
docker compose exec backend alembic upgrade head
```

## Notes

- Product management is fully implemented on backend
- Frontend UI is complete for product CRUD operations
- POC forms need to be implemented to allow product selection during POC creation/editing
- All tenant isolation rules are enforced at the database and API level
- Cascade deletes are configured to clean up associations when POCs are deleted
- Products themselves cannot be deleted if referenced by any POC (data integrity)
