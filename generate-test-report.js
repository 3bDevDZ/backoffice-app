#!/usr/bin/env node
/**
 * Generate a comprehensive test report from Playwright results
 */
const fs = require('fs');
const path = require('path');

const reportPath = path.join(__dirname, 'playwright-report', 'results.json');
const outputPath = path.join(__dirname, 'TEST_REPORT.md');

if (!fs.existsSync(reportPath)) {
  console.error('❌ Test results not found. Please run tests first: npm test');
  process.exit(1);
}

const results = JSON.parse(fs.readFileSync(reportPath, 'utf8'));

// Calculate statistics
const totalTests = results.suites.reduce((sum, suite) => {
  return sum + suite.specs.reduce((s, spec) => s + spec.tests.length, 0);
}, 0);

const passedTests = results.suites.reduce((sum, suite) => {
  return sum + suite.specs.reduce((s, spec) => {
    return s + spec.tests.filter(t => t.results[0]?.status === 'passed').length;
  }, 0);
}, 0);

const failedTests = results.suites.reduce((sum, suite) => {
  return sum + suite.specs.reduce((s, spec) => {
    return s + spec.tests.filter(t => t.results[0]?.status === 'failed').length;
  }, 0);
}, 0);

const skippedTests = results.suites.reduce((sum, suite) => {
  return sum + suite.specs.reduce((s, spec) => {
    return s + spec.tests.filter(t => t.results[0]?.status === 'skipped').length;
  }, 0);
}, 0);

// Collect issues
const issues = [];
results.suites.forEach(suite => {
  suite.specs.forEach(spec => {
    spec.tests.forEach(test => {
      const result = test.results[0];
      if (result?.status === 'failed') {
        issues.push({
          suite: suite.title,
          spec: spec.title,
          test: test.title,
          error: result.error?.message || 'Unknown error',
          duration: result.duration,
        });
      }
    });
  });
});

// Generate markdown report
const report = `# GMFlow Frontend Test Report

**Generated:** ${new Date().toLocaleString()}

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Tests** | ${totalTests} | 100% |
| **Passed** | ${passedTests} | ${((passedTests / totalTests) * 100).toFixed(1)}% |
| **Failed** | ${failedTests} | ${((failedTests / totalTests) * 100).toFixed(1)}% |
| **Skipped** | ${skippedTests} | ${((skippedTests / totalTests) * 100).toFixed(1)}% |

## Test Coverage by Module

${results.suites.map(suite => {
  const suiteTests = suite.specs.reduce((sum, spec) => sum + spec.tests.length, 0);
  const suitePassed = suite.specs.reduce((sum, spec) => {
    return sum + spec.tests.filter(t => t.results[0]?.status === 'passed').length;
  }, 0);
  const suiteFailed = suite.specs.reduce((sum, spec) => {
    return sum + spec.tests.filter(t => t.results[0]?.status === 'failed').length;
  }, 0);
  
  return `### ${suite.title}
- **Total:** ${suiteTests} tests
- **Passed:** ${suitePassed}
- **Failed:** ${suiteFailed}
- **Success Rate:** ${((suitePassed / suiteTests) * 100).toFixed(1)}%
`;
}).join('\n')}

## Issues Found

${issues.length === 0 ? '✅ No issues found! All tests passed.' : issues.map((issue, index) => `
### Issue #${index + 1}

**Module:** ${issue.suite}  
**Test:** ${issue.spec} - ${issue.test}  
**Error:** \`${issue.error}\`  
**Duration:** ${issue.duration}ms

**Recommendation:** Review the test and fix the underlying issue in the frontend code.
`).join('\n')}

## Detailed Test Results

${results.suites.map(suite => `
### ${suite.title}

${suite.specs.map(spec => `
#### ${spec.title}

${spec.tests.map(test => {
  const result = test.results[0];
  const status = result?.status || 'unknown';
  const icon = status === 'passed' ? '✅' : status === 'failed' ? '❌' : '⏭️';
  return `${icon} **${test.title}** (${result?.duration || 0}ms)`;
}).join('\n')}
`).join('\n')}
`).join('\n')}

## Recommendations

${issues.length > 0 ? `
1. **Priority Issues:** Fix ${issues.length} failing test(s) to improve test coverage
2. **Frontend Improvements:** Review and fix the issues listed above
3. **Test Maintenance:** Update tests if UI changes are intentional
` : `
1. ✅ All tests are passing! Great job!
2. Consider adding more edge case tests
3. Monitor test execution time and optimize slow tests
`}

## Next Steps

1. Review the HTML report: \`npm run test:report\`
2. Fix failing tests
3. Re-run tests: \`npm test\`
4. Update this report after fixes

---

*Report generated automatically by Playwright test runner*
`;

fs.writeFileSync(outputPath, report);
console.log(`✅ Test report generated: ${outputPath}`);
console.log(`📊 Found ${issues.length} issue(s) to fix\n`);

