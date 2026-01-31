# POC Manager - Workspace Instructions

## Project Overview
Full-stack multi-tenant POC (Proof of Concept) management application.

**Tech Stack:**
- Backend: Python FastAPI with SQLAlchemy + Alembic
- Database: PostgreSQL
- Frontend: React with TypeScript
- Authentication: JWT-based with role-based access control

## User Roles
- **Platform Admin**: Manages tenants and platform configuration
- **Tenant Admin**: Manages tenant settings, branding, and integrations
- **Administrator**: Defines reusable tasks, task groups, and manages POCs
- **Sales Engineer**: Creates POCs, invites customers, manages POC execution
- **Customer**: Participates in POCs, provides feedback and completion status

## Key Features
- Multi-tenant architecture
- Role-based access control (RBAC)
- POC lifecycle management
- Task and task group templates
- Success criteria tracking
- Internal/external comments system
- Resource management with links to success criteria
- Integrations: Slack, Jira, GitHub, Email
- Document generation: PDF, Word, Markdown
- Email notifications
- Custom branding per tenant

## Development Guidelines
- Use SQLAlchemy for database models
- Use Alembic for schema migrations
- Implement comprehensive pytest test suite
- Follow REST API best practices
- Use pre-commit hooks for code quality
- Maintain clear separation between tenant data
