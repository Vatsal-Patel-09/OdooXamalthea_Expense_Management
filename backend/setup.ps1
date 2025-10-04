# Setup script for Windows PowerShell
# This script sets up the Python virtual environment and installs dependencies

Write-Host "🚀 Setting up Expense Management Backend..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists, skipping..." -ForegroundColor Yellow
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Virtual environment created successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✅ Pip upgraded" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check if .env exists
if (Test-Path ".env") {
    Write-Host "✅ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created" -ForegroundColor Green
    Write-Host "⚠️  Please edit .env file with your configuration" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "✨ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your Supabase credentials" -ForegroundColor White
Write-Host "2. Run: python app.py" -ForegroundColor White
Write-Host ""
Write-Host "Happy coding! 🎉" -ForegroundColor Cyan
