# Check if Poetry is available
if (Test-Path "pyproject.toml") {
    Write-Host "Poetry detected (pyproject.toml)" -ForegroundColor Yellow
    Write-Host "Run: pip install poetry" -ForegroundColor Cyan
    Write-Host "Then: poetry install" -ForegroundColor Cyan
    Write-Host "And: poetry shell" -ForegroundColor Cyan
}
else {
    # Activate virtual environment
    if (Test-Path "venv") {
        .\venv\Scripts\Activate
    }
    else {
        Write-Host "Creating virtual environment..." -ForegroundColor Yellow
        python -m venv venv
        .\venv\Scripts\Activate
        pip install --upgrade pip
        pip install -r requirements.txt
        Write-Host "Virtual environment created and activated" -ForegroundColor Green
    }
}