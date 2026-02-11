# Public Share Links API

## Endpoints

### Create Public Link

Generate a new public share link for a POC. Only one active link per POC is allowed.

```http
POST /pocs/{poc_id}/public-link
Authorization: Bearer {access_token}
```

**Parameters:**
- `poc_id` (integer, path) - ID of the POC to create a link for

**Response (201 Created):**
```json
{
  "id": 1,
  "poc_id": 123,
  "access_token": "rA5k_xY2pQ8jM1nL_Z9vW4bK3tH6cJ0",
  "access_url": "https://domain.com/share/rA5k_xY2pQ8jM1nL_Z9vW4bK3tH6cJ0",
  "created_at": "2026-02-11T20:15:30Z",
  "created_by": 5
}
```

**Errors:**
- `404 Not Found` - POC does not exist or does not belong to user's tenant
- `400 Bad Request` - A public link already exists for this POC
- `401 Unauthorized` - User must be Tenant Admin
- `403 Forbidden` - User does not have access to this POC's tenant

**cURL Example:**
```bash
curl -X POST \
  'https://api.example.com/pocs/123/public-link' \
  -H 'Authorization: Bearer eyJ...' \
  -H 'Content-Type: application/json'
```

---

### Get Public Link

Retrieve the existing public link for a POC.

```http
GET /pocs/{poc_id}/public-link
Authorization: Bearer {access_token}
```

**Parameters:**
- `poc_id` (integer, path) - ID of the POC

**Response (200 OK):**
```json
{
  "id": 1,
  "poc_id": 123,
  "access_token": "rA5k_xY2pQ8jM1nL_Z9vW4bK3tH6cJ0",
  "access_url": "https://domain.com/share/rA5k_xY2pQ8jM1nL_Z9vW4bK3tH6cJ0",
  "created_at": "2026-02-11T20:15:30Z",
  "created_by": 5
}
```

**Errors:**
- `404 Not Found` - POC not found OR no public link exists for this POC
- `401 Unauthorized` - User must be Tenant Admin
- `403 Forbidden` - User does not have access to this POC's tenant

**cURL Example:**
```bash
curl -X GET \
  'https://api.example.com/pocs/123/public-link' \
  -H 'Authorization: Bearer eyJ...'
```

---

### Delete Public Link

Revoke access to a public link. This immediately prevents further access using the token.

```http
DELETE /pocs/{poc_id}/public-link
Authorization: Bearer {access_token}
```

**Parameters:**
- `poc_id` (integer, path) - ID of the POC

**Response (204 No Content):**
No body returned on success.

**Errors:**
- `404 Not Found` - POC not found OR no public link exists for this POC
- `401 Unauthorized` - User must be Tenant Admin
- `403 Forbidden` - User does not have access to this POC's tenant

**cURL Example:**
```bash
curl -X DELETE \
  'https://api.example.com/pocs/123/public-link' \
  -H 'Authorization: Bearer eyJ...'
```

---

## Public POC Access (No Authentication)

### Get Public POC Details

Access a POC via public share link without authentication.

```http
GET /public/pocs/{access_token}
```

**Parameters:**
- `access_token` (string, path) - The public access token from the share link

**Response (200 OK):**
```json
{
  "id": 123,
  "title": "Acme Corp POC",
  "description": "Proof of concept for Acme",
  "tenant_id": 1,
  "created_by": 5,
  "customer_company_name": "Acme Corporation",
  "customer_logo_url": "/uploads/logos/acme.png",
  "executive_summary": "Summary text",
  "objectives": "Key objectives",
  "start_date": "2026-01-15",
  "end_date": "2026-03-15",
  "status": "active",
  "overall_success_score": 85,
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-02-11T20:00:00Z",
  "success_criteria": [
    {
      "id": 1,
      "title": "Feature A works",
      "description": "User can use Feature A",
      "importance_level": 5,
      "is_met": true,
      "achieved_value": "Yes",
      "target_value": "Yes"
    }
  ],
  "participants": [
    {
      "id": 1,
      "poc_id": 123,
      "user_id": 5,
      "is_sales_engineer": true,
      "is_customer": false
    }
  ]
}
```

**Errors:**
- `404 Not Found` - Invalid, expired, or deleted public link

**cURL Example:**
```bash
curl -X GET \
  'https://api.example.com/public/pocs/rA5k_xY2pQ8jM1nL_Z9vW4bK3tH6cJ0'
```

---

### Get Public POC Tasks

Retrieve all standalone tasks for a public POC.

```http
GET /public/pocs/{access_token}/tasks
```

