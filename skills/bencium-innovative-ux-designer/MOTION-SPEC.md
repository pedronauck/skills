# Motion Specification

Motion should surprise and delight while serving function. Animation is a creative tool.

## Easing Curves

| Easing | CSS | Use For |
|--------|-----|---------|
| **Ease-out** | `cubic-bezier(0.0, 0.0, 0.2, 1)` | Entrances, appearing |
| **Ease-in** | `cubic-bezier(0.4, 0.0, 1, 1)` | Exits, disappearing |
| **Ease-in-out** | `cubic-bezier(0.4, 0.0, 0.2, 1)` | State changes, transforms |
| **Spring** | `cubic-bezier(0.68, -0.55, 0.265, 1.55)` | Playful, attention-grabbing |
| **Linear** | `linear` | Spinners, continuous loops |

## Duration by Element Weight

| Weight | Duration | Examples |
|--------|----------|----------|
| **Lightweight** | 150ms | Icons, badges, chips |
| **Standard** | 300ms | Cards, panels, list items |
| **Weighty** | 500ms | Modals, page transitions |

## Duration by Interaction

| Interaction | Duration |
|-------------|----------|
| Button press | 100ms |
| Hover state | 150ms |
| Tooltip appear | 200ms |
| Tab switch | 250ms |
| Modal open | 300ms |
| Page transition | 400ms |

## Common Patterns

```tsx
// Hover transition (CSS)
<button className="transition-colors duration-150 ease-out hover:bg-blue-700">

// Fade + slide (Framer Motion)
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3, ease: "easeOut" }}
/>

// Stagger children
<motion.ul variants={{ visible: { transition: { staggerChildren: 0.1 } } }}>
  <motion.li variants={{ hidden: { opacity: 0 }, visible: { opacity: 1 } }} />
</motion.ul>
```

## Performance Rules

- Only animate `transform` and `opacity` (GPU-accelerated)
- Avoid animating `width`, `height`, `margin`, `padding`
- Keep durations under 500ms for UI interactions
- Respect `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Resources

- [Framer Motion](https://www.framer.com/motion/)
- [CSS Easing Functions](https://easings.net/)
