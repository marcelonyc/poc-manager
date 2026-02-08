# POC Manager

A comprehensive multi-tenant web application for managing Proof of Concept (POC) engagements.

[Try it! Get immediate access to a fully working environment](https://pocmanager.marcelonyc.com/app/demo/request)

## 🚀 Features

### Multi-Tenant Architecture
- Isolated tenant data with custom branding
- Tenant-specific email configuration
- Configurable user limits per tenant

### User Roles & Permissions
- **Platform Admin**: Manages tenants and platform configuration
- **Tenant Admin**: Manages tenant settings, branding, and integrations
- **Administrator**: Defines reusable tasks, task groups, and manages POCs
- **Sales Engineer**: Creates POCs, invites customers, manages execution
- **Customer**: Participates in POCs, provides feedback

### POC Management
- Complete POC lifecycle management (Draft → Active → Completed → Archived)
- Success criteria tracking with target and achieved values
- Drag-and-drop task and task group assignment
- Customer logo upload and branding
- Team collaboration with role-based access

### Task Management
- Reusable task and task group templates
- Customizable tasks per POC
- Status tracking (Not Started, In Progress, Completed, Blocked)
- Success level scoring (0-100)
- Link tasks to multiple success criteria

### Collaboration Features
- Comments system with internal/external visibility
- Real-time notifications via email
- File attachments and resources
- Code snippets and formatted text
- Resource linking to success criteria

### Integrations
- **Slack**: Post POC updates and notifications to channels
- **Jira**: Create tickets from POC tasks
- **GitHub**: Read Gists, create pull requests
- **Email**: Custom SMTP configuration per tenant

### Document Generation
- Export POCs to PDF, Word, and Markdown formats
- Include all POC details, tasks, resources, and status
- Custom branding in generated documents

### Dashboards & Reporting
- POC status overview
- Success metrics and scoring
- Filter by company, date, status
- Team performance tracking

## 🛠 Tech Stack

### Backend
- **Python 3.11+** with **FastAPI**
- **PostgreSQL** database
- **SQLAlchemy** ORM
- **Alembic** for migrations
- **JWT** authentication
- **Pytest** for testing

### Frontend
- **React 18** with **TypeScript**
- **Vite** for build tooling
- **TailwindCSS** for styling
- **React Router** for navigation
- **Zustand** for state management
- **React Query** for data fetching

### DevOps
- **Docker** & **Docker Compose**
- **Pre-commit hooks** for code quality
- **GitHub Actions** ready

## 📋 Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd poc-manager

# Copy environment files
cp .env.example .env
cp .env-vite.example .env-vite

# Edit .env with your configuration (database, email, etc.)
# Edit .env-vite with your frontend configuration (optional)

# Start all services
docker compose up -d

# Run database migrations
docker compose exec backend alembic upgrade head

# Create platform admin (optional)
docker compose exec backend python -c "
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.auth import get_password_hash

db = SessionLocal()
admin = User(
    email='admin@platform.com',
    full_name='Platform Admin',
    hashed_password=get_password_hash('admin123'),
    role=UserRole.PLATFORM_ADMIN,
    is_active=True
)
db.add(admin)
db.commit()
print('Platform admin created: admin@platform.com / admin123')
"
```

Access the application:
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your configuration

# (Optional) Copy frontend-specific environment
cp .env-vite.example .env-vite
# Edit .env-vite if you need custom Vite configuration

# Create database
createdb poc_manager

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🗄 Database Setup

### Create Database

```sql
CREATE DATABASE poc_manager;
CREATE DATABASE poc_manager_test;  -- For testing
```

### Run Migrations

```bash
cd backend
alembic upgrade head
```

### Create Initial Platform Admin

```python
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.auth import get_password_hash

db = SessionLocal()
admin = User(
    email='admin@example.com',
    full_name='Platform Admin',
    hashed_password=get_password_hash('secure_password'),
    role=UserRole.PLATFORM_ADMIN,
    is_active=True
)
db.add(admin)
db.commit()
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

### Frontend Tests

```bash
cd frontend

# Run tests (when implemented)
npm test
```

## 🔧 Development

### Pre-commit Hooks

```bash
cd backend

# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Code Quality

```bash
# Format code
black app tests

# Lint
flake8 app tests

# Type checking
mypy app
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints

#### Authentication
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user
- `POST /auth/change-password` - Change password

#### Tenants
- `POST /tenants/` - Create tenant (Platform Admin)
- `GET /tenants/` - List tenants
- `PUT /tenants/{id}` - Update tenant
- `PUT /tenants/{id}/email-config` - Configure email

#### POCs
- `POST /pocs/` - Create POC
- `GET /pocs/` - List POCs
- `GET /pocs/{id}` - Get POC details
- `PUT /pocs/{id}` - Update POC
- `POST /pocs/{id}/participants` - Add participant

#### Tasks
- `POST /tasks/templates` - Create task template
- `GET /tasks/templates` - List templates
- `POST /tasks/pocs/{poc_id}/tasks` - Add task to POC
- `PUT /tasks/pocs/{poc_id}/tasks/{task_id}` - Update task

## 🔐 Security

- JWT-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- SQL injection protection via SQLAlchemy
- CORS configuration
- Environment-based secrets

## 🌐 Environment Variables

### Environment Configuration (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/poc_manager

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-password
MAIL_FROM=noreply@example.com

# Application
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=http://localhost:3001

# Platform Limits
DEFAULT_TENANT_ADMIN_LIMIT=5
DEFAULT_ADMINISTRATOR_LIMIT=10
DEFAULT_SALES_ENGINEER_LIMIT=50
DEFAULT_CUSTOMER_LIMIT=500
```

### Frontend (.env-vite)

```env
# Additional allowed hosts for the development server
__VITE_ADDITIONAL_SERVER_ALLOWED_HOSTS=localhost

# Backend API URL (used by Vite proxy)
VITE_API_URL=/api
```

**Note**: The `.env` file is also used by the frontend for backward compatibility. Vite-specific variables should be placed in `.env-vite`.

## 📦 Project Structure

```
poc-manager/
├── backend/
│   ├── alembic/              # Database migrations
│   ├── app/
│   │   ├── models/           # SQLAlchemy models
│   │   ├── routers/          # API endpoints
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic & integrations
│   │   ├── auth.py           # Authentication utilities
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database setup
│   │   └── main.py           # FastAPI application
│   ├── tests/                # Test suite
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── lib/              # Utilities
│   │   ├── store/            # State management
│   │   └── main.tsx          # Entry point
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Deployment

### Docker Production Build

```bash
# Build images
docker compose -f docker-compose.prod.yml build

# Start services
docker compose -f docker-compose.prod.yml up -d
```

### Environment-Specific Configuration

- Development: `.env.development`
- Staging: `.env.staging`
- Production: `.env.production`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is proprietary and confidential.

## 👥 Support

For support, email support@pocmanager.com or open an issue in the repository.

## 🗺 Roadmap

- [ ] Advanced analytics and reporting
- [ ] Mobile app (iOS/Android)
- [ ] Advanced integrations (Salesforce, HubSpot)
- [ ] AI-powered POC recommendations
- [ ] Real-time collaboration features
- [ ] Custom workflows and automation
- [ ] Multi-language support
- [ ] API webhooks

## 📊 Database Schema

### Core Entities
- **Tenants**: Multi-tenant isolation
- **Users**: Authentication and authorization
- **POCs**: POC lifecycle management
- **Tasks**: Reusable task templates
- **TaskGroups**: Grouped task templates
- **POCTasks**: Task instances in POCs
- **SuccessCriteria**: Success metrics
- **Comments**: Collaboration
- **Resources**: Documentation and code
- **Integrations**: External service configs

## 🎯 User Workflows

### Platform Admin
1. Create and manage tenants
2. Set user limits
3. Configure platform settings
4. Monitor usage across tenants

### Tenant Admin
1. Configure tenant branding
2. Set up integrations (Slack, Jira, GitHub)
3. Invite administrators and sales engineers
4. Monitor POC performance

### Administrator
1. Create task and task group templates
2. Archive completed POCs
3. View dashboards and analytics
4. Manage team members

### Sales Engineer
1. Create new POCs
2. Define success criteria
3. Add tasks from templates
4. Invite customer participants
5. Track progress and update status
6. Generate POC documents

### Customer
1. View assigned POCs
2. Complete tasks
3. Provide feedback via comments
4. Track success criteria progress

---

**Built with ❤️ for efficient POC management**
