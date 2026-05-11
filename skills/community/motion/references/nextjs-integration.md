# Motion + Next.js Integration Guide

This guide covers how to use Motion (Framer Motion) with Next.js, including App Router patterns, Pages Router setup, known issues, and performance optimization.

---

## TL;DR - Quick Start

**Pages Router** (Next.js 12):
```tsx
// Works out of the box, no special setup needed
import { motion } from "motion/react"

export default function Page() {
  return <motion.div animate={{ opacity: 1 }}>Content</motion.div>
}
```

**App Router** (Next.js 13+):
```tsx
// MUST add "use client" directive
"use client"

import { motion } from "motion/react-client" // Optimized import

export default function Page() {
  return <motion.div animate={{ opacity: 1 }}>Content</motion.div>
}
```

---

## App Router (Next.js 13, 14, 15)

### Key Requirement: Client Components Only

Motion uses browser APIs (DOM, window, events) that **don't exist on the server**. Therefore, Motion only works in **Client Components**, not Server Components.

---

### Pattern 1: Direct Client Component (Simplest)

Add `"use client"` directive at the top of any file using Motion:

**File**: `src/app/page.tsx`
```tsx
"use client"

import { motion } from "motion/react-client" // Optimized for Next.js

export default function Page() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      Welcome to Next.js + Motion
    </motion.div>
  )
}
```

**Pros**:
- ✅ Simple, straightforward
- ✅ Works immediately

**Cons**:
- ❌ Entire page becomes client-rendered
- ❌ Loses Server Component benefits (streaming, server-side data fetching)

---

### Pattern 2: Wrapper Component (Recommended)

Create a reusable Client Component wrapper to avoid repeating `"use client"`:

**File**: `src/components/motion-client.tsx`
```tsx
"use client"

// Optimized import for Next.js (reduces client JS)
import * as motion from "motion/react-client"

export { motion }

// Also export commonly used components/hooks
export {
  AnimatePresence,
  MotionConfig,
  LazyMotion,
  LayoutGroup,
  useMotionValue,
  useTransform,
  useScroll,
  useSpring,
  useAnimate,
  useInView,
} from "motion/react-client"
```

**File**: `src/app/page.tsx` (Server Component)
```tsx
import { motion } from "@/components/motion-client"

export default function Page() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      This page is a Server Component!
      Motion wrapper is a Client Component.
    </motion.div>
  )
}
```

**Pros**:
- ✅ Server Components can use Motion via wrapper
- ✅ Only Motion components are client-rendered
- ✅ Cleaner imports (no need to repeat `"use client"`)

**Cons**:
- ❌ Slight indirection (one extra file)

---

### Pattern 3: Server Data + Client Animation

Fetch data in Server Component, animate in Client Component:

**File**: `src/components/AnimatedCard.tsx` (Client Component)
```tsx
"use client"

import { motion } from "motion/react-client"

interface Product {
  id: number
  name: string
  price: number
}

export function AnimatedCard({ product, index }: { product: Product; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }} // Stagger
      whileHover={{ scale: 1.05 }}
      className="p-4 bg-white border rounded-lg"
    >
      <h3 className="font-bold">{product.name}</h3>
      <p className="text-gray-600">${product.price}</p>
    </motion.div>
  )
}
```

**File**: `src/app/products/page.tsx` (Server Component)
```tsx
import { AnimatedCard } from "@/components/AnimatedCard"

async function getProducts() {
  const res = await fetch('https://api.example.com/products', {
    cache: 'force-cache' // Server-side caching
  })
  return res.json()
}

export default async function ProductsPage() {
  const products = await getProducts() // Server-side fetch

  return (
    <div className="grid grid-cols-3 gap-4">
      {products.map((product, index) => (
        <AnimatedCard key={product.id} product={product} index={index} />
      ))}
    </div>
  )
}
```

**Pros**:
- ✅ Data fetched on server (SEO, performance, security)
- ✅ Animations run on client (interactivity)
- ✅ Best of both worlds

**Cons**:
- ❌ Requires splitting into two components

---

### Pattern 4: MotionConfig Provider

Wrap app in MotionConfig for global settings (reduced motion, transitions):

**File**: `src/components/MotionProvider.tsx` (Client Component)
```tsx
"use client"

import { MotionConfig } from "motion/react-client"
import { ReactNode } from "react"

export function MotionProvider({ children }: { children: ReactNode }) {
  return (
    <MotionConfig reducedMotion="user">
      {children}
    </MotionConfig>
  )
}
```

**File**: `src/app/layout.tsx` (Root Layout)
```tsx
import { MotionProvider } from "@/components/MotionProvider"

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <MotionProvider>
          {children}
        </MotionProvider>
      </body>
    </html>
  )
}
```

**Respects**: macOS/Windows/iOS/Android "Reduce Motion" accessibility setting

---

## Pages Router (Next.js 12)

