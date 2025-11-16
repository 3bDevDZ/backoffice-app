# PowerShell script to start Flask server and run Playwright tests
Write-Host "GMFlow Frontend E2E Tests (with auto-start server)" -ForegroundColor Cyan
Write-Host ""

# Check if server is already running
$serverRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "Flask server is already running" -ForegroundColor Green
    $serverRunning = $true
} catch {
    Write-Host "Starting Flask server..." -ForegroundColor Yellow
    $serverRunning = $false
    
    # Start Flask server in background
    $serverJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        python run.py 2>&1
    }
    
    # Wait for server to be ready
    $maxWait = 30
    $waited = 0
    while ($waited -lt $maxWait) {
        Start-Sleep -Seconds 2
        $waited += 2
        try {
            $testResponse = Invoke-WebRequest -Uri "http://localhost:5000" -TimeoutSec 1 -ErrorAction Stop
            Write-Host "Flask server is ready!" -ForegroundColor Green
            $serverRunning = $true
            break
        } catch {
            Write-Host "Waiting for server... ($waited/$maxWait)" -ForegroundColor Gray
        }
    }
    
    if (-not $serverRunning) {
        Write-Host "Server failed to start within $maxWait seconds" -ForegroundColor Red
        Stop-Job $serverJob -ErrorAction SilentlyContinue
        Remove-Job $serverJob -ErrorAction SilentlyContinue
        exit 1
    }
}

Write-Host ""

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js is not installed." -ForegroundColor Red
    if (-not $serverRunning) {
        Stop-Job $serverJob -ErrorAction SilentlyContinue
        Remove-Job $serverJob -ErrorAction SilentlyContinue
    }
    exit 1
}

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
    npm install --silent
}

Write-Host ""
Write-Host "Running Playwright tests..." -ForegroundColor Cyan
Write-Host ""

# Run tests
$env:BASE_URL = "http://localhost:5000"
$testResult = $false

try {
    npx playwright test --reporter=html,list,json
    if ($LASTEXITCODE -eq 0) {
        $testResult = $true
    }
} catch {
    Write-Host "Error running tests: $_" -ForegroundColor Red
}

Write-Host ""

# Generate report
Write-Host "Generating comprehensive report..." -ForegroundColor Cyan
node generate-test-report.js

Write-Host ""
if ($testResult) {
    Write-Host "Tests completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Some tests failed. Check the report for details." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Reports:" -ForegroundColor Cyan
Write-Host "   - HTML: playwright-report\index.html" -ForegroundColor White
Write-Host "   - Markdown: TEST_REPORT.md" -ForegroundColor White
Write-Host ""
Write-Host "View HTML report: npm run test:report" -ForegroundColor Yellow

# Cleanup: Stop server if we started it
if (-not $serverRunning) {
    Write-Host ""
    Write-Host "Stopping Flask server..." -ForegroundColor Yellow
    Stop-Job $serverJob -ErrorAction SilentlyContinue
    Remove-Job $serverJob -ErrorAction SilentlyContinue
    Write-Host "Server stopped" -ForegroundColor Green
}

Write-Host ""
