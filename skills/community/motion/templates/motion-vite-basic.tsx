// Motion + Vite + React + TypeScript - Basic Setup
// Production-tested with Motion v12.23.24, React 19, Vite 6

/**
 * INSTALLATION
 *
 * 1. Install Motion:
 *    pnpm add motion
 *
 * 2. Install React + TypeScript (if new project):
 *    pnpm create vite my-app --template react-ts
 *    cd my-app
 *    pnpm install
 *
 * 3. Copy this file to src/components/AnimatedExamples.tsx
 *
 * 4. Import in your App.tsx:
 *    import { AnimatedExamples } from '@/components/AnimatedExamples'
 *
 * NO VITE CONFIGURATION NEEDED - works out of the box
 */

import { motion } from "motion/react"
import { useState } from "react"

/**
 * Example 1: Basic Animation
 * Fade in and slide up on mount
 */
export function FadeInBox() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-6 bg-blue-100 rounded-lg"
    >
      <h2 className="text-xl font-bold">I fade in and slide up!</h2>
      <p className="text-gray-700">Basic animation example</p>
    </motion.div>
  )
}

/**
 * Example 2: Hover and Tap Gestures
 * Scale on hover, shrink on tap
 */
export function InteractiveButton() {
  return (
    <motion.button
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold"
    >
      Hover and Click Me
    </motion.button>
  )
}

/**
 * Example 3: Variants (Named Animation States)
 * Propagates through component tree automatically
 */
interface Item {
  id: number
  text: string
}

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1, // Delay between each child (in seconds)
    }
  }
}

const itemVariants = {
  hidden: { opacity: 0, x: -20 },
  show: { opacity: 1, x: 0 }
}

export function StaggeredList() {
  const [items] = useState<Item[]>([
    { id: 1, text: "First item" },
    { id: 2, text: "Second item" },
    { id: 3, text: "Third item" },
    { id: 4, text: "Fourth item" },
  ])

  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="space-y-2"
    >
      {items.map((item) => (
        <motion.li
          key={item.id}
          variants={itemVariants}
          className="p-4 bg-white border rounded-lg shadow-sm"
        >
          {item.text}
        </motion.li>
      ))}
    </motion.ul>
  )
}

/**
 * Example 4: Spring Physics
 * Natural, physics-based motion
 */
export function SpringButton() {
  const [isActive, setIsActive] = useState(false)

  return (
    <motion.button
      animate={{
        scale: isActive ? 1.2 : 1,
        rotate: isActive ? 180 : 0,
      }}
      transition={{
        type: "spring",
        stiffness: 300,  // Higher = more sudden movement
        damping: 10,     // Higher = less oscillation
        mass: 1,         // Higher = more lethargic
      }}
      onClick={() => setIsActive(!isActive)}
      className="w-16 h-16 bg-purple-600 text-white rounded-full"
    >
      🎨
    </motion.button>
  )
}

/**
 * Example 5: Keyframes
 * Multiple intermediate states
 */
export function KeyframeAnimation() {
  return (
    <motion.div
      animate={{
        scale: [1, 1.2, 1.2, 1, 1],
        rotate: [0, 0, 180, 180, 0],
        borderRadius: ["10%", "10%", "50%", "50%", "10%"],
      }}
      transition={{
        duration: 2,
        ease: "easeInOut",
        times: [0, 0.2, 0.5, 0.8, 1], // When each keyframe happens (0-1)
        repeat: Infinity,
        repeatDelay: 1,
      }}
      className="w-20 h-20 bg-gradient-to-br from-pink-500 to-purple-600"
    />
  )
}

/**
 * Example 6: Drag Gesture
 * Drag with constraints and elastic edges
 */
export function DraggableBox() {
  return (
    <div className="relative w-full h-64 bg-gray-100 rounded-lg overflow-hidden">
      <motion.div
        drag
        dragConstraints={{ left: 0, right: 300, top: 0, bottom: 200 }}
        dragElastic={0.2} // Elasticity at constraints (0-1)
        dragMomentum={false} // Disable momentum/inertia
        className="absolute w-16 h-16 bg-red-500 rounded-lg cursor-grab active:cursor-grabbing flex items-center justify-center text-white font-bold"
      >
        DRAG
      </motion.div>
    </div>
  )
}

