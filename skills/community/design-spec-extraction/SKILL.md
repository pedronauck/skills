---
name: design-spec-extraction
description: Extract comprehensive, production-ready JSON design specifications from visual inputs using a 7-pass serial architecture with cross-validation. Use when converting screenshots, mockups, or design exports into structured design tokens, component specs, accessibility analysis, and developer handoff artifacts.
---

# Design Specification Extraction

Extract comprehensive, production-ready JSON design specifications from visual inputs using a 7-pass serial subtask architecture that ensures complete coverage and cross-validation.

## When to Use This Skill

- Extracting design tokens from Figma exports or screenshots
- Converting visual mockups into structured component specifications
- Creating developer handoff documentation from designs
- Generating design system documentation from existing UIs
- Preparing design data for code generation tools
- Analyzing website screenshots for design reverse-engineering

## Output Format

The extraction produces JSON following the W3C Design Tokens Community Group (DTCG) 2025.10 format with extensions:

- **$version**: Schema version
- **$source**: Metadata (type, dimensions, extraction timestamp)
- **tokens**: Design tokens (colors, typography, spacing, sizing, shadows, radii)
- **components**: Hierarchical component tree with bounding boxes
- **accessibility**: WCAG analysis, contrast issues, semantic structure
- **$extensions**: Layout, component catalog, confidence scores

## CRITICAL: File-Based Architecture

**EVERY pass MUST write its output to a JSON file on disk.** This is non-negotiable.

### Directory Structure

Before starting extraction, create the output directory:

```bash
mkdir -p .tmp-design-specs/{project-name}
```

### Required File Outputs

| Pass | Output File | Description |
|------|-------------|-------------|
| 1 | `.tmp-design-specs/{project}/pass-1-layout.json` | Layout and structure |
| 2 | `.tmp-design-specs/{project}/pass-2-colors.json` | Color tokens |
| 3 | `.tmp-design-specs/{project}/pass-3-typography.json` | Typography tokens |
| 4 | `.tmp-design-specs/{project}/pass-4-components.json` | Component tree |
| 5 | `.tmp-design-specs/{project}/pass-5-spacing.json` | Spacing and dimensions |
| 6 | `.tmp-design-specs/{project}/pass-6-states.json` | States and accessibility |
| 7 | `.tmp-design-specs/{project}/design-spec.json` | **Final consolidated output** |

### Why File-Based?

1. **Persistence**: Each pass result is saved, enabling resumption if interrupted
2. **Debugging**: Intermediate files allow inspection of each extraction phase
3. **Validation**: Each JSON file can be validated independently
4. **Context Passing**: Subtask agents read previous pass files directly
5. **Audit Trail**: Complete record of extraction process

## Multipass Architecture

The extraction uses 7 serial passes. Each pass MUST:
1. Read previous pass JSON files from disk
2. Perform its analysis
3. **WRITE its output to the designated JSON file**
4. Complete before the next pass begins

```
Screenshot Input
      |
      v
[Pass 1] Source Analysis & Layout  -----> pass-1-layout.json
      |
      v
[Pass 2] Color & Visual Style      -----> pass-2-colors.json
      |
      v
[Pass 3] Typography Analysis       -----> pass-3-typography.json
      |
      v
[Pass 4] Component Detection       -----> pass-4-components.json
      |
      v
[Pass 5] Spacing & Dimensions      -----> pass-5-spacing.json
      |
      v
[Pass 6] States & Accessibility    -----> pass-6-states.json
      |
      v
[Pass 7] Consolidation             -----> design-spec.json (FINAL)
```

---

## Pass 1: Source Analysis & Layout Structure

**Objective**: Establish foundational understanding of the design source and spatial organization.

### Subtask Agent Prompt

```
You are Pass 1 of a 7-pass design specification extraction system. Your focus: LAYOUT AND STRUCTURE ONLY.

## CRITICAL REQUIREMENT
You MUST write your output to a JSON file. This is mandatory - do not just return JSON in your response.

OUTPUT FILE: `.tmp-design-specs/{project}/pass-1-layout.json`

Use the Write tool to save your analysis as valid JSON to this file.

## Input
- Screenshot: [attached image]

## Your Task

Analyze the screenshot and extract:

### 1. Source Metadata
- Identify source type: Figma export, Sketch export, website screenshot, mockup, or wireframe
- Detect dimensions and estimate device class (mobile/tablet/desktop)
- Note any visible design tool artifacts (rulers, grids, selection boxes)

### 2. Layout Type Detection
Determine the primary layout strategy:
- Single-column centered layout
- Multi-column grid (count columns, estimate gutters)
- Sidebar + main content
- Dashboard/admin layout
- Full-bleed/edge-to-edge

### 3. Region Identification
Map the major layout regions with bounding boxes:
- Header (position, height, sticky?)
- Navigation (type: sidebar, topnav, or none)
- Main content area
- Footer
- Any overlays, modals, or floating elements

### 4. Grid System Analysis
- Identify underlying grid (12-column, 4-column, etc.)
- Measure or estimate gutter width
- Note container max-width if visible

## Output Format
Return JSON:
{
  "$schema": "pass-1-layout",
  "$source": {
    "type": "figma-export|website-screenshot|mockup|...",
    "dimensions": { "width": N, "height": N, "aspectRatio": "W:H", "deviceClass": "..." },
    "confidence": 0.0-1.0
  },
  "layout": {
    "type": "single-column|multi-column|sidebar|...",
    "regions": [
      { "name": "header", "bounds": {"x":0,"y":0,"width":W,"height":H}, "sticky": true|false },
      { "name": "navigation", "type": "sidebar|topnav|none", "bounds": {...} },
      { "name": "main", "bounds": {...} },
      { "name": "footer", "bounds": {...}, "present": true|false }
    ],
    "gridSystem": {
      "columns": N,
      "gutter": "Npx",
      "margin": "Npx",
      "maxWidth": "Npx"
    }
  },
  "containers": [
    {
      "id": "container-N",
      "bounds": { "x": N, "y": N, "width": N, "height": N },
      "layout": "grid|flex|block",
      "parent": "parent-id|null",
      "childCount": N
    }
  ],
  "sections": [
    {
      "id": "section-N",
      "purpose": "hero|features|testimonials|cta|...",
      "bounds": {...}
    }
  ]
}

Use pixel values. Be precise with bounds. Note confidence level for uncertain areas.

## FINAL STEP - MANDATORY
Use the Write tool to save this JSON to: `.tmp-design-specs/{project}/pass-1-layout.json`
Do NOT proceed without writing the file. Confirm the file was written successfully.
```

