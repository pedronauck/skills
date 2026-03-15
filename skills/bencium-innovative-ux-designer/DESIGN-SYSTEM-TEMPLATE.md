# Design System Template

Meta-framework for understanding what's fixed, project-specific, and adaptable in your design system.

## Purpose

This template helps you distinguish between:
- **Fixed Elements**: Universal rules that never change
- **Project-Specific Elements**: Filled in for each project based on brand
- **Adaptable Elements**: Context-dependent implementations

---

## I. FIXED ELEMENTS

These foundations remain consistent across all projects, regardless of brand or context.

### 1. Spacing Scale

**Fixed System:**
```
4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px, 96px
```

**Usage:**
- Margins, padding, gaps between elements
- Mathematical relationships ensure visual harmony
- Use multipliers of base unit (4px)

**Why Fixed:**
Consistent spacing creates visual rhythm regardless of brand personality.

### 2. Grid System

**Fixed Structure:**
- **12-column grid** for most layouts (divisible by 2, 3, 4, 6)
- **16-column grid** for data-heavy interfaces
- **Gutters**: 16px (mobile), 24px (tablet), 32px (desktop)

**Why Fixed:**
Grid provides structural order. Brand personality shows through color, typography, content—not grid structure.

### 3. Accessibility Standards

**Fixed Requirements:**
- **WCAG 2.1 AA** compliance minimum
- **Contrast**: 4.5:1 for normal text, 3:1 for large text
- **Touch targets**: Minimum 44×44px
- **Keyboard navigation**: All interactive elements accessible
- **Screen reader**: Semantic HTML, ARIA labels where needed

**Why Fixed:**
Accessibility is not negotiable. It's a baseline requirement for ethical, legal, and usable products.

### 4. Typography Hierarchy Logic

**Fixed Structure:**
- **Mathematical scaling**: 1.25x (major third) or 1.333x (perfect fourth)
- **Hierarchy levels**: Display → H1 → H2 → H3 → Body → Small → Caption
- **Line height**: 1.5x for body text, 1.2-1.3x for headlines
- **Line length**: 45-75 characters optimal

**Why Fixed:**
Mathematical relationships create predictable, harmonious hierarchy. Specific fonts change, but the logic doesn't.

### 5. Component Architecture

**Fixed Patterns:**
- **Button states**: Default, Hover, Active, Focus, Disabled
- **Form structure**: Label above input, error below, helper text optional
- **Modal pattern**: Overlay + centered content + close mechanism
- **Card structure**: Container → Header → Body → Footer (optional)

**Why Fixed:**
Users expect consistent component behavior. Architecture is fixed; appearance is project-specific.

### 6. Animation Timing Framework

**Fixed Physics Profiles:**
- **Lightweight** (icons, chips): 150ms
- **Standard** (cards, panels): 300ms
- **Weighty** (modals, pages): 500ms

**Fixed Easing:**
- **Ease-out**: Entrances (fast start, slow end)
- **Ease-in**: Exits (slow start, fast end)
- **Ease-in-out**: Transitions (smooth both ends)

**Why Fixed:**
Natural physics feel consistent across brands. Duration and easing create that feeling.

---

## II. PROJECT-SPECIFIC ELEMENTS

Fill in these for each project based on brand personality and purpose.

### 1. Brand Color System

**Template Structure:**

```
NEUTRALS (4-5 colors):
- Background lightest: _______ (e.g., slate-50 or warm-white)
- Surface: _______ (e.g., slate-100)
- Border/divider: _______ (e.g., slate-300)
- Text secondary: _______ (e.g., slate-600)
- Text primary: _______ (e.g., slate-900)

ACCENTS (1-3 colors):
- Primary (main CTA): _______ (e.g., teal-500)
- Secondary (alternative action): _______ (optional)
- Status colors:
  - Success: _______ (green-ish)
  - Warning: _______ (amber-ish)
  - Error: _______ (red-ish)
  - Info: _______ (blue-ish)
```

**Questions to Answer:**
- What emotion should the brand evoke? (Trust, excitement, calm, urgency)
- Warm or cool neutrals?
- Conservative or bold accents?

