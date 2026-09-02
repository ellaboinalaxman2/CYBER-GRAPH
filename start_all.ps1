$ErrorActionPreference = "Stop"

$ProjectRoot = Get-Location
$LogsDir = Join-Path $ProjectRoot "logs"

if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir | Out-Null
}

Write-Host "Creating log files in $LogsDir..."

function Start-Service {
    param (
        [string]$Name,
        [string]$Path,
        [string]$Command
    )
    Write-Host "Starting $Name..."
    $LogFile = Join-Path $LogsDir "$Name.log"
    $ErrFile = Join-Path $LogsDir "$Name-error.log"
    
    # We use Start-Process to launch a hidden PowerShell window that runs the command and pipes to a log file
    $FullCommand = "cd '$Path'; $Command"
    Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", " $FullCommand > '$LogFile' 2> '$ErrFile' "
}

# 1. Blockchain
Start-Service -Name "blockchain" -Path (Join-Path $ProjectRoot "blockchain") -Command "npm install; npx hardhat node"

# 2. Frontend
Start-Service -Name "frontend" -Path (Join-Path $ProjectRoot "frontend") -Command "npm install; npm run dev"

# 3. Database Engine
Start-Service -Name "database" -Path (Join-Path $ProjectRoot "database") -Command "if (-not (Test-Path .venv)) { python -m venv .venv }; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; python run.py"

# 4. Ingestion Engine
Start-Service -Name "ingestion" -Path (Join-Path $ProjectRoot "ingestion") -Command "if (-not (Test-Path .venv)) { python -m venv .venv }; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; python run.py"

# 5. AI Engine
Start-Service -Name "ai-engine" -Path (Join-Path $ProjectRoot "ai-engine") -Command "if (-not (Test-Path .venv)) { python -m venv .venv }; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; python run.py"

# 6. Attack Engine
Start-Service -Name "attack-engine" -Path (Join-Path $ProjectRoot "attack-engine") -Command "if (-not (Test-Path .venv)) { python -m venv .venv }; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; python run.py"

# 7. Backend
Start-Service -Name "backend" -Path (Join-Path $ProjectRoot "backend") -Command "if (-not (Test-Path .venv)) { python -m venv .venv }; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; uvicorn app.main:app --host 0.0.0.0 --port 8000"

Write-Host "All services started! Check the 'logs' folder for output."
