<#
.SYNOPSIS
    DefectVision AI — Local Full-Stack Shutdown Script (Windows PowerShell)
.DESCRIPTION
    Safely terminates the FastAPI backend and Vite frontend processes and their child trees.
    Never kills arbitrary processes based solely on port bindings.
    Verifies that target processes belong to this application before issuing termination.
#>

$ScriptRoot = $PSScriptRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "      DefectVision AI — Safe Full-Stack Shutdown          " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

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

    # Must specifically match DefectVision AI backend (uvicorn app:app) or frontend (vite / npm dev)
    $isBackend = ($cmd -match "uvicorn" -and $cmd -match "app:app")
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

function Stop-ProcessTreeSafely {
    param([int]$ProcId, [string]$Name)
    if ($ProcId -le 0) { return }

    try {
        $proc = Get-Process -Id $ProcId -ErrorAction Stop
    } catch {
        Write-Host "[INFO] $Name (PID: $ProcId) is not active." -ForegroundColor Gray
        return
    }

    if (-not (Test-IsDefectVisionProcess -ProcId $ProcId)) {
        Write-Host "[WARN] Process $ProcId does not match DefectVision AI signature. Skipping." -ForegroundColor Yellow
        return
    }

    Write-Host "[INFO] Terminating $Name process tree (PID: $ProcId)..." -ForegroundColor Yellow
    try {
        $null = & taskkill.exe /PID $ProcId /T /F 2>&1
        Start-Sleep -Milliseconds 500
        Write-Host "[OK] $Name (PID: $ProcId) and child processes terminated." -ForegroundColor Green
    } catch {
        Stop-Process -Id $ProcId -Force -ErrorAction SilentlyContinue
    }
}

# 1. Terminate Backend recorded in .backend.pid
$BackendPidFile = Join-Path $ScriptRoot ".backend.pid"
if (Test-Path $BackendPidFile) {
    $raw = (Get-Content $BackendPidFile -Raw -ErrorAction SilentlyContinue)
    if ($raw) {
        $bPid = [int]$raw.Trim()
        Stop-ProcessTreeSafely -ProcId $bPid -Name "FastAPI Backend"
    }
    Remove-Item $BackendPidFile -Force -ErrorAction SilentlyContinue
}

# 2. Terminate Frontend recorded in .frontend.pid
$FrontendPidFile = Join-Path $ScriptRoot ".frontend.pid"
if (Test-Path $FrontendPidFile) {
    $raw = (Get-Content $FrontendPidFile -Raw -ErrorAction SilentlyContinue)
    if ($raw) {
        $fPid = [int]$raw.Trim()
        Stop-ProcessTreeSafely -ProcId $fPid -Name "Vite Frontend"
    }
    Remove-Item $FrontendPidFile -Force -ErrorAction SilentlyContinue
}

# 3. Check Ports 8000 and 5173 without blind killing
function Check-PortReleased {
    param([int]$Port)
    try {
        $conns = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
        if (-not $conns -or $conns.Count -eq 0) {
            Write-Host "[OK] Port $Port is free." -ForegroundColor Green
            return $true
        }

        foreach ($c in $conns) {
            $owningPid = $c.OwningProcess
            if ($owningPid -gt 0) {
                if (Test-IsDefectVisionProcess -ProcId $owningPid) {
                    Write-Host "[INFO] Releasing lingering application listener on Port $Port (PID: $owningPid)..." -ForegroundColor Yellow
                    try {
                        $null = & taskkill.exe /PID $owningPid /T /F 2>&1
                        Start-Sleep -Milliseconds 500
                    } catch {
                        Stop-Process -Id $owningPid -Force -ErrorAction SilentlyContinue
                    }
                } else {
                    $details = Get-ProcessDetails -ProcId $owningPid
                    $name = if ($details) { $details.Name } else { "Unknown" }
                    Write-Host "[WARN] Port $Port is held by an UNRELATED process (PID: $owningPid, Name: $name). Leaving untouched." -ForegroundColor Yellow
                    return $false
                }
            }
        }
        return $true
    } catch {
        return $true
    }
}

$port8000Clean = Check-PortReleased -Port 8000
$port5173Clean = Check-PortReleased -Port 5173

Write-Host "==========================================================" -ForegroundColor Green
if ($port8000Clean -and $port5173Clean) {
    Write-Host "     All DefectVision AI Services Successfully Stopped   " -ForegroundColor Green
} else {
    Write-Host "   Shutdown complete. Note: Some ports are held by other apps." -ForegroundColor Yellow
}
Write-Host "==========================================================" -ForegroundColor Green
