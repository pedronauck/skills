# Transitions API Reference

A `transition` defines the animation type between two values.

```tsx
<motion.div
  animate={{ x: 100 }}
  transition={{ ease: "easeOut", duration: 2 }}
/>
```

## Setting Transitions

On any animation prop:

```tsx
<motion.div whileHover={{ scale: 1.1, transition: { duration: 0.2 } }} />
```

### Value-Specific Transitions

```tsx
<motion.li
  animate={{ x: 0, opacity: 1 }}
  transition={{
    default: { type: "spring" },
    opacity: { ease: "linear", duration: 0.2 }
  }}
/>
```

### Default via MotionConfig

```tsx
<MotionConfig transition={{ duration: 0.4, ease: "easeInOut" }}>
  <App />
</MotionConfig>
```

### Inheritance

By default, higher-specificity transitions **replace** lower ones. Use `inherit: true` to merge:

```tsx
<MotionConfig transition={{ duration: 1, ease: "linear" }}>
  <motion.div
    animate={{ x: 100 }}
    transition={{ inherit: true, ease: "easeInOut" }}
    // duration: 1 inherited, ease: "easeInOut" overridden
  />
</MotionConfig>
```

## Transition Types

### `type: "tween"` (Duration-Based)

| Property | Default | Description |
|----------|---------|-------------|
| `duration` | `0.3` (or `0.8` for keyframes) | Duration in seconds |
| `ease` | `"easeOut"` | Easing function |
| `times` | evenly spread | Position of each keyframe (0-1) |

**Named easings**: `"linear"`, `"easeIn"`, `"easeOut"`, `"easeInOut"`, `"circIn"`, `"circOut"`, `"circInOut"`, `"backIn"`, `"backOut"`, `"backInOut"`, `"anticipate"`.

**Custom easing**: cubic bezier array `[0.17, 0.67, 0.83, 0.67]` or JS function `(t) => t`.

**Keyframe easings**: array of easings between each pair:

```tsx
<motion.div
  animate={{ x: [0, 100, 0] }}
  transition={{ ease: ["easeIn", "easeOut"] }}
/>
```

### `type: "spring"` (Physics-Based)

Two configuration modes:

**Duration-based** (easier to control):

| Property | Default | Description |
|----------|---------|-------------|
| `duration` | `0.8` | Animation duration |
| `bounce` | `0.25` | Bounciness: 0 (none) to 1 (extreme) |
| `visualDuration` | — | Time for the "bulk" of motion (overrides duration) |

```tsx
transition={{ type: "spring", visualDuration: 0.5, bounce: 0.25 }}
```

**Physics-based** (more natural, incorporates velocity):

| Property | Default | Description |
|----------|---------|-------------|
| `stiffness` | `100` | Spring stiffness (higher = snappier) |
| `damping` | `10` | Opposing force (0 = oscillate forever) |
| `mass` | `1` | Object mass (higher = more lethargic) |
| `velocity` | current | Initial velocity |
| `restSpeed` | `0.1` | Stop threshold (units/sec) |
| `restDelta` | `0.01` | Stop threshold (distance) |

```tsx
transition={{ type: "spring", stiffness: 300, damping: 20 }}
```

Physics springs incorporate gesture velocity for natural feel.

### `type: "inertia"` (Deceleration)

Decelerates from initial velocity. Used internally for `dragTransition`.

| Property | Default | Description |
|----------|---------|-------------|
| `power` | `0.8` | Higher = further target |
| `timeConstant` | `700` | Deceleration duration feel |
| `modifyTarget` | — | Snap function: `(target) => Math.round(target / 50) * 50` |
| `min` | — | Minimum constraint (springs to it) |
| `max` | — | Maximum constraint |
| `bounceStiffness` | `500` | Bounce spring stiffness at min/max |
| `bounceDamping` | `10` | Bounce spring damping at min/max |

```tsx
<motion.div
  drag
  dragTransition={{
    power: 0,
    modifyTarget: (target) => Math.round(target / 50) * 50
  }}
/>
```

## Orchestration

| Property | Default | Description |
|----------|---------|-------------|
| `delay` | `0` | Delay in seconds (negative = start mid-animation) |
| `repeat` | `0` | Repetition count (`Infinity` for forever) |
| `repeatType` | `"loop"` | `"loop"`, `"reverse"`, or `"mirror"` |
| `repeatDelay` | `0` | Delay between repetitions |

```tsx
// Infinite bouncing
<motion.div
  animate={{ y: [0, -20, 0] }}
  transition={{ repeat: Infinity, duration: 1, ease: "easeInOut" }}
/>

// Pulse with reverse
<motion.div
  animate={{ scale: 1.2 }}
  transition={{ repeat: Infinity, repeatType: "reverse", duration: 0.5 }}
/>
```

## Layout-Specific Transition

```tsx
<motion.div
  layout
  animate={{ opacity: 0.5 }}
  transition={{
    ease: "linear",
    layout: { duration: 0.3 }  // separate transition for layout
  }}
/>
```
