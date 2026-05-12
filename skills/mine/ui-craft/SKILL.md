---
name: ui-craft
description: Guardrails for user-facing UI work that enforce usability heuristics, accessibility floors, design-system discipline, and component state completeness — built primarily to prevent AI-slop UI. Use when designing, generating, reviewing, or refactoring any pixel a user will see: components, pages, dashboards, forms, dialogs, empty/error/loading states, motion, microcopy, dark mode, responsive behavior, or agent/AI interfaces. Integrates with DESIGN.md, token files, and brand-authority docs (e.g. web/CLAUDE.md, COPY.md) when present. Don't use for backend-only work, infrastructure, CLI/TUI design (use tui-design), or pure documentation editing.
---

# UI Craft

## The Fundamental Law

```
AI-GENERATED UI FAILS THE SAME WAYS EVERY TIME.
Visual sameness. Weak hierarchy. Fake interactivity.
Half the states missing. Hex codes outside the token system.
"Welcome!" microcopy that nobody asked for.
This skill exists so the UI being shipped is not slop.
```

UI craft is the discipline of producing user-facing surfaces that respect the user, the brand, and the medium. It is not "make it pretty." It is: every visible state explicit, every interactive element reachable by keyboard, every value drawn from the design system, every word earning its place, every motion serving a purpose.

A user interface is a contract with a real person. Ship slop and the contract breaks.

## Tunable Design Dials

Three named dials let the user steer taste without dragging the conversation through dozens of micro-preferences. Declare values before generating anything visual, and pin them in the deliverable so a future review can re-anchor.

| Dial                  | Range | Default | Low end (1–3)                                | High end (8–10)                                       |
| --------------------- | ----- | ------- | -------------------------------------------- | ----------------------------------------------------- |
| `VISUAL_VARIANCE`     | 1–10  | 6       | Conservative, system-aligned, recognizable   | Bold, expressive, willing to diverge from the category default |
| `MOTION_INTENSITY`    | 1–10  | 4       | Reduced/utility only: state feedback         | Rich orchestration, layered materials, premium feel   |
| `INFORMATION_DENSITY` | 1–10  | 5       | Spacious, calm, marketing-leaning            | Dense, data-heavy, dashboard-leaning                  |

What changes at each end:

- **`VISUAL_VARIANCE`** — at low values, defaults to the closest equivalent of a familiar pattern (e.g. shadcn defaults, Material 3, Apple HIG). At high values, breaks the category template deliberately — bento over grid, asymmetric over centred, branded color over neutral.
- **`MOTION_INTENSITY`** — drives durations (low → 80–150ms only; high → up to 500ms entrances, layered easing), and unlocks premium materials (blur, mask, clip-path) at ≥ 7.
- **`INFORMATION_DENSITY`** — drives spacing scale ramps (low → space-6/8/10; high → space-1/2/3), row heights, line-height, and chart annotation richness. High density implies tabular-nums and keyboard-first interactions.

When the user asks for "more bold" / "calmer" / "tighter" / "looser", translate to dial moves. Do not re-derive every other choice from scratch.

Cite: dial pattern adapted from `taste-skill` (Leonxlnx, open-design ecosystem).

## HARD-GATE

```
Do NOT generate, modify, or approve any user-facing UI surface until:

1. The brand authorities have been READ (not skimmed):
   - DESIGN.md (root) if present
   - Design token files (e.g. packages/ui/src/tokens.css, theme.ts, tailwind.config.*)
   - Frontend conventions doc (e.g. web/CLAUDE.md, .cursorrules, .ai/rules.md)
   - Copy authority (e.g. COPY.md, content/style-guide.md)
2. The surface's JOB is stated in one sentence (what the user is here to do).
3. The complete STATE LIST for the surface is enumerated
   (default, hover, active, focus-visible, disabled, loading, empty, error, success — plus any domain states).
4. The component is known to either EXIST in the design system already
   or is JUSTIFIED as a new addition with a token-level proposal.
5. The SCENE SENTENCE has been written (see below). Categories are not scenes.
6. The REGISTER has been picked: Product or Brand (see below).

This gate applies to every change — a one-line tweak, a new variant, a full page.
"It's just a small change" is the most common slop excuse.
```

