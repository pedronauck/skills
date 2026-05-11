// Motion Scroll Animations & Parallax Effects
// Production-tested with Motion v12.23.24, React 19

/**
 * INSTALLATION
 *
 * pnpm add motion
 *
 * USAGE
 *
 * Copy examples below into your components.
 * All patterns use hardware-accelerated ScrollTimeline API when available.
 *
 * For Next.js App Router, add "use client" directive at top of file.
 */

import { motion, useScroll, useTransform, useInView, useMotionValue, useSpring } from "motion/react"
import { useRef } from "react"

// ============================================================================
// PATTERN 1: Scroll-Triggered Reveal (whileInView)
// ============================================================================

/**
 * Fade in and slide up when element enters viewport.
 * Perfect for revealing sections as user scrolls.
 */
export function FadeInSection({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{
        once: true,       // Animate only once (don't re-animate on scroll up)
        margin: "-100px", // Start animation 100px before entering viewport
        amount: 0.3,      // Trigger when 30% of element is visible
      }}
      transition={{ duration: 0.5 }}
    >
      {children}
    </motion.div>
  )
}

/**
 * USAGE
 *
 * <FadeInSection>
 *   <h2>This section fades in when you scroll to it</h2>
 * </FadeInSection>
 */

// ============================================================================
// PATTERN 2: Parallax Hero Section
// ============================================================================

/**
 * Multi-layer parallax effect with different scroll speeds.
 * Perfect for hero sections and landing pages.
 */
export function ParallaxHero() {
  const { scrollY } = useScroll()

  // Transform scroll position to different speeds for each layer
  const y1 = useTransform(scrollY, [0, 1000], [0, -300])   // Fast layer (background)
  const y2 = useTransform(scrollY, [0, 1000], [0, -150])   // Medium layer (middle)
  const y3 = useTransform(scrollY, [0, 1000], [0, -50])    // Slow layer (foreground)
  const opacity = useTransform(scrollY, [0, 300], [1, 0])  // Fade out

  return (
    <div className="relative h-screen overflow-hidden">
      {/* Background layer (fastest) */}
      <motion.div
        style={{ y: y1 }}
        className="absolute inset-0 -z-10"
      >
        <img
          src="/images/background.jpg"
          alt="Background"
          className="w-full h-full object-cover"
        />
      </motion.div>

      {/* Middle layer (medium speed) */}
      <motion.div
        style={{ y: y2 }}
        className="absolute inset-0 -z-5"
      >
        <img
          src="/images/mountains.png"
          alt="Mountains"
          className="w-full h-full object-cover"
        />
      </motion.div>

      {/* Foreground content (slowest) + fade out */}
      <motion.div
        style={{ y: y3, opacity }}
        className="relative z-10 flex items-center justify-center h-full"
      >
        <div className="text-center text-white">
          <h1 className="text-6xl font-bold mb-4">Welcome</h1>
          <p className="text-2xl">Scroll down to see parallax effect</p>
        </div>
      </motion.div>
    </div>
  )
}

// ============================================================================
// PATTERN 3: Scroll-Linked Progress Bar
// ============================================================================

/**
 * Progress bar that fills as user scrolls through page.
 * Perfect for blog posts and long-form content.
 */
export function ScrollProgressBar() {
  const { scrollYProgress } = useScroll()

  return (
    <motion.div
      style={{ scaleX: scrollYProgress }}
      className="fixed top-0 left-0 right-0 h-1 bg-blue-600 origin-left z-50"
    />
  )
}

/**
 * USAGE
 *
 * // In your layout or page
 * <ScrollProgressBar />
 * <YourContent />
 */

// ============================================================================
// PATTERN 4: Section-Specific Scroll Progress
// ============================================================================

/**
 * Track scroll progress within a specific section (not entire page).
 * Perfect for multi-section landing pages.
 */
export function SectionScrollIndicator() {
  const ref = useRef<HTMLDivElement>(null)

  // Only track scroll within this section
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"], // Start when section enters, end when it leaves
  })

  // Convert 0-1 progress to 0-100 for display
  const percentage = useTransform(scrollYProgress, [0, 1], [0, 100])

  return (
    <section ref={ref} className="min-h-screen bg-gray-100 p-8">
      <motion.div
        style={{ scaleX: scrollYProgress }}
        className="h-2 bg-purple-600 mb-4 origin-left"
      />
      <motion.p className="text-2xl font-bold">
        Section Progress: {percentage.get().toFixed(0)}%
      </motion.p>
      <p className="mt-4 text-gray-700">
        Scroll through this section to see the progress bar fill.
      </p>
    </section>
  )
}

