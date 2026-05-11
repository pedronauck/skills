# Mode: `visualize` — Inline Visualizer Widget

Turn the acquired content into the best-fit visual for understanding it, rendered inline in chat via the Visualizer.

Prerequisite: the dispatcher (`SKILL.md` Step 3) has already acquired the content. This file covers format selection, the Visualizer tool contract, and design rules.

## Step 1: Analyze and choose the visual format

The Visualizer supports SVG and HTML. Pick the format that fits the content:

| Content pattern | Visual format |
|---|---|
| Process, workflow, sequence, steps | **Flowchart** (SVG) — boxes and arrows showing flow |
| System, architecture, components | **Structural diagram** (SVG) — nested containers with labeled regions |
| Timeline, phases, chronological growth | **Interactive timeline** (HTML) — clickable phases with detail panel |
| Comparison, options, tradeoffs | **Card grid** (HTML) — side-by-side cards with key differences highlighted |
| Data, metrics, trends | **Chart + stats** (HTML with Chart.js) — metric cards + bar/line chart |
| Pipeline, funnel, conversion | **Kanban/pipeline** (HTML) — multi-column cards with status badges |
| Concept, mental model, framework | **Explainer** (HTML) — hero insight + supporting structure + interactive elements |
| Mixed / complex | **Dashboard-style** (HTML) — hero metric + stats row + chart + content cards |

When in doubt, default to the **dashboard-style** layout — it handles most content well.

## Step 2: Load the Visualizer module

Before creating any visual, always call:

```
visualize:read_me
```

Load the appropriate module(s): `diagram` for SVG flowcharts/structural, `interactive` for HTML explainers, `chart` for Chart.js data viz.

## Step 3: Build the visual

Create the visual using `visualize:show_widget` and follow every Visualizer design rule.

### Core principles

- **Seamless** — should feel like a natural extension of the chat
- **Flat** — no gradients, shadows, or decorative effects
- **Compact** — show the essential inline, explain the rest in text
- **Text in response, visuals in the tool** — all explanatory prose goes OUTSIDE the tool call

### Content extraction rules

- **Extract structure, not prose.** Distill to key metrics, relationships, sequences, and takeaways.
- **Hero metric first.** Lead with the single most striking number or insight.
- **3–4 supporting stats.** Frame the story with secondary metrics.
- **Include interactivity** where the content supports it — clickable elements, hover states, `sendPrompt()` for drill-downs.

### Design tokens

- Use CSS variables for all colors (auto dark mode)
- Font sizes: 11–16px range only
- Two weights: 400 regular, 500 bold
- Borders: `0.5px solid var(--color-border-tertiary)`
- Border-radius: `var(--border-radius-md)` for elements, `var(--border-radius-lg)` for cards
- Load Chart.js from CDN: `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js`

## Step 4: Respond

Output the visual inline via `show_widget`. Add brief commentary connecting the visual to the user's context. Keep it to 2–3 sentences max.

## Mode-Specific Rules

- Always call `visualize:read_me` before creating the widget.
- Never put explanatory prose inside the HTML — text goes outside the tool call.
- Never generate image files — that belongs to mode `infographic`.
- Never publish — that belongs to mode `publish`.
- Never use Excalidraw — that belongs to mode `diagram`.
