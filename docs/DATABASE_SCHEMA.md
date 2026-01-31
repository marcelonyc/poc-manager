# Database Schema Documentation

## Entity Relationship Overview

### Core Entities

#### Tenants
Multi-tenant isolation with custom configuration.

```sql
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    slug VARCHAR NOT NULL UNIQUE,
    logo_url VARCHAR,
    primary_color VARCHAR DEFAULT '#0066cc',
    secondary_color VARCHAR DEFAULT '#333333',
    contact_email VARCHAR,
    contact_phone VARCHAR,
    
    -- Custom email config (optional)
    custom_mail_server VARCHAR,
    custom_mail_port INTEGER,
    custom_mail_username VARCHAR,
    custom_mail_password VARCHAR,
    custom_mail_from VARCHAR,
    custom_mail_tls BOOLEAN DEFAULT TRUE,
    
    -- User limits
    tenant_admin_limit INTEGER DEFAULT 5,
    administrator_limit INTEGER DEFAULT 10,
    sales_engineer_limit INTEGER DEFAULT 50,
    customer_limit INTEGER DEFAULT 500,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

#### Users
Authentication and authorization with role-based access.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR NOT NULL,
    role VARCHAR NOT NULL CHECK (role IN (
        'platform_admin',
        'tenant_admin',
        'administrator',
        'sales_engineer',
        'customer'
    )),
    is_active BOOLEAN DEFAULT TRUE,
    tenant_id INTEGER REFERENCES tenants(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    last_login TIMESTAMP
);
```

#### POCs
Proof of Concept lifecycle management.

