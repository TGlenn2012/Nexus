# Fix Nexus Pipeline Connection Script
# Run this script to diagnose and fix the pipeline connection issue

Write-Host "`n=== NEXUS PIPELINE CONNECTION FIX ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check container status
Write-Host "[1] Checking container status..." -ForegroundColor Yellow
$pipelines = docker ps --filter "name=pipelines" --format "{{.Names}}"
$openWebUI = docker ps --filter "name=open-webui" --format "{{.Names}}"

if ($pipelines -ne "pipelines") {
    Write-Host "  ERROR: Pipelines container is not running!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Pipelines container is running" -ForegroundColor Green

if ($openWebUI -ne "open-webui") {
    Write-Host "  ERROR: Open WebUI container is not running!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Open WebUI container is running" -ForegroundColor Green

# Step 2: Test connectivity
Write-Host "`n[2] Testing connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9099/models" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✓ Can reach pipelines API (Status: $($response.StatusCode))" -ForegroundColor Green
    Write-Host "  Response preview:" -ForegroundColor Cyan
    $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 2 | Select-Object -First 5
} catch {
    if ($_.Exception.Response.StatusCode -eq 403) {
        Write-Host "  ⚠ Got 403 Forbidden - Authentication issue" -ForegroundColor Yellow
        Write-Host "  This means the API is reachable but requires authentication" -ForegroundColor Yellow
    } else {
        Write-Host "  ✗ Cannot reach pipelines API: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Step 3: Check if pipeline file exists in container
Write-Host "`n[3] Checking pipeline file in container..." -ForegroundColor Yellow
$fileCheck = docker exec pipelines test -f /app/pipelines/nexus_moa.py 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Pipeline file exists in container" -ForegroundColor Green
} else {
    Write-Host "  ✗ Pipeline file NOT found in container" -ForegroundColor Red
    Write-Host "  Copying file..." -ForegroundColor Yellow
    docker cp "D:\Github\Nexus\pipelines\nexus_moa.py" pipelines:/app/pipelines/nexus_moa.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ File copied successfully" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to copy file" -ForegroundColor Red
    }
}

# Step 4: Check pipelines logs
Write-Host "`n[4] Checking pipelines logs..." -ForegroundColor Yellow
$logs = docker logs pipelines --tail 30 2>&1
if ($logs -match "nexus_moa|Loaded module: nexus_moa") {
    Write-Host "  ✓ Pipeline is loaded in logs" -ForegroundColor Green
    $logs | Select-String -Pattern "nexus_moa|Loaded module" | Select-Object -First 3
} else {
    Write-Host "  ⚠ Pipeline not found in recent logs" -ForegroundColor Yellow
}

if ($logs -match "403|Forbidden") {
    Write-Host "  ⚠ Found 403 errors - authentication issue" -ForegroundColor Yellow
    $logs | Select-String -Pattern "403|Forbidden" | Select-Object -First 3
}

# Step 5: Try to fix by restarting with proper network
Write-Host "`n[5] Attempting to fix connection..." -ForegroundColor Yellow
Write-Host "  Creating shared network..." -ForegroundColor Cyan
docker network create open-webui-network 2>&1 | Out-Null

Write-Host "  Stopping containers..." -ForegroundColor Cyan
docker stop pipelines open-webui

Write-Host "  Removing old pipelines container..." -ForegroundColor Cyan
docker rm pipelines

Write-Host "  Starting pipelines on shared network..." -ForegroundColor Cyan
docker run -d -p 9099:9099 `
  --network open-webui-network `
  --add-host=host.docker.internal:host-gateway `
  -v "D:\Github\Nexus\pipelines:/app/pipelines" `
  --name pipelines `
  --restart always `
  ghcr.io/open-webui/pipelines:main

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Pipelines container restarted on shared network" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to restart pipelines container" -ForegroundColor Red
    exit 1
}

Write-Host "  Connecting Open WebUI to shared network..." -ForegroundColor Cyan
docker network connect open-webui-network open-webui 2>&1 | Out-Null

Write-Host "  Starting Open WebUI..." -ForegroundColor Cyan
docker start open-webui

Start-Sleep -Seconds 5

# Step 6: Final verification
Write-Host "`n[6] Final verification..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9099/models" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✓ Pipelines API is responding!" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Still getting errors: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n=== FIX COMPLETE ===" -ForegroundColor Cyan
Write-Host "`nNEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Go to Open WebUI: http://localhost:3000" -ForegroundColor White
Write-Host "2. Admin Panel → Settings → Connections" -ForegroundColor White
Write-Host "3. Edit your 'Pipelines' connection" -ForegroundColor White
Write-Host "4. Change URL to: http://pipelines:9099" -ForegroundColor White
Write-Host "   (Using container name instead of host.docker.internal)" -ForegroundColor Gray
Write-Host "5. Save and restart Open WebUI: docker restart open-webui" -ForegroundColor White
Write-Host "6. Wait 15 seconds, then check model selector for 'Nexus MoA'" -ForegroundColor White
Write-Host ""
