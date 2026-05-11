#!/bin/bash
# Motion Setup Script
# Automates installation and initial setup for React + Vite + Next.js projects

set -e

echo "🎬 Motion Setup"
echo "==============="
echo ""

# Check if package.json exists
if [ ! -f "package.json" ]; then
  echo "❌ Error: package.json not found"
  echo "   Run this script from your project root"
  exit 1
fi

# Detect framework
FRAMEWORK="unknown"
USING_NEXTJS=false
USING_VITE=false
USING_CLOUDFLARE=false

if grep -q '"next"' package.json; then
  FRAMEWORK="Next.js"
  USING_NEXTJS=true
  echo "✅ Detected: Next.js project"
elif grep -q '"vite"' package.json; then
  FRAMEWORK="Vite"
  USING_VITE=true
  echo "✅ Detected: Vite project"
else
  echo "⚠️  Could not detect framework (Next.js or Vite)"
  echo "   Will proceed with generic setup"
fi

# Check for Cloudflare Workers
if grep -q '@cloudflare/vite-plugin\|wrangler' package.json; then
  USING_CLOUDFLARE=true
  echo "🔍 Detected: Cloudflare Workers project"
  echo ""
  echo "⚠️  WARNING: Motion has build compatibility issues with Wrangler"
  echo "   Recommendation: Use framer-motion v12.23.24 instead"
  echo ""
  read -p "Continue with Motion (may cause build errors) or use framer-motion? [motion/framer]: " choice
  if [ "$choice" = "framer" ]; then
    PACKAGE="framer-motion"
  else
    PACKAGE="motion"
  fi
else
  PACKAGE="motion"
fi

echo ""

# Detect package manager
if command -v pnpm &> /dev/null; then
  PKG_MANAGER="pnpm"
elif command -v yarn &> /dev/null; then
  PKG_MANAGER="yarn"
else
  PKG_MANAGER="npm"
fi

# Install Motion
echo "📦 Installing $PACKAGE using $PKG_MANAGER..."
if [ "$PKG_MANAGER" = "pnpm" ]; then
  pnpm add $PACKAGE
elif [ "$PKG_MANAGER" = "yarn" ]; then
  yarn add $PACKAGE
else
  npm install $PACKAGE
fi

echo "✅ Package installed"
echo ""

# Create directories
mkdir -p src/components
mkdir -p src/hooks

# Next.js specific setup
if [ "$USING_NEXTJS" = true ]; then
  echo "📝 Creating Next.js App Router Client Component wrapper..."

  # Create motion-client.tsx wrapper
  cat > src/components/motion-client.tsx << 'EOF'
"use client"

// Optimized import for Next.js (reduces client JS bundle)
import * as motion from "motion/react-client"

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
EOF

  echo "✅ Created: src/components/motion-client.tsx"
  echo ""

  # Create MotionProvider
  cat > src/components/MotionProvider.tsx << 'EOF'
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
EOF

  echo "✅ Created: src/components/MotionProvider.tsx"
  echo ""

  # Create example component
  cat > src/components/AnimatedButton.tsx << 'EOF'
"use client"

import { motion } from "motion/react-client"

export function AnimatedButton() {
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
EOF

  echo "✅ Created: src/components/AnimatedButton.tsx"
  echo ""
fi

# Vite specific setup
if [ "$USING_VITE" = true ]; then
  echo "📝 Creating Vite example component..."

  cat > src/components/AnimatedExample.tsx << 'EOF'
import { motion } from "motion/react"

export function AnimatedExample() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-6 bg-blue-100 rounded-lg"
    >
      <h2 className="text-xl font-bold">Motion Animation</h2>
      <p>This component fades in and slides up on mount.</p>
    </motion.div>
  )
}
EOF

  echo "✅ Created: src/components/AnimatedExample.tsx"
  echo ""
fi

# Summary
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo ""

if [ "$USING_NEXTJS" = true ]; then
  echo "1. Add MotionProvider to your root layout:"
  echo "   // src/app/layout.tsx"
  echo "   import { MotionProvider } from '@/components/MotionProvider'"
  echo "   "
  echo "   export default function RootLayout({ children }) {"
  echo "     return ("
  echo "       <html>"
  echo "         <body>"
  echo "           <MotionProvider>"
  echo "             {children}"
  echo "           </MotionProvider>"
  echo "         </body>"
  echo "       </html>"
  echo "     )"
  echo "   }"
  echo ""
  echo "2. Use Motion in any component:"
  echo "   import { motion } from '@/components/motion-client'"
  echo "   "
  echo "   <motion.div animate={{ opacity: 1 }}>Content</motion.div>"
  echo ""
  echo "3. See example:"
  echo "   import { AnimatedButton } from '@/components/AnimatedButton'"
  echo ""
elif [ "$USING_VITE" = true ]; then
  echo "1. Import the example component:"
  echo "   import { AnimatedExample } from '@/components/AnimatedExample'"
  echo ""
  echo "2. Use it in your app:"
  echo "   <AnimatedExample />"
  echo ""
fi

echo "4. Check templates/ folder for more examples:"
echo "   - Modal dialogs"
echo "   - Accordions"
echo "   - Carousels"
echo "   - Scroll animations"
echo "   - Layout transitions"
echo ""

if [ "$USING_CLOUDFLARE" = true ]; then
  echo "⚠️  IMPORTANT (Cloudflare Workers):"
  echo "   Monitor GitHub issue #2918 for Motion + Wrangler compatibility"
  echo "   Consider using framer-motion v12.23.24 if build errors occur"
  echo ""
fi

echo "📚 Documentation:"
echo "   - Official: https://motion.dev/docs/react"
echo "   - Skill docs: ../SKILL.md"
echo ""
