# Mode: `publish` — HeyGenverse Swiss Pulse Visual Publisher

Turn the acquired content into an interactive, Swiss Pulse–styled visual explainer and publish it to HeyGenverse with a shareable link.

Prerequisite: the dispatcher (`SKILL.md` Step 3) has already acquired the content. This file covers content structuring, HTML assembly, Chart.js integration, and the HeyGenverse publish contract.

## Step 1: Load design tokens

Read `assets/swiss-pulse-tokens.md` to retrieve the canonical palette (light + dark mode), typography scale, layout grid, and border/radius values used throughout the HTML below.

## Step 2: Analyze and structure the content

Extract the following elements from the content. Not all will be present — use what is available:

1. **Hero metric** — the single most striking number or statistic (e.g., "2 → 500+", "$159M ARR", "73% non-activation")
2. **Supporting stats** — 3–4 secondary metrics that frame the story
3. **Timeline or sequence** — any chronological progression, phases, or steps
4. **Architecture or structure** — systems, frameworks, hierarchies, or relationships
5. **Key examples** — concrete instances that illustrate the main points
6. **Core insight or mental model** — the "so what" — the one-line takeaway
7. **Quotable moment** — a memorable quote from the source if available

Organize these into a visual hierarchy: the hero metric leads, the structure follows, details support.

## Step 3: Build the self-contained HTML

Assemble a single self-contained HTML page using the Swiss Pulse tokens from Step 1. Every visual must include the required components below.

### Required components (all mandatory)

1. **Hero section** — large metric + one-line context
2. **Stats row** — 3–4 metric cards in a grid
3. **At least ONE chart or graph** — pick the most appropriate:
   - **Bar chart** (Chart.js) — for comparisons, rankings, or distributions
   - **Line chart** (Chart.js) — for trends over time or growth curves
   - **Timeline** — for chronological progressions (interactive, clickable phases)
   - **Funnel** — for conversion or drop-off sequences
   - **Architecture diagram** — for systems, hierarchies, or relationships (use styled HTML divs, not SVG)
   - **Progress/gauge** — for completion or achievement metrics
4. **Content cards** — key examples, insights, or categories in a grid
5. **Source attribution** — footer with source link

### Chart implementation rules

Load Chart.js from CDN:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
```

Chart.js configuration:

- Canvas **cannot** resolve CSS variables — use hardcoded hex values from `assets/swiss-pulse-tokens.md`.
- Detect dark mode at runtime: `const isDark = matchMedia('(prefers-color-scheme: dark)').matches;`
- Use accent blue (`#0066FF` light / `#4d94ff` dark) as the primary data color.
- Use gray (`#9c9c94`) for secondary data or grid lines.
- Transparent background, subtle grid lines.
- Always wrap the canvas in a div with explicit height and `position: relative`.
- Set `responsive: true, maintainAspectRatio: false`.
- Build a custom HTML legend (not the Chart.js default).
- Disable the default legend: `plugins: { legend: { display: false } }`.

For timelines, use interactive HTML — not Chart.js:

- Horizontal row of phase items with a left-border accent on the active phase.
- Click to swap detail panel content.
- Active state uses accent-blue background + border.

### Interactive elements

Add interactivity where the content supports it:

- **Clickable timeline phases** that swap a detail panel
- **Hover states** on cards (background shift, border emphasis)
- **Responsive grid** that stacks on mobile (`@media max-width: 500px`)

### Template skeleton

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[TITLE]</title>
<style>
  /* CSS variables for light/dark mode from assets/swiss-pulse-tokens.md */
  :root { /* light-mode values */ }
  @media (prefers-color-scheme: dark) { :root { /* dark-mode values */ } }
  /* Component styles */
</style>
</head>
<body>
  <!-- Hero section -->
  <!-- Stats row -->
  <!-- Chart/graph section -->
  <!-- Content cards -->
  <!-- Quote (if available) -->
  <!-- Footer with source -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
  <script>
    /* Chart initialization */
    /* Interactive timeline logic */
  </script>
</body>
</html>
```

## Step 4: Publish to HeyGenverse

Call the `HeyGenverse:create_app` tool:

```
Tool: HeyGenverse:create_app
Parameters:
  title: [Descriptive title derived from the content]
  description: [1–2 sentence summary of what this visual explains]
  html: [The complete HTML from Step 3]
  tags: ["visual", "swiss-pulse", ...topic-specific tags]
```

## Step 5: Return the shareable link

Format the link as: `https://www.heygenverse.com/a/{app-id}`

Never use the `/api/apps/serve?id=` URL for sharing. Always use the `/a/` format.

Keep the response minimal:

- The HeyGenverse link
- One sentence on what the visual covers
- A note on any interactive elements to try

## Quality Checklist

Before publishing, verify:

- [ ] Hero metric is prominent and impactful
- [ ] At least one chart/graph is present (bar, line, timeline, funnel, or architecture)
- [ ] Dark mode works (all colors use CSS variables or have dark-mode overrides)
- [ ] Responsive — stacks cleanly on mobile
- [ ] Swiss Pulse aesthetic — B&W + #0066FF only, no decoration, grid-locked
- [ ] Source attribution in footer
- [ ] Interactive elements have hover/active states
- [ ] Title is descriptive, not generic

## Mode-Specific Rules

- Always publish to HeyGenverse. Never create a local file without publishing.
- Never use colors outside the B&W + #0066FF palette defined in `assets/swiss-pulse-tokens.md`.
- Never use gradients, shadows, or decorative elements.
- Never skip the chart/graph — every visual needs at least one.
- Never use the Visualizer or Excalidraw — those belong to other modes.
- Never forget dark-mode support.