---

## Pass 2: Color & Visual Style Extraction

**Objective**: Extract complete color palette with semantic mappings.

### Subtask Agent Prompt

```
You are Pass 2 of a 7-pass design specification extraction system. Your focus: COLOR EXTRACTION.

## CRITICAL REQUIREMENT
You MUST write your output to a JSON file. This is mandatory - do not just return JSON in your response.

OUTPUT FILE: `.tmp-design-specs/{project}/pass-2-colors.json`

First, read the Pass 1 output: `.tmp-design-specs/{project}/pass-1-layout.json`
Then use the Write tool to save your analysis as valid JSON.

## Input
- Screenshot: [attached image]
- Layout data from Pass 1: Read from `.tmp-design-specs/{project}/pass-1-layout.json`

## Your Task

Extract ALL colors visible in this design:

### 1. Background Colors (by region)
- Page background
- Section/card backgrounds
- Header/footer backgrounds
- Modal/overlay backgrounds
- Input field backgrounds
- Button backgrounds (all variants)

### 2. Foreground Colors (text and icons)
- Primary heading text
- Body text
- Secondary/muted text
- Link text (if distinguishable)
- Icon colors
- Placeholder text

### 3. Border Colors
- Card/container borders
- Input field borders (default, focus, error states if visible)
- Divider/separator colors

### 4. Feedback Colors
- Error/danger indicators
- Success indicators
- Warning indicators
- Info indicators

### 5. Interactive Colors
- Primary action color (main CTA buttons)
- Secondary action color
- Hover states (if visible)
- Focus indicators

### Color Value Extraction
For each color, provide:
- Hex value (best estimate: #RRGGBB)
- Where it appears (semantic context)
- Suggested token name following pattern: color.[category].[variant]

## Output Format
Return JSON:
{
  "$schema": "pass-2-colors",
  "tokens": {
    "colors": {
      "primitive": {
        "blue": {
          "500": { "$value": "#3B82F6", "$type": "color", "$description": "Primary blue" },
          "600": { "$value": "#2563EB", "$type": "color", "$description": "Primary blue dark" }
        },
        "gray": {
          "50": { "$value": "#F9FAFB", "$type": "color" },
          "100": { "$value": "#F3F4F6", "$type": "color" },
          "500": { "$value": "#6B7280", "$type": "color" },
          "900": { "$value": "#111827", "$type": "color" }
        }
      },
      "semantic": {
        "background": {
          "default": { "$value": "{colors.primitive.gray.50}", "$type": "color", "$description": "Page background" },
          "elevated": { "$value": "#FFFFFF", "$type": "color", "$description": "Card surfaces" }
        },
        "foreground": {
          "default": { "$value": "{colors.primitive.gray.900}", "$type": "color", "$description": "Primary text" },
          "muted": { "$value": "{colors.primitive.gray.500}", "$type": "color", "$description": "Secondary text" }
        },
        "interactive": {
          "primary": { "$value": "{colors.primitive.blue.500}", "$type": "color", "$description": "Primary buttons, links" },
          "primary-hover": { "$value": "{colors.primitive.blue.600}", "$type": "color", "$description": "Primary hover" }
        },
        "border": {
          "default": { "$value": "{colors.primitive.gray.200}", "$type": "color", "$description": "Subtle borders" },
          "focus": { "$value": "{colors.primitive.blue.500}", "$type": "color", "$description": "Focus rings" }
        },
        "feedback": {
          "error": { "$value": "#EF4444", "$type": "color", "$description": "Error states" },
          "success": { "$value": "#22C55E", "$type": "color", "$description": "Success states" },
          "warning": { "$value": "#F59E0B", "$type": "color", "$description": "Warning states" },
          "info": { "$value": "#3B82F6", "$type": "color", "$description": "Info states" }
        }
      }
    }
  },
  "shadows": [
    {
      "name": "elevation-sm",
      "$type": "shadow",
      "$value": {
        "offsetX": "0px",
        "offsetY": "1px",
        "blur": "2px",
        "spread": "0px",
        "color": "rgba(0,0,0,0.05)"
      },
      "$description": "Subtle elevation"
    }
  ],
  "gradients": [],
  "componentColorMap": {
    "button-primary": {
      "background": "{colors.semantic.interactive.primary}",
      "text": "#FFFFFF",
      "border": "transparent"
    }
  }
}

Use DTCG $value and $type syntax. Include $description for AI readability.

## FINAL STEP - MANDATORY
Use the Write tool to save this JSON to: `.tmp-design-specs/{project}/pass-2-colors.json`
Do NOT proceed without writing the file. Confirm the file was written successfully.
```

