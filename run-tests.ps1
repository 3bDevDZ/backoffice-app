# PowerShell script to run Playwright tests on Windows
Write-Host "🚀 GMFlow Frontend E2E Tests" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js installed: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Check if npm is installed
try {
    $npmVersion = npm --version
    Write-Host "✅ npm installed: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm is not installed." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Check if Playwright is installed
if (-not (Test-Path "node_modules\@playwright")) {
    Write-Host "📦 Installing Playwright browsers..." -ForegroundColor Yellow
    npx playwright install chromium
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Playwright browsers" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🧪 Running Playwright tests..." -ForegroundColor Cyan
Write-Host ""

# Check if Flask app is running
$flaskRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000" -TimeoutSec 2 -ErrorAction SilentlyContinue
    $flaskRunning = $true
    Write-Host "✅ Flask app is running on http://localhost:5000" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Flask app might not be running. Starting it..." -ForegroundColor Yellow
    Write-Host "   Please start Flask app manually: python run.py" -ForegroundColor Yellow
    Write-Host "   Or wait for Playwright to start it automatically..." -ForegroundColor Yellow
}

Write-Host ""

# Run tests
$env:BASE_URL = if ($env:BASE_URL) { $env:BASE_URL } else { "http://localhost:5000" }
npx playwright test --reporter=html,list,json

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Tests completed successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Some tests failed. Check the report for details." -ForegroundColor Red
}

Write-Host ""
Write-Host "📊 Generating comprehensive report..." -ForegroundColor Cyan
node generate-test-report.js

Write-Host ""
Write-Host "📄 Reports generated:" -ForegroundColor Cyan
Write-Host "   - HTML Report: playwright-report\index.html" -ForegroundColor White
Write-Host "   - Markdown Report: TEST_REPORT.md" -ForegroundColor White
Write-Host ""
Write-Host "💡 View HTML report: npm run test:report" -ForegroundColor Yellow
Write-Host ""

