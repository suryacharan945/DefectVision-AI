<#
.SYNOPSIS
    DefectVision AI — Safe Local Full-Stack Startup (Windows PowerShell)
.DESCRIPTION
    Validates environment dependencies and checks for port conflicts.
    Never terminates unrelated third-party applications.
    Launches FastAPI backend and Vite frontend with truthful readiness verification.
#>

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "      DefectVision AI — Safe Full-Stack Startup           " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# -------------------------------------------------------------
# Helper Functions: Process & Port Inspection
# -------------------------------------------------------------
function Get-ProcessDetails {
    param([int]$ProcId)
    if ($ProcId -le 0) { return $null }
    try {
        $p = Get-CimInstance Win32_Process -Filter "ProcessId = $ProcId" -ErrorAction SilentlyContinue
        return $p
    } catch {
        return $null
    }
}

function Test-IsDefectVisionProcess {
    param([int]$ProcId)
    if ($ProcId -le 0) { return $false }
    $p = Get-ProcessDetails -ProcId $ProcId
    if (-not $p) { return $false }

    $cmd = $p.CommandLine
    if (-not $cmd) { return $false }

    # Must specifically match DefectVision AI backend (uvicorn app:app or python DefectVisionAI) or frontend (vite / npm dev)
    $isBackend = ($cmd -match "uvicorn" -and ($cmd -match "app:app" -or $cmd -match "DefectVisionAI")) -or ($cmd -match "python" -and $cmd -match "DefectVisionAI")
    $isFrontend = ($cmd -match "vite" -or ($cmd -match "npm" -and $cmd -match "dev"))

    if ($isBackend -or $isFrontend) {
        $normRoot = $ScriptRoot.Replace("/", "\").TrimEnd("\")
        if ($cmd.IndexOf($normRoot, [System.StringComparison]::OrdinalIgnoreCase) -ge 0 -or $cmd -match "DefectVisionAI") {
            return $true
        }
    }

    # Also check if PID matches a recorded DefectVision AI PID file
    $bPidFile = Join-Path $ScriptRoot ".backend.pid"
    if (Test-Path $bPidFile) {
        $savedBPid = [int](Get-Content $bPidFile -Raw -ErrorAction SilentlyContinue)
        if ($savedBPid -eq $ProcId) { return $true }
    }
    $fPidFile = Join-Path $ScriptRoot ".frontend.pid"
    if (Test-Path $fPidFile) {
        $savedFPid = [int](Get-Content $fPidFile -Raw -ErrorAction SilentlyContinue)
        if ($savedFPid -eq $ProcId) { return $true }
    }

    return $false
}

function Assert-PortAvailable {
    param([int]$Port, [string]$ServiceName)
    try {
        $conns = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
        if (-not $conns -or $conns.Count -eq 0) { return }

        foreach ($c in $conns) {
            $owningPid = $c.OwningProcess
            if ($owningPid -gt 0) {
                if (Test-IsDefectVisionProcess -ProcId $owningPid) {
                    Write-Host "[INFO] Port $Port is occupied by a previously launched DefectVision AI process (PID: $owningPid). Releasing..." -ForegroundColor Yellow
                    try {
                        $null = & taskkill.exe /PID $owningPid /T /F 2>&1
                        Start-Sleep -Milliseconds 800
                    } catch {
                        Stop-Process -Id $owningPid -Force -ErrorAction SilentlyContinue
                    }
                } else {
                    $details = Get-ProcessDetails -ProcId $owningPid
                    $name = if ($details) { $details.Name } else { "Unknown" }
                    $cmd = if ($details) { $details.CommandLine } else { "Unavailable" }
                    Write-Host ""
                    Write-Host "[ERROR] Port $Port required for $ServiceName is currently in use by an UNRELATED application!" -ForegroundColor Red
                    Write-Host "        PID:          $owningPid" -ForegroundColor Yellow
                    Write-Host "        Process Name: $name" -ForegroundColor Yellow
                    Write-Host "        Command Line: $cmd" -ForegroundColor Yellow
                    Write-Host ""
                    Write-Host "[ERROR] Aborting startup to prevent terminating foreign applications." -ForegroundColor Red
                    Write-Host "        Please stop the conflicting application or configure an alternate port." -ForegroundColor Red
                    exit 1
                }
            }
        }
    } catch {
        Write-Host "[WARN] Port inspection check encountered an issue on Port ${Port}: $_" -ForegroundColor Yellow
    }
}

# -------------------------------------------------------------
# 1. Inspect Port Availability (Never terminate foreign apps)
# -------------------------------------------------------------
Write-Host "[INFO] Checking port availability..." -ForegroundColor Gray
Assert-PortAvailable -Port 8001 -ServiceName "FastAPI Backend"
Assert-PortAvailable -Port 5174 -ServiceName "Vite React Frontend"

# -------------------------------------------------------------
# 2. Resolve & Verify Python Environment
# -------------------------------------------------------------
$PythonExe = Join-Path $ScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
    Write-Host "[WARN] Virtualenv not found at .venv. Using system python." -ForegroundColor Yellow
} else {
    Write-Host "[INFO] Python environment: $PythonExe" -ForegroundColor Green
}

