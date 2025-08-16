# PowerShell Script to Remove Docker Files and Update Deployment Config
# Moves Docker files to archive and updates deployment for FastAPI
# Created: August 16, 2025

Write-Host "Removing Docker files and updating deployment config..." -ForegroundColor Green
Write-Host "Moving Docker files to archive and updating for FastAPI..." -ForegroundColor Yellow

# Get the script directory (project root)
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ProjectRoot

# Create archive subdirectories if they don't exist
$ArchiveRoot = Join-Path $ProjectRoot "archive"
$ArchiveDirs = @(
    "cleanup_2025_08_16\docker"
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

Write-Host ""
Write-Host "Moving Docker files to archive..." -ForegroundColor Cyan

# Docker files to remove/archive
$DockerFiles = @(
    "Dockerfile",
    ".dockerignore"
)

foreach ($file in $DockerFiles) {
    Move-FileToArchive $file "docker"
}

Write-Host ""
Write-Host "Docker cleanup completed!" -ForegroundColor Green
Write-Host "Docker files archived to: archive\cleanup_2025_08_16\docker\" -ForegroundColor Yellow

Write-Host ""
Write-Host "Current deployment architecture (Docker-free):" -ForegroundColor Cyan
Write-Host "  render.yaml - Render.com native Python deployment" -ForegroundColor White
Write-Host "  Procfile - Process configuration (needs FastAPI update)" -ForegroundColor White
Write-Host "  RENDER_DEPLOY.md - Render deployment documentation" -ForegroundColor White
Write-Host "  requirements.txt - Python dependencies" -ForegroundColor White
Write-Host ""
Write-Host "NOTE: render.yaml and Procfile still reference old Streamlit files." -ForegroundColor Yellow
Write-Host "You may need to update them to use FastAPI (launch_web_dashboard.py)" -ForegroundColor Yellow

Write-Host ""
Read-Host "Press Enter to exit"
