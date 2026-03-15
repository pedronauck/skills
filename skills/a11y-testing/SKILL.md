---
name: a11y-testing
description: Automated accessibility testing with axe-core, Playwright, and jest-axe for WCAG compliance. Use when adding or validating a11y tests, running WCAG checks, or auditing UI accessibility.
context: fork
agent: test-generator
version: 1.1.0
tags: [accessibility, testing, axe-core, playwright, wcag, a11y, jest-axe]
allowed-tools: [Read, Write, Bash, Grep, Glob]
author: SkillForge
user-invocable: false
---

# Accessibility Testing

Automated accessibility testing with axe-core for WCAG 2.2 compliance. Catches 30-50% of issues automatically.

## Overview

- Implementing CI/CD accessibility gates
- Running pre-release compliance audits
- Testing component accessibility in unit tests
- Validating page-level accessibility with E2E tests
- Ensuring keyboard navigation works correctly

## Quick Reference

### jest-axe Unit Testing

```typescript
// jest.setup.ts
import { toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

// Button.test.tsx
import { render } from '@testing-library/react';
import { axe } from 'jest-axe';

it('has no a11y violations', async () => {
  const { container } = render(<Button>Click me</Button>);
  expect(await axe(container)).toHaveNoViolations();
});
```

### Playwright + axe-core E2E

```typescript
// e2e/accessibility.spec.ts
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("page has no a11y violations", async ({ page }) => {
  await page.goto("/");
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag22aa"])
    .analyze();
  expect(results.violations).toEqual([]);
});

test("modal state has no violations", async ({ page }) => {
  await page.goto("/");
  await page.click('[data-testid="open-modal"]');
  await page.waitForSelector('[role="dialog"]');

  const results = await new AxeBuilder({ page })
    .include('[role="dialog"]')
    .withTags(["wcag2a", "wcag2aa"])
    .analyze();
  expect(results.violations).toEqual([]);
});
```

### CI/CD Integration

```yaml
# .github/workflows/accessibility.yml
name: Accessibility
on: [pull_request]

jobs:
  a11y:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20", cache: "npm" }
      - run: npm ci
      - run: npm run test:a11y
      - run: npm run build
      - run: npx playwright install --with-deps chromium
      - run: npm start & npx wait-on http://localhost:3000
      - run: npx playwright test e2e/accessibility
```

## Key Decisions

| Decision       | Choice                      | Rationale                           |
| -------------- | --------------------------- | ----------------------------------- |
| Test runner    | jest-axe + Playwright       | Unit + E2E coverage                 |
| WCAG level     | AA (wcag2aa)                | Industry standard, legal compliance |
| CI gate        | Block on violations         | Prevent regression                  |
| Browser matrix | Chromium + Firefox          | Cross-browser coverage              |
| Exclusions     | Third-party widgets only    | Minimize blind spots                |
| Tags           | wcag2a, wcag2aa, wcag22aa   | Full WCAG 2.2 AA                    |
| State testing  | Test all interactive states | Modal, error, loading               |

## Anti-Patterns (FORBIDDEN)

```typescript
// BAD: Disabling rules globally
const results = await axe(container, {
  rules: { 'color-contrast': { enabled: false } }  // NEVER disable rules
});

// BAD: Excluding too much
new AxeBuilder({ page })
  .exclude('body')  // Defeats the purpose
  .analyze();

// BAD: Only testing happy path
it('form is accessible', async () => {
  const { container } = render(<Form />);
  expect(await axe(container)).toHaveNoViolations();
  // Missing: error state, loading state, disabled state
});

// BAD: No CI enforcement
// Accessibility tests exist but don't block PRs

// BAD: Manual-only testing
// Relying solely on human review - catches issues too late
```

## Related Skills

- `e2e-testing` - Playwright E2E testing patterns
- `unit-testing` - Jest unit testing fundamentals
- `design-system-starter` - Accessible component foundations

## Capability Details

### jest-axe-testing

**Keywords:** jest, axe, unit test, component test, react-testing-library
**Solves:**

- Component-level accessibility validation
- Fast feedback in development
- CI/CD unit test gates
- Testing all component states (disabled, error, loading)

### playwright-axe-testing

**Keywords:** playwright, e2e, axe-core, page scan, wcag, integration
**Solves:**

- Full page accessibility audits
- Testing interactive states (modals, menus, forms)
- Multi-browser accessibility verification
- WCAG compliance validation at page level

### ci-a11y-gates

**Keywords:** ci, cd, github actions, accessibility gate, automation
**Solves:**

- Blocking PRs with accessibility violations
- Automated regression prevention
- Compliance reporting and artifacts
- Integration with deployment pipelines
