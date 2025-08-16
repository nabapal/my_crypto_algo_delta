# PowerShell Script to Archive Old Streamlit UI Files
# Moves all Streamlit UI files to archive since project moved to FastAPI
# Created: August 16, 2025

Write-Host "Archiving old Streamlit UI files..." -ForegroundColor Green
Write-Host "Project has moved to FastAPI, cleaning up old Streamlit implementations..." -ForegroundColor Yellow

# Get the script directory (project root)
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ProjectRoot

# Create archive subdirectories if they don't exist
$ArchiveRoot = Join-Path $ProjectRoot "archive"
$ArchiveDirs = @(
    "cleanup_2025_08_16\ui"
)

foreach ($dir in $ArchiveDirs) {
    $fullPath = Join-Path $ArchiveRoot $dir
    if (!(Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "Created archive directory: $dir" -ForegroundColor Blue
    }
}

# Function to safely move files
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
            Write-Host "MOVED: $SourcePath" -ForegroundColor Green
        }
        catch {
            Write-Host "FAILED to move: $SourcePath - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    else {
        Write-Host "File not found: $SourcePath" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Moving all Streamlit UI files to archive..." -ForegroundColor Cyan

# All Streamlit UI files to move
$StreamlitUIFiles = @(
    "ui\bot_monitor.py",
    "ui\config_manager.py",
    "ui\fresh_dashboard.py",
    "ui\fresh_dashboard_fixed.py",
    "ui\simple_dashboard.py",
    "ui\trading_dashboard.py",
    "ui\requirements_ui.txt"
)

foreach ($file in $StreamlitUIFiles) {
    Move-FileToArchive $file "ui"
}

Write-Host ""
Write-Host "Checking if ui directory is empty..." -ForegroundColor Cyan

# Check if ui directory is empty and remove it
$uiDir = Join-Path $ProjectRoot "ui"
if (Test-Path $uiDir) {
    $items = Get-ChildItem $uiDir -Force
    if ($items.Count -eq 0) {
        Remove-Item $uiDir -Force
        Write-Host "REMOVED empty ui directory" -ForegroundColor Green
    }
    else {
        Write-Host "ui directory not empty, keeping it:" -ForegroundColor Yellow
        foreach ($item in $items) {
            Write-Host "  - $($item.Name)" -ForegroundColor White
        }
    }
}

Write-Host ""
Write-Host "Streamlit UI cleanup completed!" -ForegroundColor Green
Write-Host "All old Streamlit files moved to: archive\cleanup_2025_08_16\ui\" -ForegroundColor Yellow

Write-Host ""
Write-Host "Current web architecture:" -ForegroundColor Cyan
Write-Host "  web_dashboard/ - ACTIVE FastAPI web interface" -ForegroundColor White
Write-Host "  launch_web_dashboard.py - FastAPI launcher" -ForegroundColor White
Write-Host "  archive\cleanup_2025_08_16\ui\ - Old Streamlit implementations" -ForegroundColor White

Write-Host ""
Read-Host "Press Enter to exit"
