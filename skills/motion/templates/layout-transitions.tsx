// Motion Layout Animations & Shared Element Transitions
// Production-tested with Motion v12.23.24, React 19

/**
 * INSTALLATION
 *
 * pnpm add motion
 *
 * USAGE
 *
 * Copy components below into your project.
 * Layout animations use the FLIP technique for smooth, hardware-accelerated transitions.
 *
 * For Next.js App Router, add "use client" directive at top of file.
 */

import { motion, LayoutGroup } from "motion/react"
import { useState, ReactNode } from "react"

// ============================================================================
// PATTERN 1: Basic Layout Animation
// ============================================================================

/**
 * Automatically animates layout changes (position, size, etc.)
 * Uses FLIP technique: First, Last, Invert, Play
 */
export function ExpandableCard() {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <motion.div
      layout // Enable FLIP layout animations
      onClick={() => setIsExpanded(!isExpanded)}
      className={`cursor-pointer bg-white border rounded-lg shadow-md p-6 ${
        isExpanded ? "w-full" : "w-64"
      }`}
      transition={{ layout: { duration: 0.3, type: "spring" } }}
    >
      <motion.h3 layout className="text-xl font-bold mb-2">
        Click to Expand
      </motion.h3>

      {isExpanded && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <p>This content appears when expanded.</p>
          <p className="mt-2">Layout automatically animates the size change.</p>
        </motion.div>
      )}
    </motion.div>
  )
}

/**
 * KEY CONCEPT: The `layout` prop tells Motion to automatically animate
 * any layout changes (width, height, position) using GPU-accelerated transforms.
 * No JavaScript calculation needed - it's all done via FLIP technique.
 */

// ============================================================================
// PATTERN 2: Shared Element Transition (layoutId)
// ============================================================================

/**
 * Animate the same element between different states or routes.
 * Perfect for card → detail page transitions.
 */
interface Card {
  id: string
  title: string
  description: string
  color: string
}

export function SharedElementExample() {
  const [selectedCard, setSelectedCard] = useState<Card | null>(null)

  const cards: Card[] = [
    { id: "1", title: "Card 1", description: "Full description for card 1", color: "bg-red-500" },
    { id: "2", title: "Card 2", description: "Full description for card 2", color: "bg-blue-500" },
    { id: "3", title: "Card 3", description: "Full description for card 3", color: "bg-green-500" },
  ]

  return (
    <div>
      {/* Grid view */}
      {!selectedCard && (
        <div className="grid grid-cols-3 gap-4">
          {cards.map((card) => (
            <motion.div
              key={card.id}
              layoutId={card.id} // Connect this element to detail view
              onClick={() => setSelectedCard(card)}
              className={`${card.color} text-white p-6 rounded-lg cursor-pointer h-32 flex items-center justify-center`}
            >
              <motion.h3 layoutId={`title-${card.id}`} className="text-xl font-bold">
                {card.title}
              </motion.h3>
            </motion.div>
          ))}
        </div>
      )}

      {/* Detail view */}
      {selectedCard && (
        <motion.div
          layoutId={selectedCard.id} // Same layoutId = smooth transition
          onClick={() => setSelectedCard(null)}
          className={`${selectedCard.color} text-white p-12 rounded-lg cursor-pointer`}
        >
          <motion.h3 layoutId={`title-${selectedCard.id}`} className="text-4xl font-bold mb-4">
            {selectedCard.title}
          </motion.h3>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-xl"
          >
            {selectedCard.description}
          </motion.p>
        </motion.div>
      )}
    </div>
  )
}

/**
 * KEY CONCEPT: Elements with the same `layoutId` are treated as the same element
 * across different states/routes. Motion automatically morphs between them.
 */

// ============================================================================
// PATTERN 3: List Reordering with Layout
// ============================================================================

/**
 * Automatically animate items when list order changes.
 * Perfect for drag-to-reorder, filtering, sorting.
 */
interface Item {
  id: number
  text: string
}

export function AnimatedList() {
  const [items, setItems] = useState<Item[]>([
    { id: 1, text: "Item 1" },
    { id: 2, text: "Item 2" },
    { id: 3, text: "Item 3" },
    { id: 4, text: "Item 4" },
  ])

  const shuffle = () => {
    setItems([...items].sort(() => Math.random() - 0.5))
  }

  const reverse = () => {
    setItems([...items].reverse())
  }

  return (
    <div>
      <div className="flex gap-2 mb-4">
        <button onClick={shuffle} className="px-4 py-2 bg-blue-600 text-white rounded">
          Shuffle
        </button>
        <button onClick={reverse} className="px-4 py-2 bg-purple-600 text-white rounded">
          Reverse
        </button>
      </div>

      <div className="space-y-2">
        {items.map((item) => (
          <motion.div
            key={item.id}
            layout // Animate position changes automatically
            className="p-4 bg-white border rounded-lg shadow-sm"
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          >
            {item.text}
          </motion.div>
        ))}
      </div>
    </div>
  )
}

/**
 * KEY CONCEPT: When items reorder, the `layout` prop automatically animates
 * each item to its new position. No manual position calculation needed.
 */

