$ErrorActionPreference = "Stop"

$scriptDir = $PSScriptRoot
$logDir = "$scriptDir\..\production_artifacts\logs"

if (-not (Test-Path -Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$backendOut = "$logDir\backend-out.log"
$backendErr = "$logDir\backend-err.log"
$frontendOut = "$logDir\frontend-out.log"
$frontendErr = "$logDir\frontend-err.log"

Write-Host "Starting Backend..."
Start-Process -FilePath "powershell" -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "$scriptDir\backend-up.ps1" -RedirectStandardOutput $backendOut -RedirectStandardError $backendErr -WindowStyle Hidden

Write-Host "Starting Frontend..."
Start-Process -FilePath "powershell" -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "$scriptDir\frontend-up.ps1" -RedirectStandardOutput $frontendOut -RedirectStandardError $frontendErr -WindowStyle Hidden

Write-Host "Both processes started. Logs are inside production_artifacts/logs"
Write-Host "Backend: localhost:8000"
Write-Host "Frontend: localhost:5173"
