# Nexus Pipeline Troubleshooting Script
# This script diagnoses and fixes pipeline connection issues

Write-Host "`n=== NEXUS PIPELINE TROUBLESHOOTING ===" -ForegroundColor Cyan
Write-Host ""

# 1. Check if containers are running
Write-Host "[1] Checking Docker containers..." -ForegroundColor Yellow
$openWebUI = docker ps --filter "name=open-webui" --format "{{.Names}}"
$pipelines = docker ps --filter "name=pipelines" --format "{{.Names}}"

if ($openWebUI -eq "open-webui") {
    Write-Host "  ✓ Open WebUI container is running" -ForegroundColor Green
} else {
    Write-Host "  ✗ Open WebUI container is NOT running" -ForegroundColor Red
    exit 1
}

if ($pipelines -eq "pipelines") {
    Write-Host "  ✓ Pipelines container is running" -ForegroundColor Green
} else {
    Write-Host "  ✗ Pipelines container is NOT running" -ForegroundColor Red
    Write-Host "  Starting pipelines container..." -ForegroundColor Yellow
    docker run -d -p 9099:9099 `
        --add-host=host.docker.internal:host-gateway `
        -v "${PWD}\pipelines:/app/pipelines" `
        --name pipelines `
        --restart always `
        ghcr.io/open-webui/pipelines:main
    Start-Sleep -Seconds 5
}

# 2. Check pipeline file exists
Write-Host "`n[2] Checking pipeline file..." -ForegroundColor Yellow
$pipelinePath = "D:\Github\Nexus\pipelines\nexus_moa.py"
if (Test-Path $pipelinePath) {
    $fileSize = (Get-Item $pipelinePath).Length
    Write-Host "  ✓ Pipeline file exists: $pipelinePath" -ForegroundColor Green
    Write-Host "  ✓ File size: $fileSize bytes" -ForegroundColor Green
} else {
    Write-Host "  ✗ Pipeline file NOT FOUND at: $pipelinePath" -ForegroundColor Red
    exit 1
}

# 3. Check if pipeline is accessible in container
Write-Host "`n[3] Checking pipeline accessibility in container..." -ForegroundColor Yellow
$containerCheck = docker exec pipelines test -f /app/pipelines/nexus_moa.py 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Pipeline file is accessible in container" -ForegroundColor Green
} else {
    Write-Host "  ✗ Pipeline file NOT accessible in container" -ForegroundColor Red
    Write-Host "  Attempting to copy file into container..." -ForegroundColor Yellow
    
    # Try to copy the file
    docker cp $pipelinePath pipelines:/app/pipelines/nexus_moa.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ File copied successfully" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to copy file. Check volume mount." -ForegroundColor Red
        Write-Host "  Current working directory: $PWD" -ForegroundColor Yellow
        Write-Host "  Pipeline path: $pipelinePath" -ForegroundColor Yellow
    }
}

# 4. Check pipelines container logs for errors
Write-Host "`n[4] Checking pipelines container logs..." -ForegroundColor Yellow
$logs = docker logs pipelines --tail 30 2>&1
if ($logs -match "nexus|Nexus|error|Error|ERROR|exception|Exception") {
    Write-Host "  ⚠ Found potential issues in logs:" -ForegroundColor Yellow
    $logs | Select-String -Pattern "nexus|Nexus|error|Error|ERROR|exception|Exception" | ForEach-Object {
        Write-Host "    $_" -ForegroundColor Red
    }
} else {
    Write-Host "  ✓ No obvious errors in logs" -ForegroundColor Green
}

# 5. Check if pipelines API is responding
Write-Host "`n[5] Testing pipelines API..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9099/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✓ Pipelines API is responding (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Pipelines API not responding: $_" -ForegroundColor Red
}

# 6. Instructions for Open WebUI connection
Write-Host "`n[6] Open WebUI Connection Instructions:" -ForegroundColor Yellow
Write-Host "  To connect Open WebUI to the pipelines container:" -ForegroundColor Cyan
Write-Host "  1. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "  2. Log in as admin" -ForegroundColor White
Write-Host "  3. Go to: Admin Panel → Settings → Connections" -ForegroundColor White
Write-Host "  4. Add new connection:" -ForegroundColor White
Write-Host "     - Name: Pipelines" -ForegroundColor White
Write-Host "     - URL: http://pipelines:9099" -ForegroundColor White
Write-Host "     OR if that doesn't work:" -ForegroundColor Yellow
Write-Host "     - URL: http://host.docker.internal:9099" -ForegroundColor White
Write-Host "  5. Save and restart Open WebUI container" -ForegroundColor White

# 7. Restart containers to reload pipeline
Write-Host "`n[7] Restarting containers to reload pipeline..." -ForegroundColor Yellow
docker restart pipelines
Start-Sleep -Seconds 3
docker restart open-webui
Write-Host "  ✓ Containers restarted" -ForegroundColor Green

Write-Host "`n=== TROUBLESHOOTING COMPLETE ===" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Wait 10-15 seconds for containers to fully start" -ForegroundColor White
Write-Host "2. Check Open WebUI Admin Panel → Settings → Pipelines" -ForegroundColor White
Write-Host "3. Look for 'Nexus MoA' in the pipeline list" -ForegroundColor White
Write-Host "4. If it appears, select it as your model in a new chat" -ForegroundColor White
Write-Host ""
