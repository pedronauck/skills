# Animation API Reference

## Animatable Values

Motion animates **any CSS value**: `opacity`, `filter`, `background-image`, `mask-image`, `box-shadow`.

### Independent Transforms

Unlike CSS, Motion animates each transform axis independently:

| Property | Description |
|----------|-------------|
| `x`, `y`, `z` | Translation (px by default, accepts strings like `"100%"`) |
| `scale`, `scaleX`, `scaleY` | Scale factor |
| `rotate`, `rotateX`, `rotateY`, `rotateZ` | Rotation (degrees) |
| `skewX`, `skewY` | Skew (degrees) |
| `transformPerspective` | Perspective |
| `originX`, `originY`, `originZ` | Transform origin (0-1 for X/Y, px for Z) |

```tsx
// Combine independent transforms with gestures
<motion.button
  initial={{ y: 10 }}
  animate={{ y: 0 }}
  whileHover={{ scale: 1.1 }}
  whileTap={{ scale: 0.9 }}
/>
```

Enhanced `style` supports transform shorthands statically:

```tsx
<motion.section style={{ x: -20, rotate: 45 }} />
```

### Hardware-Accelerated Transform

Set `transform` directly for GPU compositing (best performance):

```tsx
<motion.li
  initial={{ transform: "translateX(-100px)" }}
  animate={{ transform: "translateX(0px)" }}
  transition={{ type: "spring" }}
/>
```

### Supported Value Types

- Numbers: `0`, `100`
- Strings with units: `"0vh"`, `"10px"`, `"50%"`
- Colors: hex, RGBA, HSLA (freely animatable between each other)
- Complex strings with numbers/colors: `box-shadow`, `background`
- `display: "none"/"block"` and `visibility: "hidden"/"visible"`

### Value Type Conversion

`x`, `y`, `width`, `height`, `top`, `left`, `right`, `bottom` can animate between different units:

```tsx
<motion.div initial={{ x: "100%" }} animate={{ x: "calc(100vw - 50%)" }} />
```

**Animate to/from `"auto"`:**

```tsx
<motion.div initial={{ height: 0 }} animate={{ height: "auto" }} />
```

If combining `height: "auto"` with `display: "none"`, use `visibility: "hidden"` instead — elements with `display: none` can't be measured.

## CSS Variables

### Animating CSS Variables

Animate a CSS variable to affect many children:

```tsx
<motion.ul
  initial={{ "--rotate": "0deg" }}
  animate={{ "--rotate": "360deg" }}
  transition={{ duration: 2, repeat: Infinity }}
>
  <li style={{ transform: "rotate(var(--rotate))" }} />
  <li style={{ transform: "rotate(var(--rotate))" }} />
</motion.ul>
```

Note: Animating CSS variables **always triggers paint**. For better performance, use `MotionValue` composition instead.

### CSS Variables as Targets

```tsx
<motion.li animate={{ backgroundColor: "var(--action-bg)" }} />
```

## SVG Attributes

For SVG, use `attrX` and `attrY` for the `x` and `y` **attributes** (as opposed to transforms):

```tsx
<motion.circle attrX={cx} attrY={cy} />
```

### Path Animations

```tsx
<motion.path
  d="M 0 0 L 100 100"
  initial={{ pathLength: 0, pathOffset: 0 }}
  animate={{ pathLength: 1 }}
  transition={{ duration: 2, ease: "easeInOut" }}
/>
```

- `pathLength`: 0 to 1, draws the path
- `pathOffset`: shifts the start point
- `pathSpacing`: spacing for dashed paths

## Enter Animations

When a `motion` component mounts, it animates from `initial` to `animate`:

```tsx
<motion.li
  initial={{ opacity: 0, scale: 0 }}
  animate={{ opacity: 1, scale: 1 }}
/>
```

Disable enter animation:

```tsx
<motion.div initial={false} animate={{ y: 100 }} />
```

## Exit Animations

Requires wrapping in `AnimatePresence`:

```tsx
<AnimatePresence>
  {isVisible && (
    <motion.div
      key="modal"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    />
  )}
</AnimatePresence>
```

## Keyframes

Animate through a sequence of values:

```tsx
<motion.div animate={{ x: [0, 100, 0] }} />
```

Use `null` for "current value":

```tsx
<motion.div animate={{ x: [null, 100, 0] }} />
```

Control timing with `times` (0-1 values matching keyframe count):

```tsx
<motion.div
  animate={{ x: [0, 100, 0] }}
  transition={{ times: [0, 0.3, 1], duration: 2 }}
/>
```

## Variants

Named animation states with automatic propagation:

```tsx
const container = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.3 }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

<motion.ul variants={container} initial="hidden" animate="visible">
  {items.map(i => <motion.li key={i} variants={item} />)}
</motion.ul>
```

### Dynamic Variants

Pass `custom` to create dynamic variants:

```tsx
const variants = {
  visible: (i: number) => ({
    opacity: 1,
    transition: { delay: i * 0.3 }
  }),
  hidden: { opacity: 0 }
}

{items.map((item, i) => (
  <motion.div custom={i} variants={variants} />
))}
```

### Variant Orchestration

Control children timing within variant transitions:

| Property | Description |
|----------|-------------|
| `delayChildren` | Delay before children start |
| `staggerChildren` | Stagger delay between each child |
| `staggerDirection` | `1` (forward) or `-1` (reverse) |
| `when` | `"beforeChildren"` or `"afterChildren"` |

## Animation Events

```tsx
<motion.div
  onAnimationStart={() => {}}
  onAnimationComplete={(definition) => {}}
  onUpdate={(latest) => {}}  // fires every frame with current values
/>
```