---

## Pass 3: Typography Analysis

**Objective**: Extract complete typography system including fonts, sizes, weights, and text styles.

### Subtask Agent Prompt

```
You are Pass 3 of a 7-pass design specification extraction system. Your focus: TYPOGRAPHY.

## CRITICAL REQUIREMENT
You MUST write your output to a JSON file. This is mandatory - do not just return JSON in your response.

OUTPUT FILE: `.tmp-design-specs/{project}/pass-3-typography.json`

First, read previous pass outputs:
- `.tmp-design-specs/{project}/pass-1-layout.json`
- `.tmp-design-specs/{project}/pass-2-colors.json`

Then use the Write tool to save your analysis as valid JSON.

## Input
- Screenshot: [attached image]
- Layout data from Pass 1: Read from `.tmp-design-specs/{project}/pass-1-layout.json`
- Color data from Pass 2: Read from `.tmp-design-specs/{project}/pass-2-colors.json`

## Your Task

Extract ALL typography information:

### 1. Font Family Detection
Analyze visible text to identify:
- Primary font family (body text, UI elements)
- Secondary font family (headings, if different)
- Monospace font (code blocks, if present)
- Is it serif, sans-serif, or display?
- Best guess at specific font name

### 2. Text Style Inventory
For EACH distinct text style visible, extract:

**Headings:**
- Display/Hero text (largest)
- H1, H2, H3, etc.
- Card titles
- Section headers

**Body:**
- Body large (lead paragraphs)
- Body regular (standard text)
- Body small (captions)

**UI Text:**
- Button labels
- Form labels
- Input text
- Link text
- Navigation items
- Badge/tag text

For each style, estimate:
- Font size (in px)
- Font weight (100-900 or light/regular/medium/bold)
- Line height (ratio like 1.5 or pixels)
- Letter spacing (normal, tight, wide)
- Text color (reference token from Pass 2)
- Text transform (none, uppercase, capitalize)

### 3. Typographic Hierarchy
- How many distinct size levels are there?
- What is the size scale ratio?

## Output Format
Return JSON:
{
  "$schema": "pass-3-typography",
  "tokens": {
    "typography": {
      "fontFamilies": {
        "sans": { "$value": ["Inter", "system-ui", "sans-serif"], "$type": "fontFamily", "$description": "Primary font" },
        "mono": { "$value": ["JetBrains Mono", "monospace"], "$type": "fontFamily", "$description": "Code font" }
      },
      "fontWeights": {
        "regular": { "$value": 400, "$type": "fontWeight" },
        "medium": { "$value": 500, "$type": "fontWeight" },
        "semibold": { "$value": 600, "$type": "fontWeight" },
        "bold": { "$value": 700, "$type": "fontWeight" }
      },
      "fontSizes": {
        "xs": { "$value": "12px", "$type": "dimension" },
        "sm": { "$value": "14px", "$type": "dimension" },
        "base": { "$value": "16px", "$type": "dimension" },
        "lg": { "$value": "18px", "$type": "dimension" },
        "xl": { "$value": "20px", "$type": "dimension" },
        "2xl": { "$value": "24px", "$type": "dimension" },
        "3xl": { "$value": "30px", "$type": "dimension" },
        "4xl": { "$value": "36px", "$type": "dimension" },
        "5xl": { "$value": "48px", "$type": "dimension" }
      },
      "lineHeights": {
        "tight": { "$value": 1.25, "$type": "number" },
        "normal": { "$value": 1.5, "$type": "number" },
        "relaxed": { "$value": 1.75, "$type": "number" }
      },
      "letterSpacing": {
        "tighter": { "$value": "-0.05em", "$type": "dimension" },
        "normal": { "$value": "0em", "$type": "dimension" },
        "wide": { "$value": "0.05em", "$type": "dimension" }
      },
      "textStyles": {
        "display": {
          "$type": "typography",
          "$value": {
            "fontFamily": "{typography.fontFamilies.sans}",
            "fontSize": "{typography.fontSizes.5xl}",
            "fontWeight": "{typography.fontWeights.bold}",
            "lineHeight": "{typography.lineHeights.tight}",
            "letterSpacing": "{typography.letterSpacing.tighter}"
          },
          "$description": "Hero headlines"
        },
        "heading-1": {
          "$type": "typography",
          "$value": {
            "fontFamily": "{typography.fontFamilies.sans}",
            "fontSize": "{typography.fontSizes.4xl}",
            "fontWeight": "{typography.fontWeights.bold}",
            "lineHeight": "{typography.lineHeights.tight}"
          },
          "$description": "Page titles"
        },
        "heading-2": {
          "$type": "typography",
          "$value": {
            "fontFamily": "{typography.fontFamilies.sans}",
            "fontSize": "{typography.fontSizes.2xl}",
            "fontWeight": "{typography.fontWeights.semibold}",
            "lineHeight": "{typography.lineHeights.tight}"
          },
          "$description": "Section headings"
        },
        "body": {
          "$type": "typography",
          "$value": {
            "fontFamily": "{typography.fontFamilies.sans}",
            "fontSize": "{typography.fontSizes.base}",
            "fontWeight": "{typography.fontWeights.regular}",
            "lineHeight": "{typography.lineHeights.normal}"
          },
          "$description": "Standard body text"
        },
        "body-small": {
          "$type": "typography",
          "$value": {
            "fontFamily": "{typography.fontFamilies.sans}",
            "fontSize": "{typography.fontSizes.sm}",
            "fontWeight": "{typography.fontWeights.regular}",
            "lineHeight": "{typography.lineHeights.normal}"
          },
          "$description": "Secondary text, captions"
        },
        "button-label": {
          "$type": "typography",
          "$value": {
            "fontFamily": "{typography.fontFamilies.sans}",
            "fontSize": "{typography.fontSizes.sm}",
            "fontWeight": "{typography.fontWeights.medium}",
            "lineHeight": "{typography.lineHeights.tight}"
          },
          "$description": "Button text"
        }
      }
    }
  },
  "typeScale": {
    "ratio": 1.25,
    "base": "16px",
    "steps": [12, 14, 16, 20, 24, 30, 36, 48]
  }
}

Reference tokens using {token.path} syntax per DTCG specification.

## FINAL STEP - MANDATORY
Use the Write tool to save this JSON to: `.tmp-design-specs/{project}/pass-3-typography.json`
Do NOT proceed without writing the file. Confirm the file was written successfully.
```

