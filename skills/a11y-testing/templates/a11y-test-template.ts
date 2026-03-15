/**
 * Accessibility Testing Template
 *
 * This template provides ready-to-use patterns for both jest-axe unit tests
 * and Playwright E2E accessibility tests.
 *
 * Usage:
 * 1. Copy sections relevant to your test type
 * 2. Replace placeholders (COMPONENT_NAME, PAGE_URL, etc.)
 * 3. Add component-specific test cases
 */

// ============================================================================
// JEST-AXE UNIT TEST TEMPLATE
// ============================================================================

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { COMPONENT_NAME } from './COMPONENT_NAME'; // Replace with your component

expect.extend(toHaveNoViolations);

describe('COMPONENT_NAME Accessibility', () => {
  /**
   * Test 1: Basic accessibility check
   * Verifies component has no violations in default state
   */
  test('has no accessibility violations', async () => {
    const { container } = render(<COMPONENT_NAME />);

    const results = await axe(container);

    expect(results).toHaveNoViolations();
  });

  /**
   * Test 2: WCAG compliance level
   * Explicitly test against WCAG 2.1 Level AA standards
   */
  test('meets WCAG 2.1 Level AA', async () => {
    const { container } = render(<COMPONENT_NAME />);

    const results = await axe(container, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa', 'wcag21aa'],
      },
    });

    expect(results).toHaveNoViolations();
  });

  /**
   * Test 3: Interactive state
   * Test accessibility after user interactions
   */
  test('maintains accessibility after interaction', async () => {
    const user = userEvent.setup();
    const { container } = render(<COMPONENT_NAME />);

    // Perform interaction (replace with actual component interaction)
    const button = screen.getByRole('button', { name: /ACTION_NAME/i });
    await user.click(button);

    const results = await axe(container);

    expect(results).toHaveNoViolations();
  });

  /**
   * Test 4: Error state
   * Verify error messages are accessible
   */
  test('error state is accessible', async () => {
    const { container } = render(
      <COMPONENT_NAME error="Error message here" />
    );

    const results = await axe(container);

    expect(results).toHaveNoViolations();
  });

  /**
   * Test 5: Disabled state
   * Verify disabled state maintains accessibility
   */
  test('disabled state is accessible', async () => {
    const { container } = render(<COMPONENT_NAME disabled />);

    const results = await axe(container);

    expect(results).toHaveNoViolations();
  });

  /**
   * Test 6: Loading state
   * Verify loading indicators are accessible
   */
  test('loading state is accessible', async () => {
    const { container } = render(<COMPONENT_NAME isLoading />);

    const results = await axe(container);

    expect(results).toHaveNoViolations();
  });

  /**
   * Test 7: With props variations
   * Test different prop combinations
   */
  test.each([
    { size: 'small', variant: 'primary' },
    { size: 'medium', variant: 'secondary' },
    { size: 'large', variant: 'tertiary' },
  ])('is accessible with props: %o', async (props) => {
    const { container } = render(<COMPONENT_NAME {...props} />);

    const results = await axe(container);

    expect(results).toHaveNoViolations();
  });
});

// ============================================================================
// PLAYWRIGHT E2E ACCESSIBILITY TEST TEMPLATE
// ============================================================================

