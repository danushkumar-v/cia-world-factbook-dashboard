# Global Insights Explorer - Quick Start Script
# This script sets up and runs the application

Write-Host "🌍 Global Insights Explorer - Setup & Launch" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "✓ Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found! Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}
Write-Host "  Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "  Virtual environment created!" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "  Virtual environment activated!" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes on first run..." -ForegroundColor Gray
pip install -q -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "  All dependencies installed!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Create .env if not exists
if (-not (Test-Path ".env")) {
    Write-Host "⚙️  Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "  Configuration file created!" -ForegroundColor Green
    Write-Host ""
}

# Display info
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "🚀 Starting Global Insights Explorer..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Application Details:" -ForegroundColor Yellow
Write-Host "  • URL: http://localhost:8050" -ForegroundColor White
Write-Host "  • Mode: Development" -ForegroundColor White
Write-Host "  • Data: 259 countries, 7 domains" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "  • Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host "  • Open http://localhost:8050 in your browser" -ForegroundColor Gray
Write-Host "  • Check README.md for usage examples" -ForegroundColor Gray
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Run the application
python app.py
