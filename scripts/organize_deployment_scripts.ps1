# PowerShell Script to Remove Fly.io Files and Organize Scripts
# Removes Fly deployment files and moves all scripts to scripts folder
# Created: August 16, 2025

Write-Host "Removing Fly.io files and organizing scripts..." -ForegroundColor Green
Write-Host "Moving deployment scripts to organized structure..." -ForegroundColor Yellow

# Get the script directory (project root)
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ProjectRoot

# Create scripts directory if it doesn't exist
$ScriptsDir = Join-Path $ProjectRoot "scripts"
if (!(Test-Path $ScriptsDir)) {
    New-Item -ItemType Directory -Path $ScriptsDir -Force | Out-Null
    Write-Host "Created scripts directory" -ForegroundColor Blue
}

# Create archive subdirectories if they don't exist
$ArchiveRoot = Join-Path $ProjectRoot "archive"
$ArchiveDirs = @(
    "cleanup_2025_08_16\fly_deployment"
)

foreach ($dir in $ArchiveDirs) {
    $fullPath = Join-Path $ArchiveRoot $dir
    if (!(Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "Created archive directory: $dir" -ForegroundColor Blue
    }
}

# Function to safely move files to archive
function Move-FileToArchive {
    param(
        [string]$SourcePath,
        [string]$DestinationSubfolder
    )
    
    $fullSourcePath = Join-Path $ProjectRoot $SourcePath
    if (Test-Path $fullSourcePath) {
        $destPath = Join-Path $ArchiveRoot "cleanup_2025_08_16\$DestinationSubfolder"
        $fileName = Split-Path $SourcePath -Leaf
        $fullDestPath = Join-Path $destPath $fileName
        
        try {
            Move-Item -Path $fullSourcePath -Destination $fullDestPath -Force
            Write-Host "MOVED TO ARCHIVE: $SourcePath" -ForegroundColor Red
        }
        catch {
            Write-Host "FAILED to archive: $SourcePath - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    else {
        Write-Host "File not found: $SourcePath" -ForegroundColor Yellow
    }
}

# Function to safely move files to scripts directory
function Move-FileToScripts {
    param(
        [string]$SourcePath
    )
    
    $fullSourcePath = Join-Path $ProjectRoot $SourcePath
    if (Test-Path $fullSourcePath) {
        $fileName = Split-Path $SourcePath -Leaf
        $fullDestPath = Join-Path $ScriptsDir $fileName
        
        try {
            Move-Item -Path $fullSourcePath -Destination $fullDestPath -Force
            Write-Host "MOVED TO SCRIPTS: $SourcePath" -ForegroundColor Green
        }
        catch {
            Write-Host "FAILED to move to scripts: $SourcePath - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    else {
        Write-Host "File not found: $SourcePath" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Removing Fly.io deployment files..." -ForegroundColor Cyan

# Fly.io files to remove/archive
$FlyFiles = @(
    "fly.toml",
    "fly-free-tier.toml",
    "FREE_TIER_DEPLOY.md"
)

foreach ($file in $FlyFiles) {
    Move-FileToArchive $file "fly_deployment"
}

Write-Host ""
Write-Host "Moving cleanup scripts to scripts folder..." -ForegroundColor Cyan

# Cleanup scripts to move to scripts folder
$CleanupScripts = @(
    "cleanup_project.ps1",
    "cleanup_project_fixed.ps1",
    "cleanup_strategy_files.ps1",
    "cleanup_ui_files.ps1"
)

foreach ($script in $CleanupScripts) {
    Move-FileToScripts $script
}

Write-Host ""
Write-Host "Moving other utility scripts to scripts folder..." -ForegroundColor Cyan

# Other utility scripts
$UtilityScripts = @(
    "render-start.sh",
    "start.sh",
    "start_dashboard.bat"
)

foreach ($script in $UtilityScripts) {
    Move-FileToScripts $script
}

Write-Host ""
Write-Host "Script organization completed!" -ForegroundColor Green
Write-Host "Fly.io files archived to: archive\cleanup_2025_08_16\fly_deployment\" -ForegroundColor Yellow
Write-Host "All scripts moved to: scripts\" -ForegroundColor Yellow

Write-Host ""
Write-Host "Current deployment architecture:" -ForegroundColor Cyan
Write-Host "  render.yaml - Active Render.com deployment config" -ForegroundColor White
Write-Host "  Dockerfile - Docker container configuration" -ForegroundColor White
Write-Host "  Procfile - Process configuration" -ForegroundColor White
Write-Host "  RENDER_DEPLOY.md - Render deployment documentation" -ForegroundColor White
Write-Host ""
Write-Host "Scripts organized in:" -ForegroundColor Cyan
Write-Host "  scripts/ - All utility and cleanup scripts" -ForegroundColor White
Write-Host "  archive/cleanup_2025_08_16/fly_deployment/ - Removed Fly.io files" -ForegroundColor White

Write-Host ""
Read-Host "Press Enter to exit"