### No Special Setup Required

Motion works out of the box with Pages Router:

**File**: `pages/index.tsx`
```tsx
import { motion } from "motion/react"

export default function HomePage() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      Welcome
    </motion.div>
  )
}
```

**No `"use client"` needed** - Pages Router renders on client by default.

---

### Server-Side Rendering (SSR)

Motion is **client-only**, so you may see hydration warnings in development. This is expected and can be ignored.

**If you see hydration errors**:

**Option 1: Dynamic Import**
```tsx
import dynamic from 'next/dynamic'

const AnimatedComponent = dynamic(
  () => import('@/components/AnimatedComponent'),
  { ssr: false }
)

export default function Page() {
  return <AnimatedComponent />
}
```

**Option 2: Conditional Rendering**
```tsx
import { useState, useEffect } from 'react'
import { motion } from 'motion/react'

export default function Page() {
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  if (!isClient) {
    return <div>Loading...</div>
  }

  return <motion.div animate={{ opacity: 1 }}>Content</motion.div>
}
```

---

## Known Issues

### Issue 1: Next.js 15 + React 19 Compatibility

**Status**: Most issues resolved in latest Motion version (12.23.24)

**Symptoms**:
- Build errors: "unsupported to use 'export *' in a client boundary"
- Runtime errors with Server Components

**Solution**: Update to latest versions:
```bash
pnpm add motion@latest react@latest next@latest
```

**If issues persist**: Check GitHub for updates: https://github.com/motiondivision/motion/issues

---

### Issue 2: AnimatePresence with Soft Navigation

**Problem**: Exit animations don't work when navigating between pages in App Router.

**Why**: Next.js soft navigation doesn't trigger React unmount, so AnimatePresence doesn't detect exit.

**Solutions**:

**Option 1: Component-level AnimatePresence** (Recommended)
```tsx
// Use AnimatePresence for modals, dropdowns, tooltips
<AnimatePresence>
  {isOpen && (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      Modal content
    </motion.div>
  )}
</AnimatePresence>
```

**Option 2: template.tsx** (Experimental)
```tsx
// src/app/template.tsx
"use client"

import { motion } from "motion/react-client"

export default function Template({ children }: { children: ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  )
}
```

**Note**: `template.tsx` creates new instances on navigation, enabling enter animations but not exit animations.

**Option 3: Middleware approach**
Use Next.js middleware to detect route changes and trigger animations manually. Complex, not recommended.

**Recommendation**: Accept that page-level exit animations don't work reliably in App Router. Use AnimatePresence for component-level animations (modals, dropdowns, etc.) where it works perfectly.

---

### Issue 3: Reorder Component Incompatibility

**Problem**: Motion's `<Reorder>` component doesn't work with Next.js routing.

**Symptoms**:
- Random stuck states
- Items don't reorder
- Console errors

**GitHub Issues**: #2183, #2101

**Solution**: Use alternative drag-to-reorder implementations:
- `@dnd-kit/core` (recommended)
- `react-beautiful-dnd`
- Manual implementation with `drag` prop

**Example with `drag` prop**:
```tsx
<motion.div
  drag="y"
  dragConstraints={{ top: 0, bottom: 0 }}
  whileDrag={{ scale: 1.05 }}
>
  Draggable item
</motion.div>
```

---

### Issue 4: Large Bundle Size

**Problem**: Full Motion component adds ~34 KB to client bundle.

**Solution**: Use optimized import and LazyMotion:

**File**: `src/components/motion-client.tsx`
```tsx
"use client"

import { LazyMotion, domAnimation } from "motion/react-client"
import { ReactNode } from "react"

export function MotionProvider({ children }: { children: ReactNode }) {
  return (
    <LazyMotion features={domAnimation}>
      {children}
    </LazyMotion>
  )
}

// Export 'm' component instead of 'motion'
export { m as motion } from "motion/react-client"
```

**Reduces bundle from 34 KB → 4.6 KB**

See `performance-optimization.md` for full guide.

---

### Issue 5: Reduced Motion Not Affecting AnimatePresence

**Problem**: MotionConfig reducedMotion prop doesn't disable AnimatePresence animations.

**GitHub Issue**: #1567

**Workaround**: Manual check:
```tsx
"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "motion/react-client"

export function Modal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)")
    setPrefersReducedMotion(mediaQuery.matches)

    const handleChange = () => setPrefersReducedMotion(mediaQuery.matches)
    mediaQuery.addEventListener("change", handleChange)
    return () => mediaQuery.removeEventListener("change", handleChange)
  }, [])

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: prefersReducedMotion ? 1 : 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: prefersReducedMotion ? 1 : 0 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.3 }}
        >
          Modal content
        </motion.div>
      )}
    </AnimatePresence>
  )
}
```

---

## Performance Optimization for Next.js

### 1. Use `motion/react-client` Import

