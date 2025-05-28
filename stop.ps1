# OmniData.AI Stop Script
Write-Host "Stopping OmniData.AI..." -ForegroundColor Yellow

# Stop the application
docker-compose down

# Check if the application is stopped
if ($LASTEXITCODE -eq 0) {
    Write-Host "OmniData.AI has been stopped successfully." -ForegroundColor Green
}
else {
    Write-Host "Failed to stop OmniData.AI. Please check the logs for more information." -ForegroundColor Red
} 