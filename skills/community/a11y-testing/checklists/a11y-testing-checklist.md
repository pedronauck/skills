# Accessibility Testing Checklist

Use this checklist to ensure comprehensive accessibility coverage.

## Automated Test Coverage

### Unit Tests (jest-axe)

- [ ] All form components tested with axe
- [ ] All interactive components (buttons, links, modals) tested
- [ ] Custom UI widgets tested (date pickers, dropdowns, sliders)
- [ ] Dynamic content updates tested
- [ ] Error states tested for proper announcements
- [ ] Loading states have appropriate ARIA attributes
- [ ] Tests cover WCAG 2.1 Level AA tags minimum
- [ ] No disabled rules without documented justification

### E2E Tests (Playwright + axe-core)

- [ ] Homepage scanned for violations
- [ ] All critical user journeys include a11y scan
- [ ] Post-interaction states scanned (after form submit, modal open)
- [ ] Multi-step flows tested (signup, checkout, settings)
- [ ] Error pages and 404s tested
- [ ] Third-party widgets excluded from scan if necessary
- [ ] Tests run in CI/CD pipeline
- [ ] Accessibility reports archived on failure

### CI/CD Integration

- [ ] Accessibility tests run on every PR
- [ ] Pre-commit hook runs a11y tests on changed files
- [ ] Lighthouse CI monitors accessibility score (>95%)
- [ ] Failed tests block deployment
- [ ] Test results published to team (GitHub comments, Slack)

## Manual Testing Requirements

### Keyboard Navigation

- [ ] **Tab Navigation**
  - [ ] All interactive elements reachable via Tab/Shift+Tab
  - [ ] Tab order follows visual layout (top to bottom, left to right)
  - [ ] Focus indicator visible on all focusable elements
  - [ ] No keyboard traps (can always Tab away)

- [ ] **Action Keys**
  - [ ] Enter/Space activates buttons and links
  - [ ] Escape closes modals, dropdowns, menus
  - [ ] Arrow keys navigate within compound widgets (tabs, menus, sliders)
  - [ ] Home/End keys navigate to start/end where appropriate

- [ ] **Form Controls**
  - [ ] All form fields accessible via keyboard
  - [ ] Enter submits forms
  - [ ] Error messages keyboard-navigable
  - [ ] Custom controls (date pickers, color pickers) keyboard-operable

- [ ] **Skip Links**
  - [ ] "Skip to main content" link present and functional
  - [ ] Appears on first Tab press
  - [ ] Actually skips navigation when activated

### Screen Reader Testing

Test with at least one screen reader:

- macOS: VoiceOver (Cmd+F5)
- Windows: NVDA (free) or JAWS
- Linux: Orca

#### Content Structure

- [ ] **Headings**
  - [ ] Logical heading hierarchy (h1 → h2 → h3, no skips)
  - [ ] Page has exactly one h1
  - [ ] Headings describe section content
  - [ ] Can navigate by heading (H key in screen reader)

- [ ] **Landmarks**
  - [ ] `<header>`, `<nav>`, `<main>`, `<footer>` present
  - [ ] Multiple landmarks of same type have unique labels
  - [ ] Can navigate by landmark (D key in screen reader)

- [ ] **Lists**
  - [ ] Navigation uses `<ul>` or `<nav>`
  - [ ] Related items grouped in lists
  - [ ] Screen reader announces list with item count

#### Interactive Elements

- [ ] **Forms**
  - [ ] All inputs have associated `<label>` or `aria-label`
  - [ ] Required fields announced as required
  - [ ] Error messages announced when they appear
  - [ ] Field types announced (email, password, number)
  - [ ] Placeholder text not used as only label

- [ ] **Buttons and Links**
  - [ ] Role announced ("button", "link")
  - [ ] Purpose clear from label alone
  - [ ] State announced (expanded/collapsed, selected)
  - [ ] Icon-only buttons have `aria-label`

- [ ] **Images**
  - [ ] Informative images have meaningful `alt` text
  - [ ] Decorative images have `alt=""` or `role="presentation"`
  - [ ] Complex images have longer description (`aria-describedby` or caption)

- [ ] **Dynamic Content**
  - [ ] Live regions announce updates (`aria-live="polite"` or `"assertive"`)
  - [ ] Loading states announced
  - [ ] Success/error messages announced
  - [ ] Content changes don't lose focus position

#### Navigation

- [ ] **Menus**
  - [ ] Menu buttons announce expanded/collapsed state
  - [ ] Arrow keys navigate menu items
  - [ ] First/last items wrap or stop appropriately
  - [ ] Escape closes menu

- [ ] **Modals/Dialogs**
  - [ ] Focus moves to modal on open
  - [ ] Focus trapped within modal
  - [ ] Modal title announced
  - [ ] Escape closes modal
  - [ ] Focus returns to trigger on close

- [ ] **Tabs**
  - [ ] Tab role announced
  - [ ] Active tab announced as selected
  - [ ] Arrow keys navigate tabs
  - [ ] Tab panel content announced

