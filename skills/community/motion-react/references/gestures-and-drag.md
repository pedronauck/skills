# Gestures & Drag Reference

## Gesture Props

```tsx
<motion.button
  whileHover={{ scale: 1.1, backgroundColor: "#f0f" }}
  whileTap={{ scale: 0.95 }}
  whileFocus={{ outline: "2px solid blue" }}
  whileDrag={{ scale: 1.1, cursor: "grabbing" }}
/>
```

### Hover

```tsx
<motion.div
  whileHover={{ scale: 1.05 }}
  onHoverStart={(event, info) => {}}
  onHoverEnd={(event, info) => {}}
/>
```

**Hover propagation**: By default, `whileHover` triggers on the element and all ancestors. Set `propagate={false}` to stop:

```tsx
<motion.div whileHover="hover" propagate={false}>
  <motion.span variants={{ hover: { color: "red" } }} />
</motion.div>
```

### Tap (Press)

```tsx
<motion.button
  whileTap={{ scale: 0.9 }}
  onTap={(event, info) => {}}
  onTapStart={(event, info) => {}}
  onTapCancel={(event, info) => {}}
/>
```

### Focus

```tsx
<motion.input
  whileFocus={{ scale: 1.02, borderColor: "#00f" }}
/>
```

### Pan

```tsx
<motion.div
  onPan={(event, info) => {}}
  onPanStart={(event, info) => {}}
  onPanEnd={(event, info) => {}}
/>
```

`info` contains: `point` (absolute), `delta` (since last event), `offset` (since start), `velocity`.

## Drag

Enable drag with the `drag` prop:

```tsx
// Both axes
<motion.div drag />

// Single axis
<motion.div drag="x" />
<motion.div drag="y" />
```

### Drag Constraints

```tsx
// Pixel constraints
<motion.div
  drag
  dragConstraints={{ top: -50, left: -50, bottom: 50, right: 50 }}
/>

// Ref constraints (contained within parent)
const constraintsRef = useRef(null)

<div ref={constraintsRef}>
  <motion.div drag dragConstraints={constraintsRef} />
</div>
```

### Drag Props

| Prop | Default | Description |
|------|---------|-------------|
| `drag` | `false` | `true`, `"x"`, or `"y"` |
| `dragConstraints` | — | `{ top, left, right, bottom }` or `RefObject` |
| `dragElastic` | `0.35` | 0 (rigid) to 1 (free). Can be per-axis: `{ top: 0.2, bottom: 0 }` |
| `dragMomentum` | `true` | Apply momentum after release |
| `dragTransition` | — | Inertia transition for momentum phase |
| `dragSnapToOrigin` | `false` | Spring back to origin on release |
| `dragPropagation` | `false` | Allow drag to propagate to parent drag |
| `dragDirectionLock` | `false` | Lock to axis after 10px threshold |
| `dragListener` | `true` | Listen for drag gestures on this element |

### Drag Events

```tsx
<motion.div
  drag
  onDrag={(event, info) => {}}
  onDragStart={(event, info) => {}}
  onDragEnd={(event, info) => {}}
  onDirectionLock={(axis) => {}}
  onMeasureDragConstraints={(constraints) => {}}
/>
```

### useDragControls

Trigger drag from a different element:

```tsx
import { useDragControls } from "motion/react"

function Component() {
  const controls = useDragControls()

  return (
    <>
      <div onPointerDown={(e) => controls.start(e)}>
        Drag handle
      </div>
      <motion.div drag="x" dragControls={controls} dragListener={false}>
        Draggable content
      </motion.div>
    </>
  )
}
```

### Drag + Snap to Grid

```tsx
<motion.div
  drag
  dragTransition={{
    power: 0,
    modifyTarget: (target) => Math.round(target / 50) * 50
  }}
/>
```

### Drag + Spring to Origin

```tsx
<motion.div
  drag
  dragSnapToOrigin
  dragElastic={0.5}
/>
```

## Reorder

Drag-to-reorder lists:

```tsx
import { Reorder } from "motion/react"

function List() {
  const [items, setItems] = useState([1, 2, 3, 4])

  return (
    <Reorder.Group axis="y" values={items} onReorder={setItems}>
      {items.map((item) => (
        <Reorder.Item key={item} value={item}>
          {item}
        </Reorder.Item>
      ))}
    </Reorder.Group>
  )
}
```

**Important**: Reorder auto-scroll only works when `Reorder.Group` is inside an element with `overflow: auto/scroll`, NOT when the document itself is scrollable.