---

## Pass 4: Component Detection & Classification

**Objective**: Build hierarchical component tree with atomic design classification.

### Subtask Agent Prompt

```
You are Pass 4 of a 7-pass design specification extraction system. Your focus: COMPONENT DETECTION.

## CRITICAL REQUIREMENT
You MUST write your output to a JSON file. This is mandatory - do not just return JSON in your response.

OUTPUT FILE: `.tmp-design-specs/{project}/pass-4-components.json`

First, read previous pass outputs:
- `.tmp-design-specs/{project}/pass-1-layout.json`
- `.tmp-design-specs/{project}/pass-2-colors.json`
- `.tmp-design-specs/{project}/pass-3-typography.json`

Then use the Write tool to save your analysis as valid JSON.

## Input
- Screenshot: [attached image]
- Layout data from Pass 1: Read from `.tmp-design-specs/{project}/pass-1-layout.json`
- Color data from Pass 2: Read from `.tmp-design-specs/{project}/pass-2-colors.json`
- Typography data from Pass 3: Read from `.tmp-design-specs/{project}/pass-3-typography.json`

## Your Task

Identify and classify ALL UI components:

### 1. Atomic Components (Atoms)
Simple, indivisible elements:
- Buttons (all variants: primary, secondary, icon, ghost)
- Icons (note semantic meaning)
- Inputs (text, password, search)
- Checkboxes, radios, toggles
- Labels and text elements
- Images and avatars
- Badges and tags
- Dividers

### 2. Molecular Components (Molecules)
Simple combinations of atoms:
- Form fields (label + input + helper)
- Search bars
- Navigation items
- Breadcrumbs
- Menu items
- List items

### 3. Organism Components (Organisms)
Complex, distinct UI sections:
- Navigation bars
- Headers
- Cards (all variants)
- Forms
- Tables
- Footers
- Hero sections

### 4. For Each Component, Extract:
- Unique ID (generated)
- Component type name
- Atomic level (atom/molecule/organism)
- Bounding box (x, y, width, height)
- Visual styles (link to tokens where possible)
- Content (text, icons)
- Current state (default, hover, active, disabled)
- Child components (for molecules/organisms)

### 5. Component Catalog
Create definitions for reusable component types:
- Suggested HTML element
- ARIA role
- Props/variants
- Token mappings

## Output Format
Return JSON:
{
  "$schema": "pass-4-components",
  "components": {
    "$root": {
      "id": "root",
      "type": "Page",
      "bounds": {"x":0,"y":0,"width":W,"height":H},
      "children": [
        {
          "id": "header-1",
          "type": "Header",
          "name": "Main Navigation Header",
          "atomicLevel": "organism",
          "bounds": {"x":0,"y":0,"width":W,"height":80},
          "styles": {
            "background": { "color": "#FFFFFF", "tokenRef": "{colors.semantic.background.elevated}" },
            "shadow": { "tokenRef": "{shadows.elevation-sm}" }
          },
          "children": [
            {
              "id": "logo-1",
              "type": "Image",
              "atomicLevel": "atom",
              "bounds": {"x":24,"y":24,"width":120,"height":32},
              "content": { "alt": "Company Logo" }
            },
            {
              "id": "nav-1",
              "type": "Navigation",
              "atomicLevel": "molecule",
              "bounds": {...},
              "children": [
                {
                  "id": "nav-item-1",
                  "type": "NavItem",
                  "atomicLevel": "atom",
                  "content": { "text": "Home" },
                  "states": { "current": "active" }
                }
              ]
            },
            {
              "id": "btn-signin",
              "type": "Button",
              "atomicLevel": "atom",
              "bounds": {...},
              "content": { "text": "Sign In" },
              "variants": { "variant": "secondary", "size": "md" },
              "states": { "current": "default" }
            }
          ]
        }
      ]
    },
    "catalog": {
      "Button": {
        "name": "Button",
        "category": "action",
        "atomicLevel": "atom",
        "htmlElement": "button",
        "ariaRole": "button",
        "variants": [
          { "name": "variant", "values": ["primary", "secondary", "ghost", "destructive"] },
          { "name": "size", "values": ["sm", "md", "lg"] }
        ],
        "tokens": {
          "background": "{colors.semantic.interactive.primary}",
          "color": "#FFFFFF",
          "borderRadius": "{radii.md}",
          "paddingX": "{spacing.4}",
          "paddingY": "{spacing.2}"
        },
        "instances": ["btn-signin", "btn-cta-1"]
      },
      "Card": {
        "name": "Card",
        "category": "layout",
        "atomicLevel": "organism",
        "htmlElement": "article",
        "ariaRole": "article",
        "variants": [
          { "name": "variant", "values": ["default", "elevated", "outlined"] }
        ],
        "tokens": {
          "background": "{colors.semantic.background.elevated}",
          "borderRadius": "{radii.lg}",
          "shadow": "{shadows.elevation-md}",
          "padding": "{spacing.6}"
        },
        "instances": ["card-1", "card-2"]
      }
    }
  },
  "statistics": {
    "totalComponents": N,
    "byType": {
      "Button": N,
      "Card": N,
      "Input": N
    },
    "byAtomicLevel": {
      "atom": N,
      "molecule": N,
      "organism": N
    }
  }
}

Be exhaustive. Every visible interactive or content element must be cataloged.

## FINAL STEP - MANDATORY
Use the Write tool to save this JSON to: `.tmp-design-specs/{project}/pass-4-components.json`
Do NOT proceed without writing the file. Confirm the file was written successfully.
```

