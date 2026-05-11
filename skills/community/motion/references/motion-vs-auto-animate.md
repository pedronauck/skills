# Motion vs AutoAnimate - Decision Guide

This document helps you choose between Motion (Framer Motion) and AutoAnimate for your animation needs.

---

## TL;DR - Quick Decision

**Use AutoAnimate when:**
- ✅ Animating list add/remove/sort operations
- ✅ Simple accordion expand/collapse
- ✅ Toast notifications fade in/out
- ✅ Form validation error messages appearing/disappearing
- ✅ Bundle size is critical (3.28 KB)
- ✅ Want zero configuration

**Use Motion when:**
- ✅ Need gesture controls (drag, hover, tap with fine control)
- ✅ Need scroll-based animations or parallax
- ✅ Need layout/shared element transitions
- ✅ Need SVG path morphing or line drawing
- ✅ Need spring physics customization
- ✅ Need complex orchestrated animations

**Rule of Thumb**: AutoAnimate for 90% of cases, Motion for 10%

---

## Bundle Size Comparison

| Package | Minified + Gzipped | Use Case |
|---------|-------------------|----------|
| **AutoAnimate** | 3.28 KB | Simple list animations |
| **Motion useAnimate mini** | 2.3 KB | Smallest React animation |
| **Motion useAnimate hybrid** | 17 KB | Imperative animations |
| **Motion with LazyMotion** | 4.6 KB | Optimized declarative |
| **Motion full component** | 34 KB | Full feature set |

**Winner for bundle size**: Motion useAnimate mini (2.3 KB) or AutoAnimate (3.28 KB)

**Winner for features**: Motion full (34 KB)

**Sweet spot**: LazyMotion (4.6 KB) for most Motion use cases

---

## API Complexity Comparison

### AutoAnimate (Zero Config)

```tsx
import { useAutoAnimate } from '@formkit/auto-animate/react'

const [parent] = useAutoAnimate()

return (
  <ul ref={parent}>
    {items.map(item => <li key={item.id}>{item.text}</li>)}
  </ul>
)
```

**Lines of code**: 3
**Configuration**: 0
**Learning curve**: Minutes

### Motion (Declarative)

```tsx
import { motion } from 'motion/react'

return (
  <ul>
    {items.map(item => (
      <motion.li
        key={item.id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        layout
      >
        {item.text}
      </motion.li>
    ))}
  </ul>
)
```

**Lines of code**: 12
**Configuration**: 4 props
**Learning curve**: Hours

**Winner for simplicity**: AutoAnimate

**Winner for control**: Motion

---

## Feature Comparison

| Feature | AutoAnimate | Motion |
|---------|-------------|--------|
| **List add/remove** | ✅ Automatic | ✅ Manual setup |
| **List reorder** | ✅ Automatic | ✅ Manual setup |
| **Accordion** | ✅ Automatic | ✅ Manual setup |
| **Drag gestures** | ❌ Not supported | ✅ Full control |
| **Hover states** | ❌ Not supported | ✅ whileHover prop |
| **Tap states** | ❌ Not supported | ✅ whileTap prop |
| **Scroll animations** | ❌ Not supported | ✅ whileInView, useScroll |
| **Parallax** | ❌ Not supported | ✅ useTransform |
| **Layout animations** | ❌ Not supported | ✅ layout prop, FLIP |
| **Shared elements** | ❌ Not supported | ✅ layoutId |
| **SVG animations** | ❌ Not supported | ✅ path, line drawing |
| **Spring physics** | ❌ Not customizable | ✅ Full control |
| **Variants/orchestration** | ❌ Not supported | ✅ Stagger, delay, sequence |
| **Exit animations** | ✅ Automatic | ✅ AnimatePresence |
| **TypeScript** | ✅ Native support | ✅ Native support |
| **SSR/Next.js** | ✅ Full support | ✅ Full support (use client) |
| **Cloudflare Workers** | ✅ Full support | ⚠️ Use framer-motion instead |
| **Accessibility** | ✅ Auto prefers-reduced-motion | ✅ Manual MotionConfig |

---

## Use Case Breakdown

### Simple List Animations (90% of use cases)

**Scenario**: Todo list, shopping cart, search results, notification list

**AutoAnimate**:
```tsx
const [parent] = useAutoAnimate()
return <ul ref={parent}>{items.map(...)}</ul>
```

**Motion**:
```tsx
<AnimatePresence>
  {items.map(item => (
    <motion.li
      key={item.id}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      layout
    >
      {item.text}
    </motion.li>
  ))}
</AnimatePresence>
```