// ============================================================================
// PATTERN 5: Smooth Parallax with Spring Physics
// ============================================================================

/**
 * Parallax with spring physics for natural, smooth motion.
 * Adds inertia/lag effect like Apple's website.
 */
export function SmoothParallax() {
  const { scrollY } = useScroll()

  // Add spring physics to parallax for smooth, natural motion
  const y = useSpring(useTransform(scrollY, [0, 1000], [0, -200]), {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001,
  })

  return (
    <div className="relative h-screen overflow-hidden">
      <motion.div
        style={{ y }}
        className="absolute inset-0"
      >
        <img
          src="/images/hero.jpg"
          alt="Hero"
          className="w-full h-full object-cover"
        />
      </motion.div>

      <div className="relative z-10 flex items-center justify-center h-full">
        <h1 className="text-6xl font-bold text-white">Smooth Parallax</h1>
      </div>
    </div>
  )
}

// ============================================================================
// PATTERN 6: Scale on Scroll
// ============================================================================

/**
 * Scale element based on scroll position.
 * Perfect for sticky headers that shrink on scroll.
 */
export function ScaleOnScroll({ children }: { children: React.ReactNode }) {
  const { scrollY } = useScroll()

  // Scale from 1 to 0.8 as user scrolls from 0 to 300px
  const scale = useTransform(scrollY, [0, 300], [1, 0.8])

  return (
    <motion.div style={{ scale }}>
      {children}
    </motion.div>
  )
}

// ============================================================================
// PATTERN 7: Horizontal Scroll Animation
// ============================================================================

/**
 * Horizontal scroll gallery triggered by vertical scroll.
 * Creates "scroll-jacking" effect like Apple product pages.
 */
export function HorizontalScrollGallery() {
  const targetRef = useRef<HTMLDivElement>(null)

  const { scrollYProgress } = useScroll({
    target: targetRef,
    offset: ["start start", "end end"],
  })

  // Convert vertical scroll to horizontal movement
  // 0 → 0%, 1 → -300% (moves 3 screens to the left)
  const x = useTransform(scrollYProgress, [0, 1], ["0%", "-300%"])

  return (
    <section ref={targetRef} className="relative h-[400vh]">
      <div className="sticky top-0 h-screen overflow-hidden">
        <motion.div style={{ x }} className="flex h-full">
          <div className="min-w-full h-full bg-red-500 flex items-center justify-center text-white text-4xl">
            Panel 1
          </div>
          <div className="min-w-full h-full bg-blue-500 flex items-center justify-center text-white text-4xl">
            Panel 2
          </div>
          <div className="min-w-full h-full bg-green-500 flex items-center justify-center text-white text-4xl">
            Panel 3
          </div>
          <div className="min-w-full h-full bg-purple-500 flex items-center justify-center text-white text-4xl">
            Panel 4
          </div>
        </motion.div>
      </div>
    </section>
  )
}

// ============================================================================
// PATTERN 8: Rotate on Scroll
// ============================================================================

/**
 * Rotate element based on scroll position.
 * Perfect for decorative elements and logos.
 */
export function RotateOnScroll() {
  const { scrollY } = useScroll()

  // Rotate 360 degrees as user scrolls 1000px
  const rotate = useTransform(scrollY, [0, 1000], [0, 360])

  return (
    <motion.div
      style={{ rotate }}
      className="w-32 h-32 bg-gradient-to-br from-pink-500 to-purple-600 rounded-full"
    />
  )
}

// ============================================================================
// PATTERN 9: Sticky Element with Scroll Effects
// ============================================================================

/**
 * Sticky element that scales and fades as user scrolls past.
 * Perfect for "scroll to continue" indicators.
 */
export function StickyScrollIndicator() {
  const { scrollY } = useScroll()

  // Fade out and scale down after scrolling 200px
  const opacity = useTransform(scrollY, [0, 200], [1, 0])
  const scale = useTransform(scrollY, [0, 200], [1, 0.5])

  return (
    <motion.div
      style={{ opacity, scale }}
      className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50"
    >
      <div className="flex flex-col items-center text-gray-600">
        <p className="mb-2">Scroll Down</p>
        <svg
          className="w-6 h-6 animate-bounce"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 14l-7 7m0 0l-7-7m7 7V3"
          />
        </svg>
      </div>
    </motion.div>
  )
}

