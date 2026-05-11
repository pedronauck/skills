# Motion Performance Optimization

This guide covers techniques to optimize Motion animations for production, including bundle size reduction, runtime performance improvements, and best practices.

---

## Bundle Size Optimization

### Problem: Full Motion Component is 34 KB

The full `motion` component includes all animation features, resulting in ~34 KB minified+gzipped. For many use cases, this is overkill.

---

### Solution 1: LazyMotion (Recommended)

**Reduces bundle from 34 KB → 4.6 KB**

LazyMotion loads animation features on-demand instead of bundling everything upfront.

**Setup**:
```tsx
import { LazyMotion, domAnimation, m } from "motion/react"

function App() {
  return (
    <LazyMotion features={domAnimation}>
      {/* Use 'm' instead of 'motion' */}
      <m.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        whileHover={{ scale: 1.1 }}
      >
        Content
      </m.div>
    </LazyMotion>
  )
}
```

**Key changes**:
1. Wrap app in `<LazyMotion features={domAnimation}>`
2. Use `m` component instead of `motion`
3. Import `m` from `motion/react` (not `motion`)

**Features included with `domAnimation`**:
- ✅ Transform animations (x, y, scale, rotate, etc.)
- ✅ Opacity animations
- ✅ Gestures (hover, tap, drag, pan)
- ✅ Layout animations
- ✅ useScroll, useTransform hooks
- ❌ SVG path animations (use `domMax` instead)
- ❌ Custom value types

**When to use `domMax` instead of `domAnimation`**:
```tsx
import { LazyMotion, domMax, m } from "motion/react"

<LazyMotion features={domMax}>
  {/* Now includes SVG path animations */}
  <m.path d="..." animate={{ pathLength: 1 }} />
</LazyMotion>
```

**Bundle size**: domAnimation (4.6 KB), domMax (~6 KB)

---

### Solution 2: useAnimate Mini (Smallest)

**Reduces bundle from 34 KB → 2.3 KB**

The `useAnimate` mini variant is the smallest React animation library available. Use for imperative animations.

**Setup**:
```tsx
import { useAnimate } from "motion/react"
import { useEffect } from "react"

function Component() {
  const [scope, animate] = useAnimate()

  useEffect(() => {
    animate(scope.current, { opacity: 1, x: 0 })
  }, [])

  return (
    <div ref={scope} style={{ opacity: 0, transform: "translateX(-20px)" }}>
      Content
    </div>
  )
}
```

**Pros**:
- ✅ Smallest bundle size (2.3 KB)
- ✅ Imperative API (full control)
- ✅ No component overhead

**Cons**:
- ❌ More verbose than declarative API
- ❌ Less ergonomic for complex animations

**When to use**:
- Bundle size is absolutely critical
- You prefer imperative animations
- Simple animations (fade in, slide in, etc.)

---

### Solution 3: useAnimate Hybrid

**Reduces bundle from 34 KB → 17 KB**

The hybrid version includes more features than mini but less than full.

**Setup**:
```tsx
import { useAnimate, stagger } from "motion/react"

function Component() {
  const [scope, animate] = useAnimate()

  const handleAnimate = () => {
    animate("li", { opacity: 1, x: 0 }, { delay: stagger(0.1) })
  }

  return (
    <ul ref={scope}>
      {items.map(item => <li key={item.id}>{item.text}</li>)}
    </ul>
  )
}
```

**Bundle size**: 17 KB

---

### Solution 4: Remove Unused Features

If you only use Motion for specific features, import only what you need:

**Example - Only scroll animations**:
```tsx
import { useScroll, useTransform } from "motion/react"
import { useRef } from "react"

function Component() {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({ container: ref })
  const y = useTransform(scrollYProgress, [0, 1], [0, -100])

  return (
    <div ref={ref} style={{ transform: `translateY(${y}px)` }}>
      Content
    </div>
  )
}
```

**No `motion` component imported** → smaller bundle

---

### Bundle Size Comparison

