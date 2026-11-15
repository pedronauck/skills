# Visual bar

These rules come from Pedro's comments on six spec prototypes (financeiro, always-on, tarefas,
campanhas, tarefas-desenvolvimento and automacoes; 100+ gallery comments). Tags in brackets name the
spec and the comment or message that produced each rule. Every rule is a standing correction: if a
screen breaks one, Pedro will comment it.

Contents: information shapes · reuse · density and spacing · calm surfaces · layout and viewports ·
scale and data · lists, filters and bars · forms and editing · language · marks and empty states ·
interaction · applying a comment.

## Information shapes

- Before writing JSX, name what each block says and pick the component that encodes it. The
  default "a few stats on top and a table for everything" was rejected in financeiro, campanhas
  and automacoes ("básico e clichê ao invés de pensado de forma individualizada"):

  | Information | Component |
  | --- | --- |
  | Count against a limit or quota | Meter or gauge with the limit drawn |
  | Parts of a whole | Distribution bar |
  | Value over time | Chart with comparison (previous period, target) |
  | Queue or backlog | Forecast with a limit line |
  | Events and history | Timeline grouped by day, "load more" |
  | Categories and nesting | Tree with guide lines (`BranchTree`-like) |
  | Steps, pipeline and funnel | Funnel or stage bar |
  | Automation or agent flow | Node graph (React Flow), one card per node type |
  | Run or trace | Waterfall with time and cost axes, slowest step, "now" line |
  | Status list | Table whose summary tiles are its filters |

- Every number has context: history, limit, split or comparison. An unknown cost is "—" or
  "N sem custo ainda", never 0. When a fixture lacks the context, add it.
- Don't be lazy about creating components ("sem preguiça de criar um componente diferente",
  financeiro). Rich metaphors are welcome when the concept asks for them: sticky notes for memories,
  sliders with limits, segmented controls, budget bars, sparklines, icons in summary rows (always-on).
- A new module gets a home or cockpit with real numbers, in the style of the most mature module.
  A table is not a home (campanhas).