### Color and Contrast

Use browser extensions (axe DevTools, WAVE) or online tools:

- [ ] **Text Contrast**
  - [ ] Normal text (< 18pt): 4.5:1 minimum ratio
  - [ ] Large text (≥ 18pt or 14pt bold): 3:1 minimum ratio
  - [ ] Passes for all text (body, headings, labels, placeholders)

- [ ] **UI Component Contrast**
  - [ ] Buttons, inputs, icons: 3:1 minimum against background
  - [ ] Focus indicators: 3:1 minimum
  - [ ] Error/success states: 3:1 minimum

- [ ] **Color Independence**
  - [ ] Information not conveyed by color alone
  - [ ] Links distinguishable without color (underline, icon, etc.)
  - [ ] Form errors indicated by icon + text, not just red border
  - [ ] Charts/graphs have patterns or labels, not just colors

### Responsive and Zoom Testing

- [ ] **Browser Zoom (200%)**
  - [ ] Test at 200% zoom level (WCAG 2.1 requirement)
  - [ ] No horizontal scrolling at 200% zoom
  - [ ] All content visible and readable
  - [ ] No overlapping or cut-off text
  - [ ] Interactive elements remain operable

- [ ] **Mobile/Touch**
  - [ ] Touch targets ≥ 44×44 CSS pixels
  - [ ] Sufficient spacing between interactive elements (at least 8px)
  - [ ] No reliance on hover (all hover info accessible on tap)
  - [ ] Pinch-to-zoom enabled (no `user-scalable=no`)
  - [ ] Orientation works in both portrait and landscape

### Animation and Motion

- [ ] **Respect Motion Preferences**
  - [ ] Check `prefers-reduced-motion` media query
  - [ ] Disable or reduce animations when preferred
  - [ ] Test with system setting enabled (macOS, Windows)

- [ ] **No Seizure Triggers**
  - [ ] No flashing content faster than 3 times per second
  - [ ] Autoplay videos have controls (pause/stop)
  - [ ] Parallax effects can be disabled

## Documentation Review

- [ ] **ARIA Usage**
  - [ ] ARIA only used when native HTML insufficient
  - [ ] ARIA roles match HTML semantics
  - [ ] All required ARIA properties present
  - [ ] No conflicting or redundant ARIA

- [ ] **Code Comments**
  - [ ] Complex accessibility patterns documented
  - [ ] Keyboard shortcuts documented
  - [ ] Focus management documented

## Cross-Browser Testing

Test in multiple browsers and assistive tech combinations:

- [ ] Chrome + NVDA (Windows)
- [ ] Firefox + NVDA (Windows)
- [ ] Safari + VoiceOver (macOS)
- [ ] Safari + VoiceOver (iOS)
- [ ] Chrome + TalkBack (Android)

## Compliance Verification

- [ ] **WCAG 2.1 Level AA**
  - [ ] Automated tests pass for wcag2a, wcag2aa, wcag21aa tags
  - [ ] Manual testing confirms keyboard accessibility
  - [ ] Manual testing confirms screen reader accessibility
  - [ ] Color contrast verified

- [ ] **Legal Requirements**
  - [ ] Section 508 (US federal)
  - [ ] ADA (US)
  - [ ] EN 301 549 (EU)
  - [ ] Accessibility statement page present (if required)

## Continuous Monitoring

- [ ] Lighthouse accessibility score tracked over time
- [ ] Accessibility tests in regression suite
- [ ] New features include a11y tests from day one
- [ ] Team trained on accessibility best practices
- [ ] Accessibility champion assigned
- [ ] Regular audits scheduled (quarterly recommended)

## When to Seek Expert Help

Engage an accessibility specialist if:

- [ ] Building complex custom widgets (ARIA patterns)
- [ ] Handling advanced screen reader interactions
- [ ] Preparing for legal compliance audit
- [ ] User feedback indicates accessibility issues
- [ ] Automated tests show many violations
- [ ] Team lacks accessibility expertise

## Quick Wins for Common Issues

### Missing Alt Text

```html
<!-- Before -->
<img src="logo.png" />

<!-- After -->
<img src="logo.png" alt="Company Logo" />
```

### Unlabeled Form Input

```html
<!-- Before -->
<input type="email" placeholder="Email" />

<!-- After -->
<label for="email">Email</label>
<input type="email" id="email" />
```

### Low Contrast Text

```css
/* Before */
color: #999; /* 2.8:1 ratio */

/* After */
color: #767676; /* 4.5:1 ratio */
```

### Keyboard Trap

```jsx
// Before
<div onClick={handleClick}>Click me</div>

// After
<button onClick={handleClick}>Click me</button>
```

### Missing Focus Indicator

```css
/* Before */
button:focus {
  outline: none;
}

/* After */
button:focus-visible {
  outline: 2px solid blue;
  outline-offset: 2px;
}
```