```sql
CREATE TABLE pocs (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    created_by INTEGER NOT NULL REFERENCES users(id),
    
    -- Customer info
    customer_company_name VARCHAR NOT NULL,
    customer_logo_url VARCHAR,
    
    -- Timeline
    start_date DATE,
    end_date DATE,
    
    status VARCHAR DEFAULT 'draft' CHECK (status IN (
        'draft', 'active', 'completed', 'archived'
    )),
    
    -- Success tracking
    overall_success_score INTEGER CHECK (
        overall_success_score >= 0 AND overall_success_score <= 100
    ),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

#### POC Participants
Links users to POCs they're participating in.

```sql
CREATE TABLE poc_participants (
    id SERIAL PRIMARY KEY,
    poc_id INTEGER NOT NULL REFERENCES pocs(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    is_sales_engineer BOOLEAN DEFAULT FALSE,
    is_customer BOOLEAN DEFAULT FALSE,
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(poc_id, user_id)
);
```

### Task Management

#### Task Templates
Reusable task definitions.

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    created_by INTEGER NOT NULL REFERENCES users(id),
    is_template BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

#### Task Group Templates
Reusable task group definitions.

```sql
CREATE TABLE task_groups (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    created_by INTEGER NOT NULL REFERENCES users(id),
    is_template BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

#### POC Tasks
Task instances within a specific POC.

```sql
CREATE TABLE poc_tasks (
    id SERIAL PRIMARY KEY,
    poc_id INTEGER NOT NULL REFERENCES pocs(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES tasks(id),
    
    -- Can be customized per POC
    title VARCHAR NOT NULL,
    description TEXT,
    
    status VARCHAR DEFAULT 'not_started' CHECK (status IN (
        'not_started', 'in_progress', 'completed', 'blocked'
    )),
    success_level INTEGER CHECK (
        success_level >= 0 AND success_level <= 100
    ),
    
    sort_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

#### POC Task Groups
Task group instances within a specific POC.

```sql
CREATE TABLE poc_task_groups (
    id SERIAL PRIMARY KEY,
    poc_id INTEGER NOT NULL REFERENCES pocs(id) ON DELETE CASCADE,
    task_group_id INTEGER REFERENCES task_groups(id),
    
    title VARCHAR NOT NULL,
    description TEXT,
    
    status VARCHAR DEFAULT 'not_started' CHECK (status IN (
        'not_started', 'in_progress', 'completed', 'blocked'
    )),
    success_level INTEGER CHECK (
        success_level >= 0 AND success_level <= 100
    ),
    
    sort_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### Success Tracking

#### Success Criteria
Measurable success metrics for a POC.

```sql
CREATE TABLE success_criteria (
    id SERIAL PRIMARY KEY,
    poc_id INTEGER NOT NULL REFERENCES pocs(id) ON DELETE CASCADE,
    
    title VARCHAR NOT NULL,
    description TEXT,
    
    -- Measurement
    target_value VARCHAR,
    achieved_value VARCHAR,
    is_met BOOLEAN DEFAULT FALSE,
    
    sort_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

#### Task-Success Criteria Links
Links tasks/task groups to success criteria (many-to-many).

```sql
CREATE TABLE task_success_criteria (
    id SERIAL PRIMARY KEY,
    success_criteria_id INTEGER NOT NULL REFERENCES success_criteria(id) ON DELETE CASCADE,
    
    -- Either task OR task group, not both
    poc_task_id INTEGER REFERENCES poc_tasks(id) ON DELETE CASCADE,
    poc_task_group_id INTEGER REFERENCES poc_task_groups(id) ON DELETE CASCADE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    CHECK (
        (poc_task_id IS NOT NULL AND poc_task_group_id IS NULL) OR
        (poc_task_id IS NULL AND poc_task_group_id IS NOT NULL)
    )
);
```

### Collaboration

#### Comments
Comments on POCs, tasks, or task groups.

```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    
    user_id INTEGER NOT NULL REFERENCES users(id),
    poc_id INTEGER NOT NULL REFERENCES pocs(id) ON DELETE CASCADE,
    
    -- Optional: comment on specific task or task group
    poc_task_id INTEGER REFERENCES poc_tasks(id) ON DELETE CASCADE,
    poc_task_group_id INTEGER REFERENCES poc_task_groups(id) ON DELETE CASCADE,
    
    -- Internal comments (only visible to sales engineers and admins)
    is_internal BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

#### Resources
Documentation, code snippets, links for a POC.

```sql
CREATE TABLE resources (
    id SERIAL PRIMARY KEY,
    poc_id INTEGER NOT NULL REFERENCES pocs(id) ON DELETE CASCADE,
    
    title VARCHAR NOT NULL,
    description TEXT,
    
    resource_type VARCHAR NOT NULL CHECK (resource_type IN (
        'link', 'code', 'text', 'file'
    )),
    
    content TEXT NOT NULL,
    
    -- Optional link to success criteria
    success_criteria_id INTEGER REFERENCES success_criteria(id),
    
    sort_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### Integrations

#### Tenant Integrations
Integration configurations per tenant.

```sql
CREATE TABLE tenant_integrations (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    integration_type VARCHAR NOT NULL CHECK (integration_type IN (
        'slack', 'jira', 'github', 'email'
    )),
    
    is_enabled BOOLEAN DEFAULT TRUE,
    
    -- JSON configuration data
    config_data TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    
    UNIQUE(tenant_id, integration_type)
);
```

## Indexes

```sql
-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_role ON users(role);

-- POCs
CREATE INDEX idx_pocs_tenant ON pocs(tenant_id);
CREATE INDEX idx_pocs_status ON pocs(status);
CREATE INDEX idx_pocs_created_by ON pocs(created_by);

-- POC Participants
CREATE INDEX idx_poc_participants_poc ON poc_participants(poc_id);
CREATE INDEX idx_poc_participants_user ON poc_participants(user_id);

-- Tasks
CREATE INDEX idx_tasks_tenant ON tasks(tenant_id);
CREATE INDEX idx_poc_tasks_poc ON poc_tasks(poc_id);
CREATE INDEX idx_poc_tasks_status ON poc_tasks(status);

-- Success Criteria
CREATE INDEX idx_success_criteria_poc ON success_criteria(poc_id);
CREATE INDEX idx_task_success_criteria_criteria ON task_success_criteria(success_criteria_id);

-- Comments
CREATE INDEX idx_comments_poc ON comments(poc_id);
CREATE INDEX idx_comments_user ON comments(user_id);
CREATE INDEX idx_comments_task ON comments(poc_task_id);

-- Resources
CREATE INDEX idx_resources_poc ON resources(poc_id);
CREATE INDEX idx_resources_criteria ON resources(success_criteria_id);
```

## Relationships

### One-to-Many
- Tenant → Users (one tenant has many users)
- Tenant → POCs (one tenant has many POCs)
- POC → POC Tasks (one POC has many tasks)
- POC → Success Criteria (one POC has many criteria)
- POC → Comments (one POC has many comments)
- POC → Resources (one POC has many resources)
- User → Comments (one user creates many comments)

### Many-to-Many
- POCs ↔ Users (via poc_participants)
- Success Criteria ↔ POC Tasks (via task_success_criteria)
- Success Criteria ↔ POC Task Groups (via task_success_criteria)

### Optional References
- POC Task → Task Template (can be created from template)
- POC Task Group → Task Group Template (can be created from template)
- Resource → Success Criteria (can be linked to criteria)

## Data Flow Example

1. **Platform Admin** creates **Tenant**
2. **Tenant** gets a **Tenant Admin** user
3. **Tenant Admin** invites **Administrators** and **Sales Engineers**
4. **Administrator** creates **Task Templates** and **Task Group Templates**
5. **Sales Engineer** creates a **POC**
6. **Sales Engineer** adds **Success Criteria** to POC
7. **Sales Engineer** adds **POC Tasks** (from templates or custom)
8. **Sales Engineer** links **Tasks to Success Criteria**
9. **Sales Engineer** invites **Customer** users as **POC Participants**
10. **Sales Engineer** and **Customer** add **Comments**
11. **Sales Engineer** adds **Resources**
12. **Customer** updates **Task Status** and **Success Levels**
13. **Sales Engineer** updates **Success Criteria** achieved values
14. **Sales Engineer** generates POC **Document** (PDF/Word/Markdown)

## Cascade Delete Behavior

- Delete POC → Deletes all POC Tasks, Task Groups, Success Criteria, Comments, Resources
- Delete User → Comments remain (orphaned) - consider soft delete for users
- Delete Tenant → All related data should be carefully handled
- Delete Task Template → POC Tasks remain (they're copies)
- Delete Success Criteria → Task-Criteria links are deleted

## Constraints

- Email addresses must be unique across all users
- Tenant slugs must be unique
- POC participant must be unique per POC
- Success levels must be 0-100
- Task-Success Criteria must reference either task OR task group, not both
