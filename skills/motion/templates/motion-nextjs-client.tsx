// Motion + Next.js App Router - Client Component Pattern
// Production-tested with Motion v12.23.24, Next.js 15, React 19

/**
 * INSTALLATION
 *
 * 1. Install Motion:
 *    pnpm add motion
 *
 * 2. Create this file structure:
 *    src/components/motion-client.tsx  ← This file (wrapper)
 *    src/components/AnimatedModal.tsx  ← Example usage
 *    src/app/page.tsx                  ← Server Component can import
 *
 * 3. CRITICAL: Motion only works in Client Components, NOT Server Components
 *
 * NO NEXT.JS CONFIGURATION NEEDED - just use "use client" directive
 */

// ============================================================================
// PATTERN 1: Client Component Wrapper (Recommended for Next.js App Router)
// ============================================================================

/**
 * File: src/components/motion-client.tsx
 *
 * Create a wrapper that re-exports Motion as a Client Component.
 * This allows you to import { motion } in any file without repeating "use client".
 */

"use client"

// Optimized import for Next.js (reduces client JS bundle)
import * as motion from "motion/react-client"

// Re-export everything from motion
export { motion }

// Also export commonly used components
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
  useDragControls,
} from "motion/react-client"

/**
 * USAGE IN SERVER COMPONENTS
 *
 * // src/app/page.tsx (Server Component)
 * import { motion } from "@/components/motion-client"
 *
 * export default function Page() {
 *   return (
 *     <motion.div
 *       initial={{ opacity: 0 }}
 *       animate={{ opacity: 1 }}
 *     >
 *       This works! The wrapper is a Client Component.
 *     </motion.div>
 *   )
 * }
 */

// ============================================================================
// PATTERN 2: Direct Client Component
// ============================================================================

/**
 * File: src/components/AnimatedModal.tsx
 *
 * For complex components, create dedicated Client Components.
 */

"use client"

import { motion, AnimatePresence } from "motion/react-client"
import { useState, ReactNode } from "react"

interface AnimatedModalProps {
  trigger: ReactNode
  title: string
  children: ReactNode
}

export function AnimatedModal({ trigger, title, children }: AnimatedModalProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      {/* Trigger button */}
      <div onClick={() => setIsOpen(true)}>
        {trigger}
      </div>

      {/* Modal with AnimatePresence */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              key="backdrop"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 bg-black/50 z-40"
            />

            {/* Dialog */}
            <motion.dialog
              key="dialog"
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              transition={{ type: "spring", damping: 20, stiffness: 300 }}
              className="fixed inset-0 m-auto w-full max-w-md h-fit bg-white rounded-lg shadow-xl z-50 p-6"
            >
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">{title}</h2>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
              <div>{children}</div>
            </motion.dialog>
          </>
        )}
      </AnimatePresence>
    </>
  )
}

/**
 * USAGE IN SERVER COMPONENT
 *
 * // src/app/page.tsx (Server Component)
 * import { AnimatedModal } from "@/components/AnimatedModal"
 *
 * export default function Page() {
 *   return (
 *     <AnimatedModal
 *       trigger={<button>Open Modal</button>}
 *       title="Hello World"
 *     >
 *       <p>Modal content here</p>
 *     </AnimatedModal>
 *   )
 * }
 */

// ============================================================================
// PATTERN 3: Reduced Motion for Accessibility
// ============================================================================

/**
 * File: src/components/MotionProvider.tsx
 *
 * Wrap your app to respect user's prefers-reduced-motion setting.
 */

"use client"

import { MotionConfig } from "motion/react-client"
import { ReactNode } from "react"

interface MotionProviderProps {
  children: ReactNode
}

export function MotionProvider({ children }: MotionProviderProps) {
  return (
    <MotionConfig reducedMotion="user">
      {children}
    </MotionConfig>
  )
}

/**
 * USAGE IN ROOT LAYOUT
 *
 * // src/app/layout.tsx (Server Component)
 * import { MotionProvider } from "@/components/MotionProvider"
 *
 * export default function RootLayout({ children }) {
 *   return (
 *     <html>
 *       <body>
 *         <MotionProvider>
 *           {children}
 *         </MotionProvider>
 *       </body>
 *     </html>
 *   )
 * }
 *
 * This respects OS-level accessibility settings:
 * - macOS: System Settings → Accessibility → Display → Reduce motion
 * - Windows: Settings → Ease of Access → Display → Show animations
 * - iOS: Settings → Accessibility → Motion
 * - Android 9+: Settings → Accessibility → Remove animations
 */

// ============================================================================
// PATTERN 4: Page Transitions with App Router
// ============================================================================

/**
 * File: src/components/PageTransition.tsx
 *
 * Animate route changes in App Router.
 */

"use client"

import { motion } from "motion/react-client"
import { ReactNode } from "react"

interface PageTransitionProps {
  children: ReactNode
}

export function PageTransition({ children }: PageTransitionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  )
}

/**
 * USAGE IN PAGE
 *
 * // src/app/about/page.tsx (Server Component)
 * import { PageTransition } from "@/components/PageTransition"
 *
 * export default function AboutPage() {
 *   return (
 *     <PageTransition>
 *       <h1>About Page</h1>
 *       <p>Content animates in on route change</p>
 *     </PageTransition>
 *   )
 * }
 *
 * Note: Exit animations require AnimatePresence, which may not work
 * reliably with Next.js soft navigation. For full page transitions,
 * consider using template.tsx file or middleware approach.
 */

// ============================================================================
// PATTERN 5: Server Data with Client Animation
// ============================================================================

