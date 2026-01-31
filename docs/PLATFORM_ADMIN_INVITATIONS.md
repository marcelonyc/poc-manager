# Platform Admin Invitation System

## Overview
A complete invitation system that allows Platform Admins to invite additional Platform Admins to the POC Manager platform.

## Features

### Backend Implementation

#### Database Model
- **Invitation Table** ([backend/app/models/invitation.py](backend/app/models/invitation.py))
  - Stores invitation details: email, full name, token, status
  - Tracks invited_by_email, created_at, expires_at, accepted_at
  - Statuses: pending, accepted, expired, revoked
  - 7-day expiration period

#### API Endpoints
All endpoints are in [backend/app/routers/invitations.py](backend/app/routers/invitations.py):

1. **POST /invitations/** - Create invitation (Platform Admin only)
   - Validates email doesn't exist
   - Prevents duplicate pending invitations
   - Generates secure token
   - Sends email invitation

2. **GET /invitations/** - List all invitations (Platform Admin only)
   - Optional status filtering
   - Ordered by creation date (newest first)

3. **GET /invitations/validate/{token}** - Validate invitation token (Public)
   - Returns invitation details if valid
   - Checks expiration status
   - Auto-marks as expired if past expiry date

4. **POST /invitations/accept** - Accept invitation and create account (Public)
   - Creates Platform Admin user
   - Marks invitation as accepted
   - Requires password (min 8 characters)

5. **DELETE /invitations/{id}** - Revoke invitation (Platform Admin only)
   - Only pending invitations can be revoked

#### Email Service
- Beautiful HTML email template with invitation link
- Includes inviter name and expiration notice
- Frontend URL configurable via FRONTEND_URL environment variable

#### Security
- Secure token generation using `secrets.token_urlsafe(32)`
- Platform Admin-only access for management endpoints
- Public endpoints for validation and acceptance
- Password hashing with bcrypt

### Frontend Implementation

#### Pages

1. **Platform Admin Invitations Page** ([frontend/src/pages/PlatformAdminInvitations.tsx](frontend/src/pages/PlatformAdminInvitations.tsx))
   - **Access**: Platform Admins only
   - **Route**: `/invitations`
   - **Features**:
     - Send new invitations (email + full name)
     - View all invitations in table format
     - Status badges (pending, accepted, expired, revoked)
     - Revoke pending invitations
     - Timestamps for created, expires, and accepted dates
   - Accessible via "Invitations" link in navigation

2. **Accept Invitation Page** ([frontend/src/pages/AcceptInvitation.tsx](frontend/src/pages/AcceptInvitation.tsx))
   - **Access**: Public (no authentication required)
   - **Route**: `/accept-invitation?token={token}`
   - **Features**:
     - Validates invitation token on load
     - Shows invitation details (email, name, invited by)
     - Password creation form with confirmation
     - Clear error messages for invalid/expired invitations
     - Redirects to login after successful account creation

#### Navigation
- "Invitations" menu item added to navigation bar (Platform Admins only)
- Located in [frontend/src/components/Layout.tsx](frontend/src/components/Layout.tsx)

### Testing

Comprehensive test suite in [backend/tests/test_invitations.py](backend/tests/test_invitations.py):

- ✅ Create invitation as Platform Admin
- ✅ Prevent non-Platform Admins from creating invitations
- ✅ Prevent duplicate pending invitations
- ✅ Prevent invitations for existing users
- ✅ List invitations (Platform Admin only)
- ✅ Validate invitation tokens
- ✅ Handle expired invitations
- ✅ Accept invitations and create accounts
- ✅ Revoke pending invitations
- ✅ Prevent revoking accepted invitations

Run tests with:
```bash
docker compose exec backend pytest tests/test_invitations.py -v
```

### Database Migration

Migration file: [backend/alembic/versions/20260130_1951-1db0f9f4d45c_add_platform_admin_invitations.py](backend/alembic/versions/20260130_1951-1db0f9f4d45c_add_platform_admin_invitations.py)

Applied with:
```bash
docker compose exec backend alembic upgrade head
```

## Configuration

### Environment Variables

Added to [backend/.env](backend/.env):
```env
FRONTEND_URL=http://localhost:3001
```

Also update [backend/app/config.py](backend/app/config.py) for production environments.

## Usage Workflow

1. **Platform Admin sends invitation**:
   - Navigate to `/invitations`
   - Click "Invite Admin"
   - Enter email and full name
   - Click "Send Invitation"

2. **Invitee receives email**:
   - Email contains invitation link with token
   - Link format: `http://localhost:3001/accept-invitation?token=...`
   - Valid for 7 days

3. **Invitee accepts invitation**:
   - Click link in email
   - Review invitation details
   - Set password (min 8 characters)
   - Click "Create Account"
   - Redirected to login page

4. **New Platform Admin logs in**:
   - Use invited email and chosen password
   - Full Platform Admin access granted

5. **Invitation management**:
   - View all invitations in `/invitations` page
   - Revoke pending invitations if needed
   - Track invitation status (pending/accepted/expired/revoked)

## Security Considerations

- ✅ Role-based access control (RBAC) enforced
- ✅ Secure token generation
- ✅ Password requirements enforced
- ✅ Expiration handling
- ✅ Duplicate prevention
- ✅ Platform Admin accounts don't belong to any tenant
- ✅ Public endpoints only expose minimal information

## API Examples

### Create Invitation
```bash
curl -X POST http://localhost:8000/invitations/ \
  -H "Authorization: Bearer {platform_admin_token}" \
  -H "Content-Type: application/json" \
  -d '{"email": "newadmin@example.com", "full_name": "New Admin"}'
```

### List Invitations
```bash
curl http://localhost:8000/invitations/ \
  -H "Authorization: Bearer {platform_admin_token}"
```

### Validate Token
```bash
curl http://localhost:8000/invitations/validate/{token}
```

### Accept Invitation
```bash
curl -X POST http://localhost:8000/invitations/accept \
  -H "Content-Type: application/json" \
  -d '{"token": "{invitation_token}", "password": "securepassword123"}'
```

### Revoke Invitation
```bash
curl -X DELETE http://localhost:8000/invitations/{invitation_id} \
  -H "Authorization: Bearer {platform_admin_token}"
```

## Files Created/Modified

### New Files
- `backend/app/models/invitation.py`
- `backend/app/schemas/invitation.py`
- `backend/app/routers/invitations.py`
- `backend/tests/test_invitations.py`
- `backend/alembic/versions/20260130_1951-1db0f9f4d45c_add_platform_admin_invitations.py`
- `frontend/src/pages/PlatformAdminInvitations.tsx`
- `frontend/src/pages/AcceptInvitation.tsx`

### Modified Files
- `backend/app/models/__init__.py` - Added Invitation model import
- `backend/app/main.py` - Registered invitations router
- `backend/app/config.py` - Added FRONTEND_URL setting
- `backend/app/services/email.py` - Added send_invitation_email function
- `backend/.env` - Added FRONTEND_URL configuration
- `backend/tests/conftest.py` - Added tenant_admin_token fixture
- `frontend/src/App.tsx` - Added invitation routes
- `frontend/src/components/Layout.tsx` - Added Invitations navigation link

## Future Enhancements

Potential improvements:
- Resend invitation emails
- Bulk invitation import
- Customizable invitation message
- Invitation templates
- Audit log for invitation activities
- Notification when invitations are accepted
- Configurable expiration periods
