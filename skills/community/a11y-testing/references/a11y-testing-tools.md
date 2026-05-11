# Accessibility Testing Tools Reference

Comprehensive guide to automated and manual accessibility testing tools.

## jest-axe Configuration

### Installation

```bash
npm install --save-dev jest-axe @testing-library/react @testing-library/jest-dom
```

### Setup

```typescript
// test-utils/axe.ts
import { configureAxe } from "jest-axe";

export const axe = configureAxe({
  rules: {
    // Disable rules if needed (use sparingly)
    "color-contrast": { enabled: false }, // Only if manual testing covers this
  },
  reporter: "v2",
});
```

```typescript
// vitest.setup.ts or jest.setup.ts
import { toHaveNoViolations } from "jest-axe";
expect.extend(toHaveNoViolations);
```

### Basic Usage

```typescript
import { render } from '@testing-library/react';
import { axe } from './test-utils/axe';

test('Button has no accessibility violations', async () => {
  const { container } = render(<Button>Click me</Button>);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

### Component-Specific Rules

```typescript
// Test form with specific WCAG level
test('Form meets WCAG 2.1 Level AA', async () => {
  const { container } = render(<ContactForm />);
  const results = await axe(container, {
    runOnly: {
      type: 'tag',
      values: ['wcag2a', 'wcag2aa', 'wcag21aa'],
    },
  });
  expect(results).toHaveNoViolations();
});
```

### Testing Specific Rules

```typescript
// Test only keyboard navigation
test('Modal is keyboard accessible', async () => {
  const { container } = render(<Modal isOpen />);
  const results = await axe(container, {
    runOnly: ['keyboard', 'focus-order-semantics'],
  });
  expect(results).toHaveNoViolations();
});
```

## Playwright + axe-core

### Installation

```bash
npm install --save-dev @axe-core/playwright
```

### Setup

```typescript
// tests/a11y.setup.ts
import { test as base } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

export const test = base.extend<{ makeAxeBuilder: () => AxeBuilder }>({
  makeAxeBuilder: async ({ page }, use) => {
    const makeAxeBuilder = () =>
      new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .exclude("#third-party-widget");
    await use(makeAxeBuilder);
  },
});

export { expect } from "@playwright/test";
```

### E2E Accessibility Test

```typescript
import { test, expect } from "./a11y.setup";

test("homepage is accessible", async ({ page, makeAxeBuilder }) => {
  await page.goto("/");

  const accessibilityScanResults = await makeAxeBuilder().analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
});
```

### Testing After Interactions

```typescript
test("modal maintains accessibility after opening", async ({ page, makeAxeBuilder }) => {
  await page.goto("/dashboard");

  // Initial state
  const initialScan = await makeAxeBuilder().analyze();
  expect(initialScan.violations).toEqual([]);

  // After opening modal
  await page.getByRole("button", { name: "Open Settings" }).click();
  const modalScan = await makeAxeBuilder().analyze();
  expect(modalScan.violations).toEqual([]);

  // Focus should be trapped in modal
  await page.keyboard.press("Tab");
  const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
  expect(focusedElement).not.toBe("BODY");
});
```

### Excluding Regions

```typescript
test("scan page excluding third-party widgets", async ({ page, makeAxeBuilder }) => {
  await page.goto("/");

  const results = await makeAxeBuilder()
    .exclude("#ads-container")
    .exclude("[data-third-party]")
    .analyze();

  expect(results.violations).toEqual([]);
});
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/a11y.yml
name: Accessibility Tests

on: [push, pull_request]

jobs:
  a11y:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run unit accessibility tests
        run: npm run test:a11y

      - name: Install Playwright
        run: npx playwright install --with-deps chromium

      - name: Build application
        run: npm run build

      - name: Start server
        run: npm run start &
        env:
          PORT: 3000

      - name: Wait for server
        run: npx wait-on http://localhost:3000

      - name: Run E2E accessibility tests
        run: npx playwright test tests/a11y/

      - name: Upload accessibility report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: a11y-report
          path: playwright-report/
          retention-days: 30
```

### Pre-commit Hook

```bash
#!/bin/sh
# .husky/pre-commit

# Run accessibility tests on staged components
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep "\.tsx\?$")