### Scene Sentence

Before any visual decision (dark vs light, density, color register, motion intensity), write a sentence of physical context: *who* uses this, *where*, under *what ambient light*, in *what mood*.

- ❌ "Observability dashboard" — that is a category. It points at a thousand average answers.
- ✅ "SRE glances at incident severity on a 27" monitor at 2am in a dim room — every UI element competes with a paged alert sound."
- ❌ "Marketing landing page"
- ✅ "Engineering lead, 11am Tuesday, second tab over from Linear, decides in 12 seconds whether to forward this to procurement."

If the scene does not force the answer, add detail until it does. Most weak visual decisions come from a missing scene — the rest comes from defaults (see `references/anti-defaults.md`).

Cite: scene-driven decisions adapted from `impeccable` (compozy/agh).

### Register: Product or Brand

Two registers, two rule sets. Pick before generating; do not blend reflexively.

| Register     | Lives in                                           | Color                                      | Type                              | Motion                                          | Bans                                              |
| ------------ | -------------------------------------------------- | ------------------------------------------ | --------------------------------- | ----------------------------------------------- | ------------------------------------------------- |
| **Product**  | App shells, dashboards, settings, forms, lists     | Restrained: tinted neutrals + 1 accent ≤10% | System fonts ok; fixed rem scale  | 150–250ms state feedback only; no decoration    | Decorative motion, reinvented affordances         |
| **Brand**    | Landing pages, hero blocks, onboarding, marketing  | Committed or Drenched: 1 saturated color carries 30–60% | Display + body pairing; expressive choice | Full orchestration welcome; entrance reveals    | Generic illustration, lazy monospace as "tech"    |

Decision rule:

- The scene sentence describes a recurring task by a known user → **Product**.
- The scene sentence describes a first impression, a deliberate impression, a campaign → **Brand**.
- If you cannot decide, the answer is almost always **Product** — brand register is the exception.

Switching registers mid-surface is the source of half of all "this feels off" reactions. Lock the register and design within its rules.

Cite: register split adapted from `impeccable` (compozy/agh).

## The Anti-Slop Operating Loop

Run every UI task through this loop in order. Skipping steps produces slop. Each step has a stop condition.

### Step 1 — Load brand authorities
Read every file listed in the HARD-GATE that exists in the repo. Treat their contents as **normative**: tokens, components, copy patterns, and naming conventions are authoritative. Never invent a value that already has a token. Never restate brand voice — quote it.

**Stop condition:** If no brand authorities exist, fall back to `references/visual-craft.md` defaults, but mark this in the deliverable as a finding: *"Project has no DESIGN.md / token system; recommend scaffolding before further UI work."* Continue, but expect to update this when bootstrapping happens.

### Step 2 — State the surface's job
One sentence, written from the user's perspective. *"The user opens this dialog to confirm destructive deletion of a project and its data."* Not *"This is the delete confirmation modal."*

**Stop condition:** If the surface has more than one job, split it. Multi-purpose surfaces are a primary source of weak hierarchy.

### Step 3 — Apply the usability filter
Run the surface through Nielsen's 10 heuristics + the load-bearing Laws of UX (Jakob, Hick, Miller, Fitts, Tesler). Identify the one or two that pose the most risk for this surface.

For depth, read `references/usability-foundations.md` when the surface is novel, complex, or being audited.

**Stop condition:** If the surface violates a heuristic without justification (e.g. no visible system status during a long-running action, hidden destructive primary action), redesign before continuing.

### Step 4 — Enforce the accessibility floor
WCAG 2.2 AA is the floor, not the ceiling. Non-negotiables for every interactive surface:

- Text contrast ≥ 4.5:1 (≥ 3:1 for ≥ 18.66px bold or ≥ 24px regular)
- Non-text UI / state indicators contrast ≥ 3:1
- Focus visible on every interactive element (2px outline minimum, not just color change)
- All interactive surfaces reachable and operable by keyboard (Tab, Shift+Tab, Enter, Space, Esc, Arrow keys per WAI-ARIA pattern)
- Target size ≥ 24×24 CSS pixels (≥ 44×44 on touch surfaces)
- `prefers-reduced-motion` honored: replace transforms/translates with opacity-only or no motion
- Semantic landmarks (`main`, `nav`, `header`, `footer`, `aside`) and headings in order (one `h1`, then `h2` siblings, no level skips)
- Form controls have programmatic labels (`<label for>`, `aria-labelledby`, or `aria-label`)
- Errors associated with their field via `aria-describedby` and announced via `aria-live="polite"` or `role="alert"` for blocking errors

For ARIA component patterns (dialog, combobox, menu, tabs, slider, listbox) and verification recipes, read `references/accessibility-floor.md`.

**Stop condition:** If a floor item cannot be met, that is a blocker, not a trade-off.

### Step 5 — Apply visual craft
Draw values from the design system. If the system is missing a value:

- **Typography:** choose from the existing scale; never one-off a font-size
- **Color:** use semantic tokens (`--color-bg-danger-subtle`), never raw hex
- **Spacing:** snap to the spacing scale (typically 4/8/12/16/24/32/48/64); no magic numbers
- **Radius:** use the radius scale (`--radius-sm`, `-md`, `-lg`); no `border-radius: 7px`
- **Motion:** duration 80–240ms for state, 240–400ms for entry/exit, easing per the system (`ease-out` for entry, `ease-in` for exit)
- **Elevation:** use the elevation scale (`--shadow-1` … `--shadow-5`); no ad-hoc box-shadows

For typography scales, color theory, spacing rhythm, dark-mode strategy, and motion physics, read `references/visual-craft.md`.

**Stop condition:** If a value cannot be drawn from the system and the gap is real, propose adding a token to DESIGN.md (see Step 9), do not inline-invent.

### Step 6 — Enumerate the state matrix
Open `assets/state-matrix.md`. For the component, fill every row that applies:

- **default** — resting state, no interaction
- **hover** — pointer over interactive surface (skip for touch-only)
- **active / pressed** — mid-interaction
- **focus-visible** — keyboard focus indicator (always required for interactive)
- **disabled** — non-interactive, ≥ 3:1 contrast for affordance, explain why if non-obvious
- **loading** — work in progress; show progress signal and disable the trigger
- **empty** — first-run / no-data; explain what goes here and provide a primary action
- **selected / on / checked** — when applicable
- **error** — validation or async failure; specific, plain-language, recovery-oriented
- **success** — confirmation that an action landed; transient unless audit-relevant

For do/don't per component (buttons, inputs, dialogs, navigation, tables, dropdowns, tabs, popovers, toasts) read `references/component-patterns.md`.

**Stop condition:** Any state listed but not designed is a known slop pattern (`StateMatrixHoles` — see anti-slop table below). Design it now, not later.

### Step 7 — Run anti-slop detection
Match the surface against the 14 named patterns in the table below **and** the literal blocklist in `references/anti-defaults.md`. Every match is a stop-and-fix, not a note.

Then run the **two-level slop test**:

- **First-order:** could a stranger guess the aesthetic from the *category alone*? ("observability → dark blue", "AI startup → purple", "SaaS landing → centred hero with gradient")? If yes, you are inside the training-data default.
- **Second-order:** could they still guess from *category + your anti-references*? If yes, you have not escaped — you have just moved to the predictable counter-default (e.g. "we hate gradients, so brutalist mono and stark monochrome instead"). Both orders are trapped.

Escape the trap by going back to the scene sentence and re-deriving from the specific user, moment, and physical context. Generic anti-defaults are still defaults.

For detection prompts, before/after examples, and remediation recipes, read `references/ai-slop-patterns.md`. For the literal-artifact blocklist (emoji-as-icon, "Inter" by reflex, centred hero, placeholder names, gradient text, etc.) read `references/anti-defaults.md`.

**Stop condition:** Any pattern hit. Any anti-default literal present without a scene-sentence justification. Fix before moving on.

### Step 8 — Apply microcopy quality
Every visible word earns its place. Rules:

- **CTA buttons:** action verb + object (`Delete project`, not `OK` / `Submit` / `Click here`)
- **Errors:** what happened + why + how to recover, in plain language, no blame (`Couldn't save — your session expired. Sign in again to continue.`)
- **Empty states:** explain what lives here, why it's empty, and the one action that fills it
- **Help text:** under the field, only when the label is ambiguous; never repeat the label
- **Confirmation dialogs:** title = the decision (`Delete this project?`), body = the consequence (`All workflows, runs, and logs will be permanently removed.`), primary = the action verb (`Delete project`)
- **No AI vocabulary:** no `seamless`, `delve`, `elevate`, `empower`, `unleash`, `harness`, `tapestry`, `landscape`, `journey`, `unlock the power of`, `take it to the next level`
- **No empty greetings:** no `Welcome!`, no `Hi there!`, no `Let's get started!`
- **No filler:** no `Please`, no `Note that`, no `In order to` (just `To`)

For tone guides per surface type and a full banned-vocabulary list, read `references/microcopy-quality.md`.

**Stop condition:** Any banned phrase appears. Replace.

### Step 9 — Verify and document deltas
Before declaring the surface done:

1. **Visually verify** in a browser at the supported breakpoints (mobile, tablet, desktop). Open DevTools, force each state in the state matrix, screenshot the ones that are not trivially default.
2. **Keyboard-test** the full interaction: Tab order, focus visibility on every step, Esc to dismiss, Enter to commit, arrow-key navigation in composite widgets.
3. **Contrast-check** any color pair using actual rendered values; do not trust the token name.
4. **Reduced-motion test:** toggle `prefers-reduced-motion: reduce` and confirm no rejected motion.
5. **Document deltas to the design system:** if a new token, variant, or component pattern was introduced, append it to `DESIGN.md` (or the relevant token file) **in the same change set**. Tokens-without-DESIGN.md updates are silent design-system drift.

For verification recipes per ARIA pattern, read `references/accessibility-floor.md#verification`.

**Stop condition:** Anything in this list that cannot be checked because the surface is not actually runnable is a blocker — say so in the deliverable, do not claim "done."

## Anti-Slop Detection Table

Match against every surface. Hits are not nits. Severity drives the response:

- **Critical** — blocks merge. Accessibility, contract-level failures, broken keyboard or focus contracts.
- **Serious** — blocks review approval. Visible UX degradation, training-data defaults, design-system drift.
- **Moderate** — nit that polishes later — *unless* three or more accumulate on the same surface, in which case treat as Serious.

| #  | Pattern              | Severity   | Symptom                                                                            | Fix                                                                                                  |
| -- | -------------------- | ---------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 1  | VisualSameness       | Moderate   | Every block looks the same: same card, same radius, same shadow, same gray border  | Establish weight hierarchy with size + spacing + contrast; demote secondary blocks to plain text     |
| 2  | WeakHierarchy        | Serious    | Eye lands on the wrong element first (decoration outranking primary action)        | One primary action, one focal point per view; demote decoration with neutral color and smaller scale |
| 3  | TextOverflow         | Serious    | Long strings clip / wrap badly / push layout in responsive sizes                   | Test with worst-case content (long names, i18n strings 30% longer, zero data); use truncation + tooltip or wrap explicitly |
| 4  | FakeInteractivity    | Critical   | Looks clickable, isn't (or vice versa); no hover/focus/active states               | Match cursor + role + state styling to actual behavior; remove decorative affordances                |
| 5  | EmojiSpam            | Moderate   | Emojis as decoration, mascots in headings, or replacing icons in the design system | Use only icons from the icon set; remove emoji from product UI unless culturally explicit            |
| 6  | GradientCrutch       | Serious    | Gradient backgrounds carrying the entire visual identity                          | Lean on type + spacing + a restrained palette; reserve gradients for brand moments, not chrome       |
| 7  | GlassmorphismAbuse   | Moderate   | `backdrop-filter: blur(...)` on everything; legibility damaged                     | Use blur on at most one elevated surface; keep text on solid backgrounds                              |
| 8  | GenericIllustration  | Serious    | Same stock 3D / isometric / "people pointing at laptops" art in every empty state | Use brand-native marks or text-only empty states; explain the data, do not perform delight            |
| 9  | DesignSystemDrift    | Serious    | Raw hex / px values / one-off radii instead of tokens                             | Replace with tokens; if no token exists, propose one in DESIGN.md                                     |
| 10 | StateMatrixHoles     | Critical   | Loading / empty / error states missing or copy-pasted from default                 | Design each state explicitly; loading shows progress, empty explains, error recovers                  |
| 11 | CenteredEverything   | Moderate   | Everything center-aligned by default; long text becomes a ragged column            | Left-align text by default; reserve center for short headlines, hero blocks, and dialog actions       |
| 12 | RandomRadii          | Moderate   | `rounded-xl` here, `rounded-2xl` there, sharp corners on the third card           | Pick a radius hierarchy (chip / control / surface / overlay) and apply consistently                   |
| 13 | GhostFocus           | Critical   | Focus-visible removed / styled identical to hover / invisible against the bg       | Restore `:focus-visible`; outline ≥ 2px, ≥ 3:1 contrast, offset from the element                      |
| 14 | MagicNumbers         | Moderate   | `width: 327px`, `margin-top: 11px`, `gap: 13px` — values not in any scale          | Snap to spacing/size scale; rebuild layout from the grid                                              |

