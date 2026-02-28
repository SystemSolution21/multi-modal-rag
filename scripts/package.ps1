# Package script for Windows

# Get project root (parent of scripts/)
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "Packaging Multi-Modal RAG application..." -ForegroundColor Green

# Create package directory
$packageDir = "MultiModalRAG-Windows-x64"
if (Test-Path $packageDir) { Remove-Item -Recurse -Force $packageDir }
New-Item -ItemType Directory -Path $packageDir | Out-Null

# Copy executable
Write-Host "Copying executable..." -ForegroundColor Yellow
Copy-Item "dist\MultiModalRAG.exe" -Destination $packageDir

# Copy .env.example and rename to .env
Write-Host "Copying configuration..." -ForegroundColor Yellow
Copy-Item ".env.example" -Destination "$packageDir\.env"

# Create directories
Write-Host "Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "$packageDir\documents" | Out-Null
New-Item -ItemType Directory -Path "$packageDir\db" | Out-Null
New-Item -ItemType Directory -Path "$packageDir\logs" | Out-Null

# Create README
@"
# Multi-Modal RAG System - Windows

## Quick Start

1. Edit the .env file with your credentials:
   - GOOGLE_CLOUD_PROJECT=your-project-id
   - GOOGLE_CLOUD_LOCATION=your-cloud-location
   - GEMINI_API_KEY=your-api-key

2. Double-click MultiModalRAG.exe to run

3. The application will create:
   - documents/ - Place your files here
   - db/ - Vector database storage
   - logs/ - Application logs

## First Run

The application automatically creates a sample document on first run.
You can load your own documents using the "Load Files" button.

## Troubleshooting

If the application doesn't start:
1. Check that .env file has valid credentials
2. Check logs/app.log for error messages
3. Run from command line to see console output:
   MultiModalRAG.exe

## Support

For issues: https://github.com/SystemSolution21/multi-modal-rag
"@ | Out-File -FilePath "$packageDir\README.txt" -Encoding UTF8

# Create ZIP
$zipFile = "$packageDir.zip"
if (Test-Path $zipFile) { Remove-Item -Force $zipFile }
Compress-Archive -Path $packageDir -DestinationPath $zipFile

Write-Host "`nPackaging complete!" -ForegroundColor Green
Write-Host "Package location: $zipFile" -ForegroundColor Cyan
Write-Host "`nContents:" -ForegroundColor Yellow
Write-Host "  - MultiModalRAG.exe" -ForegroundColor White
Write-Host "  - .env (pre-configured template)" -ForegroundColor White
Write-Host "  - documents/ (empty, ready for files)" -ForegroundColor White
Write-Host "  - db/ (empty, will store vectors)" -ForegroundColor White
Write-Host "  - logs/ (empty, will store logs)" -ForegroundColor White
Write-Host "  - README.txt" -ForegroundColor White