---
name: motion-react
description: |
  Build React animations with Motion (formerly Framer Motion) - gestures (drag, hover, tap),
  scroll effects, spring physics, layout animations, SVG, exit animations, and motion values.
  Use when: building React animations, adding hover/tap/drag interactions, scroll-triggered effects,
  layout transitions, shared element animations, exit animations with AnimatePresence, or working
  with motion values and springs. Triggers: "animate", "motion component", "framer motion",
  "gesture", "drag", "scroll animation", "layout animation", "exit animation", "spring",
  "whileHover", "whileTap", "whileInView", "AnimatePresence", "layoutId", "useScroll",
  "useSpring", "useAnimate", "motion value", "reorder", "parallax".
---

# Motion for React

Package: `motion` (formerly `framer-motion`). Import from `"motion/react"`.

## Installation

```bash
pnpm add motion
```

## Imports

```tsx
// Standard React (Vite, CRA, Pages Router)
import { motion, AnimatePresence } from "motion/react"

// Next.js App Router — use "motion/react-client" for RSC tree-shaking
"use client"
import * as motion from "motion/react-client"

// Minimal bundle (2.3 KB) — imperative API only
import { useAnimate } from "motion/react-mini"

// Reduced bundle (4.6 KB) — LazyMotion + m component
import { LazyMotion, domAnimation, m } from "motion/react"
```

## Motion Component

Every HTML/SVG element has a `motion` counterpart:

```tsx
<motion.div />
<motion.button />
<motion.svg />
<motion.circle />
```

Custom components: wrap with `motion.create()`:

```tsx
const MotionBox = motion.create(Box)
// forwardRef required — the ref must reach a DOM node
```

## Core Animation Props

```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}     // mount state (or false to skip)
  animate={{ opacity: 1, y: 0 }}      // target state
  exit={{ opacity: 0, y: -20 }}       // unmount state (needs AnimatePresence)
  transition={{ type: "spring", bounce: 0.25 }}
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  whileFocus={{ borderColor: "#00f" }}
  whileDrag={{ scale: 1.1 }}
  whileInView={{ opacity: 1 }}
  viewport={{ once: true, margin: "-100px" }}
/>
```

## Animatable Values

Motion animates **any CSS value**: `opacity`, `filter`, `background-image`, `mask-image`.

**Independent transforms** (not possible in CSS alone):
- Translate: `x`, `y`, `z`
- Scale: `scale`, `scaleX`, `scaleY`
- Rotate: `rotate`, `rotateX`, `rotateY`, `rotateZ`
- Skew: `skewX`, `skewY`
- Origin: `originX`, `originY`, `originZ`

**Value types**: numbers, strings with units (`"100px"`), colors (hex/rgba/hsla), `"auto"` for width/height.

**Hardware acceleration**: set `transform` directly for GPU compositing:

```tsx
<motion.li
  initial={{ transform: "translateX(-100px)" }}
  animate={{ transform: "translateX(0px)" }}
  transition={{ type: "spring" }}
/>
```

## Keyframes

Pass arrays to animate through a sequence:

```tsx
<motion.div animate={{ x: [0, 100, 0] }} />

// null = "use current value"
<motion.div animate={{ x: [null, 100, 0] }} />
```

## Variants

Named animation states for orchestrated animations:

```tsx
const list = {
  visible: {
    transition: { staggerChildren: 0.1 }
  },
  hidden: {}
}

const item = {
  visible: { opacity: 1, y: 0 },
  hidden: { opacity: 0, y: 20 }
}

<motion.ul initial="hidden" animate="visible" variants={list}>
  <motion.li variants={item} />
  <motion.li variants={item} />
</motion.ul>
```

Variants propagate through the tree. Children inherit `animate`/`initial`/`exit` from parent.

## AnimatePresence — Exit Animations

```tsx
import { AnimatePresence } from "motion/react"

<AnimatePresence>
  {isVisible && (
    <motion.div
      key="modal"           // REQUIRED: unique key
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    />
  )}
</AnimatePresence>
```

**Critical rules:**
1. AnimatePresence **must stay mounted** — never wrap it in a conditional
2. Direct children **must have unique `key` props**
3. `exit` prop only works on `motion` components inside AnimatePresence

```tsx
// WRONG — AnimatePresence unmounts with condition
{show && <AnimatePresence><motion.div /></AnimatePresence>}

// CORRECT — condition inside AnimatePresence
<AnimatePresence>{show && <motion.div key="k" />}</AnimatePresence>
```

**Modes**: `"sync"` (default), `"wait"` (sequential enter/exit), `"popLayout"` (pop exiting element out of flow).

**Slideshow pattern** — change `key` to trigger exit+enter:

```tsx
<AnimatePresence mode="wait">
  <motion.img
    key={image.src}
    initial={{ x: 300, opacity: 0 }}
    animate={{ x: 0, opacity: 1 }}
    exit={{ x: -300, opacity: 0 }}
  />
</AnimatePresence>
```

**Dynamic exit data** — pass via `custom` prop + `usePresenceData`:

```tsx
<AnimatePresence custom={direction}>
  <Slide key={id} />
</AnimatePresence>

// Inside Slide:
const direction = usePresenceData()
```

## Transitions

For full transition API details, see [references/transitions-api.md](references/transitions-api.md).

**Quick reference:**

