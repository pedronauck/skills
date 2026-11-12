---
name: tui-design
description: Use this skill when designing terminal user interfaces, creating TUI layouts, choosing TUI color schemes, implementing keyboard navigation, building terminal dashboards, or working with any TUI framework. Activates on mentions of TUI design, terminal UI, Ratatui layout, Ink components, Textual widgets, Bubbletea views, terminal color palette, keybinding design, panel layout, split panes, terminal dashboard, box-drawing characters, sparklines, progress bars, modal dialogs, focus management, or terminal accessibility.
---

# TUI Design System

Design around the user's repeated action, the data they must keep in view, and the terminal capabilities actually available. Keep input responsive under slow I/O and make selection, focus, and operation state explicit.

**Primary documentation checked: 2026-09-04.** Framework APIs change; use the project's versions. Follow the project's visual identity (SilkCircuit Neon for the maintainer's personal tools) rather than treating an example palette as a universal theme.

## Choose the Layout from the Work

| Work                                     | Layout                               | Useful invariant                                          |
| ---------------------------------------- | ------------------------------------ | --------------------------------------------------------- |
| Browse related lists and details         | Persistent multi-panel               | Stable panel roles and visible focus                      |
| Navigate a hierarchy                     | Miller columns or drill-down stack   | Back restores selection and scroll position               |
| Monitor changing measurements            | Widget dashboard                     | Labels, units, freshness, and a path to details           |
| Edit requests, queries, or configuration | Sidebar, editor, results             | Keep editing state when switching panels                  |
| Select a value for a shell command       | Inline picker or overlay             | Return a clean value and preserve shell scrollback        |
| Read logs or events                      | Fixed controls plus virtualized list | Follow mode is explicit; scrolling back stops auto-follow |

Read [app-patterns.md](references/app-patterns.md) for examples and tradeoffs. Read [visual-catalog.md](references/visual-catalog.md) only when selecting glyphs, borders, charts, or indicators.

### Responsive Behavior

Use constraints and content priorities. Keep the selected item visible while collapsing secondary panels; preserve state when they reappear. Recompute layout on resize without treating a zero-sized transient area as an error. Clamp scrolling after filtering, deletion, or a smaller viewport.

Test narrow, ordinary, and wide layouts, including rapid resizing. The minimum usable size follows the task; 80x24 is a useful test case, not permission to disable a picker that would work in 40 columns. A size message should retain quit and recovery input.

## Input, Focus, and Editing

| Concern             | Decision                                                                                 |
| ------------------- | ---------------------------------------------------------------------------------------- |
| Basic navigation    | Support arrows, Enter, Escape, and discoverable focus movement                           |
| Expert shortcuts    | Add vim motions or a command palette when they improve repeated work                     |
| Text fields         | Printable keys edit text; `q`, `j`, `/`, and mnemonic actions must not fire globally     |
| Multi-key shortcuts | Show pending context and resolve Escape/prefix ambiguity through the input library       |
| Modal dialog        | Route input only to the modal; restore the prior valid focus target when it closes       |
| Destructive action  | Show the exact target and consequence; choose confirmation proportional to reversibility |
| Mouse support       | Match keyboard actions and provide a way to disable capture for terminal text selection  |

Maintain one owner for input parsing. With Crossterm, do not mix `EventStream` with `read`/`poll`, or run competing readers. Handle key press, repeat, and release deliberately; one physical press must not submit twice.

Enhanced keyboard protocols can distinguish keys that legacy terminals encode identically. Negotiate support and retain usable fallback bindings. Never assume Ctrl+I differs from Tab or Ctrl+M from Enter everywhere. Treat bracketed paste as a text event; pasted newlines must not accidentally submit destructive commands.

Raw mode can disable the terminal's normal signal handling. Implement Ctrl+C and suspend/resume deliberately through the framework; do not assume the OS will handle them unchanged. Restore terminal state before handing control to an editor, pager, shell, or suspended process, then reacquire it and redraw.

Show a short footer for currently available actions and a contextual help view. Keep essential instructions visible while a task is running. Durable errors need a retrievable location; a disappearing toast cannot be the only record.

## State and Async Work

Separate input events, state transitions, effects, and rendering. Render a snapshot of state without starting network calls or mutating the domain model from a drawing function.

```dot
digraph tui_state {
    rankdir=LR;
    event -> update;
    update -> state;
    update -> effect;
    effect -> event [label="result + request identity"];
    state -> render;
}
```

| Failure mode                                          | Design response                                                                            |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Search A completes after search B                     | Tag requests and discard results that no longer match the active query                     |
| A row moves after a refresh                           | Track selection by stable identity, not only a row index                                   |
| A view closes while work runs                         | Cancel owned work or detach it deliberately; late results must not resurrect the view      |
| A cancelled write may already have reached the server | Distinguish cancelled waiting from confirmed rollback; reconcile remote state              |
| Logs arrive faster than screen updates                | Retain required events in the data layer and render a virtualized viewport                 |
| Work blocks the UI despite `async` syntax             | Identify blocking calls or CPU work and move them off the input/render path                |
| Repeated action would start duplicate writes          | Track pending operation identity and show its result before accepting a conflicting action |

Batch state updates and render changed frames. Coalesce replaceable visual snapshots, not audit events or mutations. Diagnose queue growth, indexing, and allocation costs before dropping data or capping concurrency.

## Terminal Capability Policy

Explicit application settings take precedence. In automatic mode, respect a non-empty `NO_COLOR` before color detection. A color override can opt back in deliberately; disabling color need not disable bold, underline, layout, or every terminal feature.

| Capability                    | Evidence and fallback                                                                                  |
| ----------------------------- | ------------------------------------------------------------------------------------------------------ |
| Interactive terminal          | Check the actual input/output TTYs; support plain output or explain the need for a TTY                 |
| True color                    | Use the library's detection, terminfo, or negotiated support; `COLORTERM` is a hint, not a requirement |
| 256/16 colors                 | Map semantic slots to supported colors and preserve labels and focus without hue                       |
| Images, hyperlinks, clipboard | Negotiate the protocol through multiplexers; provide a text or file alternative                        |
| Nerd Font icons               | Make them explicit or user-configurable; there is no portable reliable font-detection API              |
| Unicode layout                | Segment graphemes and measure terminal cell width; do not use byte or code-point length                |

Truncate only at grapheme boundaries, accounting for wide cells, combining marks, variation selectors, and emoji sequences. Width libraries and emulators can disagree; test representative user text and offer ASCII indicators where rendering is uncertain.

Treat filenames, logs, and remote strings as untrusted display data. Escape control sequences before writing them through raw output APIs; otherwise a displayed value can move the cursor, change a title, or invoke an OSC operation. Use the framework's supported text/sanitization path.

Terminal queries share the input stream with keystrokes. Let one parser correlate replies, limit waiting for unsupported queries, and choose a fallback without swallowing user input.

## Visual Hierarchy and Accessibility

Define semantic slots such as foreground, muted text, focus, selection, warning, and error. Keep theme values out of widget code. Use stable spacing and labels before introducing more borders. Provide dark and light variants when the application sets its own background; transparent/default backgrounds need testing against the user's theme.

Pair status colors with text or shape. Use focus indicators that survive monochrome mode, and avoid dimming important values until they become unreadable. WCAG's 4.5:1 normal-text contrast is a useful design target, but terminal font size and ANSI colors are user-controlled; a bold terminal heading does not automatically qualify for the large-text exception. Do not claim formal accessibility compliance from a palette alone.

Provide a plain or linear presentation when a full-screen interface defeats screen-reader navigation. Meaningful labels, keyboard access, and a non-animated mode still need testing with the intended terminal and assistive technology. Avoid blinking warnings or rapidly flashing status. Let users reduce motion; animation must not delay input or hide the final state.

## Rendering and Terminal Lifecycle

Use the framework's buffered rendering and cell diffing. Batch writes; use synchronized output only when supported and always pair begin/end even on errors. A single write is not proof of atomic rendering, and synchronized output is an enhancement rather than a prerequisite for a usable TUI.

Render on state changes or an active animation deadline. Measure input latency, output bandwidth, and redraw cost under the intended data rate, including SSH and multiplexers. Choose a refresh cadence for the actual workload; do not impose a universal FPS cap or artificially delay streamed text.

Acquire terminal modes through a scoped owner and restore everything the app enabled: raw mode, alternate screen, cursor visibility, mouse capture, bracketed paste, and keyboard protocol state. Cover normal exit, initialization failure, exceptions/panics, and handled signals. A framework restoration helper may cover only a subset; check its contract. SIGKILL cannot run cleanup.

## Verification That Changes Confidence

Use deterministic state-transition tests for selection after deletion, stale async results, modal focus restoration, and cancelled operations. Use the framework's test backend for layout boundaries; inspect at least one real PTY session because snapshots do not exercise terminal modes or input protocols.

Exercise launch, typing, paste, resize, modal open/close, slow or failed I/O, and exit. Include light/dark themes, color disabled, wide/combining text, and the actual supported terminal/multiplexer path. After exit, verify the shell cursor and echo behavior are restored. Expand the matrix when a portability requirement or failure justifies it.

## Anti-Patterns

| Anti-Pattern                                          | Better action                                                   |
| ----------------------------------------------------- | --------------------------------------------------------------- |
| `NO_COLOR` checked after true-color detection         | Resolve user preference before capability selection             |
| Global mnemonic shortcuts consume text input          | Route events through focus and active mode                      |
| Unicode release cutoff presented as compatibility     | Measure graphemes/cells and test supported emulators            |
| Async request completion overwrites newer state       | Correlate result identity with current view/query               |
| Screen clears or escape codes from background logging | Send logs through state or a separate sink                      |
| Lower FPS or concurrency hides an overloaded queue    | Profile the producer, state processing, and renderer separately |
| Only normal exit restores the terminal                | Use lifecycle guards and framework panic/signal handling        |

## Primary Sources

Reviewed 2026-09-04 and 2026-10-27; sources and their limits are in `references/evidence.md`.

The state-ownership and verification guidance is engineering synthesis from these contracts, not a claim that a protocol guarantees application correctness.

## What This Skill is NOT

- Not a framework API manual or a mandate to adopt a new toolkit.
- Not a reason to add animation, icons, or modes to a simple picker.
- Not a substitute for testing the actual terminal and accessibility path.
