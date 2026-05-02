$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

Write-Host "Checking database migrations..."
.\.venv\Scripts\python.exe manage.py migrate

Write-Host "Starting Expense Tracker at http://127.0.0.1:8000/"
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