**Recommendation**: **AutoAnimate** (simpler, smaller)

---

### Accordion Components

**Scenario**: FAQ, collapsible sections, navigation menus

**AutoAnimate**:
```tsx
const [parent] = useAutoAnimate()

return (
  <div ref={parent}>
    {isOpen && <div>Content</div>}
  </div>
)
```

**Motion**:
```tsx
<motion.div
  animate={{ height: isOpen ? "auto" : 0 }}
  style={{ overflow: "hidden" }}
>
  <div>Content</div>
</motion.div>
```

**Recommendation**: **AutoAnimate** for simple accordions, **Motion** if you need:
- Custom spring physics
- Staggered child animations
- Scroll-triggered expand/collapse

---

### Modal Dialogs

**Scenario**: Popup dialogs, overlays, lightboxes

**AutoAnimate**:
- Not ideal (doesn't handle backdrop animations well)

**Motion**:
```tsx
<AnimatePresence>
  {isOpen && (
    <>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="backdrop"
      />
      <motion.dialog
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
      >
        Content
      </motion.dialog>
    </>
  )}
</AnimatePresence>
```

**Recommendation**: **Motion** (more control over backdrop + dialog)

---

### Hero Sections & Landing Pages

**Scenario**: Marketing sites with parallax, scroll effects, complex animations

**AutoAnimate**:
- Not suitable

**Motion**:
```tsx
const { scrollYProgress } = useScroll()
const y = useTransform(scrollYProgress, [0, 1], [0, -300])

return <motion.div style={{ y }}>Hero content</motion.div>
```

**Recommendation**: **Motion** (only option)

---

### Carousels & Sliders

**Scenario**: Image galleries, product showcases

**AutoAnimate**:
- Not suitable

**Motion**:
```tsx
<motion.div
  drag="x"
  dragConstraints={{ left: -width, right: 0 }}
>
  {images.map(img => <img src={img.url} />)}
</motion.div>
```

**Recommendation**: **Motion** (gesture controls required)

---

### Drag-and-Drop Interfaces

**Scenario**: Kanban boards, sortable lists, reorderable items

**AutoAnimate**:
- Not supported (no drag gestures)

**Motion**:
```tsx
<motion.div
  drag
  dragConstraints={constraints}
  onDragEnd={handleDragEnd}
>
  Draggable item
</motion.div>
```

**Recommendation**: **Motion** (only option)

---

### Page/Route Transitions

**Scenario**: Animating between pages or routes

**AutoAnimate**:
- Not ideal (designed for element-level, not page-level)

**Motion**:
```tsx
<AnimatePresence mode="wait">
  <motion.div
    key={pathname}
    initial={{ opacity: 0, x: 20 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -20 }}
  >
    {page content}
  </motion.div>
</AnimatePresence>
```

**Recommendation**: **Motion** (better control)

**Note**: Next.js App Router has issues with route transitions. Consider alternatives.

---

### Card Expand to Detail View

**Scenario**: Grid of cards → click to expand → detail page

**AutoAnimate**:
- Not supported (no shared element transitions)

**Motion**:
```tsx
// Grid view
<motion.div layoutId={card.id} onClick={expand}>
  Card preview
</motion.div>

// Detail view
<motion.div layoutId={card.id}>
  Full card details
</motion.div>
```

**Recommendation**: **Motion** (shared element transition with layoutId)

---

## Performance Comparison

| Metric | AutoAnimate | Motion |
|--------|-------------|--------|
| **First paint** | Fastest (3.28 KB) | Slow (34 KB) or Fast (2.3-4.6 KB with optimization) |
| **Runtime performance** | Fast (minimal JS) | Fast (GPU-accelerated when possible) |
| **Large lists (50+ items)** | Good (auto-optimized) | Poor (needs virtualization) |
| **Scroll animations** | N/A | Excellent (ScrollTimeline API) |
| **Hardware acceleration** | Yes | Yes |

**Winner for first paint**: AutoAnimate

**Winner for runtime**: Tie (both use GPU when possible)

**Winner for large lists**: AutoAnimate (no setup needed)

---

## Accessibility Comparison

| Feature | AutoAnimate | Motion |
|---------|-------------|--------|
| **prefers-reduced-motion** | ✅ Automatic | ✅ Manual (MotionConfig) |
| **Keyboard support** | ✅ Inherits from elements | ✅ whileFocus prop |
| **Screen reader friendly** | ✅ Yes | ✅ Yes |

**Winner**: AutoAnimate (automatic reduced motion support)

**Note**: Motion requires manual setup:
```tsx
<MotionConfig reducedMotion="user">
  <App />
</MotionConfig>
```

---

## Framework Compatibility

| Framework | AutoAnimate | Motion |
|-----------|-------------|--------|
| **React 18/19** | ✅ Full support | ✅ Full support |
| **Next.js Pages Router** | ✅ Works out of the box | ✅ Works out of the box |
| **Next.js App Router** | ✅ Works out of the box | ✅ Requires "use client" |
| **Vite** | ✅ Works out of the box | ✅ Works out of the box |
| **Cloudflare Workers** | ✅ Full support | ⚠️ Use framer-motion v12 |
| **Remix** | ✅ Works out of the box | ✅ Works out of the box |
| **Astro** | ✅ Via React component | ✅ Via React component |
| **SvelteKit** | ✅ Via Svelte plugin | ❌ React only |
| **Vue/Nuxt** | ✅ Via Vue plugin | ❌ React only |

**Winner for compatibility**: AutoAnimate (supports Vue, Svelte, vanilla JS)

**Note**: Motion is React-only, but AutoAnimate has official plugins for:
- Vue: `@formkit/auto-animate/vue`
- Svelte: `@formkit/auto-animate/svelte`
- Vanilla JS: `@formkit/auto-animate`

---

## Migration Guide

### From AutoAnimate to Motion

**When to migrate**: You outgrow AutoAnimate and need gestures, scroll, or layout animations.

**Example - Animated List**:

Before (AutoAnimate):
```tsx
const [parent] = useAutoAnimate()
return <ul ref={parent}>{items.map(...)}</ul>
```

After (Motion):
```tsx
<AnimatePresence>
  {items.map(item => (
    <motion.li
      key={item.id}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      layout
    >
      {item.text}
    </motion.li>
  ))}
</AnimatePresence>
```

**Migration steps**:
1. Install Motion: `pnpm add motion`
2. Replace `<div ref={parent}>` with `<motion.div>`
3. Add animation props: `initial`, `animate`, `exit`
4. Wrap in `<AnimatePresence>` for exit animations
5. Add `layout` prop for reordering

---

### From Motion to AutoAnimate

**When to migrate**: Simplifying codebase, reducing bundle size for simple animations.

**Example - Animated List**:

Before (Motion):
```tsx
<AnimatePresence>
  {items.map(item => (
    <motion.li
      key={item.id}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      layout
    >
      {item.text}
    </motion.li>
  ))}
</AnimatePresence>
```

After (AutoAnimate):
```tsx
const [parent] = useAutoAnimate()
return <ul ref={parent}>{items.map(...)}</ul>
```

**Migration steps**:
1. Install AutoAnimate: `pnpm add @formkit/auto-animate`
2. Remove Motion props (initial, animate, exit, layout)
3. Remove AnimatePresence wrapper
4. Add `useAutoAnimate` hook and attach ref to parent

**Bundle size savings**: 34 KB → 3.28 KB (~90% reduction)

---

## Real-World Recommendations

### E-commerce Site

**Use AutoAnimate for**:
- Shopping cart item add/remove
- Product filter results
- Notification toasts

**Use Motion for**:
- Product image carousel (drag gestures)
- Hero section parallax
- Product detail page transitions (shared elements)

### Blog / Content Site

**Use AutoAnimate for**:
- Article list filtering
- Comment threads expand/collapse
- Tag selection

**Use Motion for**:
- Hero parallax on homepage
- Scroll-triggered section reveals
- Image lightbox modals

### Dashboard / SaaS App

**Use AutoAnimate for**:
- Sidebar navigation accordion
- Data table row add/remove
- Toast notifications

**Use Motion for**:
- Drag-to-reorder kanban cards
- Chart animations
- Modal dialogs with complex transitions

### Landing Page / Marketing Site

**Use AutoAnimate for**:
- FAQ accordion
- Feature comparison table filtering

**Use Motion for**:
- Hero section (parallax, scroll effects)
- Scroll-triggered reveals throughout page
- Interactive demos (gestures, drag)

---

## Cost-Benefit Analysis

### AutoAnimate

**Benefits**:
- ✅ Smallest bundle (3.28 KB)
- ✅ Zero configuration
- ✅ Works with any framework (React, Vue, Svelte, vanilla)
- ✅ Automatic prefers-reduced-motion
- ✅ Perfect for 90% of animation needs

**Costs**:
- ❌ No gesture controls
- ❌ No scroll animations
- ❌ No layout/shared element transitions
- ❌ No SVG path morphing
- ❌ Less control over animation timing/easing

### Motion

**Benefits**:
- ✅ Complete animation toolkit
- ✅ Gesture controls (drag, hover, tap, pan)
- ✅ Scroll-based animations
- ✅ Layout/shared element transitions
- ✅ SVG path morphing and line drawing
- ✅ Spring physics customization
- ✅ Hardware-accelerated (ScrollTimeline API)

**Costs**:
- ❌ Larger bundle (34 KB, optimizable to 2.3-4.6 KB)
- ❌ More complex API
- ❌ React-only
- ❌ Requires manual prefers-reduced-motion setup
- ❌ Cloudflare Workers compatibility issues

---

## Decision Flowchart

```
Start
  ↓
Do you need gestures (drag, hover with fine control)?
  ├─ Yes → Motion
  └─ No → ↓
Do you need scroll-based animations or parallax?
  ├─ Yes → Motion
  └─ No → ↓
Do you need shared element transitions (card → detail)?
  ├─ Yes → Motion
  └─ No → ↓
Do you need SVG path morphing or line drawing?
  ├─ Yes → Motion
  └─ No → ↓
Is it just list add/remove/sort animations?
  ├─ Yes → AutoAnimate
  └─ No → ↓
Is it accordion/collapse/expand?
  ├─ Yes → AutoAnimate (unless you need custom physics)
  └─ No → ↓
Do you want zero configuration?
  ├─ Yes → AutoAnimate
  └─ No → Motion
```

---

## Can You Use Both?

**Yes!** They complement each other well.

**Pattern**:
- Use AutoAnimate for simple list animations
- Use Motion for complex gestures and scroll effects

**Example**:
```tsx
// Simple list with AutoAnimate
const [listRef] = useAutoAnimate()

return (
  <>
    {/* Motion for hero parallax */}
    <motion.div style={{ y: parallaxY }}>
      Hero section
    </motion.div>

    {/* AutoAnimate for product list */}
    <ul ref={listRef}>
      {products.map(product => (
        <li key={product.id}>{product.name}</li>
      ))}
    </ul>

    {/* Motion for carousel */}
    <motion.div drag="x">
      {images.map(img => <img src={img.url} />)}
    </motion.div>
  </>
)
```

**Bundle size**: 3.28 KB (AutoAnimate) + 2.3-34 KB (Motion) = 5.58-37.28 KB total

**Recommendation**: Use AutoAnimate for 90% of cases, add Motion only for features AutoAnimate can't handle.

---

## Summary Table

| Criteria | AutoAnimate | Motion | Winner |
|----------|-------------|--------|--------|
| **Bundle Size** | 3.28 KB | 2.3-34 KB | AutoAnimate |
| **API Simplicity** | 3 lines of code | 12+ lines | AutoAnimate |
| **Feature Set** | Limited | Comprehensive | Motion |
| **Gesture Controls** | ❌ | ✅ | Motion |
| **Scroll Animations** | ❌ | ✅ | Motion |
| **Layout Animations** | ❌ | ✅ | Motion |
| **SVG Animations** | ❌ | ✅ | Motion |
| **List Animations** | ✅ Automatic | ✅ Manual | AutoAnimate |
| **Accessibility** | ✅ Automatic | ✅ Manual | AutoAnimate |
| **Framework Support** | React, Vue, Svelte, JS | React only | AutoAnimate |
| **Cloudflare Workers** | ✅ | ⚠️ | AutoAnimate |
| **Learning Curve** | Minutes | Hours | AutoAnimate |
| **Performance** | Excellent | Excellent | Tie |

---

## Final Recommendation

**Default to AutoAnimate** for:
- List animations (add/remove/sort)
- Simple accordions
- Toast notifications
- Form validation errors

**Upgrade to Motion** when you need:
- Gestures (drag, hover with fine control)
- Scroll animations or parallax
- Shared element transitions
- SVG path morphing
- Complex choreographed animations

**Use both** when building complex apps with diverse animation needs.

**80/20 Rule**: 80% of your animations can be handled by AutoAnimate, 20% require Motion.

---

## Getting Help

- **AutoAnimate**: https://auto-animate.formkit.com
- **Motion**: https://motion.dev
- **AutoAnimate Skill**: See `../SKILL.md` in this repo
- **Motion Skill**: See `../SKILL.md` in this repo