---

## Pass 5: Spacing & Dimensions

**Objective**: Extract spacing scale, sizing tokens, borders, and radii.

### Subtask Agent Prompt

```
You are Pass 5 of a 7-pass design specification extraction system. Your focus: SPACING AND DIMENSIONS.

## CRITICAL REQUIREMENT
You MUST write your output to a JSON file. This is mandatory - do not just return JSON in your response.

OUTPUT FILE: `.tmp-design-specs/{project}/pass-5-spacing.json`

First, read previous pass outputs:
- `.tmp-design-specs/{project}/pass-1-layout.json`
- `.tmp-design-specs/{project}/pass-4-components.json`

Then use the Write tool to save your analysis as valid JSON.

## Input
- Screenshot: [attached image]
- Layout data from Pass 1: Read from `.tmp-design-specs/{project}/pass-1-layout.json`
- Component data from Pass 4: Read from `.tmp-design-specs/{project}/pass-4-components.json`

## Your Task

Measure and systematize ALL spacing and dimension values:

### 1. Spacing Scale
Analyze gaps between elements to find the base spacing unit:
- Measure space between text and container edges (padding)
- Measure space between stacked elements (stack spacing)
- Measure space between inline elements (inline spacing)
- Measure grid/flex gaps

Identify the spacing scale:
- What is the base unit? (4px, 8px typical)
- What multipliers are used? (1x, 2x, 3x, 4x, 6x, 8x, 12x, 16x)

### 2. Component Sizing
Extract size patterns:
- Button heights (small, medium, large)
- Input field heights
- Icon sizes
- Avatar sizes
- Container max-widths

### 3. Border Properties
For each border type:
- Border width (1px, 2px, etc.)
- Border radius values (small, medium, large, full/circular)

### 4. Map to Component Styles
Link spacing values to specific components from Pass 4

## Output Format
Return JSON:
{
  "$schema": "pass-5-spacing",
  "tokens": {
    "spacing": {
      "scale": {
        "0": { "$value": "0px", "$type": "dimension" },
        "1": { "$value": "4px", "$type": "dimension", "$description": "Minimal spacing, icon gaps" },
        "2": { "$value": "8px", "$type": "dimension", "$description": "Tight spacing, inline elements" },
        "3": { "$value": "12px", "$type": "dimension" },
        "4": { "$value": "16px", "$type": "dimension", "$description": "Default component padding" },
        "5": { "$value": "20px", "$type": "dimension" },
        "6": { "$value": "24px", "$type": "dimension", "$description": "Card padding, form gaps" },
        "8": { "$value": "32px", "$type": "dimension", "$description": "Section spacing" },
        "10": { "$value": "40px", "$type": "dimension" },
        "12": { "$value": "48px", "$type": "dimension", "$description": "Large section gaps" },
        "16": { "$value": "64px", "$type": "dimension", "$description": "Hero section padding" }
      },
      "semantic": {
        "inset": {
          "card": { "$value": "{spacing.scale.6}", "$type": "dimension", "$description": "Card internal padding" },
          "section": { "$value": "{spacing.scale.8}", "$type": "dimension", "$description": "Section padding" }
        },
        "stack": {
          "tight": { "$value": "{spacing.scale.2}", "$type": "dimension", "$description": "Compact vertical spacing" },
          "default": { "$value": "{spacing.scale.4}", "$type": "dimension", "$description": "Standard vertical spacing" }
        },
        "gap": {
          "grid": { "$value": "{spacing.scale.6}", "$type": "dimension", "$description": "Card grid gap" }
        }
      }
    },
    "sizing": {
      "component": {
        "button-sm": { "$value": "32px", "$type": "dimension" },
        "button-md": { "$value": "40px", "$type": "dimension" },
        "button-lg": { "$value": "48px", "$type": "dimension" },
        "input-md": { "$value": "40px", "$type": "dimension" }
      },
      "icon": {
        "sm": { "$value": "16px", "$type": "dimension" },
        "md": { "$value": "20px", "$type": "dimension" },
        "lg": { "$value": "24px", "$type": "dimension" }
      },
      "avatar": {
        "sm": { "$value": "32px", "$type": "dimension" },
        "md": { "$value": "40px", "$type": "dimension" },
        "lg": { "$value": "48px", "$type": "dimension" }
      }
    },
    "radii": {
      "none": { "$value": "0px", "$type": "dimension" },
      "sm": { "$value": "4px", "$type": "dimension" },
      "md": { "$value": "8px", "$type": "dimension", "$description": "Default for cards, buttons" },
      "lg": { "$value": "12px", "$type": "dimension" },
      "xl": { "$value": "16px", "$type": "dimension" },
      "full": { "$value": "9999px", "$type": "dimension", "$description": "Pills, avatars" }
    },
    "borders": {
      "width": {
        "thin": { "$value": "1px", "$type": "dimension", "$description": "Default borders" },
        "medium": { "$value": "2px", "$type": "dimension", "$description": "Focus rings, emphasis" }
      }
    },
    "container": {
      "maxWidth": {
        "sm": { "$value": "640px", "$type": "dimension" },
        "md": { "$value": "768px", "$type": "dimension" },
        "lg": { "$value": "1024px", "$type": "dimension" },
        "xl": { "$value": "1280px", "$type": "dimension" }
      }
    }
  },
  "componentSpacing": {
    "button": {
      "paddingX": "{spacing.scale.4}",
      "paddingY": "{spacing.scale.2}",
      "gap": "{spacing.scale.2}"
    },
    "card": {
      "padding": "{spacing.scale.6}",
      "gap": "{spacing.scale.4}"
    },
    "input": {
      "paddingX": "{spacing.scale.3}",
      "paddingY": "{spacing.scale.2}"
    }
  }
}

Detect patterns and express them. Use 4px or 8px base unit convention.

## FINAL STEP - MANDATORY
Use the Write tool to save this JSON to: `.tmp-design-specs/{project}/pass-5-spacing.json`
Do NOT proceed without writing the file. Confirm the file was written successfully.
```

