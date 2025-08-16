# Git-Aware Cleanup Script Template
# Uses git mv to preserve file history when moving files
# Created: August 16, 2025

Write-Host "Git-Aware File Cleanup Script" -ForegroundColor Green
Write-Host "This script preserves Git history when moving files" -ForegroundColor Yellow

# Get the script directory (project root)
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Definition)
Set-Location $ProjectRoot

# Function to safely move files with Git tracking
function Move-FileWithGit {
    param(
        [string]$SourcePath,
        [string]$DestinationPath
    )
    
    if (Test-Path $SourcePath) {
        # Create destination directory if it doesn't exist
        $destDir = Split-Path $DestinationPath -Parent
        if (!(Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            Write-Host "Created directory: $destDir" -ForegroundColor Blue
        }
        
        try {
            # Use git mv to preserve history
            git mv $SourcePath $DestinationPath
            Write-Host "GIT MOVED: $SourcePath -> $DestinationPath" -ForegroundColor Green
        }
        catch {
            Write-Host "FAILED to git mv: $SourcePath - $($_.Exception.Message)" -ForegroundColor Red
            # Fallback to regular move if git mv fails
            try {
                Move-Item -Path $SourcePath -Destination $DestinationPath -Force
                Write-Host "FALLBACK MOVED: $SourcePath" -ForegroundColor Yellow
            }
            catch {
                Write-Host "FALLBACK FAILED: $SourcePath - $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
    else {
        Write-Host "File not found: $SourcePath" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "EXAMPLE USAGE:" -ForegroundColor Cyan
Write-Host "# Move old strategy file to archive with Git history preserved"
Write-Host "Move-FileWithGit 'strategies\old_strategy.py' 'archive\cleanup_2025_08_16\strategies\old_strategy.py'"
Write-Host ""
Write-Host "This is a template script. Modify the Move-FileWithGit calls below for your specific cleanup needs."

# Example cleanup operations (uncomment and modify as needed)
# Move-FileWithGit "old_file.py" "archive\cleanup_2025_08_16\old_file.py"

Write-Host ""
Write-Host "Template script completed. No files were moved." -ForegroundColor Green
Write-Host "Modify this script with your specific Move-FileWithGit calls and run again." -ForegroundColor Yellow

Read-Host "Press Enter to exit"