// ============================================================================
// PATTERN 4: LayoutGroup (Namespacing)
// ============================================================================

/**
 * Use LayoutGroup to namespace layoutIds for reusable components.
 * Prevents conflicts when using multiple instances.
 */
interface TabPanelProps {
  tabs: Array<{ id: string; label: string; content: ReactNode }>
}

export function TabPanel({ tabs }: TabPanelProps) {
  const [activeTab, setActiveTab] = useState(tabs[0].id)

  return (
    <LayoutGroup> {/* Namespace layoutIds within this group */}
      <div className="space-y-4">
        {/* Tab buttons */}
        <div className="flex gap-4 border-b border-gray-200">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className="relative px-4 py-2"
            >
              {tab.label}

              {/* Shared underline */}
              {activeTab === tab.id && (
                <motion.div
                  layoutId="underline" // Shared within LayoutGroup
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600"
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="p-4">
          {tabs.find((tab) => tab.id === activeTab)?.content}
        </div>
      </div>
    </LayoutGroup>
  )
}

/**
 * USAGE
 *
 * <div className="grid grid-cols-2 gap-4">
 *   <TabPanel tabs={[...]} />
 *   <TabPanel tabs={[...]} />  {/* No layoutId conflicts! */}
 * </div>
 */

// ============================================================================
// PATTERN 5: Scrollable Container (layoutScroll)
// ============================================================================

/**
 * Fix layout animations in scrollable containers.
 * Without layoutScroll, animations break when container is scrolled.
 */
export function ScrollableList() {
  const [items, setItems] = useState<Item[]>(
    Array.from({ length: 20 }, (_, i) => ({
      id: i + 1,
      text: `Item ${i + 1}`,
    }))
  )

  const removeItem = (id: number) => {
    setItems(items.filter((item) => item.id !== id))
  }

  return (
    <motion.div
      layoutScroll // CRITICAL: Fixes animations in scrolled containers
      className="h-96 overflow-auto border border-gray-200 rounded-lg p-4 space-y-2"
    >
      {items.map((item) => (
        <motion.div
          key={item.id}
          layout
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          className="p-4 bg-white border rounded-lg shadow-sm flex justify-between items-center"
        >
          <span>{item.text}</span>
          <button
            onClick={() => removeItem(item.id)}
            className="px-3 py-1 bg-red-500 text-white rounded text-sm"
          >
            Remove
          </button>
        </motion.div>
      ))}
    </motion.div>
  )
}

/**
 * KEY CONCEPT: Without `layoutScroll`, removing items from a scrolled container
 * causes incomplete/broken animations. layoutScroll fixes this by accounting
 * for scroll offset in FLIP calculations.
 */

// ============================================================================
// PATTERN 6: Fixed Position (layoutRoot)
// ============================================================================

/**
 * Fix layout animations in fixed-position elements.
 * Without layoutRoot, fixed elements animate incorrectly.
 */
export function FixedModal() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-4 py-2 bg-blue-600 text-white rounded"
      >
        Toggle Fixed Modal
      </button>

      {isOpen && (
        <motion.div
          layoutRoot // CRITICAL: Fixes animations in fixed elements
          layout
          className="fixed bottom-4 right-4 w-64 bg-white border rounded-lg shadow-2xl p-4 z-50"
        >
          <h3 className="font-bold mb-2">Fixed Modal</h3>
          <p className="text-sm text-gray-700">
            This is a fixed-position element with layout animations.
          </p>
        </motion.div>
      )}
    </>
  )
}

/**
 * KEY CONCEPT: Fixed-position elements need `layoutRoot` to correctly
 * calculate scroll offset during FLIP animations.
 */

// ============================================================================
// PATTERN 7: Grid → List View Switching
// ============================================================================

/**
 * Smooth transition between grid and list layouts.
 */
export function ViewSwitcher() {
  const [view, setView] = useState<"grid" | "list">("grid")

  const items = Array.from({ length: 9 }, (_, i) => ({
    id: i + 1,
    title: `Item ${i + 1}`,
  }))

  return (
    <div>
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setView("grid")}
          className={`px-4 py-2 rounded ${
            view === "grid" ? "bg-blue-600 text-white" : "bg-gray-200"
          }`}
        >
          Grid
        </button>
        <button
          onClick={() => setView("list")}
          className={`px-4 py-2 rounded ${
            view === "list" ? "bg-blue-600 text-white" : "bg-gray-200"
          }`}
        >
          List
        </button>
      </div>

      <motion.div
        layout
        className={view === "grid" ? "grid grid-cols-3 gap-4" : "space-y-2"}
      >
        {items.map((item) => (
          <motion.div
            key={item.id}
            layout
            className="p-6 bg-white border rounded-lg shadow-sm"
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          >
            <h3 className="font-bold">{item.title}</h3>
          </motion.div>
        ))}
      </motion.div>
    </div>
  )
}

// ============================================================================
// PATTERN 8: Drag to Reorder (Manual Implementation)
// ============================================================================

/**
 * Drag items to reorder with visual feedback.
 * Note: Motion's Reorder component has Next.js compatibility issues.
 * This is a manual implementation that works everywhere.
 */