---

## Pass 6: Interactive States & Accessibility

**Objective**: Analyze interactive states and accessibility compliance.

### Subtask Agent Prompt

```
You are Pass 6 of a 7-pass design specification extraction system. Your focus: STATES AND ACCESSIBILITY.

## CRITICAL REQUIREMENT
You MUST write your output to a JSON file. This is mandatory - do not just return JSON in your response.

OUTPUT FILE: `.tmp-design-specs/{project}/pass-6-states.json`

First, read previous pass outputs:
- `.tmp-design-specs/{project}/pass-2-colors.json`
- `.tmp-design-specs/{project}/pass-4-components.json`

Then use the Write tool to save your analysis as valid JSON.

## Input
- Screenshot: [attached image]
- Component data from Pass 4: Read from `.tmp-design-specs/{project}/pass-4-components.json`
- Color data from Pass 2: Read from `.tmp-design-specs/{project}/pass-2-colors.json`

## Your Task

### 1. Interactive States (infer from visual cues)
For each interactive component type, define state variations:
- Default/rest state
- Hover state (if visible or inferable - darken 5-10%)
- Active/pressed state (darken 10-15%, reduce shadow)
- Focus state (focus ring, 2px outline)
- Disabled state (opacity 0.5-0.6, muted colors)
- Loading state

State Changes:
- Color changes
- Shadow changes
- Border changes
- Opacity changes
- Transform effects

### 2. Accessibility Analysis

**Contrast Ratios:**
For each text-on-background combination:
- Calculate/estimate contrast ratio
- Check against WCAG AA (4.5:1 normal, 3:1 large)
- Check against WCAG AAA (7:1 normal, 4.5:1 large)
- Flag any failures

**Color Accessibility:**
- Red/green combinations (protanopia/deuteranopia)
- Blue/yellow combinations (tritanopia)
- Information conveyed by color alone

### 3. Semantic Hierarchy
- What should be the h1? (single per page)
- Heading hierarchy (h1 > h2 > h3, no skips)
- Landmark regions (header, nav, main, aside, footer)

### 4. Interactive Element Analysis
For each interactive element:
- Does it have visible text or clear label?
- What ARIA label might be needed?
- Is the clickable area sufficient (44x44px touch target)?
- Is there a visible focus indicator?

## Output Format
Return JSON:
{
  "$schema": "pass-6-states",
  "states": {
    "button": {
      "primary": {
        "default": {
          "background": "{colors.semantic.interactive.primary}",
          "text": "#FFFFFF",
          "border": "transparent",
          "shadow": "{shadows.elevation-sm}"
        },
        "hover": {
          "background": "{colors.semantic.interactive.primary-hover}",
          "shadow": "{shadows.elevation-md}",
          "$description": "Darken 10%, increase elevation"
        },
        "active": {
          "background": "{colors.primitive.blue.700}",
          "shadow": "none",
          "transform": "scale(0.98)"
        },
        "focus": {
          "outline": "2px solid {colors.semantic.interactive.primary}",
          "outlineOffset": "2px"
        },
        "disabled": {
          "background": "{colors.primitive.gray.300}",
          "text": "{colors.primitive.gray.500}",
          "cursor": "not-allowed",
          "opacity": 0.6
        }
      }
    },
    "input": {
      "default": {
        "border": "{colors.semantic.border.default}",
        "background": "#FFFFFF"
      },
      "hover": {
        "border": "{colors.primitive.gray.400}"
      },
      "focus": {
        "border": "{colors.semantic.border.focus}",
        "outline": "2px solid {colors.semantic.interactive.primary}",
        "outlineOffset": "-1px"
      },
      "error": {
        "border": "{colors.semantic.feedback.error}",
        "background": "#FEF2F2"
      },
      "disabled": {
        "background": "{colors.primitive.gray.100}",
        "opacity": 0.6
      }
    }
  },
  "transitions": {
    "fast": {
      "$type": "transition",
      "$value": {
        "duration": "150ms",
        "timingFunction": [0.4, 0, 0.2, 1]
      },
      "$description": "Micro-interactions, hovers"
    },
    "normal": {
      "$type": "transition",
      "$value": {
        "duration": "200ms",
        "timingFunction": [0.4, 0, 0.2, 1]
      },
      "$description": "Standard transitions"
    },
    "slow": {
      "$type": "transition",
      "$value": {
        "duration": "300ms",
        "timingFunction": [0.4, 0, 0.2, 1]
      },
      "$description": "Page transitions, modals"
    }
  },
  "accessibility": {
    "contrastIssues": [
      {
        "element": "components.btn-secondary",
        "foreground": "#9CA3AF",
        "background": "#FFFFFF",
        "ratio": 2.8,
        "required": 4.5,
        "wcagLevel": "AA",
        "passes": false,
        "recommendation": "Darken text to #6B7280 for 4.5:1 ratio"
      }
    ],
    "colorBlindnessIssues": [
      {
        "type": "deuteranopia",
        "affectedElements": ["error-state", "success-state"],
        "recommendation": "Add icons alongside color indicators"
      }
    ],
    "semanticHierarchy": {
      "headings": [
        { "level": 1, "text": "Welcome to Our Platform", "componentRef": "hero-title" },
        { "level": 2, "text": "Features", "componentRef": "features-heading" }
      ],
      "landmarks": [
        { "role": "banner", "componentRef": "header-1" },
        { "role": "navigation", "componentRef": "nav-1" },
        { "role": "main", "componentRef": "main-content" },
        { "role": "contentinfo", "componentRef": "footer-1" }
      ]
    },
    "touchTargets": {
      "minimumSize": "44px",
      "violations": [
        {
          "componentRef": "icon-btn-close",
          "actualSize": "32x32",
          "recommendation": "Increase to 44x44px minimum"
        }
      ]
    },
    "interactiveElements": [
      {
        "componentRef": "icon-btn-menu",
        "type": "IconButton",
        "hasVisibleLabel": false,
        "suggestedAriaLabel": "Open menu"
      }
    ]
  }
}

Infer states from visual context. When states are not visible, provide reasonable defaults.

## FINAL STEP - MANDATORY
Use the Write tool to save this JSON to: `.tmp-design-specs/{project}/pass-6-states.json`
Do NOT proceed without writing the file. Confirm the file was written successfully.
```

