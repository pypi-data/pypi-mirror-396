# Java SDK Deployment Script (Windows)
# Builds and publishes to Maven Central

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Java SDK - Build & Deploy" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Clean and build
Write-Host "Building Java SDK..." -ForegroundColor Yellow
mvn clean install

# Run tests
Write-Host ""
Write-Host "Running tests..." -ForegroundColor Yellow
mvn test

# Package
Write-Host ""
Write-Host "Creating Maven artifacts..." -ForegroundColor Yellow
mvn package

# Show artifacts
Write-Host ""
Write-Host "Artifacts ready:" -ForegroundColor Green
Get-ChildItem target\*.jar | Format-Table Name, Length

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Ready to deploy!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To deploy to Maven Central:" -ForegroundColor White
Write-Host "  1. Configure settings.xml with credentials" -ForegroundColor Gray
Write-Host "  2. Run: mvn deploy" -ForegroundColor Yellow
Write-Host ""
Write-Host "To install locally:" -ForegroundColor White
Write-Host "  mvn install:install-file -Dfile=target\mle-runtime-1.0.0.jar" -ForegroundColor Yellow
Write-Host ""
Write-Host "To test locally:" -ForegroundColor White
Write-Host "  java -cp target\mle-runtime-1.0.0.jar com.mle.runtime.MLEEngine" -ForegroundColor Yellow
Write-Host ""
