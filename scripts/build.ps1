# Build script for Windows using PyInstaller

# Get project root (parent of scripts/)
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "Building Multi-Modal RAG application for Windows..." -ForegroundColor Green

# Ensure hooks directory exists in scripts/
$hooksDir = Join-Path $PSScriptRoot "hooks"
if (-not (Test-Path $hooksDir)) {
    New-Item -ItemType Directory -Path $hooksDir | Out-Null
}

# Clean previous PyInstaller builds (in project root)
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

# Install/update PyInstaller
Write-Host "Ensuring PyInstaller is installed..." -ForegroundColor Yellow
uv pip install pyinstaller

# Build executable using absolute path to spec
Write-Host "Building executable..." -ForegroundColor Yellow
$specFile = Join-Path $PSScriptRoot "build.spec"
pyinstaller --clean $specFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nBuild successful!" -ForegroundColor Green
    Write-Host "Executable location: dist\MultiModalRAG.exe" -ForegroundColor Cyan
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "  1. Test: .\dist\MultiModalRAG.exe" -ForegroundColor White
    Write-Host "  2. Package: .\scripts\package.ps1" -ForegroundColor White
} else {
    Write-Host "`nBuild failed!" -ForegroundColor Red
    exit 1
}


