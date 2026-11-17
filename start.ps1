<#
.SYNOPSIS
    DefectVision AI — Local Full-Stack Launch Script (Windows PowerShell)
.DESCRIPTION
    Launches the FastAPI backend and Vite React frontend concurrently.
    Verifies truthful readiness on http://localhost:8000/health before launching the UI.
    Records process IDs in .backend.pid and .frontend.pid for clean termination via .\stop.ps1.
#>

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "      DefectVision AI — Local Full-Stack Startup         " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Resolve Python Interpreter
$PythonExe = Join-Path $ScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
    Write-Host "[WARN] Virtualenv not found at .venv. Using system python." -ForegroundColor Yellow
} else {
    Write-Host "[INFO] Using virtual environment: $PythonExe" -ForegroundColor Green
}

# 2. Free any stale processes on Ports 8000 and 5173
function Clear-PortOccupant {
    param([int]$Port)
    try {
        $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if ($conns) {
            foreach ($c in $conns) {
                $pidToKill = $c.OwningProcess
                if ($pidToKill -gt 0) {
                    Write-Host "[INFO] Freeing port $Port held by PID $pidToKill..." -ForegroundColor Yellow
                    Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
                }
            }
        }
    } catch {
        # Best effort
    }
}

Clear-PortOccupant -Port 8000
Clear-PortOccupant -Port 5173

# 3. Launch Backend (FastAPI + PyTorch CPU + FAISS)
Write-Host "[INFO] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Cyan
$BackendDir = Join-Path $ScriptRoot "DefectVisionAI"
$BackendOutLog = Join-Path $ScriptRoot ".backend.stdout.log"
$BackendErrLog = Join-Path $ScriptRoot ".backend.stderr.log"

$BackendProc = Start-Process `
    -FilePath $PythonExe `
    -ArgumentList "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000" `
    -WorkingDirectory $BackendDir `
    -RedirectStandardOutput $BackendOutLog `
    -RedirectStandardError $BackendErrLog `
    -PassThru

Set-Content -Path (Join-Path $ScriptRoot ".backend.pid") -Value $BackendProc.Id
Write-Host "[INFO] Backend started with PID $($BackendProc.Id). Waiting for model initialization..." -ForegroundColor Gray

# 4. Poll /health until truthful readiness is achieved
$MaxWaitSec = 60
$Elapsed = 0
$BackendReady = $false

while ($Elapsed -lt $MaxWaitSec) {
    Start-Sleep -Seconds 2
    $Elapsed += 2
    try {
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get -TimeoutSec 3 -ErrorAction Stop
        if ($resp.status -eq "ready") {
            $BackendReady = $true
            Write-Host "[OK] Backend ready in ${Elapsed}s! Status: $($resp.status), Engine: $($resp.engine_status)" -ForegroundColor Green
            break
        } else {
            Write-Host "[INFO] Backend loading: Status=$($resp.status), Engine=$($resp.engine_status) (${Elapsed}s)..." -ForegroundColor Gray
        }
    } catch {
        Write-Host "[INFO] Waiting for backend socket (${Elapsed}s)..." -ForegroundColor Gray
    }
}

if (-not $BackendReady) {
    Write-Host "[ERROR] Backend failed to achieve ready status within $MaxWaitSec seconds." -ForegroundColor Red
    Write-Host "[INFO] Inspect log output in $BackendErrLog or $BackendOutLog" -ForegroundColor Yellow
    exit 1
}

# 5. Launch Frontend (Vite React)
Write-Host "[INFO] Starting Vite React Frontend on http://127.0.0.1:5173..." -ForegroundColor Cyan
$FrontendDir = Join-Path $ScriptRoot "frontend"
$FrontendOutLog = Join-Path $ScriptRoot ".frontend.stdout.log"
$FrontendErrLog = Join-Path $ScriptRoot ".frontend.stderr.log"

$FrontendProc = Start-Process `
    -FilePath "cmd.exe" `
    -ArgumentList "/c", "npm", "run", "dev" `
    -WorkingDirectory $FrontendDir `
    -RedirectStandardOutput $FrontendOutLog `
    -RedirectStandardError $FrontendErrLog `
    -PassThru

Set-Content -Path (Join-Path $ScriptRoot ".frontend.pid") -Value $FrontendProc.Id
Write-Host "[INFO] Frontend started with PID $($FrontendProc.Id)." -ForegroundColor Gray

# 6. Poll frontend port until reachable
$FeWait = 0
$FrontendReady = $false
while ($FeWait -lt 20) {
    Start-Sleep -Seconds 1
    $FeWait += 1
    try {
        $feResp = Invoke-WebRequest -Uri "http://127.0.0.1:5173" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($feResp.StatusCode -eq 200) {
            $FrontendReady = $true
            break
        }
    } catch {
        # wait
    }
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "          DefectVision AI is Live & Ready!               " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  * Frontend Application: http://localhost:5173" -ForegroundColor White
Write-Host "  * Backend API Health:   http://localhost:8000/health" -ForegroundColor White
Write-Host "  * Swagger API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "  * Models Status:        http://localhost:8000/api/models/status" -ForegroundColor White
Write-Host "----------------------------------------------------------" -ForegroundColor Gray
Write-Host "  To stop the application cleanly, run: .\stop.ps1" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