```tsx
// Spring (default for physical props: x, y, scale)
transition={{ type: "spring", bounce: 0.25 }}
transition={{ type: "spring", stiffness: 300, damping: 20 }}
transition={{ type: "spring", visualDuration: 0.5, bounce: 0.25 }}

// Tween (default for opacity, color)
transition={{ duration: 0.3, ease: "easeInOut" }}

// Per-value transitions
transition={{
  default: { type: "spring" },
  opacity: { duration: 0.2, ease: "linear" }
}}

// Orchestration
transition={{ delay: 0.5, repeat: Infinity, repeatType: "reverse" }}

// Global default
<MotionConfig transition={{ duration: 0.3 }}>
```

## Layout Animations

For full layout animation details, see [references/layout-animations.md](references/layout-animations.md).

```tsx
// Auto-animate any layout change
<motion.div layout />

// Shared element transitions
<motion.div layoutId="underline" />

// Customize layout transition
<motion.div layout transition={{ layout: { duration: 0.3 } }} />
```

## Gestures & Drag

For full gesture/drag API, see [references/gestures-and-drag.md](references/gestures-and-drag.md).

```tsx
<motion.div
  whileHover={{ scale: 1.1 }}
  whileTap={{ scale: 0.9 }}
  drag                           // enable both axes
  drag="x"                       // constrain to x-axis
  dragConstraints={{ left: -100, right: 100 }}
  dragElastic={0.2}
/>
```

## Scroll Animations

For full scroll API, see [references/scroll-animations.md](references/scroll-animations.md).

```tsx
// Viewport-triggered
<motion.div
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true }}
/>

// Scroll-linked progress bar
const { scrollYProgress } = useScroll()
<motion.div style={{ scaleX: scrollYProgress }} />

// Element scroll progress
const ref = useRef(null)
const { scrollYProgress } = useScroll({
  target: ref,
  offset: ["start end", "end start"]
})
```

## Hooks & Motion Values

For full hooks API, see [references/hooks-and-motion-values.md](references/hooks-and-motion-values.md).

```tsx
// Manual motion values (no re-renders)
const x = useMotionValue(0)
const opacity = useTransform(x, [-200, 0, 200], [0, 1, 0])
<motion.div drag="x" style={{ x, opacity }} />

// Smooth spring following
const springX = useSpring(x, { stiffness: 100, damping: 30 })

// Imperative animation control
const [scope, animate] = useAnimate()
animate("li", { opacity: 1 }, { stagger: 0.1 })

// Event listener (no re-render)
useMotionValueEvent(scrollY, "change", (v) => console.log(v))
```

## Bundle Optimization

| Approach | Size | What you get |
|----------|------|-------------|
| `motion/react` | ~34 KB | Full API |
| `LazyMotion` + `m` | ~4.6 KB | Declarative animations, no gestures |
| `motion/react-mini` | ~2.3 KB | `useAnimate` only |

```tsx
// LazyMotion pattern
import { LazyMotion, domAnimation, m } from "motion/react"

<LazyMotion features={domAnimation}>
  <m.div animate={{ opacity: 1 }} />
</LazyMotion>
```

## Accessibility

```tsx
<MotionConfig reducedMotion="user">
  <App />
</MotionConfig>
```

Options: `"user"` (respect OS setting), `"always"` (force instant), `"never"` (ignore).

Hook: `useReducedMotion()` returns `true` when user prefers reduced motion.

## Tailwind Integration

Let each library handle its strength. **Remove Tailwind `transition-*` classes** — they conflict.

```tsx
// WRONG — Tailwind transition conflicts with Motion
<motion.div className="transition-all duration-300" animate={{ x: 100 }} />

// CORRECT — Tailwind for styling, Motion for animation
<motion.div className="rounded-lg bg-blue-600 p-4" whileHover={{ scale: 1.05 }} />
```

## Next.js App Router

Motion components require client-side rendering. Use `"motion/react-client"` for optimal tree-shaking:

```tsx
// components/motion-client.tsx
"use client"
import * as motion from "motion/react-client"
export { motion }

// app/page.tsx (Server Component)
import { motion } from "@/components/motion-client"
<motion.div animate={{ opacity: 1 }} />
```

## Common Pitfalls

1. **Exit animations not firing** — AnimatePresence must stay mounted; children need unique `key`
2. **Tailwind transition conflict** — Remove `transition-*` classes from motion elements
3. **`height: "auto"` + `display: "none"`** — Use `visibility: "hidden"` instead
4. **Layout animations in scrollable containers** — Add `layoutScroll` prop to scroll parent
5. **Layout animations in fixed elements** — Add `layoutRoot` prop to fixed parent
6. **Percentage transforms + layout** — Convert to pixels; percentage values break FLIP calculation
7. **`popLayout` mode** — Custom components must use `forwardRef` to forward ref to DOM node
8. **AnimatePresence `propagate`** — Set to `true` on nested AnimatePresence to fire child exits

## References

- **Animation API details**: [references/animation-api.md](references/animation-api.md)
- **Transition types & spring config**: [references/transitions-api.md](references/transitions-api.md)
- **Gestures & drag**: [references/gestures-and-drag.md](references/gestures-and-drag.md)
- **Layout animations**: [references/layout-animations.md](references/layout-animations.md)
- **Scroll animations**: [references/scroll-animations.md](references/scroll-animations.md)
- **Hooks & motion values**: [references/hooks-and-motion-values.md](references/hooks-and-motion-values.md)
