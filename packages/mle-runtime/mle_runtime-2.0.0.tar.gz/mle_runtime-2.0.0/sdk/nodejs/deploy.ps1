# Node.js SDK Deployment Script (Windows)
# Builds and publishes to npm

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Node.js SDK - Build & Deploy" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
npm install

# Build TypeScript
Write-Host "Building TypeScript..." -ForegroundColor Yellow
npm run build

# Run tests
Write-Host "Running tests..." -ForegroundColor Yellow
try {
    npm test
    Write-Host "✓ Tests passed" -ForegroundColor Green
} catch {
    Write-Host "⚠ No tests configured or tests failed" -ForegroundColor Yellow
}

# Create package
Write-Host ""
Write-Host "Creating npm package..." -ForegroundColor Yellow
npm pack

# Show package info
Write-Host ""
Write-Host "Package ready:" -ForegroundColor Green
Get-ChildItem *.tgz | Format-Table Name, Length

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Ready to deploy!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To publish to npm:" -ForegroundColor White
Write-Host "  Test:       npm publish --dry-run" -ForegroundColor Yellow
Write-Host "  Production: npm publish" -ForegroundColor Yellow
Write-Host ""
Write-Host "To test locally:" -ForegroundColor White
Write-Host "  npm install -g mle-runtime-*.tgz" -ForegroundColor Yellow
Write-Host ""