if [ -n "$STAGED_FILES" ]; then
  echo "Running accessibility tests on changed components..."
  npm run test:a11y -- --findRelatedTests $STAGED_FILES
  if [ $? -ne 0 ]; then
    echo "❌ Accessibility tests failed. Please fix violations before committing."
    exit 1
  fi
fi
```

### Package.json Scripts

```json
{
  "scripts": {
    "test:a11y": "vitest run tests/**/*.a11y.test.{ts,tsx}",
    "test:a11y:watch": "vitest watch tests/**/*.a11y.test.{ts,tsx}",
    "test:a11y:e2e": "playwright test tests/a11y/",
    "test:a11y:all": "npm run test:a11y && npm run test:a11y:e2e"
  }
}
```

## Manual Testing Checklist

Use this alongside automated tests for comprehensive coverage.

### Keyboard Navigation

1. **Tab Order**
   - Navigate entire page using only Tab/Shift+Tab
   - Verify logical focus order
   - Ensure all interactive elements are reachable
   - Check focus is visible (outline or custom indicator)

2. **Interactive Elements**
   - Enter/Space activates buttons and links
   - Arrow keys navigate within widgets (tabs, menus, sliders)
   - Escape closes modals and dropdowns
   - Home/End navigate to start/end of lists

3. **Form Controls**
   - All form fields reachable via keyboard
   - Labels associated with inputs
   - Error messages announced and keyboard-accessible
   - Submit works via Enter key

### Screen Reader Testing

**Tools:**

- **macOS:** VoiceOver (Cmd+F5)
- **Windows:** NVDA (free) or JAWS
- **Linux:** Orca

**Test Scenarios:**

1. Navigate by headings (H key in screen reader)
2. Navigate by landmarks (D key in screen reader)
3. Form fields announce label and type
4. Buttons announce role and state (expanded/collapsed)
5. Dynamic content changes are announced (aria-live)
6. Images have meaningful alt text or aria-label

### Color Contrast

**Tools:**

- **Browser Extensions:** axe DevTools, WAVE
- **Design Tools:** Figma has built-in contrast checker
- **Command Line:** `pa11y` or `axe-cli`

**Requirements:**

- Normal text: 4.5:1 contrast ratio (WCAG AA)
- Large text (18pt+): 3:1 contrast ratio
- UI components: 3:1 contrast ratio

### Responsive and Zoom Testing

1. **Browser Zoom**
   - Test at 200% zoom (WCAG 2.1 requirement)
   - Verify no horizontal scrolling
   - Content remains readable
   - No overlapping elements

2. **Mobile Testing**
   - Touch targets at least 44×44px
   - No reliance on hover states
   - Swipe gestures have keyboard alternative
   - Pinch-to-zoom enabled

## Continuous Monitoring

### Lighthouse CI

```yaml
# lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000', 'http://localhost:3000/dashboard'],
      numberOfRuns: 3,
    },
    assert: {
      preset: 'lighthouse:recommended',
      assertions: {
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'categories:best-practices': ['warn', { minScore: 0.9 }],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
```

### axe-cli for Quick Scans

```bash
# Install
npm install -g @axe-core/cli

# Scan a URL
axe http://localhost:3000 --tags wcag2a,wcag2aa

# Save results
axe http://localhost:3000 --save results.json

# Check multiple pages
axe http://localhost:3000 \
    http://localhost:3000/dashboard \
    http://localhost:3000/profile \
    --tags wcag21aa
```

## Common Pitfalls

1. **Automated Testing Limitations**
   - Only catches ~30-40% of issues
   - Cannot verify semantic meaning
   - Cannot test keyboard navigation fully
   - Manual testing is REQUIRED

2. **False Sense of Security**
   - Passing axe tests ≠ fully accessible
   - Must combine automated + manual testing
   - Screen reader testing is essential

3. **Ignoring Dynamic Content**
   - Test ARIA live regions with actual updates
   - Verify focus management after route changes
   - Test loading and error states

4. **Third-Party Components**
   - UI libraries may have a11y issues
   - Always test integrated components
   - Don't assume "accessible by default"

## Resources

- **WCAG 2.1 Guidelines:** https://www.w3.org/WAI/WCAG21/quickref/
- **axe Rules:** https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md
- **WebAIM:** https://webaim.org/articles/
- **A11y Project Checklist:** https://www.a11yproject.com/checklist/
