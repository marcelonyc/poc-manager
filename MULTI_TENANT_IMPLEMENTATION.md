# Multi-Tenant User Support - Implementation Guide

## Overview

This implementation adds comprehensive multi-tenant support to the POC Manager application, allowing users to be associated with multiple tenants, each with potentially different roles.

## Key Changes

### 1. Database Schema Changes

#### New Table: `user_tenant_roles`
A new association table that links users to tenants with specific roles:

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

#### New Table: `tenant_invitations`
For inviting existing users to additional tenants:

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

#### Deprecated Columns (kept for backward compatibility)
The `tenant_id` and `role` columns in the `users` table are now deprecated but kept temporarily to allow for gradual migration.

### 2. Authentication Flow Changes

#### Multi-Step Login Process

**Old Flow:**
1. User provides email/password
2. Receives JWT token immediately
3. Accesses application

**New Flow:**
1. User provides email/password
2. Receives list of available tenants
3. User selects tenant (or auto-selected if only one)
4. Receives JWT token with tenant context
5. Accesses application

#### JWT Token Structure

Tokens now include tenant context:
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "tenant_admin",
  "tenant_id": 123,
  "exp": 1234567890
}
```

### 3. New API Endpoints

#### Authentication Endpoints

**POST `/api/auth/login`**
- Returns tenant selection options
- Response includes list of tenants user has access to
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
    }
  ],
  "requires_selection": false
}
```

**POST `/api/auth/select-tenant`**
- Select tenant after login
- Requires re-authentication (email/password)
- Returns JWT token with tenant context

**POST `/api/auth/switch-tenant`**
- Switch to different tenant during active session
- Requires valid JWT token
- Returns new JWT with new tenant context

**GET `/api/auth/me`**
- Now returns all tenant associations
- Includes current tenant context from token

#### Tenant Invitation Endpoints

**POST `/api/tenant-invitations/`**
- Create invitation for existing user
- Tenant Admin or Platform Admin only
- Sends email to user

**POST `/api/tenant-invitations/accept`**
- Accept tenant invitation
- Requires user to be logged in
- Adds user to tenant with specified role

**GET `/api/tenant-invitations/validate/{token}`**
- Validate invitation token (public)
- Returns invitation details

**GET `/api/tenant-invitations/`**
- List all invitations for current tenant
- Tenant Admin only

**DELETE `/api/tenant-invitations/{invitation_id}`**
- Revoke pending invitation
- Tenant Admin only

### 4. Updated Flows

#### Demo Account Request for Existing Users

**Old Behavior:**
- Existing users requesting demo would get error notification
- No demo tenant created

**New Behavior:**
1. System detects existing user
2. Creates demo tenant immediately
3. Creates tenant invitation
4. Sends email to user
5. User logs in and accepts invitation
6. User gains access to demo tenant

#### User Invitation to New Tenant

**Scenario:** Tenant Admin wants to add an existing user to their tenant

**Flow:**
1. Tenant Admin creates tenant invitation with role
2. System sends email to user
3. User clicks "Accept Invitation" in email
4. User is redirected to login (if not already logged in)
5. After login, user accepts invitation
6. User-tenant-role association is created
7. User can now switch between tenants

### 5. Frontend Components

#### `TenantSwitcher` Component
- Dropdown menu in navigation bar
- Shows current tenant and role
- Lists all available tenants
- Allows switching between tenants
- Located: `/frontend/src/components/TenantSwitcher.tsx`

#### `TenantSelection` Page
- Shown after login if user has multiple tenants
- Radio button selection of tenant
- Continues to application after selection
- Located: `/frontend/src/pages/TenantSelection.tsx`

### 6. Migration Strategy

#### Phase 1: Create New Tables (Migration `20260206_0000`)
- Creates `user_tenant_roles` table
- Migrates existing data from `users` table
- Keeps old `tenant_id` and `role` columns for backward compatibility

#### Phase 2: Add Tenant Invitations (Migration `20260206_0001`)
- Creates `tenant_invitations` table
- Creates necessary indexes

#### Phase 3: (Future) Remove Deprecated Columns
- After all code is updated and tested
- Remove `tenant_id` and `role` from `users` table

### 7. Code Changes Summary

#### New Models
- `UserTenantRole` - Association between user, tenant, and role
- `TenantInvitation` - Invitations for existing users

#### Updated Models
- `User` - Added `tenant_roles` relationship and helper methods
  - `get_role_for_tenant(tenant_id)` - Get role for specific tenant
  - `get_default_tenant_role()` - Get default tenant
  - `has_role(role, tenant_id)` - Check if user has role
- `Tenant` - Added `user_roles` relationship

#### Updated Authentication
- `create_access_token()` - Now accepts `tenant_id` parameter
- `get_current_user()` - Extracts and stores tenant context
- Role checking functions - Updated to use tenant context

#### New Routers
- `tenant_invitations.py` - Handle tenant invitations

#### Updated Routers
- `auth.py` - Multi-tenant login flow
- `demo_request.py` - Handle existing users requesting demos

### 8. Configuration

No configuration changes required. The system automatically handles:
- Multi-tenant context in JWT tokens
- Tenant switching
- Role-based access control per tenant

### 9. Testing the Changes

#### Run Migrations
```bash
cd backend
alembic upgrade head
```

#### Test Multi-Tenant Login
1. Create user with access to multiple tenants (via seed data or invitations)
2. Login - should receive tenant selection response
3. Select tenant - should receive token with tenant context
4. Access protected endpoints - should respect tenant context

#### Test Tenant Invitation
1. As Tenant Admin, create invitation for existing user
2. Existing user receives email
3. User logs in and accepts invitation
4. User can now switch between tenants

#### Test Demo Request (Existing User)
1. User with existing account requests demo
2. Demo tenant created immediately
3. User receives invitation email
4. User logs in and accepts
5. User gains access to demo tenant

### 10. Backward Compatibility

The implementation maintains backward compatibility:
- Old `tenant_id` and `role` columns still populated
- Existing code using these columns will continue to work
- Gradual migration path to new system

### 11. Security Considerations

- Tenant context is cryptographically signed in JWT
- Users can only switch to tenants they have access to
- Invitation tokens expire after 7 days
- Re-authentication required for tenant selection
- Platform Admins maintain access to all tenants

### 12. Known Limitations

1. Users cannot have multiple roles in the same tenant (enforced by unique constraint)
2. Tenant switching requires new JWT token (current token becomes invalid)
3. Some legacy code may still reference `user.tenant_id` directly

### 13. Future Enhancements

1. Remove deprecated `tenant_id` and `role` columns from users table
2. Add ability to set default tenant per user
3. Add tenant-specific user preferences
4. Implement tenant usage analytics
5. Add bulk user invitation system

## API Documentation Updates

All endpoints now respect tenant context from JWT token. Role checks are performed against the user's role in the current tenant context.

### Migration Commands

```bash
# Run migrations
cd backend
alembic upgrade head

# Rollback if needed
alembic downgrade -1

# Check current version
alembic current
```

## Support

For issues or questions about the multi-tenant implementation:
1. Check migration logs for any errors
2. Verify user_tenant_roles table has correct associations
3. Ensure JWT tokens include tenant_id claim
4. Check frontend localStorage for proper token storage
