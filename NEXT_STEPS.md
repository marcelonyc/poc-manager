# Next Steps - Completing the Multi-Tenant Implementation

## Prerequisites Completed ✓

- [x] Database models created
- [x] Migrations written  
- [x] Authentication logic updated
- [x] API endpoints implemented
- [x] Backend routers registered
- [x] Frontend components created
- [x] Documentation written

## Steps to Complete Implementation

### 1. Backend Setup & Testing

#### Step 1.1: Activate Virtual Environment (if using one)
```bash
cd /home/marcelo/poc-manager/backend

# If venv exists
source venv/bin/activate

# If using system Python
# Continue without activation
```

#### Step 1.2: Install/Update Dependencies
```bash
pip install -r requirements.txt
```

#### Step 1.3: Run Migrations
```bash
# Check current state
alembic current

# Run migrations
alembic upgrade head

# Verify
alembic current
# Should show: 20260206_0001 (head)
```

#### Step 1.4: Verify Database Structure
```bash
# Connect to database and check tables
psql -U <db_user> -d <db_name>

# Check tables
\dt

# Should see:
# - user_tenant_roles
# - tenant_invitations

# Check data migration
SELECT COUNT(*) FROM user_tenant_roles;
# Should match number of active users
```

#### Step 1.5: Start Backend Server
```bash
cd /home/marcelo/poc-manager/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 1.6: Test API Endpoints
```bash
# Test health check
curl http://localhost:8000/health

# Test docs
open http://localhost:8000/docs
```

### 2. Frontend Setup

#### Step 2.1: Install Dependencies
```bash
cd /home/marcelo/poc-manager/frontend
npm install
```

#### Step 2.2: Update Login Component
Edit `frontend/src/pages/Login.tsx` to handle multi-tenant response:

```typescript
// After successful login API call
const loginResponse = await axios.post('/api/auth/login', {
  email,
  password
});

// Check if tenant selection required
if (loginResponse.data.requires_selection && loginResponse.data.tenants.length > 1) {
  // Navigate to tenant selection page
  navigate('/select-tenant', {
    state: {
      email,
      password,
      tenants: loginResponse.data.tenants,
      userId: loginResponse.data.user_id
    }
  });
} else {
  // Auto-select single tenant
  const response = await axios.post('/api/auth/select-tenant', {
    tenant_id: loginResponse.data.tenants[0].tenant_id
  }, {
    auth: { username: email, password }
  });
  
  // Store token and navigate
  localStorage.setItem('token', response.data.access_token);
  localStorage.setItem('user', JSON.stringify(response.data));
  navigate('/dashboard');
}
```

#### Step 2.3: Add Route for Tenant Selection
Edit `frontend/src/App.tsx` (or routes file):

```typescript
import TenantSelection from './pages/TenantSelection';

// Add route
<Route path="/select-tenant" element={<TenantSelection />} />
```

#### Step 2.4: Add TenantSwitcher to Layout
Edit `frontend/src/components/Layout.tsx`:

```typescript
import TenantSwitcher from './TenantSwitcher';
import { useState, useEffect } from 'react';
import axios from 'axios';

export default function Layout({ children }) {
  const [userInfo, setUserInfo] = useState(null);
  const token = localStorage.getItem('token');
  
  useEffect(() => {
    if (token) {
      // Fetch current user info with all tenants
      axios.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      }).then(response => {
        setUserInfo(response.data);
      });
    }
  }, [token]);
  
  const handleTenantSwitch = async (tenantId) => {
    const response = await axios.post('/api/auth/switch-tenant',
      { tenant_id: tenantId },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    
    // Update stored token
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data));
    
    // Reload to refresh with new context
    window.location.reload();
  };
  
  return (
    <div>
      <nav className="...">
        {/* Other nav items */}
        
        {userInfo && (
          <TenantSwitcher
            currentTenantId={userInfo.current_tenant_id}
            currentTenantName={userInfo.tenants?.find(
              t => t.tenant_id === userInfo.current_tenant_id
            )?.tenant_name}
            currentRole={userInfo.current_role}
            tenants={userInfo.tenants || []}
            onTenantSwitch={handleTenantSwitch}
          />
        )}
      </nav>
      
      <main>{children}</main>
    </div>
  );
}
```

#### Step 2.5: Start Frontend Development Server
```bash
cd /home/marcelo/poc-manager/frontend
npm run dev
```

### 3. Testing Scenarios

#### Test 3.1: Single Tenant User Login
1. Create/use user with single tenant
2. Login via frontend
3. Should auto-select tenant and go to dashboard
4. Verify TenantSwitcher shows single tenant (non-interactive)

#### Test 3.2: Multi-Tenant User Login
1. Create user with multiple tenant associations:
```sql
-- Example: Add second tenant to existing user
INSERT INTO user_tenant_roles (user_id, tenant_id, role, is_default)
VALUES (1, 2, 'SALES_ENGINEER', false);
```
2. Login via frontend
3. Should show tenant selection page
4. Select tenant
5. Should receive token and go to dashboard
6. Verify TenantSwitcher shows both tenants

#### Test 3.3: Tenant Switching
1. Login as multi-tenant user
2. Access dashboard
3. Click TenantSwitcher dropdown
4. Select different tenant
5. Verify page refreshes with new tenant context
6. Verify data shown is for new tenant

#### Test 3.4: Tenant Invitation Flow
1. As Tenant Admin, create invitation:
```bash
curl -X POST http://localhost:8000/api/tenant-invitations/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "existing.user@example.com",
    "role": "sales_engineer"
  }'