export function DragToReorder() {
  const [items, setItems] = useState<Item[]>([
    { id: 1, text: "Drag me" },
    { id: 2, text: "Reorder me" },
    { id: 3, text: "Move me around" },
    { id: 4, text: "Drop me anywhere" },
  ])

  return (
    <div className="space-y-2">
      {items.map((item, index) => (
        <motion.div
          key={item.id}
          layout
          drag="y"
          dragConstraints={{ top: 0, bottom: 0 }}
          dragElastic={0.1}
          whileDrag={{ scale: 1.05, boxShadow: "0 10px 40px rgba(0,0,0,0.2)" }}
          className="p-4 bg-white border rounded-lg shadow-sm cursor-grab active:cursor-grabbing"
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        >
          <div className="flex items-center gap-3">
            <span className="text-gray-400">☰</span>
            <span>{item.text}</span>
          </div>
        </motion.div>
      ))}
    </div>
  )
}

/**
 * Note: Full drag-to-reorder with position updates requires tracking
 * drag position and updating array order. For production, consider:
 * - @dnd-kit/core (recommended for Next.js)
 * - react-beautiful-dnd
 * - Motion's Reorder component (has Next.js issues, see GitHub #2183)
 */

// ============================================================================
// PATTERN 9: Masonry Layout Animation
// ============================================================================

/**
 * Animate items in masonry/Pinterest-style layout.
 */
export function MasonryLayout() {
  const [items, setItems] = useState(
    Array.from({ length: 12 }, (_, i) => ({
      id: i + 1,
      height: Math.floor(Math.random() * 200) + 100,
    }))
  )

  const shuffle = () => {
    setItems([...items].sort(() => Math.random() - 0.5))
  }

  return (
    <div>
      <button onClick={shuffle} className="px-4 py-2 bg-blue-600 text-white rounded mb-4">
        Shuffle
      </button>

      <div className="columns-3 gap-4">
        {items.map((item) => (
          <motion.div
            key={item.id}
            layout
            className="mb-4 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg p-4 text-white font-bold break-inside-avoid"
            style={{ height: item.height }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          >
            Item {item.id}
          </motion.div>
        ))}
      </div>
    </div>
  )
}

// ============================================================================
// ALL EXAMPLES DEMO
// ============================================================================

export function LayoutAnimationsDemo() {
  return (
    <div className="max-w-4xl mx-auto p-8 space-y-12">
      <h1 className="text-4xl font-bold mb-8">Layout Animations & Shared Elements</h1>

      <section>
        <h2 className="text-2xl font-bold mb-4">1. Basic Layout Animation</h2>
        <ExpandableCard />
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">2. Shared Element Transition</h2>
        <SharedElementExample />
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">3. List Reordering</h2>
        <AnimatedList />
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">4. Tab Panel with LayoutGroup</h2>
        <TabPanel
          tabs={[
            { id: "1", label: "Tab 1", content: <p>Content for tab 1</p> },
            { id: "2", label: "Tab 2", content: <p>Content for tab 2</p> },
            { id: "3", label: "Tab 3", content: <p>Content for tab 3</p> },
          ]}
        />
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">5. Scrollable Container</h2>
        <ScrollableList />
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">6. Fixed Position Modal</h2>
        <FixedModal />
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">7. Grid/List View Switcher</h2>
        <ViewSwitcher />
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">8. Drag to Reorder</h2>
        <DragToReorder />
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">9. Masonry Layout</h2>
        <MasonryLayout />
      </section>
    </div>
  )
}

/**
 * PERFORMANCE TIPS
 *
 * 1. Add willChange for layout animations:
 *    <motion.div layout style={{ willChange: "transform" }} />
 *
 * 2. Use layout prop only when needed:
 *    - If element size/position doesn't change, don't use layout
 *
 * 3. Combine with AnimatePresence for enter/exit:
 *    <AnimatePresence>
 *      {items.map(item => (
 *        <motion.div key={item.id} layout exit={{ opacity: 0 }} />
 *      ))}
 *    </AnimatePresence>
 *
 * 4. Use LayoutGroup to isolate layout calculations:
 *    - Prevents unnecessary recalculations across unrelated components
 *
 * See ../references/performance-optimization.md for full guide
 */

/**
 * COMMON ISSUES
 *
 * 1. Broken animations in scrollable containers
 *    Solution: Add layoutScroll prop
 *
 * 2. Incorrect animations in fixed elements
 *    Solution: Add layoutRoot prop
 *
 * 3. layoutId conflicts in reusable components
 *    Solution: Wrap in LayoutGroup
 *
 * 4. Elements not unmounting with layoutId + AnimatePresence
 *    Solution: Use LayoutGroup or avoid mixing exit + layout animations
 *
 * See ../SKILL.md for full troubleshooting guide
 */

/**
 * NEXT.JS USAGE
 *
 * Add "use client" directive at top of file:
 *
 * "use client"
 *
 * import { motion, LayoutGroup } from "motion/react-client"
 *
 * See ../references/nextjs-integration.md for comprehensive guide
 */