---

## Pass 7: Consolidation & Validation

**Objective**: Merge all passes into final spec, validate completeness, resolve conflicts.

### Subtask Agent Prompt

```
You are Pass 7 (FINAL) of a 7-pass design specification extraction system. Your focus: CONSOLIDATION.

## CRITICAL REQUIREMENT
You MUST write your final output to a JSON file. This is mandatory - do not just return JSON in your response.

OUTPUT FILE: `.tmp-design-specs/{project}/design-spec.json`

First, read ALL previous pass outputs:
- `.tmp-design-specs/{project}/pass-1-layout.json`
- `.tmp-design-specs/{project}/pass-2-colors.json`
- `.tmp-design-specs/{project}/pass-3-typography.json`
- `.tmp-design-specs/{project}/pass-4-components.json`
- `.tmp-design-specs/{project}/pass-5-spacing.json`
- `.tmp-design-specs/{project}/pass-6-states.json`

Then use the Write tool to save your consolidated analysis as valid JSON.

## Input
- All previous pass outputs (Passes 1-6) - Read from the JSON files listed above

## Your Task

Create the final, validated design specification:

### 1. Merge Token Groups
Combine all token extractions into unified structure:
- Resolve any duplicate tokens
- Ensure consistent naming
- Verify all references resolve correctly

### 2. Validate Component Tree
- Check all components have required fields
- Verify parent-child relationships
- Ensure style references link to valid tokens
- Check bounding boxes don't overlap incorrectly

### 3. Cross-Reference Validation
- Every color used in components should exist in tokens
- Every font used should be in typography tokens
- Every spacing value should map to spacing scale

### 4. Quality Scoring
Assign confidence scores:
- Overall extraction confidence
- Per-section confidence
- Flag areas of uncertainty

### 5. Generate Recommendations
Based on analysis:
- Accessibility fixes needed
- Token consolidation opportunities
- Component naming suggestions

## Final Output Format
Return complete JSON matching the schema at references/design-tokens-schema.json:

{
  "$schema": "https://design-tokens.org/schema.json",
  "$version": "1.0.0",
  "$source": {
    "type": "<figma-export|website-screenshot|mockup>",
    "dimensions": { "width": N, "height": N, "aspectRatio": "W:H", "deviceClass": "..." },
    "extractedAt": "<ISO timestamp>",
    "confidence": 0.0-1.0
  },
  
  "tokens": {
    "colors": {
      "primitive": {...},
      "semantic": {...}
    },
    "typography": {
      "fontFamilies": {...},
      "fontWeights": {...},
      "fontSizes": {...},
      "lineHeights": {...},
      "letterSpacing": {...},
      "textStyles": {...}
    },
    "spacing": {
      "scale": {...},
      "semantic": {...}
    },
    "sizing": {...},
    "radii": {...},
    "borders": {...},
    "shadows": {...},
    "transitions": {...}
  },
  
  "components": {
    "$root": {...},
    "catalog": {...}
  },
  
  "layout": {
    "type": "...",
    "regions": [...],
    "gridSystem": {...}
  },
  
  "accessibility": {
    "contrastIssues": [...],
    "colorBlindnessIssues": [...],
    "semanticHierarchy": {...},
    "touchTargets": {...}
  },
  
  "semantics": {
    "designPatterns": [
      { "pattern": "Hero Section", "confidence": 0.95, "instances": [...] },
      { "pattern": "Card Grid", "confidence": 0.9, "instances": [...] }
    ],
    "contentTypes": ["marketing", "e-commerce"],
    "brandPersonality": {
      "traits": ["modern", "professional"],
      "tone": "friendly"
    }
  },
  
  "$extensions": {
    "com.design-spec.extraction": {
      "passesCompleted": 7,
      "confidence": {
        "overall": 0.85,
        "layout": 0.9,
        "colors": 0.95,
        "typography": 0.8,
        "components": 0.85,
        "spacing": 0.9,
        "accessibility": 0.75
      },
      "recommendations": [
        "Increase contrast on secondary buttons",
        "Add aria-labels to icon-only buttons"
      ]
    }
  }
}

The final file MUST be valid JSON. Validate all references resolve correctly.

## FINAL STEP - MANDATORY
Use the Write tool to save this JSON to: `.tmp-design-specs/{project}/design-spec.json`
This is the FINAL deliverable. Do NOT proceed without writing the file. Confirm the file was written successfully.
```

