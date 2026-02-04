# Nexus MoA Pipeline - Setup Script
# ==================================
# Run this script in PowerShell to set up the complete Nexus environment

param(
    [switch]$PullModels,
    [switch]$StartOpenWebUI,
    [switch]$CheckStatus,
    [switch]$All
)

$ErrorActionPreference = "Continue"
$ollama = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"

function Write-Status {
    param([string]$Message, [string]$Color = "Cyan")
    Write-Host "`n[$([DateTime]::Now.ToString('HH:mm:ss'))] " -NoNewline
    Write-Host $Message -ForegroundColor $Color
}

function Test-OllamaRunning {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5
        return $true
    } catch {
        return $false
    }
}

function Start-OllamaServer {
    if (-not (Test-OllamaRunning)) {
        Write-Status "Starting Ollama server..." "Yellow"
        Start-Process $ollama -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3
    }
    
    if (Test-OllamaRunning) {
        Write-Status "Ollama server is running!" "Green"
        return $true
    } else {
        Write-Status "Failed to start Ollama server" "Red"
        return $false
    }
}

function Get-ModelStatus {
    Write-Status "Checking installed models..."
    $models = & $ollama list 2>$null
    Write-Host $models
    
    $required = @("phi3", "gemma2:2b", "qwen2:1.5b", "llama3")
    $installed = @()
    $missing = @()
    
    foreach ($model in $required) {
        $modelBase = $model.Split(":")[0]
        if ($models -match $modelBase) {
            $installed += $model
        } else {
            $missing += $model
        }
    }
    
    return @{
        Installed = $installed
        Missing = $missing
    }
}

function Install-Models {
    if (-not (Start-OllamaServer)) { return }
    
    $status = Get-ModelStatus
    
    if ($status.Missing.Count -eq 0) {
        Write-Status "All required models are installed!" "Green"
        return
    }
    
    Write-Status "Models to install: $($status.Missing -join ', ')" "Yellow"
    
    foreach ($model in $status.Missing) {
        Write-Status "Pulling $model... (this may take several minutes)" "Cyan"
        & $ollama pull $model
        if ($LASTEXITCODE -eq 0) {
            Write-Status "$model installed successfully!" "Green"
        } else {
            Write-Status "Failed to install $model" "Red"
        }
    }
}

function Start-OpenWebUI {
    Write-Status "Checking Docker..."
    
    $dockerRunning = docker info 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Status "Docker is not running. Please start Docker Desktop first." "Red"
        return $false
    }
    
    Write-Status "Docker is running!" "Green"
    
    # Check if container already exists
    $existing = docker ps -a --filter name=open-webui --format "{{.Names}}"
    
    if ($existing -eq "open-webui") {
        Write-Status "Open WebUI container already exists. Starting it..." "Yellow"
        docker start open-webui
    } else {
        Write-Status "Creating and starting Open WebUI container..." "Cyan"
        docker run -d `
            -p 3000:8080 `
            --add-host=host.docker.internal:host-gateway `
            -v open-webui:/app/backend/data `
            --name open-webui `
            --restart always `
            ghcr.io/open-webui/open-webui:main
    }
    
    Write-Status "Waiting for Open WebUI to be ready..." "Yellow"
    $attempts = 0
    while ($attempts -lt 30) {
        Start-Sleep -Seconds 5
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
            Write-Status "Open WebUI is ready!" "Green"
            Write-Status "Access it at: http://localhost:3000" "Cyan"
            return $true
        } catch {
            $attempts++
            Write-Host "." -NoNewline
        }
    }
    
    Write-Status "Open WebUI did not start in time. Check docker logs open-webui" "Red"
    return $false
}

function Show-Status {
    Write-Host "`n" + "="*60 -ForegroundColor Cyan
    Write-Host "  NEXUS MOA PIPELINE - STATUS CHECK" -ForegroundColor Cyan  
    Write-Host "="*60 -ForegroundColor Cyan
    
    # Ollama Status
    Write-Host "`n[OLLAMA]" -ForegroundColor Yellow
    if (Test-Path $ollama) {
        Write-Host "  Installation: OK" -ForegroundColor Green
        $version = & $ollama --version 2>$null
        Write-Host "  Version: $version"
        
        if (Test-OllamaRunning) {
            Write-Host "  Server: Running" -ForegroundColor Green
        } else {
            Write-Host "  Server: Stopped" -ForegroundColor Red
        }
        
        $status = Get-ModelStatus
        Write-Host "  Models installed: $($status.Installed.Count)/4"
        if ($status.Missing.Count -gt 0) {
            Write-Host "  Missing: $($status.Missing -join ', ')" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  Installation: NOT FOUND" -ForegroundColor Red
    }
    
    # Docker Status
    Write-Host "`n[DOCKER]" -ForegroundColor Yellow
    $dockerInfo = docker info 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Status: Running" -ForegroundColor Green
        
        $container = docker ps --filter name=open-webui --format "{{.Status}}"
        if ($container) {
            Write-Host "  Open WebUI: $container" -ForegroundColor Green
        } else {
            $stopped = docker ps -a --filter name=open-webui --format "{{.Status}}"
            if ($stopped) {
                Write-Host "  Open WebUI: Stopped ($stopped)" -ForegroundColor Yellow
            } else {
                Write-Host "  Open WebUI: Not installed" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "  Status: Not running" -ForegroundColor Red
    }
    
    # Pipeline Status
    Write-Host "`n[PIPELINE]" -ForegroundColor Yellow
    $pipelinePath = "D:\Github\Nexus\pipelines\nexus_moa.py"
    if (Test-Path $pipelinePath) {
        Write-Host "  nexus_moa.py: OK" -ForegroundColor Green
    } else {
        Write-Host "  nexus_moa.py: NOT FOUND" -ForegroundColor Red
    }
    
    Write-Host "`n" + "="*60 -ForegroundColor Cyan
}

# Main execution
if ($CheckStatus -or (-not $PullModels -and -not $StartOpenWebUI -and -not $All)) {
    Show-Status
}

if ($PullModels -or $All) {
    Install-Models
}

if ($StartOpenWebUI -or $All) {
    Start-OpenWebUI
}

if ($All) {
    Write-Host "`n" + "="*60 -ForegroundColor Green
    Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
    Write-Host "="*60 -ForegroundColor Green
    Write-Host @"

Next steps:
1. Open http://localhost:3000 in your browser
2. Create an account (first user becomes admin)
3. Go to Admin Panel > Settings > Connections
4. Verify Ollama connection (should auto-detect)
5. Select 'Nexus MoA' pipeline for your chat

Test with this prompt:
  "Diagnose latency spike on Cluster-Alpha. 
   Network metrics show 40% packet loss on node-04."

"@ -ForegroundColor Cyan
}
