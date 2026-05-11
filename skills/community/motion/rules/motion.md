---
paths: "**/*.ts", "**/*.tsx", "**/motion*.ts", "**/animate*.ts"
---

# Motion (formerly Framer Motion) Corrections

Claude's training may reference Framer Motion. The library was **renamed to Motion** in late 2024.

## Package Name Change

```bash
# ❌ Old package name
npm install framer-motion

# ✅ New package name (2024+)
npm install motion
```

## Import Changes

```typescript
/* ❌ Old imports */
import { motion, AnimatePresence } from 'framer-motion'

/* ✅ New imports */
import { motion, AnimatePresence } from 'motion/react'
```

## React 19 Compatibility

```typescript
/* ❌ May cause issues with React 19 */
import { motion } from 'framer-motion'

/* ✅ motion/react is React 19 compatible */
import { motion } from 'motion/react'
```

## Variants Pattern (Unchanged)

```typescript
/* ✅ Same API, just new import */
import { motion } from 'motion/react'

const variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
}

<motion.div
  initial="hidden"
  animate="visible"
  variants={variants}
/>
```

## useAnimation Hook

```typescript
/* ❌ Old import */
import { useAnimation } from 'framer-motion'

/* ✅ New import */
import { useAnimation } from 'motion/react'

const controls = useAnimation()
await controls.start({ opacity: 1 })
```

## Layout Animations

```typescript
/* ❌ Old import */
import { LayoutGroup } from 'framer-motion'

/* ✅ New import */
import { LayoutGroup } from 'motion/react'

<LayoutGroup>
  <motion.div layout />
</LayoutGroup>
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `npm install framer-motion` | `npm install motion` |
| `from 'framer-motion'` | `from 'motion/react'` |
| `import { motion }` from framer-motion | `import { motion } from 'motion/react'` |
| `motion` package without `/react` | Use `motion/react` for React components |