import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('PAGE_NAME Accessibility', () => {
  /**
   * Test 1: Page-level accessibility check
   * Scans entire page for violations
   */
  test('page has no accessibility violations', async ({ page }) => {
    await page.goto('/PAGE_URL'); // Replace with your page URL

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  /**
   * Test 2: Specific region accessibility
   * Test a specific section of the page
   */
  test('navigation is accessible', async ({ page }) => {
    await page.goto('/PAGE_URL');

    const results = await new AxeBuilder({ page })
      .include('nav') // Replace with your selector
      .analyze();

    expect(results.violations).toEqual([]);
  });

  /**
   * Test 3: User journey accessibility
   * Test accessibility through a complete user flow
   */
  test('user journey is accessible', async ({ page }) => {
    // Step 1: Initial page
    await page.goto('/PAGE_URL');
    let results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    // Step 2: Navigate or interact
    await page.getByRole('button', { name: 'ACTION_NAME' }).click();
    await page.waitForURL('/NEXT_PAGE_URL');
    results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    // Step 3: Fill form (if applicable)
    await page.getByLabel('Field Label').fill('Value');
    results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    // Step 4: Submit or complete action
    await page.getByRole('button', { name: 'Submit' }).click();
    await page.waitForURL('/SUCCESS_PAGE_URL');
    results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });

  /**
   * Test 4: Modal accessibility
   * Test modal opens, content is accessible, and focus is managed
   */
  test('modal is accessible', async ({ page }) => {
    await page.goto('/PAGE_URL');

    // Open modal
    await page.getByRole('button', { name: 'Open Modal' }).click();
    await page.waitForSelector('[role="dialog"]');

    // Scan modal
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);

    // Verify focus trap
    const firstFocusable = await page.locator('[role="dialog"] button').first();
    await expect(firstFocusable).toBeFocused();
  });

  /**
   * Test 5: Form validation accessibility
   * Test that validation errors are accessible
   */
  test('form validation errors are accessible', async ({ page }) => {
    await page.goto('/FORM_PAGE_URL');

    // Submit empty form
    await page.getByRole('button', { name: 'Submit' }).click();

    // Wait for error messages
    await page.waitForSelector('[role="alert"]');

    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });

  /**
   * Test 6: Dynamic content accessibility
   * Test accessibility of content that loads dynamically
   */
  test('dynamic content is accessible', async ({ page }) => {
    await page.goto('/PAGE_URL');

    // Trigger dynamic content load
    await page.getByRole('searchbox').fill('search query');

    // Wait for results
    await page.waitForSelector('[role="listbox"]');

    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });

  /**
   * Test 7: Keyboard navigation
   * Verify keyboard navigation works and is accessible
   */
  test('keyboard navigation is accessible', async ({ page }) => {
    await page.goto('/PAGE_URL');

    // Tab through interactive elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Verify focus is visible
    const focusedElement = await page.evaluate(() => {
      const el = document.activeElement;
      const styles = window.getComputedStyle(el);
      return styles.outline !== 'none';
    });

    expect(focusedElement).toBe(true);

    // Scan page state
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });

  /**
   * Test 8: Exclude third-party content
   * Scan page excluding elements you don't control
   */
  test('page without third-party widgets is accessible', async ({ page }) => {
    await page.goto('/PAGE_URL');

    const results = await new AxeBuilder({ page })
      .exclude('#ads-container')
      .exclude('[data-third-party]')
      .analyze();

    expect(results.violations).toEqual([]);
  });
});

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Custom axe configuration for specific testing needs
 */
export function createCustomAxe(options = {}) {
  const { configureAxe } = require('jest-axe');

  return configureAxe({
    rules: {
      // Disable specific rules if needed (document why)
      // 'color-contrast': { enabled: false },
      ...options.rules,
    },
    reporter: 'v2',
    ...options,
  });
}

/**
 * Helper to scan only a specific region
 */
export async function scanRegion(container: HTMLElement, selector: string) {
  const { axe } = require('jest-axe');
  const region = container.querySelector(selector);

  if (!region) {
    throw new Error(`Region not found: ${selector}`);
  }

  return axe(region);
}

/**
 * Helper to wait for dynamic content and then scan
 */
export async function waitAndScan(
  container: HTMLElement,
  selector: string,
  timeout = 3000
) {
  const { axe } = require('jest-axe');

  // Wait for element to appear
  const startTime = Date.now();
  while (Date.now() - startTime < timeout) {
    if (container.querySelector(selector)) {
      break;
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }

  return axe(container);
}

// ============================================================================
// TEST DATA FIXTURES
// ============================================================================

/**
 * Mock data for testing forms
 */
export const mockFormData = {
  valid: {
    email: 'test@example.com',
    name: 'John Doe',
    message: 'This is a test message',
  },
  invalid: {
    email: 'invalid-email',
    name: '',
    message: '',
  },
};

/**
 * Mock user for authentication tests
 */
export const mockUser = {
  id: '1',
  email: 'test@example.com',
  name: 'Test User',
  role: 'user',
};

// ============================================================================
// COMMON ASSERTIONS
// ============================================================================

/**
 * Assert element has accessible name
 */
export function assertAccessibleName(element: HTMLElement, expectedName: string) {
  const accessibleName = element.getAttribute('aria-label') ||
                         element.textContent ||
                         element.getAttribute('title');

  expect(accessibleName).toBe(expectedName);
}

/**
 * Assert form field has associated label
 */
export function assertFieldHasLabel(
  container: HTMLElement,
  fieldId: string,
  expectedLabel: string
) {
  const field = container.querySelector(`#${fieldId}`);
  const label = container.querySelector(`label[for="${fieldId}"]`);

  expect(field).toBeTruthy();
  expect(label).toBeTruthy();
  expect(label?.textContent).toBe(expectedLabel);
}

/**
 * Assert element has proper ARIA role
 */
export function assertAriaRole(element: HTMLElement, expectedRole: string) {
  const role = element.getAttribute('role');
  expect(role).toBe(expectedRole);
}

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

/*
Example 1: Basic Button Component Test

import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button } from './Button';

expect.extend(toHaveNoViolations);

test('Button is accessible', async () => {
  const { container } = render(<Button>Click me</Button>);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
*/

/*
Example 2: E2E Login Flow

test('login flow is accessible', async ({ page }) => {
  await page.goto('/login');

  // Initial page
  let results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);

  // Fill form
  await page.getByLabel('Email').fill('test@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Log in' }).click();

  // After login
  await page.waitForURL('/dashboard');
  results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
*/

/*
Example 3: Custom Rule Test

import { createCustomAxe } from './templates/a11y-test-template';

const axe = createCustomAxe({
  rules: {
    'custom-rule': { enabled: true },
  },
});

test('component follows custom rules', async () => {
  const { container } = render(<Component />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
*/