## Red-Flag Self-Audit

Catch these thought patterns and STOP:

| Thought                                                       | What It Means                                              |
| ------------------------------------------------------------- | ---------------------------------------------------------- |
| "The design system doesn't have this exact component"         | DesignSystemDrift incoming — propose a token, do not improvise |
| "It's just an internal tool, ship it"                         | The internal tool is where slop habits become muscle memory |
| "I'll add the loading state later"                            | StateMatrixHoles — later never ships                       |
| "The empty state is fine with just 'No data yet'"             | GenericIllustration sibling — explain what goes here       |
| "We'll skip a11y for v1"                                      | A11y added later is a rewrite, not a polish                 |
| "Just add a gradient to make it pop"                          | GradientCrutch                                              |
| "Center it"                                                   | CenteredEverything — left-align text by default            |
| "Use 12 for the margin, looks better"                         | MagicNumber — snap to the scale                            |
| "Add some emoji to make it friendly"                          | EmojiSpam — friendliness comes from copy, not decoration   |
| "The user will figure it out"                                 | Recognition over recall — they should not have to figure it out |
| "Looks good on my screen"                                     | Test mobile + dense data + long strings + reduced motion   |

## Reference Index

Read JIT, never preload:

- `references/usability-foundations.md` — read when designing a novel surface or auditing an existing one. Covers Nielsen 10 heuristics, Laws of UX, progressive disclosure, mental models.
- `references/accessibility-floor.md` — read when implementing or verifying any interactive widget, especially dialogs, menus, comboboxes, tabs, sliders. Includes ARIA patterns and verification recipes.
- `references/visual-craft.md` — read when there is no token system or the existing system needs extending. Typography scales, color systems, spacing rhythm, motion physics, dark mode, elevation.
- `references/component-patterns.md` — read when designing or reviewing one of: buttons, inputs/forms, dialogs/modals, navigation, tables, cards, dropdown/combobox, tabs, popovers/tooltips, toasts.
- `references/microcopy-quality.md` — read when writing or reviewing any user-visible text. Includes the full banned-vocabulary list and tone guides per surface.
- `references/ai-slop-patterns.md` — read when auditing AI-generated UI or when a detection-table hit needs full detail. Includes before/after for each of the 14 patterns.
- `references/anti-defaults.md` — read when a request feels like a category default. 17 literal artifacts to refuse on sight (emoji-as-icon, "Inter" by reflex, centred hero, placeholder names, gradient text, glassmorphism padrão, modal-as-first-thought, etc.).
- `references/human-ai-ux.md` — read when building agent or AI-feature interfaces (chat, streaming responses, citations, confidence, recovery). Microsoft + IBM guidelines distilled.
- `references/design-system-integration.md` — read when reading or extending DESIGN.md, working with semantic tokens, structuring shadcn/Radix composition, or writing rules-files for AI codegen.
- `references/performance.md` — read when shipping any new surface, when Core Web Vitals regress, or when motion / images / fonts / bundle size enter the picture. Includes the 80ms perceived-performance threshold, font-loading zero-CLS strategy, and an executable pre-ship gate.
- `references/motion-patterns.md` — read when adding or reviewing any animation. Includes the 100/300/500 duration rule, quality easing curves, code patterns for Tailwind / CSS / Framer Motion, reduced-motion templates, and severity-tagged anti-patterns.
- `references/dark-mode.md` — read when implementing or reviewing a dark theme, when adding tokens that need a dark counterpart, or when "the dark mode looks worse" is a real comment. Surface-lightness elevation, accent desaturation, semantic token strategy, focus visibility, dangerous combinations.
- `references/archetypes.md` — read when picking a pattern or when "we need a [thing] like Linear / Notion" is the brief. Seven named archetypes (Bento, Command Palette, Focus Mode, Live Status, Intelligent List, Empty State Hero, Inline Editor) each with a six-slot signature contract.