**Parameters:**
- `access_token` (string, path) - The public access token

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "poc_id": 123,
    "title": "Setup environment",
    "description": "Configure dev environment",
    "status": "completed",
    "order": 1,
    "success_criteria_ids": [1, 2],
    "assignees": [
      {
        "id": 1,
        "participant_id": 1,
        "participant_email": "john@acme.com",
        "participant_name": "John Smith"
      }
    ]
  }
]
```

**Errors:**
- `404 Not Found` - Invalid or expired public link

**cURL Example:**
```bash
curl -X GET \
  'https://api.example.com/public/pocs/rA5k_xY2pQ8jM1nL_Z9vW4bK3tH6cJ0/tasks'
```

---

### Get Public POC Task Groups

Retrieve all task groups with child tasks for a public POC.

```http
GET /public/pocs/{access_token}/task-groups
```

**Parameters:**
- `access_token` (string, path) - The public access token

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "poc_id": 123,
    "title": "Phase 1: Setup",
    "description": "Initial setup phase",
    "status": "in_progress",
    "order": 1,
    "success_criteria_ids": [1],
    "tasks": [
      {
        "id": 1,
        "poc_id": 123,
        "title": "Configure system",
        "description": "Set up config",
        "status": "completed",
        "order": 1,
        "success_criteria_ids": [1],
        "assignees": []
      }
    ]
  }
]
```

**Errors:**
- `404 Not Found` - Invalid or expired public link

**cURL Example:**
```bash
curl -X GET \
  'https://api.example.com/public/pocs/rA5k_xY2pQ8jM1nL_Z9vW4bK3tH6cJ0/task-groups'
```

---

## Authentication & Authorization

### Protected Endpoints (Create, Get, Delete)
- **Required Role:** Tenant Admin
- **Authorization Header:** `Authorization: Bearer {jwt_token}`
- **Returns 401:** If token is missing or invalid
- **Returns 403:** If user is not a Tenant Admin or lacks access to POC's tenant

### Public Endpoints (Get Details, Tasks, Groups)
- **Required Role:** None (unauthenticated)
- **Authorization Header:** Not required
- **Token Validation:** Only the `access_token` URL parameter is validated
- **Returns 404:** If token is invalid, expired, or has been deleted

---

## Implementation Notes

### Token Generation
- Tokens are generated using `secrets.token_urlsafe(32)`
- Results in ~43 character, URL-safe, cryptographically random strings
- Example: `rA5k_xY2pQ8jM1nL_Z9vW4bK3tH6cJ0`

### One Link Per POC
- Each POC can have only ONE active public link
- Attempting to create a second link returns 400 Bad Request
- Deleting and recreating generates a NEW token
- Old tokens cannot be reactivated

### Soft Deletes
- Deleted links are marked with `is_deleted = true` and `deleted_at` timestamp
- Database maintains audit trail
- Prevents token reuse and maintains history

### Rate Limiting
- Public endpoints are NOT rate-limited
- No usage tracking or analytics available
- Each request is independent

### CORS & Security
- Public endpoints allow CORS requests
- No special headers required
- Suitable for public, unauthenticated access

---

## Integration Examples

### Node.js / JavaScript
```javascript
// Create public link
async function createPublicLink(pocId) {
  const response = await fetch(`/pocs/${pocId}/public-link`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
  return response.json()
}

// Access public POC
async function getPublicPOC(accessToken) {
  const response = await fetch(`/public/pocs/${accessToken}`)
  return response.json()
}
```

### Python
```python
import requests

# Create public link
def create_public_link(poc_id, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = requests.post(
        f'https://api.example.com/pocs/{poc_id}/public-link',
        headers=headers
    )
    return response.json()

# Access public POC
def get_public_poc(access_token):
    response = requests.get(
        f'https://api.example.com/public/pocs/{access_token}'
    )
    return response.json()
```

### cURL (Bash)
```bash
# Create public link
curl -X POST \
  'https://api.example.com/pocs/123/public-link' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'

# Access public POC
curl -X GET \
  'https://api.example.com/public/pocs/rA5k_xY2pQ8jM1nL_Z9vW4bK3tH6cJ0'
```

---

## Database Schema

### poc_public_links Table
```sql
CREATE TABLE poc_public_links (
  id INTEGER PRIMARY KEY,
  poc_id INTEGER NOT NULL,
  tenant_id INTEGER NOT NULL,
  created_by INTEGER NOT NULL,
  access_token VARCHAR UNIQUE NOT NULL,
  is_deleted BOOLEAN DEFAULT false,
  deleted_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (poc_id) REFERENCES pocs(id) ON DELETE CASCADE,
  FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_poc_public_links_access_token ON poc_public_links(access_token);
```

---

## See Also

- [Features: Public Share Links](../features/public-share-links.md)
- [Tenant Admin: Managing Public Links](../tenant-admin/public-share-links.md)
- [Customer: Accessing Public POCs](../customer/accessing-public-pocs.md)
- [API Documentation](./API.md)