**Examples:**

**Project A: Fintech App**
```
Neutrals: Cool greys (slate-50 → slate-900)
Primary: Deep blue (#0A2463) – trust, professionalism
Success: Muted green (#10B981)
Why: Financial products need trust, not playfulness
```

**Project B: Creative Community**
```
Neutrals: Warm greys with beige undertones
Primary: Coral (#FF6B6B) – energy, creativity
Success: Teal (#06D6A0) – fresh, unexpected
Why: Creative spaces should feel inviting, not corporate
```

**Project C: Healthcare Platform**
```
Neutrals: Pure greys (minimal color temperature)
Primary: Soft blue (#4A90E2) – calm, clinical
Success: Medical green (#38A169)
Why: Healthcare needs clarity and calm, not distraction
```

### 2. Typography Pairing

**Template:**

```
HEADLINE FONT: _______
- Weight: _______ (e.g., Bold 700)
- Use case: H1, H2, display text
- Personality: _______ (geometric/humanist/serif/etc.)

BODY FONT: _______
- Weight: _______ (e.g., Regular 400, Medium 500)
- Use case: Paragraphs, UI text
- Personality: _______ (neutral/readable/efficient)

OPTIONAL ACCENT FONT: _______
- Weight: _______
- Use case: _______ (special headlines, callouts)
```

**Pairing Logic:**
- Serif + Sans-serif (classic, editorial)
- Geometric + Humanist (modern + warm)
- Display + System (distinctive + efficient)

**Examples:**

**Project A: Editorial Platform**
```
Headline: Playfair Display (Serif, Bold 700)
Body: Inter (Sans-serif, Regular 400)
Why: Serif headlines = trustworthy, editorial feel
```

**Project B: Tech Startup**
```
Headline: DM Sans (Sans-serif, Bold 700)
Body: DM Sans (Regular 400, Medium 500)
Why: Single-font system = modern, efficient, cohesive
```

**Project C: Luxury Brand**
```
Headline: Cormorant Garamond (Serif, Light 300)
Body: Lato (Sans-serif, Regular 400)
Why: Elegant serif + readable sans = sophisticated
```

### 3. Tone of Voice

**Template:**

```
BRAND PERSONALITY:
- Formal ↔ Casual: _______ (1-10 scale)
- Professional ↔ Friendly: _______ (1-10 scale)
- Serious ↔ Playful: _______ (1-10 scale)
- Authoritative ↔ Conversational: _______ (1-10 scale)

MICROCOPY EXAMPLES:
- Button label (submit form): _______
- Error message (invalid email): _______
- Success message (saved): _______
- Empty state: _______

ANIMATION PERSONALITY:
- Speed: _______ (quick/moderate/slow)
- Feel: _______ (precise/smooth/bouncy)
```

**Examples:**

**Project A: Banking App**
```
Personality: Formal (8), Professional (9), Serious (8)
Button: "Submit Application"
Error: "Email address format is invalid"
Success: "Application submitted successfully"
Animation: Quick (precise, efficient, no-nonsense)
```

**Project B: Social App**
```
Personality: Casual (8), Friendly (9), Playful (7)
Button: "Let's go!"
Error: "Hmm, that email doesn't look right"
Success: "Nice! You're all set 🎉"
Animation: Moderate (smooth, friendly bounce)
```

### 4. Animation Speed & Feel

**Template:**

```
SPEED PREFERENCE:
- UI interactions: _______ (100-150ms / 150-200ms / 200-300ms)
- State changes: _______ (200ms / 300ms / 400ms)
- Page transitions: _______ (300ms / 500ms / 700ms)

ANIMATION STYLE:
- Easing preference: _______ (sharp / standard / bouncy)
- Movement type: _______ (minimal / smooth / expressive)
```

**Examples:**

**Project A: Trading Platform**
```
Speed: Fast (100ms UI, 200ms states, 300ms pages)
Style: Sharp easing, minimal movement
Why: Traders need speed, not distraction
```

**Project B: Wellness App**
```
Speed: Slow (200ms UI, 400ms states, 500ms pages)
Style: Smooth easing, gentle movement
Why: Calm, relaxing experience matches brand
```