| Approach | Bundle Size | Features | Best For |
|----------|-------------|----------|----------|
| **Full motion** | 34 KB | All features | Kitchen sink approach |
| **LazyMotion + domAnimation** | 4.6 KB | Most features | **Recommended default** |
| **LazyMotion + domMax** | ~6 KB | All features except custom | SVG animations |
| **useAnimate hybrid** | 17 KB | Imperative + stagger | Imperative animations |
| **useAnimate mini** | 2.3 KB | Basic imperative | **Smallest bundle** |
| **Hooks only** | <5 KB | Specific features | Scroll/transform only |

**Recommendation**: Start with LazyMotion + domAnimation (4.6 KB) for 90% of use cases.

---

## Runtime Performance Optimization

### 1. Add `willChange` for Transforms

**Problem**: Browser doesn't know which properties will animate, causing reflows.

**Solution**: Tell browser to optimize for animation.

```tsx
<motion.div
  style={{ willChange: "transform" }}
  animate={{ x: 100, rotate: 45 }}
/>
```

**Also add for**:
- `opacity`
- `backgroundColor`
- `clipPath`
- `filter`

**How it works**:
- Browser promotes element to its own layer
- Uses GPU compositing
- Avoids reflow/repaint during animation

**Warning**: Don't overuse! Only add to elements that actually animate.

---

### 2. Use Hardware-Accelerated Properties

**Good properties** (GPU-accelerated):
- ✅ `transform` (x, y, scale, rotate, skew)
- ✅ `opacity`
- ✅ `filter` (blur, brightness, etc.)

**Bad properties** (causes reflow):
- ❌ `width`, `height`
- ❌ `top`, `left`, `right`, `bottom`
- ❌ `padding`, `margin`

**Example - Wrong**:
```tsx
<motion.div
  animate={{ width: 300, height: 200 }} // ❌ Causes layout reflow
/>
```

**Example - Correct**:
```tsx
<motion.div
  animate={{ scale: 1.5 }} // ✅ GPU-accelerated transform
/>
```

**Rule**: Prefer `transform` over layout properties.

---

### 3. Use `layout` Prop for FLIP Animations

**Problem**: Animating width/height directly causes reflow.

**Solution**: Use `layout` prop for FLIP technique (First, Last, Invert, Play).

```tsx
<motion.div layout>
  {isExpanded ? <LargeContent /> : <SmallContent />}
</motion.div>
```

**How it works**:
1. Measures element before change (First)
2. Applies change immediately (Last)
3. Inverts with transform to match first position
4. Animates to last position (Play)

**Result**: Smooth animation without reflow, all via GPU-accelerated transforms.

---

### 4. Optimize Scroll Animations

Motion uses native ScrollTimeline API when available for hardware-accelerated scroll animations.

**Setup**:
```tsx
import { useScroll, useTransform } from "motion/react"

const { scrollYProgress } = useScroll()
const y = useTransform(scrollYProgress, [0, 1], [0, -300])

<motion.div style={{ y }}>
  Content
</motion.div>
```

**Performance**:
- ✅ Runs on compositor thread (not main thread)
- ✅ 120fps on capable devices
- ✅ No JavaScript execution on scroll

**Fallback**: On browsers without ScrollTimeline API, Motion falls back to JavaScript `requestAnimationFrame`.

---

### 5. Debounce Complex Calculations

For expensive calculations in scroll/transform hooks, debounce updates:

**Problem**:
```tsx
const { scrollY } = useScroll()

// Recalculates on every pixel scrolled
const complexValue = useTransform(scrollY, (value) => {
  return expensiveCalculation(value) // ❌ Too frequent
})
```

**Solution**:
```tsx
const { scrollY } = useScroll()

// Only update when scroll changes by 10px
const complexValue = useTransform(scrollY, (value) => {
  return Math.floor(value / 10) * 10
})
```

---

### 6. Use `transition` Type Wisely

Different transition types have different performance characteristics:

**Spring** (default):
```tsx
transition={{ type: "spring", stiffness: 100, damping: 10 }}
```
- ✅ Natural, physics-based motion
- ❌ More JavaScript calculation

**Tween**:
```tsx
transition={{ type: "tween", duration: 0.3, ease: "easeOut" }}
```
- ✅ Predictable timing
- ✅ Less JavaScript calculation
- ❌ Less natural than spring

**Recommendation**: Use tween for simple animations, spring for interactive gestures.

---

## Large Lists Optimization

### Problem: 50-100+ Animated Items Cause Severe Slowdown

Animating many items simultaneously overwhelms the browser.

---

### Solution 1: Virtualization (Recommended)

Only render visible items.

**Install**:
```bash
pnpm add react-window
# or
pnpm add react-virtuoso
# or
pnpm add @tanstack/react-virtual
```

**Example with react-window**:
```tsx
import { FixedSizeList } from 'react-window'
import { motion } from 'motion/react'

function VirtualizedList({ items }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {({ index, style }) => (
        <motion.div
          style={style}
          layout
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          {items[index].text}
        </motion.div>
      )}
    </FixedSizeList>
  )
}
```

**Benefits**:
- ✅ Only renders ~20 items at a time (instead of 1000+)
- ✅ Dramatically reduces DOM nodes
- ✅ Maintains smooth 60fps

**Drawback**: Slightly more complex setup

---

### Solution 2: Stagger with `delayChildren`

For moderately-sized lists (10-30 items), use stagger to spread out animations:

```tsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05, // 50ms delay between each child
      delayChildren: 0.1,    // 100ms delay before first child
    }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

<motion.ul variants={container} initial="hidden" animate="show">
  {items.map(item => (
    <motion.li key={item.id} variants={item}>
      {item.text}
    </motion.li>
  ))}
</motion.ul>
```

**Benefits**:
- ✅ Avoids animating all items simultaneously
- ✅ Creates pleasing wave effect
- ✅ Reduces performance spike

**Limit**: Still struggles above ~50 items

---

### Solution 3: Lazy Load with `whileInView`

Only animate items when they enter viewport:

```tsx
{items.map(item => (
  <motion.div
    key={item.id}
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, margin: "-100px" }}
  >
    {item.content}
  </motion.div>
))}
```

**Benefits**:
- ✅ Only animates visible items
- ✅ Spreads performance cost over time
- ✅ No virtualization library needed

**Drawback**: Doesn't help with initial render if all items visible

---

### Solution 4: Simplify Animations

For very large lists, simplify or remove animations:

```tsx
const useReducedAnimations = items.length > 50

<motion.div
  initial={{ opacity: useReducedAnimations ? 1 : 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: useReducedAnimations ? 0 : 0.3 }}
>
  {item.content}
</motion.div>
```

---

### Performance Comparison (1000 Items)

| Approach | FPS | DOM Nodes | User Experience |
|----------|-----|-----------|-----------------|
| **No optimization** | 5-10 fps | 1000+ | Unusable, browser hangs |
| **Stagger only** | 15-20 fps | 1000+ | Laggy, still poor |
| **Virtualization** | 60 fps | ~20 | Smooth, production-ready |
| **whileInView** | 40-50 fps | 1000+ | Acceptable for long lists |
| **Simplified animations** | 50-60 fps | 1000+ | Smooth but less polished |

**Recommendation**: Use virtualization for lists with 50+ items.

---

## AnimatePresence Optimization

### 1. Use `mode` Prop

**Wait mode** (sequential):
```tsx
<AnimatePresence mode="wait">
  {isVisible && <motion.div key="content">Content</motion.div>}
</AnimatePresence>
```

- Waits for exit animation to complete before entering
- Prevents both elements from being in DOM simultaneously
- Better performance

**Sync mode** (simultaneous):
```tsx
<AnimatePresence mode="sync">
  {isVisible && <motion.div key="content">Content</motion.div>}
</AnimatePresence>
```

- Enter and exit happen simultaneously
- More DOM nodes temporarily
- Higher performance cost

