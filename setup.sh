#!/bin/bash
set -e

echo "🚀 RAG MVP Setup Script"
echo "======================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Start database
echo "📦 Starting PostgreSQL + pgvector..."
docker compose up -d db
echo "✅ Database container started"
echo ""

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 5

# Check if database exists
DB_EXISTS=$(docker compose exec -T db psql -U rag_user -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='rag_db'" 2>/dev/null || echo "")

if [ -z "$DB_EXISTS" ]; then
    echo "📊 Creating database 'rag_db'..."
    docker compose exec -T db createdb -U rag_user rag_db
    echo "✅ Database created"
else
    echo "✅ Database 'rag_db' already exists"
fi
echo ""

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install Poetry first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

echo "✅ Poetry is installed"
echo ""

# Install dependencies
echo "📚 Installing Python dependencies..."
poetry install
echo "✅ Dependencies installed"
echo ""

# Set DATABASE_URL
export DATABASE_URL="postgresql+psycopg2://rag_user:rag_pass@localhost:5432/rag_db"

# Run migrations
echo "🔄 Running database migrations..."
poetry run alembic upgrade head
echo "✅ Migrations completed"
echo ""

# Verify tables
echo "🔍 Verifying database tables..."
TABLES=$(docker compose exec -T db psql -U rag_user -d rag_db -tAc "SELECT COUNT(*) FROM pg_tables WHERE schemaname='public'")
echo "✅ Found $TABLES tables in database"
echo ""

echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Start the API server:"
echo "     export DATABASE_URL=\"postgresql+psycopg2://rag_user:rag_pass@localhost:5432/rag_db\""
echo "     poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "  2. Open API docs: http://localhost:8000/docs"
echo ""
echo "  3. Upload a document:"
echo "     curl -X POST http://localhost:8000/documents -F \"file=@your_file.pdf\""
echo ""
echo "  4. Query documents:"
echo "     curl -X POST http://localhost:8000/query -H \"Content-Type: application/json\" \\"
echo "       -d '{\"question\": \"your question here\", \"top_k\": 5}'"
echo ""
