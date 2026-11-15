# Project notes

Each project keeps its prototyping notes in `docs/design/prototyping.md` (with `AGENTS.md` and
`proto.config.ts`), and those are authoritative. Private projects such as branas-dashboard record
Pedro's standing corrections there in a "Spec prototypes" section. Read it before research. This
file only holds notes for the open-source CompozyOS repo. Paths were verified on 2026-11-15; if one
is gone, search for the name before assuming it was removed.

## CompozyOS (`~/Dev/compozy/compozy`)

- **Components Pedro asked for by name instead of hand-made substitutes:**
  - `RuntimeSelector` (`web/src/systems/runtime/...`);
  - from `packages/ui/src/components/custom/`: `MarkdownEditor`, `SymbolPicker`, `ResizableDrawer`
    (every drawer), `ListingPage`, `StateGlyph`, `data-surface`, `page-content`;
  - `ProviderUsageRow`, `SessionListToolbar`;
  - the real session header (`os-window-frame`), the `Dock`, and the permission dock view.
- **Shell:** every screen sits inside the real shell (top bar, dock, tabs, sidebar). Only catalogs
  (such as avatars) may be loose component sheets.
- **Graphs:** use React Flow (`@xyflow/react`) built properly, with one card per node type, state
  variants and stories. It is the reference for any flow canvas, including in other projects.
- **Vocabulary:** "Stays on", "On demand", "Global", "Model", "What it does", "Where it works",
  "Check-ins", "How often". Never "instance", "persona", "runtime" or "scope" in the UI.
- **Avatars:** a Blobatar per slug; only `working` animates; the provider badge appears from 24 px
  up; needs-you is the small orange product triangle and sorts first.
- **Patterns that came out of comments:**
  - the session header has the project on the left;
  - Dashboard comes first in the dock;
  - the permission dock shows the command in a code block;
  - long skill or markdown content opens in a modal with a file tree.
- **Craft references:** AffectUI components and the Autopilot captures. When Pedro is unsure, he
  asks for 2–3 variations side by side.
