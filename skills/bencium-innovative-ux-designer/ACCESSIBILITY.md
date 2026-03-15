# Accessibility Essentials

Accessibility enables creativity - it's a foundation, not a limitation. WCAG 2.1 AA compliance.

## Core Principles (POUR)

- **Perceivable**: Content must be perceivable (alt text, contrast, captions)
- **Operable**: UI must be keyboard/touch accessible
- **Understandable**: Clear, predictable behavior
- **Robust**: Works with assistive technologies

## Contrast Requirements

| Element | Minimum Ratio |
|---------|---------------|
| Normal text | 4.5:1 |
| Large text (18pt+) | 3:1 |
| UI components | 3:1 |

**Tools**: Chrome DevTools Accessibility tab, WebAIM Contrast Checker

## Keyboard Navigation

```tsx
// All interactive elements need focus states
<button className="focus:ring-4 focus:ring-blue-500 focus:outline-none">
  Accessible
</button>

// Custom elements need tabindex and key handlers
<div
  role="button"
  tabIndex={0}
  onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && handleClick()}
>
  Custom Button
</div>
```

**Essentials:**
- Tab through entire interface
- Enter/Space activates elements
- Escape closes modals
- Visible focus indicators always

## Essential ARIA

```tsx
// Buttons without text
<button aria-label="Close dialog"><X /></button>

// Expandable elements
<button aria-expanded={isOpen} aria-controls="menu">Menu</button>

// Live regions for dynamic content
<div role="status" aria-live="polite">{statusMessage}</div>
<div role="alert" aria-live="assertive">{errorMessage}</div>

// Form errors
<input aria-invalid={hasError} aria-describedby="error-msg" />
{hasError && <p id="error-msg" role="alert">Error text</p>}
```

## Semantic HTML

```tsx
// Use semantic elements, not divs
<header><nav>...</nav></header>
<main><article><h1>...</h1></article></main>
<footer>...</footer>

// Heading hierarchy (never skip levels)
<h1>Page Title</h1>
  <h2>Section</h2>
    <h3>Subsection</h3>
```

## Touch Targets

- Minimum **44x44px** for all interactive elements
- Adequate spacing between targets
- `touch-manipulation` CSS for responsive touch

## Screen Reader Content

```tsx
// Hidden but announced
<span className="sr-only">Additional context</span>

// Skip link
<a href="#main" className="sr-only focus:not-sr-only">
  Skip to main content
</a>
```

## Quick Checklist

- [ ] Keyboard: Can tab through everything
- [ ] Focus: Visible focus indicators
- [ ] Contrast: 4.5:1 for text
- [ ] Alt text: All images have appropriate alt
- [ ] Headings: Logical h1-h6 hierarchy
- [ ] Forms: Labels associated with inputs
- [ ] Errors: Announced to screen readers
- [ ] Touch: 44px minimum targets

## Resources

- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
