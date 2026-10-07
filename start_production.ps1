# ==============================================================================
# Windows Production Runner for Incident Response Agent
# Starts Hindsight API Server, builds frontend, and runs production FastAPI app
# ==============================================================================

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "🛡️  Incident Response Agent - Production Runner" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 1. Check Python Virtualenv
$VenvPython = Join-Path $ScriptDir "backend\.venv\Scripts\python.exe"
$VenvUvicorn = Join-Path $ScriptDir "backend\.venv\Scripts\uvicorn.exe"
$HindsightExe = Join-Path $ScriptDir "backend\.venv\Scripts\hindsight-api.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "[-] Virtualenv not found at backend\.venv. Please create it first." -ForegroundColor Red
    exit 1
}

# Install the server package separately from hindsight-client when this is an older venv.
if (-not (Test-Path $HindsightExe)) {
    Write-Host "[*] Hindsight API executable is missing. Installing hindsight-api==0.10.1..." -ForegroundColor Yellow
    & $VenvPython -m pip install "hindsight-api==0.10.1"
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $HindsightExe)) {
        Write-Host "[-] Could not install hindsight-api. Run: backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt" -ForegroundColor Red
        exit 1
    }
}

# 2. Check / Start Hindsight API Server
Write-Host "[*] Checking Hindsight API Server on http://127.0.0.1:8888..." -ForegroundColor Yellow
$HindsightHealthy = $false
try {
    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8888/health" -TimeoutSec 2 -ErrorAction Stop
    if ($resp.status -eq "healthy") {
        $HindsightHealthy = $true
        Write-Host "[+] Hindsight API Server is already running and healthy!" -ForegroundColor Green
    }
} catch {
    Write-Host "[*] Hindsight is not running. Starting background Hindsight API server..." -ForegroundColor Yellow
    $env:PYTHONUTF8 = "1"
    $env:PYTHONIOENCODING = "utf-8"
    $env:HINDSIGHT_API_LLM_PROVIDER = "mock"
    Start-Process -FilePath $HindsightExe -ArgumentList "--host", "127.0.0.1", "--port", "8888" -WindowStyle Hidden
    
    # Wait for ready
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Seconds 1
        try {
            $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8888/health" -TimeoutSec 2 -ErrorAction Stop
            if ($resp.status -eq "healthy") {
                $HindsightHealthy = $true
                Write-Host "[+] Hindsight Server is up and ready!" -ForegroundColor Green
                break
            }
        } catch {}
    }
}

if (-not $HindsightHealthy) {
    Write-Host "[-] Hindsight server did not become healthy at http://127.0.0.1:8888/health. Check the server startup output and retry." -ForegroundColor Red
    exit 1
}

# 3. Verify / Build Frontend
$DistIndex = Join-Path $ScriptDir "frontend\dist\index.html"
if (-not (Test-Path $DistIndex)) {
    Write-Host "[*] Building React production frontend bundle..." -ForegroundColor Yellow
    Set-Location (Join-Path $ScriptDir "frontend")
    npm run build
    Set-Location $ScriptDir
} else {
    Write-Host "[+] Frontend production bundle is up-to-date in frontend\dist." -ForegroundColor Green
}

# 4. Initialize Database
Write-Host "[*] Initializing SQLite database and verifying incident seed data..." -ForegroundColor Yellow
Set-Location (Join-Path $ScriptDir "backend")
& $VenvPython -c "import asyncio; from app.core.database import async_session_factory; from app.services.seed_service import seed_all; async def init(): async with async_session_factory() as s: await seed_all(s); asyncio.run(init())"
Set-Location $ScriptDir

# 5. Launch FastAPI Application
Write-Host "`n========================================================" -ForegroundColor Green
Write-Host "🚀 Application is ready for production use!" -ForegroundColor Green
Write-Host "   Frontend & API: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "   Swagger Docs:   http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "   Hindsight API:  http://127.0.0.1:8888" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Green

Start-Process "http://127.0.0.1:8000/"

Set-Location (Join-Path $ScriptDir "backend")
& $VenvUvicorn app.main:app --host 127.0.0.1 --port 8000