---

## Execution Instructions

### IMPORTANT: File-Based Workflow

Before launching any pass:

1. **Create the output directory:**
```bash
mkdir -p .tmp-design-specs/{project-name}
```

2. **Each pass MUST write to its designated file** - Subtask agents will use the Write tool
3. **Verify file exists before proceeding to next pass** - Read the file to confirm

### Delegating Extraction Passes

Execute each pass as a delegated worker. **Replace `{project}` with actual project name in ALL prompts.**

```javascript
// Step 0: Create directory for intermediate files
mkdir -p .tmp-design-specs/my-design

// Steps 1-6: Delegate each pass sequentially
teams(action: 'delegate', tasks: [{
  text: '[Pass 1 prompt - worker MUST write to .tmp-design-specs/my-design/pass-1-layout.json]',
  assignee: 'design-pass-1'
}])
// VERIFY: Read .tmp-design-specs/my-design/pass-1-layout.json exists

// Continue for Passes 2-6, verifying each file exists ...

// Step 7: Final Consolidation
teams(action: 'delegate', tasks: [{
  text: '[Pass 7 prompt - worker reads ALL pass files, MUST write to design-spec.json]',
  assignee: 'design-consolidator'
}])
// VERIFY: Read .tmp-design-specs/my-design/design-spec.json exists

// Step 8: Save final spec as a ticket
todos_oneshot(
  title: "Design spec: my-design",
  description: "<contents of design-spec.json>",
  tags: "design-spec",
  type: "task"
)
```

### Verification After Each Pass

After each subtask completes, verify the output file was written:

```javascript
// After Pass N completes:
Read(".tmp-design-specs/{project}/pass-N-{type}.json")
// If file doesn't exist or is invalid JSON, re-run the pass
```

### Model Recommendations

- **Passes 1-6**: Use Sonnet for focused visual analysis tasks
- **Pass 7 (Consolidation)**: Use Opus for complex synthesis and validation

### Output Delivery

After extraction, provide:

1. **Summary**: Key statistics and findings
2. **Complete JSON**: Full spec matching schema
3. **Recommendations**: Suggested improvements
4. **Confidence Report**: Areas of uncertainty

### Example Summary Output

```markdown
## Design Spec Extraction Complete

### Statistics
- Colors extracted: 24 (8 primitive, 16 semantic)
- Typography styles: 12
- Components detected: 47 (18 atoms, 15 molecules, 14 organisms)
- Spacing values: 11
- Accessibility issues: 2 (contrast)

### Key Findings
- Layout: 12-column grid with 24px gutters
- Primary font: Inter (sans-serif)
- Design patterns: Hero, Card Grid, Feature List, CTA
- Device class: Desktop (1440px width)

### Accessibility Notes
- 2 contrast failures requiring attention
- Recommend adding icons to status indicators

### Confidence
- Overall: 0.89
- Colors: 0.95
- Typography: 0.88
- Components: 0.85
- Spacing: 0.90

[Full JSON spec attached]
```

---

## Best Practices

### For Accurate Extraction

1. Use highest resolution source available
2. Prefer Figma exports over screenshots when possible
3. Ensure design shows actual content (not lorem ipsum)
4. Include multiple states if analyzing interactions
5. Provide context about target platform

### For AI-Readable Output

1. Use semantic naming (intent over appearance)
2. Include $description explaining when/how to use tokens
3. Document token relationships and pairings
4. Show which tokens apply to which components
5. Include usage examples for complex tokens

### For Processing Efficiency

1. Start with layout pass to establish structure
2. Use component IDs consistently across passes
3. Pass only relevant previous results to each subtask
4. Validate incrementally, not just at end

---

## Reference Files

- `references/design-tokens-schema.json` - Complete JSON Schema for output validation
- `references/extraction-patterns.md` - Detailed patterns for visual analysis

Load these references as needed during extraction for detailed guidance on specific analysis tasks.

## Schema Compliance

Output follows W3C Design Tokens Community Group format (2025.10):
- All tokens use `$value`, `$type`, `$description` properties
- Token references use `{group.token}` syntax
- Extensions use reverse domain notation in `$extensions`
