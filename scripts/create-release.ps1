# Create and push a release tag

param(
    [Parameter(Mandatory=$true)]
    [string]$Version  # e.g., "1.0.0"
)

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "Creating release v$Version..." -ForegroundColor Green

# Ensure we're on main branch
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    Write-Host "⚠ Warning: Not on main branch (currently on $currentBranch)" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") { exit 0 }
}

# Check for uncommitted changes
$status = git status --porcelain
if ($status) {
    Write-Host "✗ You have uncommitted changes:" -ForegroundColor Red
    git status --short
    Write-Host "`nCommit or stash changes first!" -ForegroundColor Yellow
    exit 1
}

# Create and push tag
Write-Host "`nCreating tag v$Version..." -ForegroundColor Yellow
git tag -a "v$Version" -m "Release version $Version"

Write-Host "Pushing tag to GitHub..." -ForegroundColor Yellow
git push origin "v$Version"

Write-Host "`n✓ Release tag created and pushed!" -ForegroundColor Green
Write-Host "`nGitHub Actions will now:" -ForegroundColor Cyan
Write-Host "  1. Build executables for Windows, macOS, Linux"
Write-Host "  2. Build Docker images"
Write-Host "  3. Create GitHub Release with all files"
Write-Host "`nCheck progress at:" -ForegroundColor Yellow
Write-Host "  https://github.com/SystemSolution21/multi-modal-rag/actions"
Write-Host "`nRelease will be available at:" -ForegroundColor Yellow
Write-Host "  https://github.com/SystemSolution21/multi-modal-rag/releases/tag/v$Version"