```
2. Check email (or check database for token)
3. Login as invited user
4. Accept invitation via API or frontend
5. Verify user can now switch to invited tenant

#### Test 3.5: Demo Request (Existing User)
1. Logout from frontend
2. Go to demo request page
3. Submit request with existing user's email
4. Verify demo tenant created in database
5. Check email for invitation
6. Login as existing user
7. Accept invitation
8. Verify access to demo tenant

### 4. Database Verification Queries

```sql
-- Check all user-tenant associations
SELECT 
    u.email,
    u.full_name,
    t.name as tenant_name,
    utr.role,
    utr.is_default
FROM users u
JOIN user_tenant_roles utr ON u.id = utr.user_id
LEFT JOIN tenants t ON utr.tenant_id = t.id
ORDER BY u.email, t.name;

-- Check pending invitations
SELECT 
    ti.email,
    t.name as tenant_name,
    ti.role,
    ti.status,
    ti.expires_at > NOW() as is_valid
FROM tenant_invitations ti
JOIN tenants t ON ti.tenant_id = t.id
WHERE ti.status = 'PENDING'
ORDER BY ti.created_at DESC;

-- Check users with multiple tenants
SELECT 
    u.email,
    COUNT(DISTINCT utr.tenant_id) as tenant_count,
    STRING_AGG(DISTINCT t.name, ', ') as tenants
FROM users u
JOIN user_tenant_roles utr ON u.id = utr.user_id
LEFT JOIN tenants t ON utr.tenant_id = t.id
GROUP BY u.id, u.email
HAVING COUNT(DISTINCT utr.tenant_id) > 1;
```

### 5. Optional: Create Test Data

```sql
-- Create second tenant
INSERT INTO tenants (name, slug, is_active)
VALUES ('Test Corp', 'test-corp', true);

-- Get IDs
SELECT id FROM tenants WHERE slug = 'test-corp';  -- Let's say it's 99
SELECT id FROM users WHERE email = 'admin@example.com';  -- Let's say it's 1

-- Add user to second tenant
INSERT INTO user_tenant_roles (user_id, tenant_id, role, is_default)
VALUES (1, 99, 'TENANT_ADMIN', false);

-- Verify
SELECT * FROM user_tenant_roles WHERE user_id = 1;
```

### 6. Common Issues & Solutions

#### Issue: Migrations fail
**Solution:**
```bash
# Check Alembic version
alembic current

# If stuck, check database
psql -U <user> -d <db> -c "SELECT * FROM alembic_version;"

# Reset if needed (CAUTION: Development only)
alembic downgrade base
alembic upgrade head
```

#### Issue: Frontend can't find React
**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Issue: CORS errors
**Solution:**
Check `backend/app/config.py` - ensure frontend URL in CORS origins

#### Issue: JWT token doesn't include tenant_id
**Solution:**
Ensure using `/api/auth/select-tenant` endpoint, not old login flow

### 7. Deployment Checklist

Before deploying to production:

- [ ] Run all migrations on staging first
- [ ] Backup production database
- [ ] Test rollback procedure
- [ ] Update API documentation
- [ ] Update user guides
- [ ] Test with real user data
- [ ] Monitor error logs during rollout
- [ ] Have rollback plan ready

### 8. Monitoring

After deployment, monitor:
- Login success/failure rates
- Tenant switching frequency
- Invitation acceptance rate
- API endpoint latency
- Database query performance

## Support & Resources

- **Detailed Documentation:** `MULTI_TENANT_IMPLEMENTATION.md`
- **Quick Reference:** `QUICK_REFERENCE.md`
- **Implementation Summary:** `IMPLEMENTATION_SUMMARY.md`
- **API Docs:** `http://localhost:8000/docs` (when running)

## Questions?

Common questions answered in documentation:
1. How do I add a user to multiple tenants?
2. How do I create a tenant invitation?
3. How does tenant switching work?
4. What happens to existing users?
5. How do I test the multi-tenant flow?

All answers are in the documentation files created.

---

**You're now ready to complete the implementation!** Follow the steps above in order, and you'll have a fully functional multi-tenant system. Good luck! 🚀
