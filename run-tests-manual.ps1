# PowerShell script to run Playwright tests (server must be running manually)
Write-Host "🚀 GMFlow Frontend E2E Tests" -ForegroundColor Cyan
Write-Host ""

# Check if Flask server is running
Write-Host "Checking if Flask server is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "✅ Flask server is running on http://localhost:5000" -ForegroundColor Green
} catch {
    Write-Host "❌ Flask server is not running!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start the Flask server first:" -ForegroundColor Yellow
    Write-Host "   python run.py" -ForegroundColor White
    Write-Host ""
    Write-Host "Then run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed." -ForegroundColor Red
    exit 1
}

# Check if dependencies are installed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Run tests
Write-Host ""
Write-Host "🧪 Running Playwright tests..." -ForegroundColor Cyan
Write-Host ""

$env:BASE_URL = "http://localhost:5000"
npx playwright test --reporter=html,list,json

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Tests completed successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️  Some tests failed. Check the report for details." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📊 Generating comprehensive report..." -ForegroundColor Cyan
node generate-test-report.js

Write-Host ""
Write-Host "📄 Reports:" -ForegroundColor Cyan
Write-Host "   - HTML: playwright-report\index.html" -ForegroundColor White
Write-Host "   - Markdown: TEST_REPORT.md" -ForegroundColor White
Write-Host ""
Write-Host "💡 View HTML report: npm run test:report" -ForegroundColor Yellow
Write-Host ""