**Recommendation**: Use `mode="wait"` for modals/dialogs, `mode="sync"` for crossfades.

---

### 2. Limit AnimatePresence Usage

**Problem**: Wrapping entire app in AnimatePresence adds overhead.

**Solution**: Only wrap components that actually exit:

**Bad**:
```tsx
<AnimatePresence>
  <Layout>
    <StaticHeader />
    <DynamicContent />
    <StaticFooter />
  </Layout>
</AnimatePresence>
```

**Good**:
```tsx
<Layout>
  <StaticHeader />
  <AnimatePresence>
    <DynamicContent />
  </AnimatePresence>
  <StaticFooter />
</Layout>
```

---

## Layout Animation Performance

### 1. Use `layoutId` for Shared Elements

**Problem**: Multiple separate layout animations calculated independently.

**Solution**: Use `layoutId` to connect related elements:

```tsx
// Card view
<motion.div layoutId={card.id}>
  <CardPreview />
</motion.div>

// Detail view
<motion.div layoutId={card.id}>
  <CardDetail />
</motion.div>
```

**Performance**: Motion knows these are the same element, optimizes FLIP calculation.

---

### 2. Add `layoutRoot` for Fixed Elements

**Problem**: Fixed-position elements cause expensive layout calculations.

**Solution**: Mark as layout root to isolate calculations:

```tsx
<motion.div
  layoutRoot
  layout
  className="fixed top-0 left-0"
>
  Fixed content
</motion.div>
```

---

### 3. Add `layoutScroll` for Scrollable Containers

**Problem**: Layout animations in scrolled containers are incomplete/broken.

**Solution**: Add `layoutScroll` to account for scroll offset:

```tsx
<motion.div
  layoutScroll
  className="overflow-auto h-96"
>
  {items.map(item => (
    <motion.div key={item.id} layout>
      {item.content}
    </motion.div>
  ))}
</motion.div>
```

---

## Gesture Performance

### 1. Use `dragMomentum={false}` When Not Needed

**Problem**: Momentum calculations add overhead.

**Solution**: Disable if you don't need inertia:

```tsx
<motion.div
  drag
  dragMomentum={false} // Disable inertia
>
  Drag me
</motion.div>
```

**Use momentum** for: Carousels, swiping
**Disable momentum** for: Precise positioning, drag-to-reorder

---

### 2. Set `dragElastic` Lower

**Problem**: Higher elasticity = more calculations.

**Solution**: Use 0-0.2 for most cases:

```tsx
<motion.div
  drag
  dragElastic={0.1} // Low elasticity
>
  Drag me
</motion.div>
```

**Default**: 0.5 (high)
**Recommended**: 0.1-0.2 (medium)
**Performance mode**: 0 (none)

---

## Measuring Performance

### 1. React DevTools Profiler

**Enable**:
1. Install React DevTools
2. Open "Profiler" tab
3. Click record
4. Trigger animations
5. Stop recording

**Look for**:
- Flame graph spikes during animations
- Components re-rendering unnecessarily
- Long commit times

---

### 2. Browser Performance Tab

**Enable**:
1. Open Chrome DevTools
2. "Performance" tab
3. Click record
4. Trigger animations
5. Stop recording

**Look for**:
- Frame rate (should be 60fps or 120fps)
- Long JavaScript tasks (should be <16ms)
- Layout reflows (should be minimal)
- Paint operations (should be green, not red)

---

### 3. Frame Rate Monitor

Add visual FPS counter during development:

```tsx
import { useState, useEffect } from "react"

function FPSMonitor() {
  const [fps, setFps] = useState(0)

  useEffect(() => {
    let lastTime = performance.now()
    let frames = 0

    function loop() {
      frames++
      const now = performance.now()
      if (now >= lastTime + 1000) {
        setFps(Math.round((frames * 1000) / (now - lastTime)))
        lastTime = now
        frames = 0
      }
      requestAnimationFrame(loop)
    }

    loop()
  }, [])

  return (
    <div className="fixed top-4 right-4 bg-black text-white p-2 rounded text-sm">
      {fps} FPS
    </div>
  )
}
```

