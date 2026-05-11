# Accessibility Testing Examples

Complete code examples for automated accessibility testing.

## jest-axe Component Tests

### Basic Button Test

```typescript
// src/components/Button.test.tsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button } from './Button';

expect.extend(toHaveNoViolations);

describe('Button Accessibility', () => {
  test('has no accessibility violations', async () => {
    const { container } = render(<Button>Click me</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('disabled button is accessible', async () => {
    const { container } = render(<Button disabled>Cannot click</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('icon-only button has accessible name', async () => {
    const { container } = render(
      <Button aria-label="Close dialog">
        <XIcon />
      </Button>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### Form Component Test

```typescript
// src/components/LoginForm.test.tsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { LoginForm } from './LoginForm';

expect.extend(toHaveNoViolations);

describe('LoginForm Accessibility', () => {
  test('form has no accessibility violations', async () => {
    const { container } = render(<LoginForm />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('form with errors is accessible', async () => {
    const { container } = render(
      <LoginForm
        errors={{
          email: 'Invalid email address',
          password: 'Password is required',
        }}
      />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('form with loading state is accessible', async () => {
    const { container } = render(<LoginForm isLoading />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('meets WCAG 2.1 Level AA', async () => {
    const { container } = render(<LoginForm />);
    const results = await axe(container, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa', 'wcag21aa'],
      },
    });
    expect(results).toHaveNoViolations();
  });
});
```

### Modal Component Test

```typescript
// src/components/Modal.test.tsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Modal } from './Modal';

expect.extend(toHaveNoViolations);

describe('Modal Accessibility', () => {
  test('open modal has no violations', async () => {
    const { container } = render(
      <Modal isOpen onClose={() => {}}>
        <h2>Modal Title</h2>
        <p>Modal content</p>
      </Modal>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('modal has proper ARIA attributes', async () => {
    const { container } = render(
      <Modal isOpen onClose={() => {}} ariaLabel="Settings">
        <p>Settings content</p>
      </Modal>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('modal with complex content is accessible', async () => {
    const { container } = render(
      <Modal isOpen onClose={() => {}}>
        <h2>Complex Modal</h2>
        <form>
          <label htmlFor="name">Name</label>
          <input id="name" type="text" />
          <button type="submit">Save</button>
        </form>
      </Modal>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### Custom Dropdown Test

```typescript
// src/components/Dropdown.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Dropdown } from './Dropdown';

expect.extend(toHaveNoViolations);

describe('Dropdown Accessibility', () => {
  const options = [
    { value: 'apple', label: 'Apple' },
    { value: 'banana', label: 'Banana' },
    { value: 'cherry', label: 'Cherry' },
  ];

  test('closed dropdown has no violations', async () => {
    const { container } = render(
      <Dropdown label="Select fruit" options={options} />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('open dropdown has no violations', async () => {
    const user = userEvent.setup();
    const { container } = render(
      <Dropdown label="Select fruit" options={options} />
    );

    const button = screen.getByRole('button', { name: /select fruit/i });
    await user.click(button);

    await waitFor(async () => {
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  test('dropdown with selected value is accessible', async () => {
    const { container } = render(
      <Dropdown
        label="Select fruit"
        options={options}
        value="banana"
      />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('disabled dropdown is accessible', async () => {
    const { container } = render(
      <Dropdown
        label="Select fruit"
        options={options}
        disabled
      />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

## Playwright + axe-core E2E Tests

### Page-Level Test

```typescript
// tests/a11y/homepage.spec.ts
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.describe("Homepage Accessibility", () => {
  test("should not have accessibility violations", async ({ page }) => {
    await page.goto("/");

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test("navigation menu is accessible", async ({ page }) => {
    await page.goto("/");

    // Scan only the navigation
    const results = await new AxeBuilder({ page }).include("nav").analyze();

    expect(results.violations).toEqual([]);
  });

  test("footer is accessible", async ({ page }) => {
    await page.goto("/");

    const results = await new AxeBuilder({ page }).include("footer").analyze();

    expect(results.violations).toEqual([]);
  });
});
```

### User Journey Test

```typescript
// tests/a11y/checkout.spec.ts
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.describe("Checkout Flow Accessibility", () => {
  test("entire checkout flow is accessible", async ({ page }) => {
    // Step 1: Cart page
    await page.goto("/cart");
    let results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    expect(results.violations).toEqual([]);

    // Step 2: Add item and proceed
    await page.getByRole("button", { name: "Proceed to Checkout" }).click();

    // Step 3: Shipping form
    await page.waitForURL("/checkout/shipping");
    results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    // Fill form
    await page.getByLabel("Email").fill("test@example.com");
    await page.getByLabel("Street Address").fill("123 Main St");
    await page.getByRole("button", { name: "Continue to Payment" }).click();

    // Step 4: Payment form
    await page.waitForURL("/checkout/payment");
    results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    // Step 5: Review order
    await page.getByRole("button", { name: "Review Order" }).click();
    await page.waitForURL("/checkout/review");
    results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });

  test("validation errors are accessible", async ({ page }) => {
    await page.goto("/checkout/shipping");

    // Submit without filling required fields
    await page.getByRole("button", { name: "Continue" }).click();

    // Wait for error messages to appear
    await page.waitForSelector('[role="alert"]');

    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });
});
```

### Dynamic Content Test

```typescript
// tests/a11y/search.spec.ts
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.describe("Search Accessibility", () => {
  test("search interface is accessible", async ({ page }) => {
    await page.goto("/search");

    // Initial state
    let results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    // Type search query
    await page.getByRole("searchbox", { name: "Search products" }).fill("laptop");

    // Wait for autocomplete suggestions
    await page.waitForSelector('[role="listbox"]');

    // Scan with suggestions visible
    results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    // Select a suggestion
    await page
      .getByRole("option", { name: /laptop/i })
      .first()
      .click();

    // Wait for results page
    await page.waitForURL("**/search?q=laptop");

    // Scan results page
    results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });

  test("empty search results accessible", async ({ page }) => {
    await page.goto("/search?q=nonexistentproduct123");

    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });
});
```

### Modal Interaction Test

```typescript
// tests/a11y/modal.spec.ts
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.describe("Modal Accessibility", () => {
  test("modal maintains accessibility through interactions", async ({ page }) => {
    await page.goto("/dashboard");

    // Initial state (modal closed)
    let results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    // Open modal
    await page.getByRole("button", { name: "Open Settings" }).click();
    await page.waitForSelector('[role="dialog"]');

    // Modal open state
    results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    // Interact with modal form
    await page.getByLabel("Display Name").fill("John Doe");
    await page.getByLabel("Email Notifications").check();

    // Still accessible after interactions
    results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    // Close modal
    await page.getByRole("button", { name: "Save" }).click();
    await page.waitForSelector('[role="dialog"]', { state: "hidden" });

    // After modal closes
    results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });

  test("focus is trapped in modal", async ({ page }) => {
    await page.goto("/dashboard");
    await page.getByRole("button", { name: "Open Settings" }).click();
    await page.waitForSelector('[role="dialog"]');

    // Tab through all elements
    const focusableElements = await page.locator('[role="dialog"] :focus-visible').count();

    for (let i = 0; i < focusableElements + 2; i++) {
      await page.keyboard.press("Tab");
    }

    // Focus should still be within modal
    const focusedElement = await page.evaluate(() => {
      const activeElement = document.activeElement;
      return activeElement?.closest('[role="dialog"]') !== null;
    });

    expect(focusedElement).toBe(true);
  });
});
```

## Custom axe Rules

### Creating a Custom Rule

```typescript
// tests/utils/custom-axe-rules.ts
import { configureAxe } from "jest-axe";

export const axeWithCustomRules = configureAxe({
  rules: {
    // Ensure all buttons have explicit type attribute
    "button-type": {
      enabled: true,
      selector: "button:not([type])",
      any: [],
      none: [],
      all: ["button-has-type"],
    },
  },
  checks: [
    {
      id: "button-has-type",
      evaluate: () => false,
      metadata: {
        impact: "minor",
        messages: {
          fail: "Button must have explicit type attribute (button, submit, or reset)",
        },
      },
    },
  ],
});
```

### Using Custom Rules in Tests

```typescript
// src/components/Form.test.tsx
import { render } from '@testing-library/react';
import { toHaveNoViolations } from 'jest-axe';
import { axeWithCustomRules } from '../tests/utils/custom-axe-rules';

expect.extend(toHaveNoViolations);

test('form buttons have explicit type', async () => {
  const { container } = render(
    <form>
      <button type="button">Cancel</button>
      <button type="submit">Submit</button>
    </form>
  );

  const results = await axeWithCustomRules(container);
  expect(results).toHaveNoViolations();
});
```

## CI Pipeline Configuration

### GitHub Actions Workflow

```yaml
# .github/workflows/a11y-tests.yml
name: Accessibility Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  unit-a11y:
    name: Unit Accessibility Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run jest-axe tests
        run: npm run test:a11y:unit

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage/lcov.info
          flags: accessibility

  e2e-a11y:
    name: E2E Accessibility Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright
        run: npx playwright install --with-deps chromium

      - name: Build application
        run: npm run build
        env:
          CI: true

      - name: Start application
        run: npm run start &
        env:
          PORT: 3000
          NODE_ENV: test

      - name: Wait for application
        run: npx wait-on http://localhost:3000 --timeout 60000

      - name: Run Playwright accessibility tests
        run: npx playwright test tests/a11y/

      - name: Upload Playwright report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-a11y-report
          path: playwright-report/
          retention-days: 30

      - name: Comment PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('playwright-report/index.html', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '## ♿ Accessibility Test Results\n\nView full report in artifacts.'
            });

  lighthouse:
    name: Lighthouse Accessibility Audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install dependencies
        run: npm ci

      - name: Build application
        run: npm run build

      - name: Start application
        run: npm run start &

      - name: Wait for application
        run: npx wait-on http://localhost:3000

      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli@0.13.x
          lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}

      - name: Upload Lighthouse results
        uses: actions/upload-artifact@v4
        with:
          name: lighthouse-results
          path: .lighthouseci/
```

### Package.json Test Scripts

```json
{
  "scripts": {
    "test:a11y:unit": "vitest run --coverage src/**/*.a11y.test.{ts,tsx}",
    "test:a11y:unit:watch": "vitest watch src/**/*.a11y.test.{ts,tsx}",
    "test:a11y:e2e": "playwright test tests/a11y/",
    "test:a11y:all": "npm run test:a11y:unit && npm run test:a11y:e2e",
    "test:a11y:lighthouse": "lhci autorun"
  }
}
```

These examples provide a comprehensive foundation for implementing automated accessibility testing in your application.
