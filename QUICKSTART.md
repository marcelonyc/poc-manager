# POC Manager - Quick Start Guide

## 🎯 What You've Got

A complete full-stack POC (Proof of Concept) management application with:

- **Backend**: Python FastAPI with PostgreSQL
- **Frontend**: React with TypeScript
- **Authentication**: JWT with role-based access
- **Database**: SQLAlchemy + Alembic migrations
- **Integrations**: Slack, Jira, GitHub, Email
- **Documents**: PDF, Word, Markdown generation
- **Testing**: Comprehensive pytest suite
- **Docker**: Ready-to-deploy containers

## 🚀 Get Started in 3 Steps

### Option 1: Docker (Recommended)

```bash
# 1. Run the setup script
./setup.sh

# 2. Open your browser
# Frontend: http://localhost:3001
# API Docs: http://localhost:8000/docs

# 3. Login with default credentials
# Email: admin@platform.com
# Password: admin123
```

### Option 2: Manual Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
createdb poc_manager
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (in new terminal)
cd frontend
npm install
npm run dev
```

## 📋 Project Structure

```
poc-manager/
├── backend/              # Python FastAPI application
│   ├── app/
│   │   ├── models/      # Database models
│   │   ├── routers/     # API endpoints
│   │   ├── schemas/     # Request/response schemas
│   │   ├── services/    # Business logic & integrations
│   │   └── main.py      # Application entry point
│   ├── tests/           # Test suite
│   ├── alembic/         # Database migrations
│   └── requirements.txt
├── frontend/            # React TypeScript application
│   ├── src/
│   │   ├── components/  # Reusable components
│   │   ├── pages/       # Page components
│   │   ├── lib/         # Utilities
│   │   └── store/       # State management
│   └── package.json
├── docs/                # Documentation
├── docker-compose.yml   # Docker setup
├── Makefile            # Helper commands
└── README.md           # Comprehensive documentation
```

## 🎭 User Roles Explained

1. **Platform Admin**
   - Manages all tenants
   - Creates new tenants
   - Sets platform-wide limits
   - Login: `admin@platform.com / admin123`

2. **Tenant Admin**
   - Manages their tenant
   - Configures branding
   - Sets up integrations
   - Invites team members

3. **Administrator**
   - Creates task templates
   - Manages POCs
   - Views analytics
   - Manages team

4. **Sales Engineer**
   - Creates new POCs
   - Defines success criteria
   - Invites customers
   - Tracks progress

5. **Customer**
   - Views assigned POCs
   - Completes tasks
   - Adds feedback
   - Tracks success

## 🛠 Common Commands

```bash
# Start everything
make start
# or
docker compose up -d

# View logs
make logs
# or
docker compose logs -f

# Run tests
make backend-test

# Run database migrations
make migrate
# or
docker compose exec backend alembic upgrade head

# Seed sample data
make seed

# Stop everything
make stop
# or
docker compose down

# Clean everything (including data!)
make clean
```

## 🔑 Default Credentials

After running setup, you'll have:

**Platform Admin:**
- Email: `admin@platform.com`
- Password: `admin123`

**Sample Tenant (if seeded):**
- Tenant Admin: `admin@acme.com / admin123`
- Administrator: `manager@acme.com / manager123`
- Sales Engineer: `sales@acme.com / sales123`

⚠️ **Change these passwords immediately in production!**

## 📚 Key Features to Try

### 1. Create a Tenant (Platform Admin)
- Go to Tenants → Create New
- Add company name, logo, colors
- Set user limits

### 2. Define Task Templates (Administrator)
- Go to Templates
- Create reusable tasks
- Organize into task groups

### 3. Create a POC (Sales Engineer)
- Go to POCs → Create New
- Add customer info
- Define success criteria
- Drag and drop tasks
- Invite participants

### 4. Collaborate (Customer/Sales Engineer)
- Add comments (internal/external)
- Update task status
- Track success levels
- Upload resources

### 5. Generate Documents
- Export POC to PDF/Word/Markdown
- Include all details and status
- Share with stakeholders

## 🔗 Important URLs

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

## 📖 More Documentation

- `README.md` - Complete documentation
- `docs/API.md` - API endpoint reference
- `backend/README.md` - Backend specifics
- `frontend/README.md` - Frontend specifics

## 🧪 Running Tests

```bash
# All backend tests
cd backend
pytest

# With coverage report
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_auth.py -v

# Run pre-commit hooks
pre-commit run --all-files
```

## 🐛 Troubleshooting

### Database Connection Error
```bash
# Make sure PostgreSQL is running
docker compose ps

# Check logs
docker compose logs db

# Recreate database
docker compose down -v
docker compose up -d
```

### Port Already in Use
```bash
# Check what's using the port
lsof -i :3001
lsof -i :8000
lsof -i :5432

# Change ports in docker-compose.yml or .env
```

### Frontend Can't Connect to Backend
```bash
# Check CORS settings in .env
CORS_ORIGINS=http://localhost:3001

# Restart backend
docker compose restart backend
```

## 🔐 Security Notes

1. **Change default passwords** immediately
2. **Set strong SECRET_KEY** in production
3. **Use environment variables** for sensitive data
4. **Enable HTTPS** in production
5. **Regularly update dependencies**
6. **Review access logs**

## 🚀 Next Steps

1. ✅ Run `./setup.sh` or `make setup`
2. ✅ Login and explore the interface
3. ✅ Create your first tenant
4. ✅ Set up task templates
5. ✅ Create a test POC
6. ✅ Configure integrations (Slack, Jira, GitHub)
7. ✅ Customize branding
8. ✅ Invite team members
9. ✅ Generate your first POC document

## 💡 Tips

- Use **drag-and-drop** to reorder tasks
- Mark comments as **internal** for team-only visibility
- Link **resources to success criteria** for easy tracking
- Use **task templates** to speed up POC creation
- Set up **Slack notifications** for real-time updates
- Export POCs to **multiple formats** for different audiences

## 🤝 Support

Need help? 
- Check the full `README.md`
- Review API docs at `/docs`
- Check example code in `tests/`
- Review the issue tracker

## 🎉 You're Ready!

Everything is set up and ready to go. Start by logging in with the platform admin credentials and creating your first tenant!

**Happy POC Managing! 🚀**
