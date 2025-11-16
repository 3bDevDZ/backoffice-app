#!/usr/bin/env node
/**
 * Script to run Playwright tests and generate a comprehensive report
 */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Starting Playwright E2E Tests for GMFlow...\n');

// Ensure we're in the project root
const projectRoot = __dirname;
process.chdir(projectRoot);

// Check if node_modules exists
if (!fs.existsSync(path.join(projectRoot, 'node_modules'))) {
  console.log('📦 Installing dependencies...');
  try {
    execSync('npm install', { stdio: 'inherit' });
  } catch (error) {
    console.error('❌ Failed to install dependencies');
    process.exit(1);
  }
}

// Check if Playwright is installed
if (!fs.existsSync(path.join(projectRoot, 'node_modules', '@playwright'))) {
  console.log('📦 Installing Playwright...');
  try {
    execSync('npx playwright install chromium', { stdio: 'inherit' });
  } catch (error) {
    console.error('❌ Failed to install Playwright browsers');
    process.exit(1);
  }
}

// Run tests
console.log('🧪 Running Playwright tests...\n');
try {
  execSync('npx playwright test --reporter=html,list,json', { 
    stdio: 'inherit',
    env: { ...process.env, BASE_URL: process.env.BASE_URL || 'http://localhost:5000' }
  });
  
  console.log('\n✅ Tests completed!');
  console.log('\n📊 View HTML report: npm run test:report');
  console.log('📄 JSON results: playwright-report/results.json\n');
  
} catch (error) {
  console.error('\n❌ Some tests failed. Check the report for details.');
  console.log('📊 View HTML report: npm run test:report\n');
  process.exit(1);
}

