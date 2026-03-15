# Scroll Animations Reference

## Viewport-Triggered Animations

### `whileInView`

Animate when element enters the viewport:

```tsx
<motion.div
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
/>
```

### `viewport` Options

```tsx
<motion.div
  whileInView={{ opacity: 1 }}
  viewport={{
    once: true,           // only animate once (default: false)
    margin: "-100px",     // trigger margin (CSS margin syntax)
    amount: 0.5,          // 0-1, fraction visible to trigger (default: "some")
    root: scrollRef,      // scroll container ref (default: window)
  }}
/>
```

### `onViewportEnter` / `onViewportLeave`

```tsx
<motion.div
  onViewportEnter={(entry) => console.log("entered")}
  onViewportLeave={(entry) => console.log("left")}
  viewport={{ once: true }}
/>
```

## `useInView` Hook

React hook that returns `true` when element is in viewport:

```tsx
import { useInView } from "motion/react"

function Component() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  return (
    <div ref={ref}>
      {isInView && <span>Visible!</span>}
    </div>
  )
}
```

Options: `{ root, margin, amount, once, initial }`.

`initial` (default: `true`): the value returned before detection starts. Set to `false` to avoid hydration mismatch.

## `usePageInView` Hook

Detects if the current page/tab is visible:

```tsx
import { usePageInView } from "motion/react"

function Component() {
  const isPageInView = usePageInView()
  // Pause expensive animations when tab is hidden
}
```

## `useScroll` Hook

Creates scroll-linked motion values:

```tsx
import { useScroll } from "motion/react"

const { scrollX, scrollY, scrollXProgress, scrollYProgress } = useScroll()
```

Returns four motion values:
- `scrollX` / `scrollY`: absolute scroll position (px)
- `scrollXProgress` / `scrollYProgress`: progress between offsets (0-1)

**Performance**: Uses native `ScrollTimeline` API when available for hardware acceleration.

### Page Scroll Progress Bar

```tsx
function ProgressBar() {
  const { scrollYProgress } = useScroll()

  return (
    <motion.div
      style={{
        scaleX: scrollYProgress,
        position: "fixed",
        top: 0, left: 0, right: 0,
        height: 4,
        originX: 0,
        backgroundColor: "#ff0088",
      }}
    />
  )
}
```

### Element Scroll Progress

Track an element's scroll progress relative to its container:

```tsx
const ref = useRef(null)
const { scrollYProgress } = useScroll({
  target: ref,
  offset: ["start end", "end start"]
})

<div ref={ref}>
  <motion.div style={{ opacity: scrollYProgress }} />
</div>
```

### Container Scroll

Track scroll inside a specific container:

```tsx
const containerRef = useRef(null)
const { scrollYProgress } = useScroll({ container: containerRef })

<div ref={containerRef} style={{ overflow: "scroll" }}>
  {/* scrollable content */}
</div>
```

### Scroll Offsets

`offset` defines the start and end of the scroll range as an array of two intersection descriptions:

```tsx
offset: ["start end", "end start"]
//        ↑ target  ↑ container
```

Each intersection is `"<target-edge> <container-edge>"`:

| Edge | Description |
|------|-------------|
| `"start"` | Top of element/container |
| `"center"` | Center |
| `"end"` | Bottom |
| `0` - `1` | Normalized position |
| `"100px"` | Pixel offset |

**Common offset patterns:**

```tsx
// Element enters bottom, leaves top
offset: ["start end", "end start"]

// Element reaches center of viewport
offset: ["start center", "end center"]

// Full page scroll
offset: ["start", "end"]   // (default for page scroll)
```

## Composing with Motion Values

### Parallax with `useTransform`

```tsx
const { scrollYProgress } = useScroll()
const y = useTransform(scrollYProgress, [0, 1], [0, -300])
const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [1, 1, 0])

<motion.div style={{ y, opacity }} />
```

### Smooth Scroll Indicator with `useSpring`

```tsx
const { scrollYProgress } = useScroll()
const scaleX = useSpring(scrollYProgress, {
  stiffness: 100,
  damping: 30,
  restDelta: 0.001,
})

<motion.div style={{ scaleX }} />
```

### Multi-Layer Parallax

```tsx
function ParallaxHero() {
  const { scrollYProgress } = useScroll()
  const bgY = useTransform(scrollYProgress, [0, 1], [0, -100])
  const fgY = useTransform(scrollYProgress, [0, 1], [0, -300])

  return (
    <div style={{ position: "relative", height: "200vh" }}>
      <motion.div style={{ y: bgY }} className="bg-layer" />
      <motion.div style={{ y: fgY }} className="fg-layer" />
    </div>
  )
}
```

### Element-Based Scroll Transform

```tsx
const ref = useRef(null)
const { scrollYProgress } = useScroll({
  target: ref,
  offset: ["start end", "end start"],
})
const scale = useTransform(scrollYProgress, [0, 0.5, 1], [0.8, 1, 0.8])

<motion.div ref={ref} style={{ scale }}>
  Scales up as it enters viewport, down as it leaves
</motion.div>
```