### Scripts

- `scripts/check-contrast.mjs` — verify foreground/background WCAG AA/AAA + APCA Lc for any color pair or JSON token batch. Zero-dependency, accepts hex / rgb / oklch. Wire into CI as a gate when token files change.
- `scripts/detect-token-drift.mjs` — scan source for raw hex / rgb / hsl / oklch values used outside designated token paths. Reports file:line with replacement suggestion. Wire into the pre-ship checklist or pre-commit hook.
- `scripts/validate-metadata.py` — validate this skill's own `name`/`description` frontmatter against the agentskills.io spec.

## DESIGN.md Integration

This skill is not a DESIGN.md skill. It is a UI craft skill that respects DESIGN.md when present.

**On every UI task:**
1. **Locate.** Check repo root for `DESIGN.md`. Also check `packages/ui/`, `apps/web/`, `docs/`, and `.ai/`. Treat the first hit as authoritative.
2. **Read.** Load it fully before generating UI. Tokens, components, and don'ts are normative.
3. **Respect.** Never invent values that have tokens. Never override a documented don't.
4. **Propose, don't rewrite.** When a new variant or token is genuinely needed, add it to DESIGN.md as a focused diff in the same change set as the UI work. Do not rewrite the file.
5. **Bootstrap only when invited.** If DESIGN.md does not exist and the user wants UI work to continue, fall back to `references/visual-craft.md` defaults and surface the gap as a finding. Defer authoring DESIGN.md to a dedicated DESIGN.md skill or workflow when one exists — do not bootstrap as a side effect of a UI ticket.

For the canonical DESIGN.md sections, token discipline, and how DESIGN.md interacts with shadcn/Tailwind and rules-files, read `references/design-system-integration.md`.

## When NOT To Use

- Backend-only work (database, API, infra) — UI craft does not apply
- CLI / TUI design — use `tui-design`
- Pure copy edits with no visual change — use a writing skill
- Internal scripts and tooling with no user surface
- Performance optimization that does not change the visual or interaction layer

## Error Handling

- **No brand authorities found:** fall back to `references/visual-craft.md` defaults. Mark this in the deliverable. Do not invent brand identity silently.
- **Surface cannot be rendered for verification:** state explicitly in the deliverable that visual verification is pending. Do not claim "done."
- **Conflicting tokens between DESIGN.md and a token file:** trust DESIGN.md; flag the divergence as a finding for the user to resolve.
- **State matrix exceeds what is reasonable for the surface:** prune to the states the surface actually supports, but justify each pruning in the deliverable. Do not silently drop states.
- **The skill detects a violation but the user insists on shipping it:** record the override in the deliverable as a known-slop hit with rationale. Do not pretend it is fixed.

## Bottom Line

```
Every UI surface is a contract with a user.
Respect the user by drawing from the system.
Respect the medium by completing every state.
Respect the work by refusing slop.
```

For tonal kinship with the rest of the toolkit, this skill is the UI sibling of `no-workarounds`: name the failure mode, gate the fix, document the override.