---

## III. ADAPTABLE ELEMENTS

Context-dependent implementations that vary based on use case.

### 1. Component Variations

**Button Variants:**
- **Primary**: Full background color (high emphasis)
- **Secondary**: Outline only (medium emphasis)
- **Tertiary**: Text only (low emphasis)
- **Destructive**: Red-ish (danger actions)
- **Ghost**: Minimal (navigation, toolbars)

**Adaptation Rules:**
- Primary: Main CTA, one per screen section
- Secondary: Alternative actions
- Tertiary: Less important actions, multiple allowed
- Use brand colors, but hierarchy logic is fixed

### 2. Responsive Breakpoints

**Fixed Ranges:**
- XS: 0-479px (small phones)
- SM: 480-767px (large phones)
- MD: 768-1023px (tablets)
- LG: 1024-1439px (laptops)
- XL: 1440px+ (desktop)

**Adaptable Implementations:**

**Simple Content Site:**
```
XS-SM: Single column
MD: 2 columns
LG-XL: 3 columns max
Why: Content-focused, don't overwhelm
```

**Dashboard/Data App:**
```
XS: Collapsed, cards stack
SM: Simplified sidebar
MD: Full sidebar + main content
LG-XL: Sidebar + main + right panel
Why: Data apps need more screen real estate
```

### 3. Dark Mode Palette

**Adaptation Strategy:**

Not a simple inversion. Dark mode needs adjusted contrast:

**Light Mode:**
```
Background: #FFFFFF (white)
Text: #0F172A (slate-900) → 21:1 contrast
```

**Dark Mode (Adapted):**
```
Background: #0F172A (slate-900)
Text: #E2E8F0 (slate-200) → 15.8:1 contrast (still AA, but softer)
```

**Why Adapt:**
Pure white on pure black is too harsh. Dark mode needs slightly lower contrast for eye comfort.

### 4. Loading States

**Context-Dependent:**

**Fast operations (<500ms):**
- No loading indicator (feels instant)

**Medium operations (500ms-2s):**
- Spinner or skeleton screen

**Long operations (>2s):**
- Progress bar with percentage
- Or: Skeleton + estimated time

