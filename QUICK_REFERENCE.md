# Multi-Tenant Quick Reference Guide

## API Endpoints Quick Reference

### Authentication Flow

#### 1. Initial Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "tenants": [
    {
      "tenant_id": 1,
      "tenant_name": "Acme Corp",
      "tenant_slug": "acme-corp",
      "role": "tenant_admin",
      "is_default": true
    },
    {
      "tenant_id": 2,
      "tenant_name": "Demo Corp",
      "tenant_slug": "demo-corp",
      "role": "sales_engineer",
      "is_default": false
    }
  ],
  "requires_selection": true
}
```

#### 2. Select Tenant (if multiple tenants)
```http
POST /api/auth/select-tenant
Content-Type: application/json
Authorization: Basic <base64(email:password)>

{
  "tenant_id": 1
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "tenant_id": 1,
  "tenant_name": "Acme Corp",
  "tenant_slug": "acme-corp",
  "role": "tenant_admin",
  "user_id": 1,
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

#### 3. Switch Tenant (during session)
```http
POST /api/auth/switch-tenant
Content-Type: application/json
Authorization: Bearer <current_token>

{
  "tenant_id": 2
}
```

**Response:** Same as select-tenant, but with new tenant context

#### 4. Get Current User Info
```http
GET /api/auth/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "current_tenant_id": 1,
  "current_role": "tenant_admin",
  "tenants": [
    {
      "tenant_id": 1,
      "tenant_name": "Acme Corp",
      "tenant_slug": "acme-corp",
      "role": "tenant_admin",
      "is_default": true,
      "is_active": true
    }
  ]
}
```

### Tenant Invitations

#### 1. Create Invitation
```http
POST /api/tenant-invitations/
Content-Type: application/json
Authorization: Bearer <token>

{
  "email": "existing.user@example.com",
  "role": "sales_engineer"
}
```

#### 2. Validate Invitation (public)
```http
GET /api/tenant-invitations/validate/{token}
```

#### 3. Accept Invitation (authenticated)
```http
POST /api/tenant-invitations/accept
Content-Type: application/json
Authorization: Bearer <token>

{
  "token": "invitation_token_here"
}
```

## Database Schema Quick Reference

### user_tenant_roles Table
```sql
CREATE TABLE user_tenant_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
    role userrole NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    UNIQUE(user_id, tenant_id)
);
```

### tenant_invitations Table
```sql
CREATE TABLE tenant_invitations (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL,
    tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
    role userrole NOT NULL,
    token VARCHAR UNIQUE NOT NULL,
    status tenantinvitationstatus DEFAULT 'PENDING',
    invited_by_user_id INTEGER REFERENCES users(id),
    invited_by_email VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    accepted_at TIMESTAMP
);
```

## Code Examples

### Backend: Check User's Role in Current Tenant
```python
from app.auth import get_current_user, get_current_tenant_id, get_current_role

@router.get("/some-endpoint")
def my_endpoint(
    current_user: User = Depends(get_current_user),
):
    # Get current tenant and role from token
    tenant_id = get_current_tenant_id(current_user)
    role = get_current_role(current_user)
    
    # Or check if user has specific role in specific tenant
    if current_user.has_role(UserRole.TENANT_ADMIN, tenant_id):
        # Do something
        pass
```

### Backend: Get User's Role for Specific Tenant
```python
user = db.query(User).filter(User.id == user_id).first()
role = user.get_role_for_tenant(tenant_id)

if role == UserRole.TENANT_ADMIN:
    # User is admin in this tenant
    pass
```

### Backend: Create Tenant Invitation
```python
from app.models.tenant_invitation import TenantInvitation, TenantInvitationStatus
import secrets
from datetime import datetime, timedelta

token = secrets.token_urlsafe(32)
invitation = TenantInvitation(
    email="user@example.com",
    tenant_id=current_tenant_id,
    role=UserRole.SALES_ENGINEER,
    token=token,
    status=TenantInvitationStatus.PENDING,
    invited_by_user_id=current_user.id,
    invited_by_email=current_user.email,
    expires_at=datetime.utcnow() + timedelta(days=7),
)
db.add(invitation)
db.commit()
```

### Frontend: Store Token with Tenant Context
```typescript
// After receiving token from select-tenant or switch-tenant
const response = await axios.post('/api/auth/select-tenant', data);

localStorage.setItem('token', response.data.access_token);
localStorage.setItem('user', JSON.stringify({
    id: response.data.user_id,
    email: response.data.email,
    full_name: response.data.full_name,
    role: response.data.role,
    tenant_id: response.data.tenant_id,
    tenant_name: response.data.tenant_name,
    tenant_slug: response.data.tenant_slug,
}));
```

### Frontend: Use TenantSwitcher Component
```tsx
import TenantSwitcher from '@/components/TenantSwitcher';

function Navbar() {
    const [userInfo, setUserInfo] = useState(null);
    
    const handleTenantSwitch = async (tenantId: number) => {
        const response = await axios.post('/api/auth/switch-tenant', 
            { tenant_id: tenantId },
            { headers: { Authorization: `Bearer ${token}` } }
        );
        
        // Update token and user info
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data));
        
        // Refresh page or update state
        window.location.reload();
    };
    
    return (
        <nav>
            <TenantSwitcher
                currentTenantId={userInfo?.tenant_id}
                currentTenantName={userInfo?.tenant_name}
                currentRole={userInfo?.role}
                tenants={userInfo?.tenants}
                onTenantSwitch={handleTenantSwitch}
            />
        </nav>
    );
}
```

## Common Use Cases

### Use Case 1: User Logs in with Multiple Tenants
1. User enters email/password → `/api/auth/login`
2. System returns list of tenants
3. Frontend shows tenant selection page
4. User selects tenant → `/api/auth/select-tenant`
5. System returns JWT with tenant context
6. User accesses application

### Use Case 2: User Switches Tenants
1. User clicks tenant switcher dropdown
2. User selects different tenant
3. Frontend calls `/api/auth/switch-tenant`
4. System returns new JWT with new tenant context
5. Frontend updates token and refreshes state
6. User now working in new tenant context

### Use Case 3: Invite Existing User to Tenant
1. Tenant Admin creates invitation → `/api/tenant-invitations/`
2. System sends email to user
3. User clicks link in email
4. User redirected to login (if not logged in)
5. After login, user accepts invitation → `/api/tenant-invitations/accept`
6. System adds user to tenant with specified role
7. User can now switch to new tenant

### Use Case 4: Existing User Requests Demo
1. User submits demo request with email
2. System detects existing user
3. System creates demo tenant
4. System creates tenant invitation
5. System sends invitation email
6. User logs in with existing credentials
7. User accepts invitation
8. User gains access to demo tenant

## JWT Token Structure

```json
{
  "sub": "123",           // User ID
  "email": "user@example.com",
  "role": "tenant_admin", // Role in current tenant
  "tenant_id": 1,         // Current tenant ID
  "exp": 1234567890       // Expiration timestamp
}
```

## Migration Commands

```bash
# Upgrade to latest
alembic upgrade head

# Downgrade one step
alembic downgrade -1

# Check current version
alembic current

# View history
alembic history

# Specific version
alembic upgrade 20260206_0000
```

## Troubleshooting

### Issue: User can't see any tenants after login
**Check:**
1. Verify user_tenant_roles table has entries for the user
2. Check if tenants are active (`is_active = true`)
3. Verify migration ran successfully

### Issue: Token doesn't include tenant_id
**Check:**
1. Ensure `/api/auth/select-tenant` was called (not just `/api/auth/login`)
2. Verify token was generated with tenant context
3. Check JWT decode to see claims

### Issue: Role checks failing
**Check:**
1. Ensure token includes tenant_id claim
2. Verify user has role in the specified tenant
3. Check `user_tenant_roles` table for correct association

### Issue: Can't switch tenants
**Check:**
1. Verify user has access to target tenant in `user_tenant_roles`
2. Check target tenant is active
3. Ensure current token is valid

## Migration Data Check

```sql
-- Check user tenant associations
SELECT u.email, t.name as tenant_name, utr.role, utr.is_default
FROM users u
JOIN user_tenant_roles utr ON u.id = utr.user_id
LEFT JOIN tenants t ON utr.tenant_id = t.id
ORDER BY u.email, t.name;

-- Check pending invitations
SELECT ti.email, t.name as tenant_name, ti.role, ti.status, ti.expires_at
FROM tenant_invitations ti
JOIN tenants t ON ti.tenant_id = t.id
WHERE ti.status = 'PENDING'
ORDER BY ti.created_at DESC;

-- Check users with multiple tenants
SELECT u.email, COUNT(utr.id) as tenant_count
FROM users u
JOIN user_tenant_roles utr ON u.id = utr.user_id
GROUP BY u.id, u.email
HAVING COUNT(utr.id) > 1;
```

---

**Quick Tip:** Always include `Authorization: Bearer <token>` header in API requests after authentication.
