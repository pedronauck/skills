# Mode: `diagram` — Excalidraw Content Diagrammer

Turn the acquired content into a clear, well-structured Excalidraw diagram rendered inline in chat.

Prerequisite: the dispatcher (`SKILL.md` Step 3) has already acquired the content. This file covers diagram selection, the Excalidraw format contract, and layout rules.

## Step 1: Analyze and choose diagram type

Read the content and identify what kind of structure it conveys. Then pick the best diagram type:

| Content pattern | Diagram type |
|---|---|
| Steps, process, workflow, sequence | **Flowchart** — boxes connected by arrows in a clear flow direction |
| System, architecture, components, layers | **Structural diagram** — nested containers with labeled regions |
| Timeline, phases, chronological progression | **Timeline** — horizontal or vertical sequence with milestones |
| Hierarchy, org chart, taxonomy | **Tree** — parent-child relationships branching outward |
| Comparison, tradeoffs, axes | **2×2 matrix** or **comparison grid** |
| Relationships, dependencies, network | **Network/graph** — nodes and edges showing connections |
| Mental model, framework, concept map | **Concept map** — central idea with branching related concepts |
| Decisions, branching logic | **Decision tree** — diamond decisions with yes/no paths |

When in doubt, default to a **flowchart** for sequential content or a **structural diagram** for systems.

## Step 2: Read the Excalidraw format reference

Before creating the diagram, always call:

```
Excalidraw:read_me
```

This returns the element format, color palettes, and examples. Follow it exactly.

## Step 3: Build the Excalidraw diagram

Create the diagram using `Excalidraw:create_view` with these principles.

### Layout rules

- **Flow direction:** top-to-bottom for processes, left-to-right for timelines.
- **Spacing:** minimum 60px between elements, 80px+ between rows/columns.
- **Alignment:** keep elements on a grid — consistent x-coordinates for columns, consistent y-coordinates for rows.
- **Grouping:** cluster related elements visually with clear whitespace separating groups.

### Content rules

- **Extract the structure, not the prose.** A 2000-word article becomes 8–12 nodes, not 30.
- **Box labels:** 2–5 words max. If more is needed, split into two boxes.
- **One idea per box.** Do not merge distinct concepts.
- **Arrows have meaning.** Every arrow represents a relationship — flow, dependency, causation, sequence. Do not add arrows for decoration.
- **Use color sparingly.** 2–3 colors max to encode categories. Gray/neutral for structural elements.
- **Include key numbers.** If the content has important metrics, put them in the diagram (e.g., "92% adoption", "$159M ARR", "5 months").

### Element hierarchy

1. **Primary nodes** — the main concepts/steps (larger boxes, bolder colors)
2. **Secondary nodes** — supporting details or sub-steps (smaller boxes, muted colors)
3. **Connectors** — arrows showing relationships between nodes
4. **Labels** — text annotations on arrows or near groups (use sparingly)
5. **Containers** — dashed rectangles grouping related nodes (for structural diagrams)

## Step 4: Respond

Output the Excalidraw diagram inline. Keep commentary minimal — the diagram speaks for itself. Add a one-line note on what the diagram shows if needed.

## Mode-Specific Rules

- Always call `Excalidraw:read_me` before creating the diagram.
- Do not overcrowd. If the content is very complex, focus on top-level structure and offer to drill into sub-sections.
- Do not add decorative elements — every element earns its place.
