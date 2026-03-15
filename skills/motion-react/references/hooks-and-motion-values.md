# Hooks & Motion Values Reference

## Motion Values

Motion values are composable, signal-like values that update styles **without re-renders**.

### `useMotionValue`

```tsx
import { motion, useMotionValue } from "motion/react"

function Component() {
  const x = useMotionValue(0)

  return <motion.div style={{ x }} />
}
```

**API:**

| Method | Description |
|--------|-------------|
| `get()` | Get current value |
| `set(value)` | Set value (batched to next frame, no re-render) |
| `jump(value)` | Set value, reset velocity, stop animations, ignore springs |
| `getVelocity()` | Current velocity (per second). Returns 0 for strings. |
| `isAnimating()` | Returns true if animating |
| `stop()` | Stop active animation |
| `on(event, callback)` | Subscribe to events. Returns unsubscribe function. |

**Events**: `"change"`, `"animationStart"`, `"animationComplete"`, `"animationCancel"`.

Pass motion values to multiple components to synchronize them:

```tsx
const x = useMotionValue(0)

<motion.div style={{ x }} />
<motion.div style={{ x }} /> {/* Both move together */}
```

### `useMotionValueEvent`

React-safe event listener (auto-cleans up):

```tsx
import { useMotionValueEvent } from "motion/react"

useMotionValueEvent(x, "change", (latest) => {
  console.log("x changed to", latest)
})

useMotionValueEvent(x, "animationComplete", () => {
  console.log("animation finished")
})
```

## Composition Hooks

### `useTransform`

Create a motion value derived from other motion values:

```tsx
import { useTransform } from "motion/react"

// Range mapping
const opacity = useTransform(x, [-200, 0, 200], [0, 1, 0])

// Function form (recalculates reactively)
const y = useTransform(() => x.get() * 2)

// With custom easing per segment
const color = useTransform(
  scrollYProgress,
  [0, 0.5, 1],
  ["#ff0000", "#00ff00", "#0000ff"]
)
```

**Range mapping signature:**

```tsx
useTransform(
  motionValue,        // input motion value
  inputRange,         // input breakpoints
  outputRange,        // output values at each breakpoint
  { clamp?: boolean } // default true: clamps output to range
)
```

### `useSpring`

Attach a spring to a motion value:

```tsx
import { useSpring } from "motion/react"

// Spring from another motion value
const x = useMotionValue(0)
const springX = useSpring(x, { stiffness: 100, damping: 30, restDelta: 0.001 })

// Spring from a static value (re-animates when value changes)
const scale = useSpring(1)
```

Spring options: `stiffness`, `damping`, `mass`, `bounce`, `visualDuration`, `restSpeed`, `restDelta`.

**Pattern: smooth scroll indicator**

```tsx
const { scrollYProgress } = useScroll()
const scaleX = useSpring(scrollYProgress, {
  stiffness: 100,
  damping: 30,
  restDelta: 0.001,
})
```

**Pattern: spring-dampened drag**

```tsx
const dragX = useMotionValue(0)
const dragY = useMotionValue(0)
const x = useSpring(dragX)
const y = useSpring(dragY)

<motion.div
  drag
  style={{ x: dragX, y: dragY }}
/>
<motion.div style={{ x, y }} /> {/* Follows with spring delay */}
```

### `useVelocity`

Get velocity of a motion value as a new motion value:

```tsx
import { useVelocity } from "motion/react"

const x = useMotionValue(0)
const xVelocity = useVelocity(x)
const xAcceleration = useVelocity(xVelocity) // chain for acceleration

// Tilt based on scroll speed
const { scrollY } = useScroll()
const scrollVelocity = useVelocity(scrollY)
const skewX = useTransform(scrollVelocity, [-1000, 0, 1000], [-10, 0, 10])
```

### `useMotionTemplate`

Build complex CSS strings from motion values:

```tsx
import { useMotionTemplate } from "motion/react"

const x = useMotionValue(0)
const blur = useMotionValue(10)
const filter = useMotionTemplate`blur(${blur}px)`
const transform = useMotionTemplate`translateX(${x}px) rotate(45deg)`

<motion.div style={{ filter }} />
```

## Animation Hooks

### `useAnimate`

Imperative animation control scoped to a component:

```tsx
import { useAnimate } from "motion/react"

function Component() {
  const [scope, animate] = useAnimate()

  useEffect(() => {
    // Selector scoped to scope element's children
    animate("li", { opacity: 1 }, { stagger: 0.1 })
  }, [])

  return <ul ref={scope}>{children}</ul>
}
```

**Animate the scope element directly:**

```tsx
animate(scope.current, { opacity: 1 }, { duration: 1 })
```

**Sequential animations (timeline):**

```tsx
async function sequence() {
  await animate(scope.current, { x: 100 })
  await animate(scope.current, { rotate: 90 })
  await animate("li", { opacity: 1 }, { stagger: 0.1 })
}
```

**With useInView:**

```tsx
const [scope, animate] = useAnimate()
const isInView = useInView(scope)

useEffect(() => {
  if (isInView) {
    animate(scope.current, { opacity: 1 })
  }
}, [isInView])
```

**With usePresence (manual exit animations):**

```tsx
const [isPresent, safeToRemove] = usePresence()
const [scope, animate] = useAnimate()

useEffect(() => {
  if (!isPresent) {
    const exit = async () => {
      await animate("li", { opacity: 0, x: -100 })
      await animate(scope.current, { opacity: 0 })
      safeToRemove()
    }
    exit()
  }
}, [isPresent])
```

All animations started with `animate` auto-cleanup when the component unmounts.

### `useAnimationFrame`

Run a callback every animation frame:

```tsx
import { useAnimationFrame } from "motion/react"

useAnimationFrame((time, delta) => {
  // time: ms since mount
  // delta: ms since last frame
  ref.current.style.transform = `rotate(${time / 10}deg)`
})
```

### `useTime`

Motion value that updates with current time (ms):

```tsx
import { useTime, useTransform } from "motion/react"

const time = useTime()
const rotate = useTransform(time, [0, 2000], [0, 360], { clamp: false })

<motion.div style={{ rotate }} /> {/* Continuous rotation */}
```

## Utility Hooks

### `useDragControls`

See [gestures-and-drag.md](gestures-and-drag.md#usedragcontrols).

### `useReducedMotion`

```tsx
import { useReducedMotion } from "motion/react"

const shouldReduceMotion = useReducedMotion()
// Returns true when user has "prefers-reduced-motion: reduce"
```

### `useIsPresent`

Check if component is still in the DOM (inside AnimatePresence):

```tsx
import { useIsPresent } from "motion/react"

const isPresent = useIsPresent()
// false when component is performing exit animation
```

### `usePresenceData`

Access data passed to AnimatePresence `custom` prop from within exiting children:

```tsx
import { usePresenceData } from "motion/react"

function Slide() {
  const direction = usePresenceData() // value from <AnimatePresence custom={direction}>
}
```

## Components

### `MotionConfig`

Set default transition/reducedMotion for all descendants:

```tsx
import { MotionConfig } from "motion/react"

<MotionConfig
  transition={{ duration: 0.3, ease: "easeInOut" }}
  reducedMotion="user"
>
  <App />
</MotionConfig>
```

### `LazyMotion`

Reduce bundle by loading animation features on demand:

```tsx
import { LazyMotion, domAnimation, m } from "motion/react"

// domAnimation: ~4.6 KB (basic animations)
// domMax: full feature set (gestures, layout, etc.)

<LazyMotion features={domAnimation}>
  <m.div animate={{ opacity: 1 }} />  {/* Use m instead of motion */}
</LazyMotion>

// Async loading
const loadFeatures = () => import("./motion-features").then(mod => mod.default)
<LazyMotion features={loadFeatures} strict>
  <m.div />
</LazyMotion>
```

`strict` mode warns if `motion` components are used instead of `m`.
