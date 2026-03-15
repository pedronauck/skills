# Design Specification Extraction Patterns

This reference provides comprehensive patterns for extracting design specifications from visual sources (screenshots, Figma exports, mockups).

## Table of Contents

1. [Visual Analysis Fundamentals](#visual-analysis-fundamentals)
2. [Layout Detection Patterns](#layout-detection-patterns)
3. [Component Detection Patterns](#component-detection-patterns)
4. [Color Extraction Patterns](#color-extraction-patterns)
5. [Typography Extraction Patterns](#typography-extraction-patterns)
6. [Spacing and Dimensions Patterns](#spacing-and-dimensions-patterns)
7. [State Inference Rules](#state-inference-rules)
8. [Accessibility Analysis Patterns](#accessibility-analysis-patterns)
9. [Component Classification Taxonomy](#component-classification-taxonomy)
10. [Confidence Scoring](#confidence-scoring)
11. [Output Format Conversions](#output-format-conversions)

---

## Visual Analysis Fundamentals

### Image Preprocessing Considerations

Before extraction, assess the source image:

**1. Resolution Assessment**
- High resolution (2x/3x): Scale coordinates by density factor
- Low resolution: Note reduced confidence in fine details
- Variable density: Normalize to 1x for consistent measurements

**2. Source Type Identification**

| Source Type | Characteristics | Confidence Impact |
|-------------|-----------------|-------------------|
| Figma Export | Clean vectors, precise measurements | High |
| Website Screenshot | May include browser chrome | Medium-High |
| Mockup/Wireframe | Lower fidelity, focus on structure | Medium |
| Mobile Screenshot | Status bar, navigation gestures | Medium |
| Photo of Screen | Perspective issues, artifacts | Low |

**3. Content Area Detection**
- Identify actual design area vs. surrounding artifacts
- Browser chrome, device frames should be excluded from analysis
- Status bars, navigation bars may or may not be part of design

### Hierarchical Decomposition Strategy

Extract structure using depth-first analysis:

```
1. Identify major regions (header, main, sidebar, footer)
2. Within each region, identify containers/sections
3. Within containers, identify individual components
4. Within components, identify atomic elements
5. Validate parent-child containment relationships
```

---

## Layout Detection Patterns

### Viewport Classification

| Aspect Ratio | Width Range | Classification |
|--------------|-------------|----------------|
| < 0.6 | < 480px | Mobile Portrait |
| 0.6 - 0.8 | 480-768px | Mobile Landscape / Small Tablet |
| 0.8 - 1.2 | 768-1024px | Tablet |
| > 1.2 | > 1024px | Desktop |

### Primary Layout Types

#### Single Column Layout
**Visual Indicators:**
- Content centered horizontally
- Elements stacked vertically
- Consistent left/right margins
- Maximum width constraint visible

#### Multi-Column Grid
**Visual Indicators:**
- Visible column divisions (2, 3, 4, or 12-column)
- Consistent gutter spacing between columns
- Elements aligned to grid lines
- Responsive breakpoint hints

#### Sidebar + Main Layout
**Visual Indicators:**
- Narrow fixed-width column on left or right
- Wider flexible main content area
- Clear visual separation (border, background, or space)
- Navigation elements typically in sidebar

### Region Detection Heuristics

**Header Detection:**
- Located in top 15% of viewport
- Full width or near-full width
- Contains logo (top-left corner image)
- Contains navigation elements
- Typically 60-100px height

**Navigation Detection:**
- Sidebar: Left or right edge, narrow width (200-300px), full height
- Top nav: Within header region, horizontal list of links
- Contains repeated similar elements (nav items)

**Main Content Detection:**
- Largest contiguous content area
- Excludes header, footer, sidebar regions
- Contains primary content blocks

**Footer Detection:**
- Located in bottom 10-15% of viewport
- Full width
- Often darker background than main content
- Contains links, copyright text, social icons

### Layout Regions Reference

| Region | Visual Cues | Typical Elements |
|--------|-------------|------------------|
| Header | Top position, full width, distinct background | Logo, navigation, search, auth buttons |
| Navigation | Horizontal or vertical menu structure | Links, icons, dropdowns |
| Hero | Large top section, prominent heading | Headline, CTA, image/illustration |
| Main | Central content area | Primary page content |
| Sidebar | Narrow column, secondary info | Filters, navigation, widgets |
| Footer | Bottom position, darker background | Links, copyright, social icons |

### Grid System Detection

**Step 1: Identify Container Width**
- Look for consistent outer margins
- Note if content is centered or full-bleed
- Measure visual max-width

**Step 2: Count Columns**
- Align visible elements to potential column lines
- Look for patterns: 12-col (Bootstrap), 4-col, 6-col
- Check responsive behavior hints

**Step 3: Measure Gutters**
- Find consistent horizontal gaps between elements
- Common values: 16px, 20px, 24px, 32px

**Grid Calculation:**
```
Column Width = (Container Width - (Gaps * (Columns - 1))) / Columns
Gutter Width = Gap between adjacent columns
```

### Flexbox vs Grid Indicators

**Flexbox Indicators:**
- Items of varying widths in same row
- Items wrapping to next line
- Single-axis alignment dominance
- Unequal distribution of remaining space

**Grid Indicators:**
- Strict column alignment across rows
- Items spanning multiple columns
- Both row and column tracks visible
- Consistent cell sizing

---

## Component Detection Patterns

### Component Detection Decision Tree

```
Is it interactive?
├── Yes → Does it trigger an action?
│   ├── Yes → Button/Link/Icon Button
│   └── No → Does it accept input?
│       ├── Yes → Input/Select/Checkbox/Radio
│       └── No → Toggle/Switch
└── No → Is it a container?
    ├── Yes → Card/Modal/Drawer/Section
    └── No → Is it text?
        ├── Yes → Heading/Paragraph/Label/Caption
        └── No → Is it visual?
            ├── Yes → Image/Icon/Avatar/Badge
            └── No → Divider/Spacer
```

### Bounding Box Detection Heuristics

**Visual Boundary Detection:**
- Look for clear edges (borders, shadows, background changes)
- Identify whitespace gaps that separate elements
- Group elements by visual proximity (Gestalt proximity principle)
- Consider alignment lines as grouping indicators

### Common Component Signatures

| Component Type | Visual Indicators |
|----------------|-------------------|
| Button | Rounded rectangle, consistent height, centered text, possible icon |
| Card | Shadow, border-radius, contained content group, consistent padding |
| Input | Bordered rectangle, placeholder text, label above/beside |
| Navigation | Horizontal or vertical list, evenly spaced items, highlight state |
| Avatar | Circular or rounded-square image, typically 24-64px |
| Badge | Small pill shape, high-contrast colors, near other elements |
| Modal | Centered overlay, shadow, close button, dimmed background |
| Dropdown | Text + chevron icon, bounded width |
| Table | Grid of cells, header row, alternating row colors |

### Button Detection

**Visual Characteristics:**
- Distinct background color (different from surroundings)
- Rounded corners (border-radius > 0)
- Centered text
- Horizontal padding visible
- Consistent height (32-48px typical)
- Often contains icon + text or text only

**Button Variants:**

| Variant | Background | Border | Text |
|---------|------------|--------|------|
| Primary | Solid brand color | None | White/inverse |
| Secondary | Transparent/light | 1-2px solid | Brand color |
| Tertiary | Transparent | None | Brand color |
| Ghost | Transparent | None | Muted color |
| Destructive | Red/danger color | None | White |

### Input Field Detection

**Visual Characteristics:**
- Rectangular shape
- Border visible (light gray typical)
- Background (white or very light)
- Placeholder text (muted color)
- Height: 36-44px typical
- Often has label above

**Input Variants:**
- Text input: Single line, cursor position
- Textarea: Multi-line, taller
- Select: Dropdown arrow icon on right
- Checkbox: Square, small (16-20px)
- Radio: Circle, small (16-20px)
- Toggle/Switch: Pill shape, binary state indicator

### Card Detection

**Visual Characteristics:**
- Distinct container boundary
- Background different from page
- Shadow or border creating separation
- Contains multiple child elements
- Consistent padding around content
- Often in repeating grid patterns

**Card Anatomy:**
1. Image area (top, optional)
2. Header/title
3. Body content
4. Footer/actions (optional)

### Container Recognition Patterns

**Flex Container Detection:**
- Children aligned in single direction (row or column)
- Consistent gap between children
- Children may have different sizes
- Look for: justify-content and align-items behavior

**Grid Container Detection:**
- Elements aligned in both rows and columns
- Consistent column widths or repeated patterns
- Gaps between grid cells
- Often used for: card grids, image galleries, data tables

---

## Color Extraction Patterns

### Systematic Color Sampling

#### Background Colors (Priority Order)
1. Page background (outermost)
2. Section backgrounds (cards, modals)
3. Component backgrounds (buttons, inputs)
4. Hover/active state backgrounds

#### Foreground Colors (Priority Order)
1. Primary text (headings, body)
2. Secondary text (captions, metadata)
3. Muted/disabled text
4. Link colors (default, hover, visited)
5. Error/success/warning text

#### Border and Divider Colors
- Card borders
- Input field borders (default, focus, error)
- Divider lines
- Table borders

### Color Categorization System

**Primary Palette:**
- Primary: Main brand color, CTAs
- Secondary: Supporting brand color
- Accent: Highlight, emphasis

**Neutral Palette:**
- Background colors (lightest to darkest)
- Text colors (body, muted, heading)
- Border colors
- Divider colors

**Semantic Colors:**
- Success: Typically green spectrum (hue 100-140)
- Warning: Typically yellow/orange spectrum (hue 30-50)
- Error/Danger: Typically red spectrum (hue 0-10, 350-360)
- Info: Typically blue spectrum (hue 200-220)

### Color Semantic Mapping Table

| Visual Context | Semantic Token Name | Usage Description |
|----------------|---------------------|-------------------|
| Page background | `color.background.default` | Main page backdrop |
| Card surface | `color.background.elevated` | Raised containers |
| Primary button | `color.interactive.primary` | Main CTAs |
| Button hover | `color.interactive.primary-hover` | Primary button hover state |
| Body text | `color.foreground.default` | Standard text content |
| Muted text | `color.foreground.muted` | Secondary information |
| Error indicator | `color.feedback.error` | Error states and messages |
| Success indicator | `color.feedback.success` | Success confirmations |
| Warning indicator | `color.feedback.warning` | Warning notices |
| Input border | `color.border.input` | Form field boundaries |
| Focus ring | `color.border.focus` | Keyboard focus indicators |

### Color Extraction Algorithm

```
1. Sample colors from each detected component
2. Cluster similar colors (within delta-E threshold of ~3)
3. Identify dominant colors by frequency
4. Assign semantic meaning based on usage context:
   - Large area backgrounds -> background tokens
   - Text on backgrounds -> foreground tokens
   - Small interactive elements -> interactive tokens
   - Borders and lines -> border tokens
```

### Color Palette Extraction Steps

1. Extract all unique colors
2. Group similar colors (within deltaE 2.0)
3. Sort each group by lightness
4. Create scale (50, 100, 200, ... 900)
5. Identify semantic roles

---

## Typography Extraction Patterns

### Font Family Detection

**Visual Analysis:**
- Serif vs Sans-serif (look for feet/stems)
- Monospace (equal character width)
- Display/decorative fonts (headings only)

**Common Font Signatures:**

| Font | Visual Identifier |
|------|-------------------|
| Inter | Clean sans-serif, slight humanist curves |
| Roboto | Geometric with open counters |
| SF Pro | Apple system font, compact |
| Helvetica | Classic, uniform stroke width |
| Georgia | Serif with modern proportions |
| Source Code Pro | Monospace, distinct 0 and O |

**Common Font Stacks:**
- System: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto
- Sans-serif: Inter, Helvetica Neue, Arial
- Serif: Georgia, "Times New Roman", serif
- Mono: "SF Mono", Monaco, Consolas, monospace

### Type Scale Detection

**Common Scale Ratios:**

| Ratio | Name | Example Scale |
|-------|------|---------------|
| 1.067 | Minor Second | 16, 17, 18, 19, 21 |
| 1.125 | Major Second | 16, 18, 20, 23, 26 |
| 1.200 | Minor Third | 16, 19, 23, 28, 33 |
| 1.250 | Major Third | 16, 20, 25, 31, 39 |
| 1.333 | Perfect Fourth | 16, 21, 28, 38, 50 |
| 1.414 | Augmented Fourth | 16, 23, 32, 45, 64 |
| 1.500 | Perfect Fifth | 16, 24, 36, 54, 81 |

**Detection Algorithm:**
1. Collect all font sizes
2. Sort ascending
3. Calculate ratios between consecutive sizes
4. Find most common ratio
5. Match to standard scale

### Text Style Hierarchy

**Typical Hierarchy:**

| Level | Usage | Size Range | Weight |
|-------|-------|------------|--------|
| Display | Hero headlines | 48-72px | Bold/Black |
| H1 | Page titles | 32-48px | Bold |
| H2 | Section headers | 24-32px | Semibold |
| H3 | Subsection headers | 20-24px | Semibold |
| H4 | Card titles | 18-20px | Medium |
| Body Large | Lead paragraphs | 18-20px | Regular |
| Body | Standard text | 14-16px | Regular |
| Body Small | Captions | 12-14px | Regular |
| Caption | Metadata | 10-12px | Regular |
| Label | Form labels | 12-14px | Medium |
| Button | Button text | 14-16px | Medium/Semibold |

### Line Height Patterns

| Use Case | Line Height |
|----------|-------------|
| Headings | 1.1 - 1.3 |
| Body text | 1.4 - 1.6 |
| UI elements | 1.0 - 1.2 |
| Long-form reading | 1.6 - 1.8 |

### Font Weight Detection

- Thin/Light: 100-300 (barely visible stroke)
- Normal/Regular: 400 (standard body text)
- Medium: 500 (slightly emphasized)
- Semibold: 600 (subheadings)
- Bold: 700 (headings, emphasis)
- Black: 800-900 (display text)

---

## Spacing and Dimensions Patterns

### Base Unit Detection Algorithm

1. Measure all gaps between elements
2. Find Greatest Common Divisor (GCD)
3. Validate GCD is reasonable (4px or 8px typical)
4. Build scale from base unit

**Common Base Units:**
- 4px system: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64
- 8px system: 8, 16, 24, 32, 40, 48, 64, 80, 96

### Spacing Scale Reference

**4px Base Scale (Tailwind-style):**
```
0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96
```

**8px Base Scale:**
```
0, 8, 16, 24, 32, 48, 64, 96, 128
```

### Padding vs Margin Detection

**Padding (Internal Spacing):**
- Distance from container edge to content
- Consistent within component types
- Often symmetric (same top/bottom, left/right)

**Margin (External Spacing):**
- Distance between components
- May vary by context
- Often uses larger values than padding

### Component Spacing Patterns

| Component | Padding X | Padding Y | Gap |
|-----------|-----------|-----------|-----|
| Button SM | 12px | 6px | 8px |
| Button MD | 16px | 8px | 8px |
| Button LG | 24px | 12px | 12px |
| Card | 24px | 24px | 16px |
| Input | 12px | 8px | - |
| Modal | 32px | 24px | 24px |

### Spacing Relationship Map

```
Component Internal Padding: spacing-sm to spacing-md (8-16px)
Component Gap (siblings): spacing-md to spacing-lg (16-24px)
Section Gap: spacing-xl to spacing-2xl (32-64px)
Page Margins: spacing-lg to spacing-xl (24-48px)
```

### Dimension Tokens

**Container Widths:**
- Full width: 100% of viewport
- Constrained: Common max-widths (1024px, 1200px, 1440px)
- Content width: Typical 600-800px for readability

**Component Sizing:**

| Component | SM | MD | LG |
|-----------|----|----|-----|
| Button Height | 32px | 40px | 48px |
| Input Height | 32px | 40px | 48px |
| Icon Size | 16px | 20px | 24px |
| Avatar | 32px | 40px | 48px |

---

## State Inference Rules

### Interactive States

| State | Visual Indicators |
|-------|-------------------|
| Default | Base appearance |
| Hover | Slight color change, cursor pointer |
| Active/Pressed | Darker shade, slight scale reduction |
| Focus | Visible ring/outline, increased contrast |
| Disabled | Muted colors, reduced opacity |
| Loading | Spinner, skeleton, pulsing |
| Error | Red borders/text, error icon |
| Success | Green indicators, checkmark |

### Button States Inference

**From Static Screenshot:**
- Default: Base styling visible
- Hover: Infer +10% darker background, elevated shadow
- Active: Infer +20% darker, no shadow, slight scale down
- Focus: Infer focus ring (2px outline, offset 2px)
- Disabled: Infer reduced opacity (0.5-0.6), muted colors

**When Multiple States Visible:**
- Different buttons may show different states
- Look for visual variations in similar components
- Catalog each variation as a state

### Input States Inference

- Default: Standard border color
- Hover: Slightly darker border
- Focus: Primary color border, focus ring
- Filled: Content present, potentially different label position
- Error: Red/danger border, error message below
- Disabled: Gray background, muted text

### Interactive Feedback Patterns

| State | Background | Border | Shadow | Transform |
|-------|------------|--------|--------|-----------|
| Default | Base | Base | Level 1 | none |
| Hover | Darken 5% | Darken 10% | Level 2 | none |
| Active | Darken 10% | Darken 15% | none | scale(0.98) |
| Focus | Base | Primary | Base | none |
| Disabled | Gray 200 | Gray 300 | none | none |

---

## Accessibility Analysis Patterns

### Contrast Ratio Requirements

**WCAG 2.1 Requirements:**

| Level | Normal Text | Large Text | UI Components |
|-------|-------------|------------|---------------|
| AA | 4.5:1 | 3:1 | 3:1 |
| AAA | 7:1 | 4.5:1 | 4.5:1 |

Large text defined as: >= 18pt (24px) or >= 14pt bold (19px)

**Contrast Calculation Formula:**
```
L = 0.2126 * R + 0.7152 * G + 0.0722 * B (relative luminance)
Contrast Ratio = (L1 + 0.05) / (L2 + 0.05)
where L1 > L2
```

### Touch Target Analysis

**Minimum Size Requirements:**

| Standard | Size |
|----------|------|
| WCAG 2.5.5 (AAA) | 44x44 CSS pixels |
| WCAG 2.5.8 (AA) | 24x24 CSS pixels with spacing |
| iOS HIG | 44x44 points |
| Material Design | 48x48dp (with 8dp spacing minimum) |

**Detection Approach:**
1. Identify interactive elements (buttons, links, inputs)
2. Measure bounding box dimensions
3. Check spacing between adjacent touch targets
4. Flag elements below minimum thresholds

### Semantic Structure Analysis

**Expected Semantic Roles:**

| Element | Role | Usage |
|---------|------|-------|
| Navigation | nav, role="navigation" | Main navigation |
| Main Content | main, role="main" | Primary content |
| Header | header, role="banner" | Page header |
| Footer | footer, role="contentinfo" | Page footer |
| Sidebar | aside, role="complementary" | Secondary content |
| Search | role="search" | Search functionality |
| Form | form, role="form" | Form container |
| Button | button, role="button" | Interactive action |
| Link | a, role="link" | Navigation link |

### Color Blindness Considerations

**Types and Prevalence:**
- Protanopia (red-blind): 1% of males
- Deuteranopia (green-blind): 1% of males
- Tritanopia (blue-blind): <0.01%

**Critical Rule:** Color must not be the only visual means of conveying information (WCAG 1.4.1)

**Check For:**
- Information conveyed only by color
- Error states without icon/text
- Status without additional indicators
- Charts/graphs without patterns

---

## Component Classification Taxonomy

### Atomic Components (Atoms)

**Text Elements:**
- `heading`: h1-h6 equivalent
- `paragraph`: Body text blocks
- `caption`: Small descriptive text
- `label`: Form labels, UI labels
- `badge`: Small status indicators
- `tag`: Categorization chips

**Interactive Elements:**
- `button`: Primary action trigger
- `icon-button`: Icon-only button
- `link`: Navigation link
- `checkbox`: Binary selection
- `radio`: Single selection from group
- `switch`: Toggle control
- `input`: Text input field
- `textarea`: Multi-line input
- `select`: Dropdown selection
- `slider`: Range selection

**Media Elements:**
- `image`: Static images
- `avatar`: User/entity images
- `icon`: Symbolic graphics
- `logo`: Brand marks
- `video`: Video players

**Feedback Elements:**
- `spinner`: Loading indicator
- `progress`: Progress bar
- `skeleton`: Loading placeholder
- `alert`: Inline feedback
- `toast`: Temporary notification

### Molecular Components (Molecules)

- `form-field`: Label + input + helper
- `search-bar`: Input + icon + button
- `nav-item`: Icon + text + indicator
- `breadcrumb`: Path navigation
- `menu-item`: Icon + text + shortcut
- `list-item`: Content + actions

### Organism Components (Organisms)

**Layout Components:**
- `header`: Page header
- `navigation`: Nav container
- `sidebar`: Side navigation
- `footer`: Page footer
- `card`: Bounded content group
- `modal`: Dialog overlay
- `drawer`: Slide-in panel

**Content Components:**
- `hero`: Hero section
- `feature-section`: Feature list
- `testimonial`: User testimonial
- `pricing-table`: Pricing comparison
- `data-table`: Tabular data
- `form`: Form container

### Component Naming Conventions

**Hierarchical Naming:**
```
{category}-{type}-{variant}

Examples:
- button-primary
- button-secondary
- button-ghost
- input-text
- input-password
- card-product
- card-user
- nav-horizontal
- nav-vertical
```

**State-Aware Naming:**
```
{component}-{state}

Examples:
- button-hover
- button-active
- button-disabled
- input-focus
- input-error
- card-selected
```

---

## Confidence Scoring

### Per-Category Confidence Levels

**High Confidence (0.8-1.0):**
- Clear, high-resolution input
- Standard design patterns
- Consistent styling throughout
- Multiple examples of each element type

**Medium Confidence (0.5-0.79):**
- Some ambiguity in element boundaries
- Mix of standard and custom patterns
- Minor inconsistencies
- Limited examples of some elements

**Low Confidence (0.0-0.49):**
- Low resolution or artifacts
- Highly custom/unusual design
- Significant inconsistencies
- Minimal examples to pattern match

### Confidence Factors (Weighted)

| Factor | Weight | Description |
|--------|--------|-------------|
| Resolution | 0.20 | Image quality and clarity |
| Consistency | 0.25 | Design system coherence |
| Coverage | 0.20 | % of elements successfully identified |
| Pattern Match | 0.20 | Alignment with known patterns |
| Completeness | 0.15 | All token categories populated |

### Confidence Reporting Format

```json
{
  "$extensions": {
    "com.design-spec.confidence": {
      "overall": 0.85,
      "byCategory": {
        "layout": 0.9,
        "components": 0.8,
        "colors": 0.95,
        "typography": 0.75,
        "spacing": 0.85,
        "states": 0.7
      },
      "notes": [
        "Typography font family inferred from visual characteristics",
        "Button hover states not visible, using standard inference"
      ]
    }
  }
}
```

---

## Output Format Conversions

### CSS Custom Properties

```css
:root {
  /* Colors */
  --color-primary: #3B82F6;
  --color-secondary: #6366F1;
  --color-text-primary: #1F2937;
  
  /* Typography */
  --font-family-primary: 'Inter', system-ui, sans-serif;
  --font-size-base: 16px;
  --font-weight-medium: 500;
  --line-height-normal: 1.5;
  
  /* Spacing */
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-4: 16px;
  
  /* Border Radius */
  --radius-md: 8px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
}
```

### SCSS Variables

```scss
// Colors
$color-primary: #3B82F6;
$color-secondary: #6366F1;

// Typography
$font-family-primary: 'Inter', system-ui, sans-serif;
$font-sizes: (
  'xs': 12px,
  'sm': 14px,
  'base': 16px,
  'lg': 18px
);

// Spacing
$spacing-scale: (
  1: 4px,
  2: 8px,
  3: 12px,
  4: 16px
);
```

### Tailwind Config

```javascript
module.exports = {
  theme: {
    colors: {
      primary: {
        DEFAULT: '#3B82F6',
        dark: '#2563EB',
        light: '#60A5FA'
      }
    },
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif']
    },
    fontSize: {
      'xs': '12px',
      'sm': '14px',
      'base': '16px'
    },
    spacing: {
      '1': '4px',
      '2': '8px',
      '4': '16px'
    },
    borderRadius: {
      'sm': '4px',
      'md': '8px',
      'lg': '12px'
    }
  }
}
```

### Style Dictionary Format

```json
{
  "color": {
    "primary": { "value": "#3B82F6" },
    "secondary": { "value": "#6366F1" }
  },
  "font": {
    "family": {
      "primary": { "value": "Inter, system-ui, sans-serif" }
    },
    "size": {
      "base": { "value": "16px" }
    }
  }
}
```

### Figma Variables JSON

```json
{
  "colors/primary": {
    "type": "COLOR",
    "value": "#3B82F6",
    "scopes": ["ALL_SCOPES"]
  },
  "spacing/md": {
    "type": "FLOAT",
    "value": 16,
    "scopes": ["GAP", "WIDTH_HEIGHT"]
  }
}
```

---

## Validation Checklist

### Token Extraction
- [ ] All colors captured with hex/RGB values
- [ ] Font families identified accurately
- [ ] Font sizes mapped to scale
- [ ] Spacing values follow consistent scale
- [ ] Border radii captured
- [ ] Shadow values captured (offset, blur, spread, color)

### Component Tree
- [ ] All visible components identified
- [ ] Correct parent-child relationships
- [ ] Appropriate atomic level assigned
- [ ] Bounding boxes accurate
- [ ] States and variants noted

### Accessibility
- [ ] Contrast ratios checked
- [ ] Heading hierarchy validated
- [ ] Interactive elements identified
- [ ] Focus indicators noted
- [ ] Semantic landmarks mapped

### Layout
- [ ] Grid system detected
- [ ] Major regions identified
- [ ] Spacing patterns recognized
- [ ] Responsive hints captured

---

## Best Practices Summary

### For Accurate Extraction

1. **Start with layout** - Understand the structure before details
2. **Use reference points** - Identify repeating patterns as calibration
3. **Cross-validate** - Compare findings across passes
4. **Document uncertainty** - Mark low-confidence areas
5. **Preserve relationships** - Maintain token references, don't flatten

### For AI-Readable Output

1. **Semantic naming** - Use intent-based names (color.interactive.primary)
2. **Rich descriptions** - Add $description explaining when/how to use
3. **Explicit relationships** - Document token pairings and dependencies
4. **Component mapping** - Show which tokens apply to which components
5. **Usage examples** - Include context for complex tokens

### For Developer Handoff

1. **Complete tokens** - Include all variations needed for implementation
2. **Clear hierarchy** - Organize logically (primitive -> semantic -> component)
3. **State coverage** - Document all interactive states
4. **Responsive values** - Note breakpoint variations if detected
5. **Accessibility notes** - Include WCAG compliance information
