# Orchestrating a spec prototype

Pedro usually asks a conductor session to "orquestrar/conduzir" several agents. The rules below
reflect what he accepted and what he had to correct.

## Models and effort

- Use the model and effort Pedro names, per agent, and confirm it in the session status. If a pass
  ran at a different effort, say so.
- When he names none, use Opus High for prototype lanes and Sonnet High for research subagents. The
  campanhas round 1 on Fable Medium was rejected wholesale and redone on Opus High.

## Research

- Before any lane edits a file, run research subagents in parallel by area. The areas are: the
  product's own repo (components, sibling modules), the design-system catalog (for example
  reui-blocks/BnUI), Inspo, Savee, Dribbble, and any reference Pedro named (AffectUI, Linear, a
  screenshot).
- Capture the real sibling screens and keep them for the side-by-side gate.
- Read every reference image yourself. Treat it as the bar for craft and richness, not as a layout
  to copy.
- Each subagent returns decisions, not links: "screen → component → why → path or URL →
  screenshot". For external references, add the top ideas worth stealing per component.
- Write the result to `research-<lane>.md` (or the spec's `_uiux.md`). `_uiux.md` describes a
  visualization per kind of information. If it says "plain table" or a table home, rewrite it
  before the lanes start.

## Lanes

- **Split.** One base lane first builds the shared runtime: shell, fixtures, scenario control and
  kit. Then one lane per group of screens. Each lane owns disjoint files, with no lane-prefixed
  file soup inside a single draft.
- **The first deliverable is the reference.** Shell, home or cockpit and the main list. Compare
  them side by side with the sibling module and fix them, then release the other lanes.
- **Every lane brief contains:**
  - Pedro's directions quoted literally;
  - the screens it owns, with the visualization map;
  - the component inventory to reuse, with paths;
  - the gallery-structure rules from `SKILL.md`;
  - the viewport and theme to judge by;
  - "Done = these states render in both themes and `proto check` is clean".
- **Never write a brief that forbids touching production views.** Allow minimal prop, slot and
  container changes.
- **Workers run only `proto check --json` and `proto flow coverage --json`.** No lint, test,
  build, doctor, `proto dev`, screenshots, `bun install` or the repo's `verify`. They don't commit.
  Pedro has asked "porque ele tá rodando lint e test se eu falei pra só rodar no final?" more than
  once.
- **The conductor integrates and runs the final gates once.** Those are `proto check`, typecheck,
  lint, format, doctor and build. Then the conductor captures and opens every state and sends
  defects back as a second round before Pedro sees anything.
- **Hard limits.** Compozy caps active children (5). Queue the lanes instead of failing them. If a
  worker stops mid-task, another finishes its scope; never leave threads half-applied.
- **Run independent reviews in parallel.** Pedro asks "porque isso não rodou em paralelo?" when
  they run in sequence.

## Independent review

- After the lanes, run a reviewer (Opus High) with the screenshots before showing Pedro. Give it
  the visual bar, the sibling captures and his standing comments. It catches blockers such as
  unreadable columns, truncated names and broken states. Fix them, then show Pedro.

## Showing Pedro

- Start the gallery on the project's documented port, in a visible terminal. Never start a second
  gallery on a port already serving him. Lanes use other ports.
- Send direct links per screen and state. Answer "em que pé?" with what is already live.
- If an agent is still editing the same worktree, warn that the gallery will change under him and
  that comments he makes now still count.

## Comment rounds

- Pull the threads with `proto comments list --json` (open by default; `--status resolved` for
  history), then run `proto-apply-comments`.
- Split threads by screen across workers with disjoint files. Brief them that each comment is a
  pattern to sweep.
- Workers don't use the comments CLI. The conductor answers each thread after checking the change
  at the comment's viewport, with a screenshot.
- After the round, report which comments became spec changes, and ask any open product question in
  `Q1 - a)` form.
- Mark the prototype approved only when Pedro says so, after integration and commit, because
  approval records the commit.

## Handoff to implementation

- The implementation brief cites the draft as the source of parity and lists every state and every
  resolved comment.
- Implementation lanes reuse the prototype's components (they were born as production components)
  and confirm on the real route with real data that each state appears.
- A parity reviewer compares prototype and real screen state by state. It counts divergences, and
  any high-severity one blocks.
- Every UI capability gets its API or MCP twin and role checks when the project requires it.
- The PR carries before/after screenshots in light and dark, regenerated after the last fix.
