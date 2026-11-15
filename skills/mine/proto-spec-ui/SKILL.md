---
name: proto-spec-ui
description: Prototype the screens of a spec in the proto gallery (@compozy/proto or @protohq/cli) to Pedro's quality bar, from reference research through gallery structure, visual QA, comment rounds and implementation parity. Use when asked to make the /proto of a spec, to redo or review such a prototype, to apply a round of gallery comments across a spec, or to implement a spec from its approved prototypes. CLI, meta and guard mechanics belong to the proto skill; a single comment thread belongs to proto-apply-comments.
---

# Prototype a spec's UI

The prototype is where Pedro decides what the product looks like, and the implementation must match it:
"igual OU melhor, nunca pior". The usual failure is a first round of basic screens that Pedro rejects, followed by
him repeating the same corrections over and over:
- "alguns stats em cima e tabela em tudo, básico e clichê"
- the layout is cramped
- components are hand-made when the app already has them
- the gallery is a mess

This skill stops those repeats. Mechanics (`proto check`, `meta`, drafts, flows, guards, comments CLI) live in the
`proto` skill. Load it alongside this one. The project's `docs/design/prototyping.md` and `AGENTS.md` override
anything here for that project.

## Procedure

Order matters at steps 2→3→4 and 5→6. The rest adapts to the request.

1. **Read the spec and map the screens.** Use `_spec.md`, `_uiux.md`, roles and the data each screen shows. List
   the real navigable screens (routes and settings sections) in the order a user meets them. Spec gaps found while
   drawing go to Pedro as `Q1 - a)` questions: a short "why" first, no jargon, recommended option first and marked.
   Don't decide for him or turn the doubt into a gallery state.
2. **Research before drawing anything.** For each screen, produce a visualization map:
   - the question the screen answers;
   - the shape of each piece of information and the component that encodes it;
   - the product components it reuses, with their paths;
   - the reference it learns from, from captures of the app's most mature sibling modules, the design-system
     catalog and external references.

   Run this research in parallel subagents per area. The output is decisions per screen, not a list of links.
   See `references/visual-bar.md` §Information shapes and `references/orchestration.md` §Research.
3. **Build one reference first.** Build the shell, the home or cockpit, and the main list screen. Compare them side
   by side with the sibling module's real screens. Fan out only after they hold that level.
4. **Fan out by surface.** Use one strong agent (Opus High unless Pedro names another model and effort) per group
   of screens, with disjoint files and a brief carrying Pedro's literal directions and this skill. Workers run only
   `proto check --json` and `proto flow coverage --json`. See `references/orchestration.md` §Lanes.
5. **Run conductor QA before Pedro sees anything.** Render every state, open the images and click every interaction.
   Return defects to the lanes and repeat until clean. See §Visual QA below.
6. **Show it live.** Keep the gallery server running and send direct links for each screen and state. Never ask
   Pedro to start a command. Before pointing him there, check that the server is still up. Commit screen by screen,
   most visible first. Never leave placeholder screens in a gallery he is watching.
7. **Apply comment rounds.** Use `proto-apply-comments`. Every comment is a pattern: fix its whole class on every
   screen that shares it, then name those screens in the reply. Answer each thread with what changed and a screenshot
   at the viewport he commented from. Resolve threads but never approve them. When a comment changes product
   behaviour, update the spec, `_uiux.md` and the ADRs or Q list too.
8. **Commit and hand off.** Commit after Pedro approves. The approved prototype becomes the frontend contract (§Parity).

Done when Pedro approves in chat or in the gallery. Before that, `proto check` and flow coverage are clean, there
are no console errors in any state, and the conductor has looked at every state in both themes.

## Gallery structure

- **One entry per real screen.** A screen is something the user navigates to.
  - Dialogs, drawers, popovers, pickers, ⌘K, shortcut panels and confirmations are states of the screen where they
    open, rendered over the full screen.
  - Atoms, fixtures, data and shared kits live in a folder with no `index.proto.tsx`.
  - Never put a whole module into one prototype as states (one campanhas prototype had 114 states).
