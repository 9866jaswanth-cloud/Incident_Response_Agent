#!/bin/sh
set -e

echo "========================================================"
echo "🛡️  Starting Incident Response Agent (Production)"
echo "========================================================"

# 1. Start real Hindsight API server in the background
echo "[*] Launching Hindsight API Server on 127.0.0.1:8888..."
hindsight-api --host 127.0.0.1 --port 8888 &
HINDSIGHT_PID=$!

# 2. Wait for Hindsight health check
echo "[*] Waiting for Hindsight server to become ready..."
MAX_RETRIES=30
RETRY_COUNT=0
until curl -s http://127.0.0.1:8888/health > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "[-] ERROR: Hindsight failed to become ready in time."
        kill $HINDSIGHT_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done
echo "[+] Hindsight Server is healthy and ready!"

# 3. Initialize / Seed Database
echo "[*] Initializing SQLite database and seeding synthetic incidents..."
cd /app/backend
python -c "import asyncio; from app.core.database import async_session_factory; from app.services.seed_service import seed_all; async def init(): async with async_session_factory() as s: await seed_all(s); asyncio.run(init())"
echo "[+] Database successfully initialized!"

# 4. Launch FastAPI production server with Uvicorn
echo "[*] Launching Unified FastAPI + React Web Application on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 2