**Target**: 60 FPS (or 120 FPS on high-refresh displays)

---

## Production Checklist

Before deploying Motion animations, verify:

- [ ] Bundle size optimized (LazyMotion or useAnimate)
- [ ] `willChange` added for animated transforms
- [ ] Only GPU-accelerated properties used (transform, opacity)
- [ ] `layout` prop used instead of animating width/height directly
- [ ] Large lists use virtualization (50+ items)
- [ ] Scroll animations use `whileInView` or `useScroll`
- [ ] AnimatePresence only wraps necessary components
- [ ] `mode="wait"` used for modals (if applicable)
- [ ] `layoutScroll` added to scrollable containers
- [ ] `layoutRoot` added to fixed elements
- [ ] Tested on low-end devices (throttle CPU in DevTools)
- [ ] Tested with `prefers-reduced-motion` enabled
- [ ] Frame rate verified (60fps minimum)
- [ ] No console warnings from Motion

---

## Performance Budget

Recommended limits for production:

| Metric | Target | Maximum |
|--------|--------|---------|
| **Bundle size (Motion)** | <5 KB | 10 KB |
| **Total JavaScript** | <200 KB | 300 KB |
| **Frame rate** | 60 FPS | 40 FPS minimum |
| **Animated elements (simultaneous)** | <20 | <50 |
| **AnimatePresence wrappers** | <5 | <10 |
| **Layout animations (simultaneous)** | <10 | <20 |

---

## Common Performance Anti-Patterns

### ❌ Anti-Pattern 1: Animating All List Items on Mount

```tsx
{items.map(item => (
  <motion.div
    key={item.id}
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }} // ❌ All 100 items animate at once
  >
    {item.content}
  </motion.div>
))}
```

**Fix**: Use stagger or `whileInView`:
```tsx
const container = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.05 }
  }
}

<motion.div variants={container} initial="hidden" animate="show">
  {items.map(item => (
    <motion.div key={item.id} variants={item}>
      {item.content}
    </motion.div>
  ))}
</motion.div>
```

---

### ❌ Anti-Pattern 2: No `key` Props with AnimatePresence

```tsx
<AnimatePresence>
  {items.map(item => (
    <motion.div> {/* ❌ Missing key */}
      {item.content}
    </motion.div>
  ))}
</AnimatePresence>
```

**Fix**: Always add unique `key` props:
```tsx
<AnimatePresence>
  {items.map(item => (
    <motion.div key={item.id}> {/* ✅ Unique key */}
      {item.content}
    </motion.div>
  ))}
</AnimatePresence>
```

---

### ❌ Anti-Pattern 3: Animating Non-Accelerated Properties

```tsx
<motion.div
  animate={{ width: 300, top: 100 }} // ❌ Causes reflow
/>
```

**Fix**: Use transforms:
```tsx
<motion.div
  animate={{ scale: 1.5, y: 100 }} // ✅ GPU-accelerated
/>
```

---

### ❌ Anti-Pattern 4: Full Motion Bundle for Simple Use Case

```tsx
import { motion } from "motion/react" // ❌ 34 KB for simple fade

<motion.div animate={{ opacity: 1 }}>Content</motion.div>
```

**Fix**: Use LazyMotion or useAnimate:
```tsx
import { LazyMotion, domAnimation, m } from "motion/react"

<LazyMotion features={domAnimation}>
  <m.div animate={{ opacity: 1 }}>Content</m.div>
</LazyMotion>
```

---

## Getting Help

- **Performance Issues**: https://github.com/motiondivision/motion/issues
- **Bundle Size Analysis**: https://bundlephobia.com/package/motion
- **Official Optimization Guide**: https://motion.dev/docs/react-reduce-bundle-size

---

**Key Takeaway**: For 90% of use cases, use **LazyMotion + domAnimation** (4.6 KB) and follow the optimization checklist above. This provides excellent performance while maintaining a small bundle size.
