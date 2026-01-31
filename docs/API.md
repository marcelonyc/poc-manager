# API Endpoints Reference

## Base URL
- Development: `http://localhost:8000`
- Production: `https://api.pocmanager.com`

## Authentication

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer {token}
```

### Change Password
```http
POST /auth/change-password
Authorization: Bearer {token}
Content-Type: application/json

{
  "old_password": "oldpass123",
  "new_password": "newpass123"
}
```

## Tenants

### Create Tenant (Platform Admin)
```http
POST /tenants/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Acme Corp",
  "slug": "acme-corp",
  "initial_admin_email": "admin@acme.com",
  "initial_admin_name": "Admin User",
  "initial_admin_password": "admin123"
}
```

### List Tenants
```http
GET /tenants/?skip=0&limit=100
Authorization: Bearer {token}
```

### Get Tenant
```http
GET /tenants/{tenant_id}
Authorization: Bearer {token}
```

### Update Tenant
```http
PUT /tenants/{tenant_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Updated Name",
  "primary_color": "#ff0000"
}
```

## POCs

### Create POC
```http
POST /pocs/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Enterprise Platform POC",
  "description": "Testing enterprise features",
  "customer_company_name": "Customer Inc",
  "start_date": "2024-01-01",
  "end_date": "2024-03-01"
}
```

### List POCs
```http
GET /pocs/?skip=0&limit=100&status=active
Authorization: Bearer {token}
```

### Get POC Details
```http
GET /pocs/{poc_id}
Authorization: Bearer {token}
```

### Update POC
```http
PUT /pocs/{poc_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Updated Title",
  "status": "active",
  "overall_success_score": 85
}
```

### Add Participant to POC
```http
POST /pocs/{poc_id}/participants
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_id": 123,
  "is_sales_engineer": true,
  "is_customer": false
}
```

## Tasks

### Create Task Template
```http
POST /tasks/templates
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Setup Environment",
  "description": "Configure development environment"
}
```

### List Task Templates
```http
GET /tasks/templates?skip=0&limit=100
Authorization: Bearer {token}
```

### Add Task to POC
```http
POST /tasks/pocs/{poc_id}/tasks
Authorization: Bearer {token}
Content-Type: application/json

{
  "task_id": 5,
  "title": "Setup Environment",
  "description": "Configure development environment",
  "sort_order": 1,
  "success_criteria_ids": [1, 2]
}
```

### Update POC Task
```http
PUT /tasks/pocs/{poc_id}/tasks/{task_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "completed",
  "success_level": 95
}
```

## Success Criteria

### Create Success Criteria
```http
POST /pocs/{poc_id}/success-criteria
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Performance Requirements",
  "description": "System must handle 1000 requests/sec",
  "target_value": "1000 req/sec",
  "sort_order": 1
}
```

### Update Success Criteria
```http
PUT /pocs/{poc_id}/success-criteria/{criteria_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "achieved_value": "1200 req/sec",
  "is_met": true
}
```

## Comments

### Create Comment
```http
POST /pocs/{poc_id}/comments
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": "Great progress on this task!",
  "is_internal": false,
  "poc_task_id": 10
}
```

### List Comments
```http
GET /pocs/{poc_id}/comments?task_id=10
Authorization: Bearer {token}
```

## Resources

### Create Resource
```http
POST /pocs/{poc_id}/resources
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Sample Code",
  "description": "Example implementation",
  "resource_type": "code",
  "content": "def hello_world():\n    print('Hello!')",
  "success_criteria_id": 1
}
```

### List Resources
```http
GET /pocs/{poc_id}/resources
Authorization: Bearer {token}
```

## Users

### Create User
```http
POST /users/
Authorization: Bearer {token}
Content-Type: application/json

{
  "email": "newuser@example.com",
  "full_name": "New User",
  "password": "secure123",
  "role": "sales_engineer"
}
```

### Invite User
```http
POST /users/invite
Authorization: Bearer {token}
Content-Type: application/json

{
  "email": "invite@example.com",
  "full_name": "Invited User",
  "role": "customer"
}
```

### List Users
```http
GET /users/?skip=0&limit=100
Authorization: Bearer {token}
```

---

For interactive API documentation, visit: http://localhost:8000/docs
