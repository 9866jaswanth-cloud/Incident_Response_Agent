#!/bin/bash
# ==============================================================================
# Unix/Linux/macOS Production Runner for Incident Response Agent
# Starts Hindsight API Server, builds frontend, and runs production FastAPI app
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================================"
echo "🛡️  Incident Response Agent - Production Runner"
echo "========================================================"

# 1. Check Python Virtualenv
VENV_PYTHON="$SCRIPT_DIR/backend/.venv/bin/python"
VENV_UVICORN="$SCRIPT_DIR/backend/.venv/bin/uvicorn"
HINDSIGHT_BIN="$SCRIPT_DIR/backend/.venv/bin/hindsight-api"

if [ ! -f "$VENV_PYTHON" ]; then
    VENV_PYTHON="python3"
    VENV_UVICORN="uvicorn"
    HINDSIGHT_BIN="hindsight-api"
fi

# The client SDK does not install the server executable. Repair older environments here.
if ! command -v "$HINDSIGHT_BIN" >/dev/null 2>&1; then
    echo "[*] Hindsight API executable is missing. Installing hindsight-api==0.10.1..."
    if ! "$VENV_PYTHON" -m pip install "hindsight-api==0.10.1"; then
        echo "[-] Could not install hindsight-api. Install backend/requirements.txt and retry."
        exit 1
    fi
    if [ -x "$SCRIPT_DIR/backend/.venv/bin/hindsight-api" ]; then
        HINDSIGHT_BIN="$SCRIPT_DIR/backend/.venv/bin/hindsight-api"
    fi
fi

# 2. Check / Start Hindsight API Server
echo "[*] Checking Hindsight API Server on http://127.0.0.1:8888..."
if curl -s http://127.0.0.1:8888/health >/dev/null 2>&1; then
    echo "[+] Hindsight API Server is already running and healthy!"
else
    echo "[*] Starting background Hindsight API server..."
    export PYTHONUTF8=1
    export HINDSIGHT_API_LLM_PROVIDER=mock
    "$HINDSIGHT_BIN" --host 127.0.0.1 --port 8888 &
    HINDSIGHT_PID=$!
    
    # Wait for ready
    MAX_WAIT=60
    COUNT=0
    until curl -s http://127.0.0.1:8888/health >/dev/null 2>&1; do
        sleep 1
        COUNT=$((COUNT+1))
        if [ $COUNT -ge $MAX_WAIT ]; then
            echo "[-] Hindsight server did not become healthy at http://127.0.0.1:8888/health. Check the server startup output and retry."
            kill "$HINDSIGHT_PID" 2>/dev/null || true
            exit 1
        fi
    done
    echo "[+] Hindsight Server is up and ready!"
fi

# 3. Verify / Build Frontend
if [ ! -f "$SCRIPT_DIR/frontend/dist/index.html" ]; then
    echo "[*] Building React production frontend bundle..."
    cd "$SCRIPT_DIR/frontend"
    npm ci
    npm run build
    cd "$SCRIPT_DIR"
else
    echo "[+] Frontend production bundle is up-to-date in frontend/dist."
fi

# 4. Initialize Database
echo "[*] Initializing SQLite database and verifying incident seed data..."
cd "$SCRIPT_DIR/backend"
$VENV_PYTHON -c "import asyncio; from app.core.database import async_session_factory; from app.services.seed_service import seed_all; async def init(): async with async_session_factory() as s: await seed_all(s); asyncio.run(init())"
cd "$SCRIPT_DIR"

# 5. Launch FastAPI Application
echo ""
echo "========================================================"
echo "🚀 Application is ready for production use!"
echo "   Frontend & API: http://127.0.0.1:8000"
echo "   Swagger Docs:   http://127.0.0.1:8000/docs"
echo "   Hindsight API:  http://127.0.0.1:8888"
echo "========================================================"
echo ""

cd "$SCRIPT_DIR/backend"
exec "$VENV_UVICORN" app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 2
