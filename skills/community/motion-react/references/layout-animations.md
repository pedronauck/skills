# Layout Animations Reference

## Basic Layout Animation

Add the `layout` prop to animate any layout change automatically:

```tsx
<motion.div layout />
```

This animates previously unanimatable CSS changes like `justify-content`, `flex-direction`, `width`, `height`, grid columns, and reordering.

```tsx
<motion.div
  layout
  style={{ justifyContent: isOn ? "flex-start" : "flex-end" }}
/>
```

**Performance**: Layout animations use CSS `transform` internally for hardware acceleration.

**Important**: Make layout changes via `style` or `className`, NOT via `animate`/`whileHover`. The `layout` prop handles the animation.

## `layout` Prop Values

| Value | Behavior |
|-------|----------|
| `true` | Animate position and size |
| `"position"` | Only animate position changes |
| `"size"` | Only animate size changes |
| `"preserve-aspect"` | Animate both, preserve aspect ratio |
| `false` | Disabled (default) |

## Shared Layout Animations (`layoutId`)

Connect two separate elements for "magic motion" transitions:

```tsx
// Only rendered when selected
{isSelected && <motion.div layoutId="underline" />}
```

When a new component mounts with a matching `layoutId`, it animates from the old one's position/size.

### Tab Underline Example

```tsx
function Tabs({ tabs, selectedTab, onSelect }) {
  return (
    <ul>
      {tabs.map((tab) => (
        <li key={tab.id} onClick={() => onSelect(tab)}>
          {tab.label}
          {tab === selectedTab && (
            <motion.div layoutId="underline" className="absolute bottom-0 h-0.5 bg-blue-500" />
          )}
        </li>
      ))}
    </ul>
  )
}
```

### Modal Expand/Collapse

```tsx
<motion.div layoutId="card" onClick={() => setSelected(item.id)}>
  <Card />
</motion.div>

<AnimatePresence>
  {selected && (
    <motion.div layoutId="card">
      <ExpandedCard />
    </motion.div>
  )}
</AnimatePresence>
```

### Crossfade

When both old and new `layoutId` elements exist simultaneously, they crossfade automatically.

## Customizing Layout Transitions

```tsx
<motion.div
  layout
  transition={{ duration: 0.3 }}
/>
```

Separate layout transition from other animations:

```tsx
<motion.div
  layout
  animate={{ opacity: 0.5 }}
  transition={{
    ease: "linear",
    layout: { duration: 0.3, type: "spring" }
  }}
/>
```

For shared layout animations, the transition on the **destination** element is used.

## Fixing Scale Distortion

Layout animations use `transform: scale()` internally. This distorts children (border-radius, text, shadows). Fix with `layout` on children:

```tsx
<motion.div layout style={{ borderRadius: 20 }}>
  <motion.p layout="position">
    Text won't distort during parent scale animation
  </motion.p>
</motion.div>
```

**Key rule**: Apply `borderRadius` and `boxShadow` to the same element with `layout` — Motion corrects these automatically. For child content, add `layout="position"`.

## `layoutDependency`

Optimize performance by telling Motion when to measure:

```tsx
<motion.div layout layoutDependency={items.length} />
```

Layout is only measured when `layoutDependency` changes, instead of every render.

## Scroll Correction

### `layoutScroll`

Fix layout animations inside scrollable containers:

```tsx
<motion.div layoutScroll style={{ overflow: "auto" }}>
  {items.map((item) => (
    <motion.div key={item.id} layout />
  ))}
</motion.div>
```

### `layoutRoot`

Fix layout animations inside fixed-position elements:

```tsx
<motion.div layoutRoot style={{ position: "fixed" }}>
  <motion.div layout />
</motion.div>
```

## LayoutGroup

Synchronize layout animations across components that don't share a parent:

```tsx
import { LayoutGroup } from "motion/react"

<LayoutGroup>
  <motion.ul layout>
    <AnimatePresence>
      {items.map((item) => (
        <motion.li layout key={item.id} exit={{ opacity: 0 }} />
      ))}
    </AnimatePresence>
  </motion.ul>
  <Sidebar /> {/* Also animates when list changes */}
</LayoutGroup>
```

### Namespaced LayoutGroups

Prevent `layoutId` conflicts between unrelated components:

```tsx
<LayoutGroup id="sidebar">
  <motion.div layoutId="highlight" />
</LayoutGroup>
<LayoutGroup id="main">
  <motion.div layoutId="highlight" /> {/* Different from sidebar's */}
</LayoutGroup>
```

## Troubleshooting

### Layout animations teleport/snap

- **Percentage transforms**: Convert to pixels. `x: "50%"` breaks FLIP calculation in flex containers.
- **Scaled containers**: Layout animations in scaled parents have incorrect positions. Use `transformTemplate` to compensate.

### popLayout mode issues

- Custom components must use `forwardRef` to forward ref to DOM node.
- Sub-pixel precision loss can cause 1px shift. Use whole-pixel values.

### Layout + AnimatePresence

Wrap in `LayoutGroup` to ensure siblings know about layout changes:

```tsx
<LayoutGroup>
  <motion.ul layout>
    <AnimatePresence>
      {items.map((item) => (
        <motion.li layout key={item.id} exit={{ opacity: 0 }} />
      ))}
    </AnimatePresence>
  </motion.ul>
</LayoutGroup>
```
