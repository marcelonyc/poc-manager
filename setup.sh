#!/bin/bash

# POC Manager Setup Script
echo "🚀 Setting up POC Manager..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration before proceeding."
    read -p "Press enter to continue..."
fi

# Create .env-vite file if it doesn't exist
if [ ! -f .env-vite ]; then
    echo "📝 Creating .env-vite file..."
    cp .env-vite.example .env-vite
    echo "✅ .env-vite file created for frontend configuration."
fi

# Start services
echo "🐳 Starting Docker containers..."
docker compose up -d

# Wait for database to be ready with health check
echo "⏳ Waiting for database to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0
until docker compose exec -T db pg_isready -U postgres > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo "❌ Database failed to become ready after $MAX_RETRIES attempts"
        echo "📋 Check database logs with: docker compose logs db"
        exit 1
    fi
    echo "⏳ Waiting for database... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done
echo "✅ Database is ready!"

# Additional delay to ensure database is fully initialized
sleep 3

# Run migrations
echo "🗄️  Running database migrations..."
docker compose exec -T backend alembic upgrade head

# Create platform admin
echo "👤 Creating platform admin user..."
docker compose exec -T backend python -c "
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.auth import get_password_hash

db = SessionLocal()

# Check if admin exists
existing = db.query(User).filter(User.email == 'admin@platform.com').first()
if existing:
    print('Platform admin already exists.')
else:
    admin = User(
        email='admin@platform.com',
        full_name='Platform Admin',
        hashed_password=get_password_hash('admin123'),
        role=UserRole.PLATFORM_ADMIN,
        is_active=True
    )
    db.add(admin)
    db.commit()
    print('✅ Platform admin created!')
    print('Email: admin@platform.com')
    print('Password: admin123')
    print('⚠️  Please change this password after first login!')
db.close()
"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📍 Access the application:"
echo "   Frontend: http://localhost:3001"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🔐 Login credentials:"
echo "   Email: admin@platform.com"
echo "   Password: admin123"
echo ""
echo "📚 To view logs:"
echo "   docker compose logs -f"
echo ""
echo "🛑 To stop services:"
echo "   docker compose down"