- Give every screen the same effort. Settings, structure and admin screens fall behind ("parece que
  ficou pra trás de tão básica", financeiro C10). After any redesign, sweep every screen to the new
  level.

## Reuse before you build

- Inventory the product before drawing: the UI kits, `components/dashboard`-style folders, and the
  sibling modules' real screens. Hand-rolling something that exists is a defect. Reuse made up 7 of
  the 19 always-on comments and 4 of the tarefas-desenvolvimento ones.
- When a comment says "não segue o padrão" or "olhe nos outros módulos", open the equivalent
  production screen and copy its pattern exactly: header, tabs with counters, panels and tables.
  Say in the reply which one you followed.
- Search the design-system catalog per widget (calendar, timeline, tree, stepper, number field,
  toggle group, upload) before composing from primitives. Install the module or write down why not
  (financeiro C1, C11).
- Mirror the sibling modules Pedro treats as the bar, which each project names in its
  `docs/design/prototyping.md`.
  Adapt them, don't copy them ("não é pra só copiar e colar", automacoes).
- Allow minimal production changes, such as a prop, a slot or a container fix, and fix a shared
  component at its root when the bug is there. A brief that forbids touching production forces
  hand-made substitutes (always-on, admitted by the conductor).
- Never copy helpers locally to get around a guard. If a guard blocks a pure module the app already
  ships, propose narrowing the guard and tell Pedro early (financeiro).

## Density and spacing

Density is the most repeated complaint in every spec: "apertado", "tudo pequeno/compactado", "não
tem space suficiente", "spacing mal feito", "jogado de qualquer jeito".

- Roomy is the default. Use one spacing scale with an 8 px rhythm. Section headers get breathing
  room.
- Data-table rows are about 56–64 px with 20 px side padding. List and link rows inside dialogs are
  40–44 px. Numbers are tabular and right-aligned.
- Never shrink type to make things fit. Scroll inside the card, fold finished items ("Concluídos
  (n)"), or paginate.
- Long secondary sections (activity, development, advanced) collapse. They open by default when
  they have content and stay closed with a count when they hold history. A collapsed section shows
  icon, title and a summary on the right. Use tabs when sections are peers.
- Explanatory text goes into a `(?)` tooltip with the same icon everywhere. Inline callouts are
  only for blocking information. A warning is an indented yellow note inside the card, with no
  alert border.
- Fix density as a class: define the roomy table or list once and apply it to every instance. When
  Pedro comments one table, he means all of them ("rever isso em todos os lugares", financeiro C15).

## Calm surfaces and color

- One surface per area, at most two nesting levels (card plus flat body). Separate with dividers,
  not more boxes. "Card dentro do card, dentro do card" was rejected in campanhas, financeiro and
  automacoes.
- Borders only when they do a job. Neutral by default. Red only for negatives and errors. Chips
  only when there is a category to tell apart; a plain status is text.
- Selected or current is neutral gray (foreground at about 15%), never a green accent tint. It must
  contrast clearly with unselected in both themes (tarefas-1, automacoes u16).
- Attention states mark and sort. A small icon plus sort-first is enough. No full-row red
  background and no large ring around the avatar (always-on).
- Archived or read-only objects get a notice on top, and the rest drops to reduced opacity and
  becomes inert. Restore stays at full opacity (tarefas-dev 04-3).

## Layout and viewports

- Pedro reviews in dark at about 1396×693 on a laptop and at 2084–2560 px on large screens. Design
  for both. A single stretched column on a wide screen gets commented.
- Use `@container`: two columns (main plus side) from about `@4xl`, and a reading column that grows
  (760/880/1040 px). Card grids go 1 / 2 (≥672 px) / 3 (≥1024 px) by container width.
- Side columns, samples and lists inside panels get a max height, internal scroll and a sticky
  header. Test them with 20+ items (campanhas-publicos-1).
- Dialogs respond to content: set a defined width, `min-w-0` on grid columns, internal scroll and
  bottom padding. Expand every "Advanced" section and scroll to the end (financeiro C13, always-on).

## Scale and data

- Design for volume from the first state:
  - 1,000+ rows with pagination (design the paginator);
  - 50 projects (searchable picker, never one select per project);
  - 100 agents (load more);
  - long names, one full column next to an empty one.
- Fixtures are realistic and agree across screens: totals add up, the same count shows on every
  screen, and dates are not in the past for "draft" things. Use thousand separators, outliers and
  plausible magnitudes ("150 mil, não milhões"), and make charts survive an outlier.
- Use real sources when they exist: the model catalog with per-model reasoning levels, error codes
  and copy from the spec or `_dx.md`, and avatar photos rather than initials. Initials in a
  prototype hid a missing-photo bug in tarefas.
- When a value is invented (limits, ranges), mark it as a question for Pedro rather than presenting
  it as fact. Show where data comes from (webhook, CRM, site) when he would ask "da onde vem isso?".

## Lists, filters and bars

- Every list toolbar has entity filters: chips with icons, nested property submenus that open
  without closing, per-property counts, "Limpar filtros", a no-results state and URL params. Linear
  is the interaction reference.
- An overloaded bar keeps the title or period plus 2–3 controls. Counts, grouping, "show done" and
  the legend move into a well-formatted "Exibição" popover (shortcut V), and the decision applies to
  every similar bar.
- Clicking a milestone or facet filters the list and shows "Limpar filtro" next to it, with a
  removable chip in the list.
- Section navigation of an object (team, board, project) is a sidebar toggle with icons, not header
  tabs. Personal boards and teams are separate groups.

## Forms and editing

- One screen, not a wizard, unless the steps are independent. A five-step wizard was "PÉSSIMO,
  burocrático" (always-on). Use sensible defaults, one obvious action, and advanced options behind a
  quiet disclosure.
- Design each form field on its own from the kit's primitives (number field, toggle group with
  icons, segmented control, slider with limit) instead of a column of text inputs.
- Edit a few fields (name, description, avatar) inline in the header, not in a drawer. Long content
  (markdown, skill files) opens in its own modal with a file tree; it never blows up inline.
- When a setting depends on an external entity, let the user link it right there (add repository or
  project) instead of sending them to the other system (tarefas-dev 07-1).

## Language

- Write for a non-technical user ("prova de ignorante"). No implementation words in the UI:
  runtime, provider, persona, scope, heartbeat, slug, instance. Show instead of explain (a live
  preview).
- Use the product language with sentence case, and keep its fixed terms (listed in the project's prototyping notes).

## Marks, icons and empty states

- A company, integration or model provider shows its colored logo everywhere it is named: lists,
  connections, triggers, steps, tool calls, model picker and empty states. Use one central component
  for this (automacoes u13).
- First-use and empty screens are visual (logo orbit, marquee, recipes), not text and a button.
- Icons come from the app's icon set and mean one thing each. No sparkle icon for "decision".

## Interaction

- Clicks work. Navigation between states uses the shared helper (`goToState`, `setParam` per the
  `proto` skill), not a URL change that renders nothing. Nobody had clicked always-on v1 before it
  was called done.
- Hover, focus and keyboard work. Sequence keys (`g i`) beat screen shortcuts. Esc closes only the
  innermost layer. No permanent `role=listbox/menu` outside overlays.
- Watch for content that jumps on click, panels that cannot scroll, dialogs over drawers without a
  dark overlay, and a dragged card that disappears.
- Pedro prefers drill-down to hover-only reveals for important data.

## Applying a comment

- Read the comment as a pattern. Find every screen with the same structure and fix them all.
- If the comment says the screen ignores the product's pattern, open that production screen first.
- If it changes behavior (a new capability, linking an entity, a protocol version), update the
  spec, `_uiux.md`, the ADRs or Q list, the stories and the tests, not only the draft.
- Reply in the thread with the file, what changed, and a screenshot at the comment's viewport and
  theme. Then resolve the thread. Approval belongs to Pedro.
