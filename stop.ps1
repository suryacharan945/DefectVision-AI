<#
.SYNOPSIS
    DefectVision AI — Local Full-Stack Shutdown Script (Windows PowerShell)
.DESCRIPTION
    Gracefully stops the FastAPI backend and Vite frontend services,
    terminates associated processes by PID or port binding, and cleans up lock/log files.
#>

$ScriptRoot = $PSScriptRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "      DefectVision AI — Full-Stack Shutdown              " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

function Stop-ProcessSafely {
    param([int]$ProcId, [string]$Name)
    if ($ProcId -gt 0) {
        try {
            $p = Get-Process -Id $ProcId -ErrorAction Stop
            Write-Host "[INFO] Stopping $Name (PID: $ProcId)..." -ForegroundColor Yellow
            Stop-Process -Id $ProcId -Force -ErrorAction SilentlyContinue
            Write-Host "[OK] $Name terminated." -ForegroundColor Green
        } catch {
            Write-Host "[INFO] $Name (PID: $ProcId) is no longer running." -ForegroundColor Gray
        }
    }
}

function Clear-Port {
    param([int]$Port)
    try {
        $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if ($conns) {
            foreach ($c in $conns) {
                $pId = $c.OwningProcess
                if ($pId -gt 0) {
                    Write-Host "[INFO] Freeing Port $Port (PID: $pId)..." -ForegroundColor Yellow
                    Stop-Process -Id $pId -Force -ErrorAction SilentlyContinue
                }
            }
        }
    } catch {
        # best effort
    }
}

# 1. Terminate Backend via PID
$BackendPidFile = Join-Path $ScriptRoot ".backend.pid"
if (Test-Path $BackendPidFile) {
    $bPid = [int](Get-Content $BackendPidFile -Raw).Trim()
    Stop-ProcessSafely -ProcId $bPid -Name "FastAPI Backend"
    Remove-Item $BackendPidFile -Force -ErrorAction SilentlyContinue
}

# 2. Terminate Frontend via PID
$FrontendPidFile = Join-Path $ScriptRoot ".frontend.pid"
if (Test-Path $FrontendPidFile) {
    $fPid = [int](Get-Content $FrontendPidFile -Raw).Trim()
    Stop-ProcessSafely -ProcId $fPid -Name "Vite React Frontend"
    Remove-Item $FrontendPidFile -Force -ErrorAction SilentlyContinue
}

# 3. Clean remaining listeners on ports 8000 and 5173
Clear-Port -Port 8000
Clear-Port -Port 5173

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "     All DefectVision AI Services Successfully Stopped   " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
