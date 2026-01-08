# Start Knowledge Base Server
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Knowledge Base Server" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Activate virtual environment
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\Activate
}

Write-Host "`nServer starting on localhost:8080..." -ForegroundColor Green
Write-Host "`nAccess URLs:" -ForegroundColor Yellow
Write-Host "  API Documentation:  http://localhost:8080/docs" -ForegroundColor White
Write-Host "  Health Check:       http://localhost:8080/health" -ForegroundColor White
Write-Host "  Frontend:           http://localhost:8080/" -ForegroundColor White
Write-Host "  Alternative URL:    http://127.0.0.1:8080/docs" -ForegroundColor White
Write-Host "`nPress Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host "=========================================" -ForegroundColor Cyan

uvicorn app.main:app --reload --host localhost --port 8080