// ============================================================================
// PATTERN 10: useInView Hook (Manual Control)
// ============================================================================

/**
 * More control than whileInView prop.
 * Trigger custom animations when element enters viewport.
 */
export function CustomInViewAnimation() {
  const ref = useRef<HTMLDivElement>(null)

  // Returns true when element is in viewport
  const isInView = useInView(ref, {
    once: true,
    margin: "-100px",
    amount: 0.5,
  })

  return (
    <div ref={ref} className="min-h-screen flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.5 }}
        animate={isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.5 }}
        transition={{ duration: 0.5 }}
        className="p-8 bg-blue-100 rounded-lg"
      >
        <h2 className="text-2xl font-bold">
          {isInView ? "I'm in view!" : "Scroll to me"}
        </h2>
      </motion.div>
    </div>
  )
}

// ============================================================================
// PATTERN 11: Scroll-Linked Color Change
// ============================================================================

/**
 * Change background color based on scroll position.
 * Perfect for section transitions.
 */
export function ScrollColorChange() {
  const { scrollYProgress } = useScroll()

  // Interpolate between colors
  const backgroundColor = useTransform(
    scrollYProgress,
    [0, 0.33, 0.66, 1],
    ["#ef4444", "#3b82f6", "#10b981", "#8b5cf6"] // red → blue → green → purple
  )

  return (
    <motion.div
      style={{ backgroundColor }}
      className="min-h-[200vh] flex items-center justify-center"
    >
      <div className="text-white text-4xl font-bold">
        Background changes as you scroll
      </div>
    </motion.div>
  )
}

// ============================================================================
// ALL EXAMPLES COMPONENT
// ============================================================================

/**
 * Demo page showing all scroll patterns.
 */
export function ScrollAnimationExamples() {
  return (
    <div>
      <ScrollProgressBar />

      <ParallaxHero />

      <FadeInSection>
        <div className="container mx-auto p-8">
          <h2 className="text-4xl font-bold mb-4">Fade In Section</h2>
          <p className="text-gray-700">
            This section fades in when you scroll to it.
          </p>
        </div>
      </FadeInSection>

      <SectionScrollIndicator />

      <SmoothParallax />

      <div className="container mx-auto p-8">
        <ScaleOnScroll>
          <h2 className="text-4xl font-bold mb-4">Scale on Scroll</h2>
          <p className="text-gray-700">This scales down as you scroll.</p>
        </ScaleOnScroll>
      </div>

      <HorizontalScrollGallery />

      <div className="container mx-auto p-8 flex justify-center">
        <RotateOnScroll />
      </div>

      <StickyScrollIndicator />

      <CustomInViewAnimation />

      <ScrollColorChange />

      <div className="h-screen" /> {/* Spacer to allow scrolling */}
    </div>
  )
}

/**
 * PERFORMANCE TIPS
 *
 * 1. Add willChange for transforms:
 *    <motion.div style={{ willChange: "transform" }} />
 *
 * 2. Use ScrollTimeline API (automatic in Motion):
 *    - Hardware-accelerated
 *    - Runs on compositor thread (no JavaScript on scroll)
 *    - 120fps on capable devices
 *
 * 3. Avoid animating expensive properties:
 *    ✅ Good: transform, opacity
 *    ❌ Bad: width, height, top, left (causes layout reflow)
 *
 * 4. Use useSpring for smooth, natural motion:
 *    const y = useSpring(useTransform(scrollY, [0, 1000], [0, -200]))
 *
 * 5. Debounce complex calculations:
 *    Only update on significant scroll changes, not every pixel
 */

/**
 * ACCESSIBILITY
 *
 * 1. Respect prefers-reduced-motion:
 *
 *    import { MotionConfig } from "motion/react"
 *
 *    <MotionConfig reducedMotion="user">
 *      <ScrollAnimationExamples />
 *    </MotionConfig>
 *
 * 2. Don't rely on scroll animations for critical content:
 *    - Ensure content is visible without JavaScript
 *    - Provide alternative navigation
 *    - Don't hide important UI behind scroll triggers
 *
 * 3. Test with keyboard navigation:
 *    - Tab through page
 *    - Ensure animations don't block keyboard focus
 *
 * See ../references/performance-optimization.md for full guide
 */

/**
 * NEXT.JS USAGE
 *
 * Add "use client" directive at top of file:
 *
 * "use client"
 *
 * import { motion, useScroll, ... } from "motion/react-client"
 *
 * See ../references/nextjs-integration.md for comprehensive guide
 */
