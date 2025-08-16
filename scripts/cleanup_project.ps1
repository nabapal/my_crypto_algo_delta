# PowerShell Script to Clean Up Project Directory
# Moves redundant and obsolete files to archive folder
# Created: August 16, 2025

Write-Host "🧹 Starting Project Cleanup..." -ForegroundColor Green
Write-Host "Moving redundant files to archive folder for safe cleanup..." -ForegroundColor Yellow

# Get the script directory (project root)
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ProjectRoot

# Create archive subdirectories if they don't exist
$ArchiveRoot = Join-Path $ProjectRoot "archive"
$ArchiveDirs = @(
    "cleanup_2025_08_16",
    "cleanup_2025_08_16\backtests",
    "cleanup_2025_08_16\doc",
    "cleanup_2025_08_16\debug",
    "cleanup_2025_08_16\test",
    "cleanup_2025_08_16\performance"
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
            Write-Host "✅ Moved: $SourcePath" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Failed to move: $SourcePath - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    else {
        Write-Host "⚠️  File not found: $SourcePath" -ForegroundColor Yellow
    }
}

Write-Host "`n📁 Moving redundant backtest files..." -ForegroundColor Cyan

# 1. Redundant Backtest Files
$BacktestFiles = @(
    "backtests\backtest_ema_atr_strategy_v1_test.py",
    "backtests\backtest_ema_atr_strategy_v2.py",
    "backtests\backtest_ema_atr_strategy_v3.py",
    "backtests\backtest_ema_atr_strategy_v4.py",
    "backtest_ema_atr_strategy.py",
    "backtest_ema_atr_strategy_v2.py"
)

foreach ($file in $BacktestFiles) {
    Move-FileToArchive $file "backtests"
}

Write-Host "`n📄 Moving redundant documentation versions..." -ForegroundColor Cyan

# 2. Redundant Documentation Versions
$DocFiles = @(
    "doc\EMA_ATR_Strategy_Rules_v1.md",
    "doc\EMA_ATR_Strategy_Rules_v2.md",
    "doc\EMA_ATR_Strategy_Rules_v3.md",
    "doc\EMA_ATR_Strategy_Rules_v4.md",
    "EMA_ATR_Strategy_Rules.md",
    "IMPLEMENTATION_COMPLETE.md",
    "UI_DASHBOARD_GUIDE.md"
)

foreach ($file in $DocFiles) {
    Move-FileToArchive $file "doc"
}

Write-Host "`n🐛 Moving debug and test files..." -ForegroundColor Cyan

# 3. Debug and Test Files
$DebugFiles = @(
    "debug_api.py",
    "debug_bot_detection.py",
    "debug_logs.py",
    "test_api_response.py",
    "test_bot_components.py",
    "simple_test.py",
    "check_candle_age.py",
    "check_candle_age_delta_client.py"
)

foreach ($file in $DebugFiles) {
    Move-FileToArchive $file "debug"
}

Write-Host "`n🔄 Moving duplicate/development files..." -ForegroundColor Cyan

# 4. Duplicate/Development Files
$DuplicateFiles = @(
    "data_feed_simple.py",
    "launch_dashboard.py",
    "ideal_dashboard_structure.py",
    "dashboard_data_structure.json"
)

foreach ($file in $DuplicateFiles) {
    Move-FileToArchive $file "debug"
}

Write-Host "`n📊 Moving performance comparison scripts..." -ForegroundColor Cyan

# 5. Performance Comparison Scripts
$PerformanceFiles = @(
    "compare_strategy_performance.py",
    "compare_strategy_performance_detailed.py",
    "compare_strategy_performance_fresh.py",
    "print_top10_pnl_v2.py"
)

foreach ($file in $PerformanceFiles) {
    Move-FileToArchive $file "performance"
}

Write-Host "`n🧪 Moving test directory files..." -ForegroundColor Cyan

# 6. Test Directory Files
$TestFiles = @(
    "test\debug_bot_detection.py",
    "test\test_dashboard_detection.py",
    "tests\debug_api.py",
    "tests\debug_data_feed.py",
    "tests\debug_logs.py",
    "tests\test_api_format.py",
    "tests\test_api_response.py",
    "tests\test_clean_implementation.py",
    "tests\ideal_dashboard_structure.py"
)

foreach ($file in $TestFiles) {
    Move-FileToArchive $file "test"
}

Write-Host "`n🗑️  Removing empty directories..." -ForegroundColor Cyan

# Remove empty test directories if they exist and are empty
$EmptyDirs = @("test", "tests")
foreach ($dir in $EmptyDirs) {
    $fullPath = Join-Path $ProjectRoot $dir
    if (Test-Path $fullPath) {
        $items = Get-ChildItem $fullPath -Force
        if ($items.Count -eq 0) {
            Remove-Item $fullPath -Force
            Write-Host "✅ Removed empty directory: $dir" -ForegroundColor Green
        }
        else {
            Write-Host "⚠️  Directory not empty, keeping: $dir" -ForegroundColor Yellow
        }
    }
}

Write-Host "`n✨ Project cleanup completed!" -ForegroundColor Green
Write-Host "📁 All files moved to: archive\cleanup_2025_08_16\" -ForegroundColor Yellow
Write-Host "📋 You can review and permanently delete the archive folder later if satisfied." -ForegroundColor Yellow

Write-Host "`n📈 Remaining core files in project:" -ForegroundColor Cyan
Write-Host "  ✅ config.py - Core configuration" -ForegroundColor White
Write-Host "  ✅ paper_trading_bot.py - Main trading bot" -ForegroundColor White
Write-Host "  ✅ delta_exchange_api.py - API wrapper" -ForegroundColor White
Write-Host "  ✅ data_feed.py - Data fetching" -ForegroundColor White
Write-Host "  ✅ launch_web_dashboard.py - Web interface" -ForegroundColor White
Write-Host "  ✅ tradingview_strategies/ - Pine Script files" -ForegroundColor White
Write-Host "  ✅ requirements.txt - Dependencies" -ForegroundColor White
Write-Host "  ✅ Deployment files (Dockerfile, render.yaml, etc.)" -ForegroundColor White

Read-Host "Press Enter to exit..."