/**
 * Example 7: Hover Color Change
 * Animate any CSS property
 */
export function ColorChangeCard() {
  return (
    <motion.div
      whileHover={{
        backgroundColor: "#3b82f6", // Tailwind blue-600
        color: "#ffffff",
      }}
      transition={{ duration: 0.3 }}
      className="p-6 bg-gray-200 text-gray-900 rounded-lg cursor-pointer"
    >
      <h3 className="text-lg font-bold">Hover me!</h3>
      <p>Background and text color change on hover</p>
    </motion.div>
  )
}

/**
 * Example 8: TypeScript Types
 * Motion components are fully typed
 */
interface AnimatedCardProps {
  title: string
  description: string
  delay?: number
}

export function AnimatedCard({ title, description, delay = 0 }: AnimatedCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="p-6 bg-white border rounded-lg shadow-sm"
    >
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-gray-700">{description}</p>
    </motion.div>
  )
}

/**
 * Example 9: Tailwind Integration
 * ⚠️ IMPORTANT: Remove Tailwind transition classes to avoid conflicts
 */
export function TailwindIntegration() {
  return (
    <div className="space-y-4">
      {/* ❌ Wrong - Tailwind transition conflicts with Motion */}
      {/* <motion.div className="transition-all duration-300" animate={{ x: 100 }} /> */}

      {/* ✅ Correct - Let Motion handle animations, Tailwind for styles */}
      <motion.div
        whileHover={{ scale: 1.05 }}
        className="px-6 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg"
      >
        Tailwind styles + Motion animations (no transition classes)
      </motion.div>
    </div>
  )
}

/**
 * All Examples Component
 * Demo of all patterns above
 */
export function AnimatedExamples() {
  return (
    <div className="max-w-4xl mx-auto p-8 space-y-8">
      <h1 className="text-3xl font-bold mb-8">Motion Animation Examples</h1>

      <section>
        <h2 className="text-2xl font-bold mb-4">1. Basic Animation</h2>
        <FadeInBox />
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">2. Hover & Tap Gestures</h2>
        <InteractiveButton />
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">3. Staggered List (Variants)</h2>
        <StaggeredList />
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">4. Spring Physics</h2>
        <SpringButton />
        <p className="text-sm text-gray-600 mt-2">Click to toggle</p>
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">5. Keyframe Animation</h2>
        <KeyframeAnimation />
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">6. Drag Gesture</h2>
        <DraggableBox />
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">7. Color Change</h2>
        <ColorChangeCard />
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">8. TypeScript Example</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <AnimatedCard
            title="Card 1"
            description="First card with no delay"
            delay={0}
          />
          <AnimatedCard
            title="Card 2"
            description="Second card with 0.2s delay"
            delay={0.2}
          />
          <AnimatedCard
            title="Card 3"
            description="Third card with 0.4s delay"
            delay={0.4}
          />
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">9. Tailwind Integration</h2>
        <TailwindIntegration />
      </section>
    </div>
  )
}

/**
 * USAGE IN APP.TSX
 *
 * import { AnimatedExamples } from '@/components/AnimatedExamples'
 *
 * function App() {
 *   return <AnimatedExamples />
 * }
 */

/**
 * PERFORMANCE TIPS
 *
 * 1. Add willChange for transforms:
 *    <motion.div style={{ willChange: "transform" }} />
 *
 * 2. Use LazyMotion for smaller bundle (34 KB → 4.6 KB):
 *    import { LazyMotion, domAnimation, m } from "motion/react"
 *    <LazyMotion features={domAnimation}>
 *      <m.div animate={{ x: 100 }} />
 *    </LazyMotion>
 *
 * 3. For large lists (50+ items), use virtualization:
 *    pnpm add react-window
 *
 * See ../references/performance-optimization.md for full guide
 */

/**
 * ACCESSIBILITY
 *
 * Respect prefers-reduced-motion:
 *
 * import { MotionConfig } from "motion/react"
 *
 * <MotionConfig reducedMotion="user">
 *   <App />
 * </MotionConfig>
 *
 * User settings:
 * - macOS: System Settings → Accessibility → Display → Reduce motion
 * - Windows: Settings → Ease of Access → Display → Show animations
 * - iOS: Settings → Accessibility → Motion
 * - Android 9+: Settings → Accessibility → Remove animations
 */