/**
 * File: src/components/AnimatedProductCard.tsx
 *
 * Fetch data in Server Component, animate in Client Component.
 */

"use client"

import { motion } from "motion/react-client"

interface Product {
  id: number
  name: string
  price: number
  image: string
}

interface AnimatedProductCardProps {
  product: Product
  index: number
}

export function AnimatedProductCard({ product, index }: AnimatedProductCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }} // Stagger
      whileHover={{ scale: 1.05 }}
      className="p-4 bg-white border rounded-lg shadow-sm cursor-pointer"
    >
      <img
        src={product.image}
        alt={product.name}
        className="w-full h-48 object-cover rounded mb-4"
      />
      <h3 className="text-lg font-bold">{product.name}</h3>
      <p className="text-gray-600">${product.price}</p>
    </motion.div>
  )
}

/**
 * USAGE WITH SERVER DATA
 *
 * // src/app/products/page.tsx (Server Component)
 * import { AnimatedProductCard } from "@/components/AnimatedProductCard"
 *
 * async function getProducts() {
 *   const res = await fetch('https://api.example.com/products')
 *   return res.json()
 * }
 *
 * export default async function ProductsPage() {
 *   const products = await getProducts() // Server-side fetch
 *
 *   return (
 *     <div className="grid grid-cols-3 gap-4">
 *       {products.map((product, index) => (
 *         <AnimatedProductCard
 *           key={product.id}
 *           product={product}
 *           index={index}
 *         />
 *       ))}
 *     </div>
 *   )
 * }
 *
 * Benefits:
 * - Data fetched on server (SEO, performance)
 * - Animation runs on client (interactivity)
 * - Best of both worlds
 */

// ============================================================================
// KNOWN ISSUES & WORKAROUNDS
// ============================================================================

/**
 * ISSUE 1: "motion is not defined" or SSR Errors
 *
 * Cause: Forgot "use client" directive
 *
 * Solution: Add "use client" at top of file:
 *
 * "use client"
 * import { motion } from "motion/react"
 */

/**
 * ISSUE 2: AnimatePresence Exit Animations Not Working
 *
 * Cause: Next.js soft navigation doesn't trigger React unmount
 *
 * Solution: Use route-level AnimatePresence is unreliable in App Router.
 * For component-level modals/dropdowns, it works fine. For page transitions,
 * consider alternatives like view transitions API or middleware approach.
 *
 * GitHub issue: Check Next.js docs for latest recommendations
 */

/**
 * ISSUE 3: Large Bundle Size
 *
 * Cause: Full motion component is ~34 KB minified+gzipped
 *
 * Solution: Use LazyMotion for 4.6 KB:
 *
 * "use client"
 *
 * import { LazyMotion, domAnimation, m } from "motion/react-client"
 *
 * export function App() {
 *   return (
 *     <LazyMotion features={domAnimation}>
 *       <m.div animate={{ x: 100 }} />
 *     </LazyMotion>
 *   )
 * }
 *
 * See ../references/performance-optimization.md for full guide
 */

/**
 * ISSUE 4: Next.js 15 + React 19 Compatibility
 *
 * Status: Most issues resolved in latest Motion version
 *
 * Solution: Update to latest:
 * pnpm add motion@latest react@latest next@latest
 *
 * If issues persist, check GitHub: https://github.com/motiondivision/motion/issues
 */

/**
 * ISSUE 5: Reorder Component Doesn't Work
 *
 * Cause: Reorder component incompatible with Next.js routing
 *
 * Solution: Use alternative drag-to-reorder implementations or avoid Reorder
 *
 * GitHub issues: #2183, #2101
 */

// ============================================================================
// PERFORMANCE OPTIMIZATION
// ============================================================================

/**
 * 1. Use "motion/react-client" import (not "motion/react")
 *    - Reduces client JS bundle
 *    - Optimized for Next.js App Router
 *
 * 2. Add willChange for transforms:
 *    <motion.div style={{ willChange: "transform" }} animate={{ x: 100 }} />
 *
 * 3. Use LazyMotion for smaller bundle (see Issue 3 above)
 *
 * 4. For large lists (50+ items), use virtualization:
 *    pnpm add @tanstack/react-virtual
 *
 * 5. Memoize expensive components:
 *    import { memo } from "react"
 *    export const AnimatedCard = memo(AnimatedCardComponent)
 */

// ============================================================================
// TYPESCRIPT TYPES
// ============================================================================

/**
 * Motion includes full TypeScript support out of the box.
 * No @types package needed.
 *
 * Common types:
 */

import type {
  HTMLMotionProps,
  SVGMotionProps,
  Variants,
  Target,
  Transition,
  MotionValue,
  AnimationControls,
  DragControls,
} from "motion/react-client"

// Example: Typed motion component props
interface AnimatedBoxProps extends HTMLMotionProps<"div"> {
  title: string
}

export function AnimatedBox({ title, ...motionProps }: AnimatedBoxProps) {
  return (
    <motion.div {...motionProps}>
      <h3>{title}</h3>
    </motion.div>
  )
}

// Example: Typed variants
const typedVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
}

/**
 * QUICK REFERENCE
 *
 * App Router Requirements:
 * ✅ Add "use client" to files using Motion
 * ✅ Use "motion/react-client" import for optimized bundle
 * ✅ Server Components can import Client Components
 * ✅ Wrap app in MotionProvider for reduced motion support
 * ❌ Don't use Motion in Server Components
 * ❌ Don't rely on AnimatePresence for route transitions (unreliable)
 *
 * See ../references/nextjs-integration.md for comprehensive guide
 */
