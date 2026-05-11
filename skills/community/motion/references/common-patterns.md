# Motion Common Patterns - Quick Reference

Production-tested animation patterns with code examples. Copy-paste ready.

---

## 1. Modal Dialog

```tsx
import { motion, AnimatePresence } from "motion/react"

<AnimatePresence>
  {isOpen && (
    <>
      <motion.div
        key="backdrop"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 bg-black/50 z-40"
      />
      <motion.dialog
        key="dialog"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="fixed inset-0 m-auto w-96 bg-white rounded-lg shadow-xl z-50"
      >
        Content
      </motion.dialog>
    </>
  )}
</AnimatePresence>
```

---

## 2. Accordion

```tsx
<motion.div
  animate={{ height: isOpen ? "auto" : 0 }}
  style={{ overflow: "hidden" }}
  transition={{ duration: 0.3 }}
>
  <div className="p-4">Content</div>
</motion.div>
```

---

## 3. Tabs with Shared Underline

```tsx
<div className="flex gap-4 border-b">
  {tabs.map(tab => (
    <button key={tab.id} onClick={() => setActive(tab.id)}>
      {tab.label}
      {active === tab.id && (
        <motion.div
          layoutId="underline"
          className="absolute bottom-0 h-0.5 bg-blue-600"
        />
      )}
    </button>
  ))}
</div>
```

---

## 4. Staggered List

```tsx
const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } }
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

---

## 5. Parallax Hero

```tsx
const { scrollY } = useScroll()
const y = useTransform(scrollY, [0, 1000], [0, -300])

<motion.div style={{ y }}>
  <img src="/background.jpg" />
</motion.div>
```

---

## 6. Scroll Progress Bar

```tsx
const { scrollYProgress } = useScroll()

<motion.div
  style={{ scaleX: scrollYProgress }}
  className="fixed top-0 h-1 bg-blue-600 origin-left"
/>
```

---

## 7. Fade In on Scroll

```tsx
<motion.div
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, margin: "-100px" }}
>
  Content
</motion.div>
```

---

## 8. Drag to Reorder

```tsx
<motion.div
  drag="y"
  dragConstraints={{ top: 0, bottom: 0 }}
  dragElastic={0.1}
  whileDrag={{ scale: 1.05 }}
>
  Drag me
</motion.div>
```

---

## 9. Card Expand

```tsx
<motion.div layout onClick={toggle} className={isExpanded ? "w-full" : "w-64"}>
  {isExpanded && <p>Extra content</p>}
</motion.div>
```

---

## 10. Shared Element Transition

```tsx
// Grid view
<motion.div layoutId={card.id} onClick={() => expand(card)}>
  Preview
</motion.div>

// Detail view
<motion.div layoutId={card.id}>
  Full details
</motion.div>
```

---

## 11. Carousel

```tsx
<motion.div
  drag="x"
  dragConstraints={{ left: -width, right: 0 }}
  className="flex"
>
  {images.map(img => <img key={img.id} src={img.url} />)}
</motion.div>
```

---

## 12. Hover & Tap Button

```tsx
<motion.button
  whileHover={{ scale: 1.1 }}
  whileTap={{ scale: 0.95 }}
>
  Click me
</motion.button>
```

---

## 13. Toast Notification

```tsx
<AnimatePresence>
  {isVisible && (
    <motion.div
      initial={{ opacity: 0, x: 300 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 300 }}
      className="fixed top-4 right-4 bg-blue-600 text-white p-4 rounded"
    >
      Message
    </motion.div>
  )}
</AnimatePresence>
```

---

## 14. SVG Line Drawing

```tsx
<motion.path
  d="M 0 50 Q 50 0 100 50"
  initial={{ pathLength: 0 }}
  animate={{ pathLength: 1 }}
  transition={{ duration: 2 }}
  stroke="black"
  strokeWidth={2}
  fill="none"
/>
```

---

## 15. Spring Physics

```tsx
<motion.div
  animate={{ x: 100 }}
  transition={{
    type: "spring",
    stiffness: 300,
    damping: 10
  }}
/>
```

---

See templates/ for full component examples.
