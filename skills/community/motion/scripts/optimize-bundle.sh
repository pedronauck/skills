#!/bin/bash
# Motion Bundle Optimizer
# Converts full motion component to LazyMotion for smaller bundle (34 KB → 4.6 KB)

set -e

echo "📦 Motion Bundle Optimizer"
echo "=========================="
echo ""

# Check if we're in a project with Motion
if [ ! -f "package.json" ]; then
  echo "❌ Error: package.json not found"
  exit 1
fi

if ! grep -q '"motion"\|"framer-motion"' package.json; then
  echo "❌ Error: Motion or Framer Motion not found in package.json"
  exit 1
fi

echo "✅ Motion detected"
echo ""

# Estimate current bundle impact
echo "📊 Current bundle impact: ~34 KB (full motion component)"
echo "📊 After optimization: ~4.6 KB (LazyMotion + domAnimation)"
echo "📊 Savings: ~29.4 KB (~86% reduction)"
echo ""

echo "⚠️  This script will:"
echo "   1. Show you how to set up LazyMotion"
echo "   2. Provide conversion examples"
echo "   3. NOT automatically modify your code (manual conversion required)"
echo ""

read -p "Continue? [y/N]: " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  exit 0
fi

echo ""
echo "===================="
echo "STEP 1: Add LazyMotion Provider"
echo "===================="
echo ""
echo "Create a LazyMotion wrapper component:"
echo ""

cat << 'EOF'
// src/components/MotionProvider.tsx (or app/providers.tsx for Next.js)
"use client" // Add this for Next.js App Router

import { LazyMotion, domAnimation } from "motion/react"
import { ReactNode } from "react"

export function MotionProvider({ children }: { children: ReactNode }) {
  return (
    <LazyMotion features={domAnimation}>
      {children}
    </LazyMotion>
  )
}
EOF

echo ""
echo "Then wrap your app:"
echo ""

cat << 'EOF'
// For Vite: src/main.tsx or src/App.tsx
import { MotionProvider } from "@/components/MotionProvider"

function App() {
  return (
    <MotionProvider>
      <YourApp />
    </MotionProvider>
  )
}

// For Next.js: app/layout.tsx
import { MotionProvider } from "@/components/MotionProvider"

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <MotionProvider>
          {children}
        </MotionProvider>
      </body>
    </html>
  )
}
EOF

echo ""
echo "===================="
echo "STEP 2: Convert Components"
echo "===================="
echo ""
echo "Change all 'motion' imports to 'm':"
echo ""

cat << 'EOF'
// BEFORE:
import { motion } from "motion/react"

<motion.div animate={{ x: 100 }} />

// AFTER:
import { m } from "motion/react"

<m.div animate={{ x: 100 }} />
EOF

echo ""
echo "===================="
echo "STEP 3: Find and Replace"
echo "===================="
echo ""
echo "Use find-and-replace in your editor:"
echo ""
echo "1. Find:    import { motion"
echo "   Replace: import { m"
echo ""
echo "2. Find:    from \"motion/react\""
echo "   Keep as is (or use motion/react-client for Next.js)"
echo ""
echo "3. Find:    <motion."
echo "   Replace: <m."
echo ""
echo "4. Find:    </motion."
echo "   Replace: </m."
echo ""

echo "===================="
echo "STEP 4: Verify Bundle Size"
echo "===================="
echo ""
echo "After converting, build your project and check bundle size:"
echo ""

cat << 'EOF'
# Vite
pnpm build
# Check dist/ folder size

# Next.js
pnpm build
# Check .next/ folder size or use @next/bundle-analyzer
EOF

echo ""
echo "Expected results:"
echo "  Before: ~34 KB for motion"
echo "  After:  ~4.6 KB for LazyMotion + domAnimation"
echo ""

echo "===================="
echo "STEP 5: Features Included"
echo "===================="
echo ""
echo "domAnimation includes:"
echo "  ✅ Transform animations (x, y, scale, rotate)"
echo "  ✅ Opacity animations"
echo "  ✅ Gestures (hover, tap, drag, pan)"
echo "  ✅ Layout animations"
echo "  ✅ useScroll, useTransform hooks"
echo "  ❌ SVG path animations (use domMax instead)"
echo ""
echo "If you need SVG animations, use domMax:"
echo ""

cat << 'EOF'
import { LazyMotion, domMax } from "motion/react"

<LazyMotion features={domMax}>
  {/* Now includes SVG */}
</LazyMotion>
EOF

echo ""
echo "Bundle size with domMax: ~6 KB (still better than 34 KB)"
echo ""

echo "===================="
echo "TROUBLESHOOTING"
echo "===================="
echo ""
echo "Issue: Animations not working after conversion"
echo "Solution: Verify LazyMotion wrapper is at root of component tree"
echo ""
echo "Issue: SVG animations not working"
echo "Solution: Use domMax instead of domAnimation"
echo ""
echo "Issue: Still seeing large bundle"
echo "Solution: Clear cache and rebuild"
echo ""

echo "===================="
echo "OPTIMIZATION COMPLETE"
echo "===================="
echo ""
echo "Summary:"
echo "  1. ✅ Wrap app in <LazyMotion features={domAnimation}>"
echo "  2. ✅ Change all motion.* to m.*"
echo "  3. ✅ Rebuild and verify bundle size"
echo ""
echo "Expected bundle reduction: ~86% (34 KB → 4.6 KB)"
echo ""
echo "📚 Full guide: ../references/performance-optimization.md"
echo ""