**Interactive Operations:**
- Button shows spinner inside (don't disable, show state)

### 5. Error Handling Strategy

**Context-Dependent:**

**Form Errors:**
```
Validate: On blur (after user leaves field)
Display: Inline below field
Recovery: Clear error on fix
```

**API Errors:**
```
Transient (network): Show retry button
Permanent (404): Show helpful message + next steps
Critical (500): Contact support option
```

**Data Errors:**
```
Missing: Show empty state with action
Corrupt: Show error boundary with reload
Invalid: Highlight + explain what's wrong
```

---

## DECISION TREE

When implementing a feature, ask:

### Is this...

**FIXED?**
- Does it affect structure, accessibility, or universal UX?
- Examples: Spacing scale, grid, contrast ratios, component architecture
- **Action**: Use the fixed system, no variation

**PROJECT-SPECIFIC?**
- Does it express brand personality or purpose?
- Examples: Colors, typography, tone of voice, animation feel
- **Action**: Fill in the template for this project

**ADAPTABLE?**
- Does it depend on context, content, or use case?
- Examples: Component variants, responsive behavior, error handling
- **Action**: Choose appropriate variation based on context

---

## EXAMPLE: Implementing a "Submit" Button

### Fixed Elements (Always the same):
- Touch target: 44px minimum height
- Padding: 16px horizontal (from spacing scale)
- States: Default, Hover, Active, Focus, Disabled
- Animation: 150ms ease-out (lightweight profile)

### Project-Specific (Filled per project):
- **Project A (Bank)**: Dark blue background, white text, "Submit Application"
- **Project B (Social)**: Coral background, white text, "Let's Go!"
- **Project C (Healthcare)**: Soft blue background, white text, "Continue"

### Adaptable (Context-dependent):
- **Form context**: Primary button (full color)
- **Toolbar context**: Ghost button (text only)
- **Danger context**: Destructive variant (red-ish)

---

## VALIDATION CHECKLIST

Before finalizing a design, check:

### Fixed Elements
- [ ] Uses spacing scale (4/8/12/16/24/32/48/64/96px)
- [ ] Follows grid system (12 or 16 columns)
- [ ] Meets WCAG AA contrast (4.5:1 normal, 3:1 large)
- [ ] Touch targets ≥ 44px
- [ ] Typography follows mathematical scale
- [ ] Components follow standard architecture

### Project-Specific Elements
- [ ] Brand colors filled in and intentional
- [ ] Typography pairing chosen and justified
- [ ] Tone of voice defined and consistent
- [ ] Animation speed matches brand personality

### Adaptable Elements
- [ ] Component variants appropriate for context
- [ ] Responsive behavior fits content type
- [ ] Loading states match operation duration
- [ ] Error handling fits error type

---

## PROJECT KICKOFF TEMPLATE

Use this to start a new project:

```
PROJECT NAME: _______________________
PURPOSE: ____________________________

BRAND PERSONALITY:
- Primary emotion: _______
- Warm or cool: _______
- Formal or casual: _______
- Conservative or bold: _______

COLORS (fill the template):
- Neutral base: _______
- Primary accent: _______
- Status colors: _______ / _______ / _______

TYPOGRAPHY (fill the template):
- Headline font: _______
- Body font: _______
- Pairing rationale: _______

TONE:
- Button labels style: _______
- Error message style: _______
- Success message style: _______

ANIMATION:
- Speed preference: _______ (fast/moderate/slow)
- Feel preference: _______ (sharp/smooth/bouncy)

TARGET DEVICES:
- Primary: _______ (mobile/desktop/both)
- Secondary: _______
```

---

## MAINTAINING CONSISTENCY

### Documentation
- Keep this template updated as system evolves
- Document WHY choices were made, not just WHAT

### Communication
- Share with designers: "Here's what varies vs. what's fixed"
- Share with developers: "Here are the design tokens"

### Tooling
- Use CSS variables for project-specific values
- Use Tailwind config for spacing scale
- Use design tokens in Figma/Storybook

### Reviews
- Audit: Does new work follow fixed elements?
- Validate: Are project-specific elements intentional?
- Question: Are adaptations justified by context?

---

## EXAMPLES OF COMPLETE SYSTEMS

### System A: B2B SaaS (Conservative)

**Fixed**: Standard spacing, 12-col grid, WCAG AA, major third type scale
**Project-Specific**:
- Colors: Cool greys + corporate blue
- Typography: DM Sans (headlines + body)
- Tone: Professional, formal
- Animation: Quick, precise (150ms)
**Adaptable**:
- Dashboard gets multi-panel layout
- Forms are extensive (use progressive disclosure)
- Errors show detailed technical info

### System B: Consumer Social App (Playful)

**Fixed**: Same spacing/grid/accessibility/type logic
**Project-Specific**:
- Colors: Warm greys + vibrant coral
- Typography: Poppins (headlines) + Inter (body)
- Tone: Casual, friendly, playful
- Animation: Moderate, bouncy (200ms)
**Adaptable**:
- Mobile-first (most users on phones)
- Forms are minimal (progressive profiling)
- Errors are friendly, not technical

### System C: Healthcare Platform (Clinical)

**Fixed**: Same foundational structure
**Project-Specific**:
- Colors: Pure greys + medical blue
- Typography: System fonts (SF Pro / Segoe)
- Tone: Clear, authoritative, calm
- Animation: Slow, smooth (300ms)
**Adaptable**:
- Desktop-first (clinical use at workstations)
- Forms are complex (HIPAA compliance)
- Errors are precise with next steps

---

## KEY TAKEAWAY

**The system flexibility framework lets you:**
- Maintain consistency (fixed elements)
- Express brand personality (project-specific)
- Adapt to context (adaptable elements)

**Without this framework:**
- Designers reinvent spacing every project
- Components feel inconsistent across products
- Brand personality overrides accessibility
- Context-blind implementations feel wrong

**With this framework:**
- Speed: Start from proven foundations
- Consistency: Fixed elements guarantee it
- Flexibility: Express unique brand identity
- Context: Adapt without breaking system
