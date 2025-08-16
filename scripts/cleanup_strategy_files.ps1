# PowerShell Script to Keep Only Unified Strategy and Backtest Files
# Moves non-unified versions to archive folder
# Created: August 16, 2025

Write-Host "Cleaning up strategy and backtest files..." -ForegroundColor Green
Write-Host "Keeping only unified versions, moving others to archive..." -ForegroundColor Yellow

# Get the script directory (project root)
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ProjectRoot

# Create archive subdirectories if they don't exist
$ArchiveRoot = Join-Path $ProjectRoot "archive"
$ArchiveDirs = @(
    "cleanup_2025_08_16\strategies",
    "cleanup_2025_08_16\backtests"
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
Write-Host "Moving non-unified strategy files..." -ForegroundColor Cyan

# Strategy files to move (keep only unified)
$StrategyFiles = @(
    "strategies\ema_atr_strategy.py",
    "strategies\ema_atr_strategy_final.py",
    "strategies\ema_atr_strategy_v1_1.py",
    "strategies\ema_atr_strategy_v2.py",
    "strategies\ema_atr_strategy_v3.py",
    "strategies\ema_atr_strategy_v4.py"
)

foreach ($file in $StrategyFiles) {
    Move-FileToArchive $file "strategies"
}

Write-Host ""
Write-Host "Moving non-unified backtest files..." -ForegroundColor Cyan

# Backtest files to move (keep only unified)
$BacktestFiles = @(
    "backtests\backtest_ema_atr_strategy.py",
    "backtests\backtest_ema_atr_strategy_final.py"
)

foreach ($file in $BacktestFiles) {
    Move-FileToArchive $file "backtests"
}

Write-Host ""
Write-Host "Strategy and backtest cleanup completed!" -ForegroundColor Green
Write-Host "Files moved to: archive\cleanup_2025_08_16\" -ForegroundColor Yellow

Write-Host ""
Write-Host "Remaining strategy and backtest files:" -ForegroundColor Cyan
Write-Host "  strategies\ema_atr_strategy_unified.py - UNIFIED STRATEGY" -ForegroundColor White
Write-Host "  strategies\__init__.py - Module init file" -ForegroundColor White
Write-Host "  backtests\backtest_ema_atr_strategy_unified.py - UNIFIED BACKTEST" -ForegroundColor White

Write-Host ""
Read-Host "Press Enter to exit"
