# Swiss Pulse Design Tokens

Canonical design system shared by mode `infographic` and mode `publish`. Every Swiss Pulse visual must draw from these tokens exactly — no color, weight, or size outside this file is permitted.

## Color Palette

### Light mode

| Role | Value |
|---|---|
| Background | `#ffffff` |
| Surface | `#f5f5f0` |
| Text primary | `#1a1a1a` |
| Text secondary | `#6b6b65` |
| Text tertiary | `#9c9c94` |
| Accent | `#0066FF` |
| Accent background | `#e8f0fe` |
| Borders | `rgba(0,0,0,0.1)` |

### Dark mode

| Role | Value |
|---|---|
| Background | `#1a1a1a` |
| Surface | `#252523` |
| Text primary | `#e8e8e0` |
| Text secondary | `#a0a098` |
| Text tertiary | `#73726c` |
| Accent | `#4d94ff` |
| Accent background | `#1a2a44` |
| Borders | `rgba(255,255,255,0.1)` |

Exactly three color families are permitted: black/neutral, white/off-white, and electric blue (#0066FF light / #4d94ff dark). Any other hue is forbidden.

## Typography

- **Font stack:** `-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif`
- **Hero number:** 42–48px, weight 600
- **Section labels:** 11px, uppercase, letter-spacing 0.08em, weight 600
- **Card titles:** 13–15px, weight 600
- **Body / descriptions:** 11–13px, weight 400
- **Allowed weights:** 400 (regular) and 600 (bold) only. Never 700 or heavier.

For the Gemini infographic prompt, map the font stack to "Helvetica or Swiss grotesque style only — clean, bold headings, light body text."

## Layout

- **Max width:** 720px, centered
- **Page padding:** 32px 24px
- **Grid:** CSS Grid with 10–12px gaps
- **Section whitespace:** 2–2.5rem between major sections
- **Border-radius:** 8px for elements, 12px for cards
- **Border width:** 0.5px (subtle separation)
- **Dark mode:** always support via `@media (prefers-color-scheme: dark)`
- **Mobile breakpoint:** `@media (max-width: 500px)` — stack grids into single columns

## Forbidden

- Any color outside the palette above (including red, green, yellow, purple, or custom brand hues)
- Gradients
- Box shadows / drop shadows
- Decorative borders, flourishes, icons-as-decoration
- Font weights above 600
- Font sizes outside the scale above
- Decorative illustrations that do not encode data