# Verify Python runs and core dependencies are installed
Write-Host "[INFO] Verifying Python dependencies..." -ForegroundColor Gray
try {
    $depCheck = & $PythonExe -c "import fastapi, uvicorn, torch, cv2" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Missing critical Python dependencies." -ForegroundColor Red
        Write-Host "        $depCheck" -ForegroundColor Yellow
        Write-Host "        Please install requirements: pip install -r requirements.txt" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "[ERROR] Failed to execute Python interpreter '$PythonExe'." -ForegroundColor Red
    exit 1
}

# -------------------------------------------------------------
# 3. Verify Node.js Environment for Frontend
# -------------------------------------------------------------
try {
    $npmVersion = & npm --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Node.js / npm is required to run the frontend but was not found on PATH." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] npm is not accessible. Please install Node.js 18+." -ForegroundColor Red
    exit 1
}

# -------------------------------------------------------------
# 4. Launch Backend (FastAPI + PyTorch CPU + FAISS)
# -------------------------------------------------------------
Write-Host "[INFO] Launching FastAPI Backend on http://127.0.0.1:8001..." -ForegroundColor Cyan
$BackendDir = Join-Path $ScriptRoot "DefectVisionAI"
$BackendOutLog = Join-Path $ScriptRoot ".backend.stdout.log"
$BackendErrLog = Join-Path $ScriptRoot ".backend.stderr.log"

$BackendProc = Start-Process `
    -FilePath $PythonExe `
    -ArgumentList "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8001" `
    -WorkingDirectory $BackendDir `
    -RedirectStandardOutput $BackendOutLog `
    -RedirectStandardError $BackendErrLog `
    -PassThru

Set-Content -Path (Join-Path $ScriptRoot ".backend.pid") -Value $BackendProc.Id
Write-Host "[INFO] Backend started with PID $($BackendProc.Id). Loading 15 PatchCore models..." -ForegroundColor Gray

# -------------------------------------------------------------
# 5. Poll /health for Truthful Readiness
# -------------------------------------------------------------
$BackendTimeoutSec = 90
$Elapsed = 0
$BackendReady = $false

while ($Elapsed -lt $BackendTimeoutSec) {
    Start-Sleep -Seconds 2
    $Elapsed += 2

    # Check if backend process crashed prematurely
    if ($BackendProc.HasExited) {
        Write-Host ""
        Write-Host "[ERROR] Backend process terminated prematurely with exit code $($BackendProc.ExitCode)!" -ForegroundColor Red
        Write-Host "        Logs available at: $BackendErrLog and $BackendOutLog" -ForegroundColor Yellow
        if (Test-Path $BackendErrLog) {
            Write-Host "--- Backend Stderr Tail ---" -ForegroundColor Yellow
            Get-Content $BackendErrLog -Tail 15 | Write-Host -ForegroundColor Yellow
        }
        Remove-Item (Join-Path $ScriptRoot ".backend.pid") -Force -ErrorAction SilentlyContinue
        exit 1
    }

    try {
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8001/health" -Method Get -TimeoutSec 3 -ErrorAction Stop
        $allReady = ($resp.all_required_models_ready -eq $true) -or ($resp.all_models_ready -eq $true)
        $mCount = if ($resp.ready_category_models_count) { $resp.ready_category_models_count } elseif ($resp.models_ready_count) { $resp.models_ready_count } else { 0 }
        $clsReady = ($resp.classifier_ready -eq $true)
        $optReady = ($resp.optical_engine_ready -eq $true) -or ($resp.optical_engine_initialized -eq $true)

        if ($resp.status -eq "ready" -and $allReady -and $clsReady -and $optReady -and ($mCount -ge 15)) {
            $BackendReady = $true
            Write-Host "[OK] Backend ready in ${Elapsed}s! Status: $($resp.status), Models: $mCount/15, Classifier: OK, OpticalEngine: OK" -ForegroundColor Green
            break
        } else {
            Write-Host "[INFO] Initializing memory banks: status=$($resp.status), models=$mCount/15, classifier=$clsReady (${Elapsed}s)..." -ForegroundColor Gray
        }
    } catch {
        Write-Host "[INFO] Waiting for backend socket (${Elapsed}s)..." -ForegroundColor Gray
    }
}

