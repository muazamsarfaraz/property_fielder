# PowerShell script to deploy Flutter mobile app to Railway

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Flutter Mobile App - Railway Deployment" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""

# Check if Railway CLI is installed
Write-Host "Checking Railway CLI..." -ForegroundColor Yellow
$railwayVersion = railway --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Railway CLI not found!" -ForegroundColor Red
    Write-Host "Install it from: https://docs.railway.app/develop/cli" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Railway CLI installed: $railwayVersion" -ForegroundColor Green
Write-Host ""

# Check if logged in
Write-Host "Checking Railway authentication..." -ForegroundColor Yellow
$whoami = railway whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Not logged in to Railway!" -ForegroundColor Red
    Write-Host "Run: railway login" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Logged in as: $whoami" -ForegroundColor Green
Write-Host ""

# Link to project
Write-Host "Linking to Railway project..." -ForegroundColor Yellow
$projectId = "1da4fd12-9fe3-4daa-aec7-33cd8e164098"

# Create .railway directory if it doesn't exist
if (-not (Test-Path ".railway")) {
    New-Item -ItemType Directory -Path ".railway" | Out-Null
}

# Create config.json
$config = @{
    project = $projectId
    environment = "production"
} | ConvertTo-Json

Set-Content -Path ".railway/config.json" -Value $config
Write-Host "✅ Linked to project: property-fielder" -ForegroundColor Green
Write-Host ""

# Ask user to create service
Write-Host "⚠️  MANUAL STEP REQUIRED" -ForegroundColor Yellow
Write-Host ""
Write-Host "Please create a new service in Railway:" -ForegroundColor White
Write-Host "1. Go to: https://railway.app/project/$projectId" -ForegroundColor Cyan
Write-Host "2. Click '+ New Service'" -ForegroundColor Cyan
Write-Host "3. Select 'Empty Service'" -ForegroundColor Cyan
Write-Host "4. Name it: 'mobile-app'" -ForegroundColor Cyan
Write-Host "5. Press Enter here when done..." -ForegroundColor Cyan
Read-Host

# Deploy
Write-Host ""
Write-Host "Deploying to Railway..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes..." -ForegroundColor Gray
Write-Host ""

railway up --service mobile-app

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Deployment successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Generate domain: railway domain" -ForegroundColor Cyan
    Write-Host "2. Access your app at the generated URL" -ForegroundColor Cyan
    Write-Host "3. Test login with admin/admin or inspector/inspector123" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    Write-Host "Check logs: railway logs --deployment" -ForegroundColor Yellow
}

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan

