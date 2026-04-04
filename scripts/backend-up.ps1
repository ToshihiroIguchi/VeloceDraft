param(
    [int]$Port = 8400
)
$ErrorActionPreference = "Stop"
cd "$PSScriptRoot\..\app_build\backend"
..\..\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port $Port