**Regular import** (full bundle):
```tsx
import { motion } from "motion/react"
```

**Optimized import** (smaller bundle):
```tsx
import { motion } from "motion/react-client"
```

**Difference**: `react-client` variant excludes server-side code, reducing client JavaScript.

---

### 2. Code Splitting with Dynamic Imports

For animations not needed on initial load:

```tsx
import dynamic from 'next/dynamic'

const AnimatedHero = dynamic(
  () => import('@/components/AnimatedHero'),
  { ssr: false }
)

export default function HomePage() {
  return <AnimatedHero />
}
```

**Benefits**:
- ✅ Reduces initial JavaScript bundle
- ✅ Loads animation code only when needed

---

### 3. LazyMotion for Smaller Bundle

**Setup**:
```tsx
"use client"

import { LazyMotion, domAnimation, m } from "motion/react-client"

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <LazyMotion features={domAnimation}>
      {children}
    </LazyMotion>
  )
}
```

**Then use `m` instead of `motion`**:
```tsx
"use client"

import { m } from "motion/react-client"

export function Component() {
  return <m.div animate={{ opacity: 1 }}>Content</m.div>
}
```

**Bundle size**: 34 KB → 4.6 KB

---

### 4. Optimize Images with Next/Image

Combine Motion with Next.js Image optimization:

```tsx
"use client"

import { motion } from "motion/react-client"
import Image from "next/image"

export function AnimatedImage() {
  return (
    <motion.div whileHover={{ scale: 1.05 }}>
      <Image
        src="/hero.jpg"
        width={1200}
        height={600}
        alt="Hero"
        priority
      />
    </motion.div>
  )
}
```

**Benefits**:
- ✅ Automatic image optimization
- ✅ Smooth animations

---

## Testing & Debugging

### 1. Verify Client Component Boundary

**Problem**: Accidentally using Motion in Server Component.

**Check**:
1. Look for `"use client"` directive at top of file
2. If using wrapper, verify wrapper has `"use client"`

**Error message**:
```
Error: motion is not defined
```

**Fix**: Add `"use client"` to the file.

---

### 2. Check Bundle Size

**Analyze**:
```bash
pnpm build

# Then check .next/analyze or use @next/bundle-analyzer
```

**Target**: Motion should be <5 KB (with LazyMotion)

**If larger**: Switch to LazyMotion or useAnimate mini.

---

### 3. Test Reduced Motion

**Enable in OS**:
- **macOS**: System Settings → Accessibility → Display → Reduce motion
- **Windows**: Settings → Ease of Access → Display → Show animations
- **iOS**: Settings → Accessibility → Motion
- **Android 9+**: Settings → Accessibility → Remove animations

**Verify**: Animations should be instant (no transitions).

---

### 4. Lighthouse Performance

**Run**:
```bash
pnpm build
pnpm start
# Open Chrome DevTools → Lighthouse → Run analysis
```

**Target Scores**:
- Performance: >90
- Accessibility: 100

**If low performance**: Check for:
- Large bundle size (optimize with LazyMotion)
- Too many animated elements (use virtualization)
- Non-accelerated animations (use transform, not width/height)

---

## Deployment Checklist

Before deploying Next.js + Motion:

- [ ] All Motion files have `"use client"` directive (App Router)
- [ ] Using `motion/react-client` import (not `motion/react`)
- [ ] LazyMotion enabled (if bundle size matters)
- [ ] MotionConfig with reducedMotion set up
- [ ] No Motion usage in Server Components
- [ ] AnimatePresence only for component-level animations (not routes)
- [ ] Images optimized with next/image
- [ ] Tested with prefers-reduced-motion enabled
- [ ] Bundle analyzed (<5 KB for Motion recommended)
- [ ] Lighthouse performance score >90

---

## Quick Reference

### App Router

| Task | Solution |
|------|----------|
| **Use Motion** | Add `"use client"` to file |
| **Optimize import** | `import from "motion/react-client"` |
| **Reduce bundle** | Use LazyMotion |
| **Global config** | Wrap in MotionProvider |
| **Server data + animation** | Fetch in Server Component, animate in Client Component |
| **Route transitions** | Not reliable, use component-level only |

### Pages Router

| Task | Solution |
|------|----------|
| **Use Motion** | Just import and use (no setup) |
| **Avoid hydration errors** | Use dynamic import with `ssr: false` |
| **Optimize bundle** | Use LazyMotion |

---

## Getting Help

- **Next.js Docs**: https://nextjs.org/docs
- **Motion Docs**: https://motion.dev/docs/react
- **Motion + Next.js Issues**: https://github.com/motiondivision/motion/issues
- **Stack Overflow**: Tag: `framer-motion` + `next.js`

---

**Key Takeaway**: For App Router, always use `"use client"` and `motion/react-client` import. For Pages Router, it just works. Use LazyMotion to keep bundle size small.
