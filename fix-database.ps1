Write-Host "Fixing database issues..." -ForegroundColor Green

# Останавливаем старый контейнер
docker stop postgres-db
docker rm postgres-db

# Запускаем новый
docker run --name postgres-db `
  -e POSTGRES_PASSWORD=password `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_DB=knowledge_base `
  -p 5432:5432 `
  -d postgres:15

Write-Host "Waiting for PostgreSQL to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Создаем таблицы
python scripts/simple_create_tables.py

# Проверяем
docker exec -it postgres-db psql -U postgres -d knowledge_base -c "\dt"

Write-Host "Database should be fixed now!" -ForegroundColor Green
Write-Host "Start the application with: uvicorn app.main:app --reload --port 8000" -ForegroundColor Cyan