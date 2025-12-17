#!/bin/bash
set -e

echo "🚀 Starting {{PROJECT_NAME}} application..."

# Wait for database if needed
if [ -n "$POSTGRES_HOST" ]; then
    echo "⏳ Waiting for database..."
    until python -c "import asyncio; from src.db.base import engine; from sqlalchemy import text; asyncio.run(engine.connect().__aenter__().execute(text('SELECT 1')))" 2>/dev/null; do
        echo "Database is unavailable - sleeping"
        sleep 1
    done
    echo "✅ Database is ready!"
fi

echo "✅ Entrypoint complete!"

