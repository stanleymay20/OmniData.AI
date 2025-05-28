# OmniData.AI Run Script
Write-Host "Starting OmniData.AI..." -ForegroundColor Green

# Check if Docker is running
try {
    $dockerStatus = docker info
    Write-Host "Docker is running." -ForegroundColor Green
}
catch {
    Write-Host "Docker is not running. Please start Docker and try again." -ForegroundColor Red
    exit 1
}

# Build the application
Write-Host "Building the application..." -ForegroundColor Yellow
docker-compose build

# Start the application
Write-Host "Starting the application..." -ForegroundColor Yellow
docker-compose up -d

# Check if the application is running
Write-Host "Checking if the application is running..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Display service URLs
Write-Host "`nOmniData.AI is running!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "MLflow: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Airflow: http://localhost:8080" -ForegroundColor Cyan
Write-Host "`nTo stop the application, run: docker-compose down" -ForegroundColor Yellow 

docker-compose down
docker system prune -af
pwsh ./run.ps1 