if (-not $BackendReady) {
    Write-Host ""
    Write-Host "[ERROR] Backend failed to achieve ready status within $BackendTimeoutSec seconds." -ForegroundColor Red
    Write-Host "        Log location: $BackendErrLog" -ForegroundColor Yellow
    # Rollback: Clean up started backend process
    try { & taskkill.exe /PID $BackendProc.Id /T /F 2>&1 } catch {}
    Remove-Item (Join-Path $ScriptRoot ".backend.pid") -Force -ErrorAction SilentlyContinue
    exit 1
}

# -------------------------------------------------------------
# 6. Launch Frontend (Vite React)
# -------------------------------------------------------------
Write-Host "[INFO] Launching Vite Frontend on http://127.0.0.1:5174..." -ForegroundColor Cyan
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
Write-Host "[INFO] Frontend launcher started with PID $($FrontendProc.Id)." -ForegroundColor Gray

# -------------------------------------------------------------
# 7. Poll Frontend Socket & Verify HTTP 200
# -------------------------------------------------------------
$FrontendTimeoutSec = 30
$FeElapsed = 0
$FrontendReady = $false

while ($FeElapsed -lt $FrontendTimeoutSec) {
    Start-Sleep -Seconds 1
    $FeElapsed += 1

    if ($FrontendProc.HasExited) {
        Write-Host ""
        Write-Host "[ERROR] Frontend process exited prematurely with exit code $($FrontendProc.ExitCode)!" -ForegroundColor Red
        Write-Host "        Logs available at: $FrontendErrLog and $FrontendOutLog" -ForegroundColor Yellow
        # Rollback: terminate backend
        try { & taskkill.exe /PID $BackendProc.Id /T /F 2>&1 } catch {}
        Remove-Item (Join-Path $ScriptRoot ".backend.pid") -Force -ErrorAction SilentlyContinue
        Remove-Item (Join-Path $ScriptRoot ".frontend.pid") -Force -ErrorAction SilentlyContinue
        exit 1
    }

    try {
        $feResp = Invoke-WebRequest -Uri "http://127.0.0.1:5174" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($feResp.StatusCode -eq 200) {
            $FrontendReady = $true
            Write-Host "[OK] Frontend responding on http://127.0.0.1:5174 (HTTP 200)!" -ForegroundColor Green
            break
        }
    } catch {
        # continue polling
    }
}

if (-not $FrontendReady) {
    Write-Host ""
    Write-Host "[ERROR] Frontend failed to achieve HTTP 200 readiness within $FrontendTimeoutSec seconds." -ForegroundColor Red
    Write-Host "        Inspect logs: $FrontendErrLog and $FrontendOutLog" -ForegroundColor Yellow
    # Rollback: terminate both backend and frontend processes started by this script
    try { & taskkill.exe /PID $FrontendProc.Id /T /F 2>&1 } catch {}
    try { & taskkill.exe /PID $BackendProc.Id /T /F 2>&1 } catch {}
    Remove-Item (Join-Path $ScriptRoot ".backend.pid") -Force -ErrorAction SilentlyContinue
    Remove-Item (Join-Path $ScriptRoot ".frontend.pid") -Force -ErrorAction SilentlyContinue
    exit 1
}

# -------------------------------------------------------------
# 8. Success Banner (Only printed when BOTH services are verified)
# -------------------------------------------------------------
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "          DefectVision AI is Live & Ready!                " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  * Frontend Application: http://localhost:5174" -ForegroundColor White
Write-Host "  * Backend API Health:   http://localhost:8001/health" -ForegroundColor White
Write-Host "  * Swagger API Docs:     http://localhost:8001/docs" -ForegroundColor White
Write-Host "  * Models Status:        http://localhost:8001/api/models/status" -ForegroundColor White
Write-Host "----------------------------------------------------------" -ForegroundColor Gray
Write-Host "  To stop the application cleanly, run: .\stop.ps1" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