- **Name screens by order of use.** Slugs follow `<spec>-NN-<screen>` in that order. The title is only the screen
  name, since the gallery already groups by spec. `route` is the real route. Declare `roles`.
- **6–14 states per screen.** The first is the normal, populated screen. Labels describe what the reviewer sees,
  in the product's language. Cover empty, loading, error, permission/role, long content and volume. Data scenarios
  can live in a scenario control instead of multiplying states.
- **No `proposta-*` alternatives** unless Pedro asks or hesitates. When he does, put labelled variations (A/B/C)
  side by side with stress data.
- **Real chrome.** Every state renders inside the module's real chrome (rail, sidebar, header, dock), not as a loose
  component.
- **Flows connect the screens**, and every state belongs to some journey.

## Visual bar

`references/visual-bar.md` is the full rulebook. Read it before the first draft and again before QA. The rules
Pedro repeats most:

- **Shape follows information.** "KPI strip + table" is never a default layout.
  - A count with a limit is a meter. A split is a distribution bar. A series is a chart with comparison. A queue is
    a forecast with its limit line. A history is a timeline. A hierarchy is a tree. A flow is a graph.
  - Every number carries context. A new module gets a home or cockpit with data.
- **Product components first.** Hand-rolling something the app already has is a defect. Workers may make minimal
  production-view changes (a prop, a slot, a container fix), so never forbid them.
- **Roomy, calm, consistent.** Use one spacing scale, real padding and rows that breathe. Never shrink type to fit.
  - One surface per area, never card inside card.
  - Neutral by default; color only means something. Selection is neutral gray, never green.
  - Attention marks with a small icon and sort order, never a red row.
- **Equal effort on every screen**, settings and structure screens included.
- **Built for scale and real data:** volume states, realistic and consistent fixtures, real avatar photos, real
  catalogs.
- **Interactions work** when clicked, not just when they render.

## Visual QA

The conductor does this, not the workers:

- **Viewports.** Capture each state at Pedro's review viewports: 1396×693 dark first, then 1440×900, ≥2084 wide
  and 390 mobile, in light and dark.
- **Open every image.** A capture that comes back stale or unchanged is a failure, not a pass.
- **Click every flow.** Continue, back, tabs, open and close, expand and collapse, scroll to the end, keyboard and
  Esc.
- **Zero console errors.** Look for truncation, overflow, overlap, missing thousand separators, numbers that
  disagree across screens, and a selected state that is barely different from unselected.
- **Side-by-side gate.** Each screen is compared with the sibling module's capture.
  - "No padrão do produto" is a claim that needs that comparison.
  - Count imports from the product kit (page, panel, table, KPI, charts). If a screen has zero, block it.
- **Heavy gates only at the end.** Prototype gates are `proto check`, typecheck, lint, format, doctor and build,
  once, by the conductor. Never run the repo's full `verify` or integration tests for a prototype.

## Parity

The approved prototype is the frontend contract:

- **Production components.** New charts, pagers and tables are born as data-agnostic production components, so the
  implementation reuses them.
- **Real routes and view models.** They must produce every state the prototype shows: privacy modes, never-published
  entities, real catalogs, role limits.
- **Port every resolved comment.** Each comment resolved in the prototype must hold on the real screen. Check them
  one by one.
- **Parity review.** Compare each prototype state with the real screen fed by real data, not only the components.
- **The PR.** It carries before/after screenshots in light and dark, updated to the final version.

## References

- `references/visual-bar.md`: before drafting, before QA, and when a comment names a visual problem.
- `references/orchestration.md`: when orchestrating workers. Covers research subagents, lane briefs, the gate split
  and comment rounds with several workers.
- The project's `docs/design/prototyping.md` (its "Spec prototypes" section when present): before step 2, for
  the sibling modules to mirror, the component kit and local traps.
- `references/projects.md`: when the repo is CompozyOS (component names, vocabulary, avatar and shell patterns).
