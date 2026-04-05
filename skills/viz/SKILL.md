---
name: viz
description: Transforms content (URLs, uploaded documents, pasted text, meeting transcripts) into professional visualizations across four output modes. Accepts a mode argument or a keyword trigger in the user message. Mode "diagram" produces an Excalidraw diagram via Excalidraw:create_view. Mode "infographic" generates a Swiss Pulse PNG via the Gemini image-generation API. Mode "visualize" renders an inline Visualizer widget (SVG or HTML) via visualize:show_widget. Mode "publish" ships an interactive Swiss Pulse HTML visual to HeyGenverse via HeyGenverse:create_app and returns a shareable link. Keywords that activate the skill: "diagram it", "excalidraw this", "draw a diagram of this", "nano this", "vis it", "ver it", "hey it", "heygenverse this". Do not use for plain-text summaries, code explanations, prose responses, or generic chat visualizations without a chosen output format.
argument-hint: <diagram|infographic|visualize|publish> [content-or-url]
---

# Viz Pack — Multi-Mode Visual Dispatcher

Transform any content into a professional visualization via one of four output modes. This skill is a dispatcher: it resolves the active mode, loads the mode-specific workflow from `references/`, and executes it.

## Step 1: Resolve the active mode

Inspect the invocation in this priority order:

1. **Positional argument.** The first positional argument is `$0`. If `$0` matches `diagram`, `infographic`, `visualize`, or `publish`, use it as the mode. Remaining arguments (`$ARGUMENTS` after the mode token) are the optional content reference (URL, file path, or inline text).

2. **Keyword trigger.** If `$0` is empty or not a valid mode, scan the most recent user message for a trigger keyword and map it to a mode:

   | Trigger keyword(s)                                                            | Mode          |
   | ----------------------------------------------------------------------------- | ------------- |
   | "diagram it", "excalidraw this", "draw a diagram of this"                     | `diagram`     |
   | "nano this"                                                                   | `infographic` |
   | "vis it"                                                                      | `visualize`   |
   | "ver it", "hey it", "heygenverse this", "put this on heygenverse as a visual" | `publish`     |

3. **Ask the user.** If neither signal yields a mode, stop and ask which output to produce — `diagram` (Excalidraw), `infographic` (Swiss Pulse PNG via Gemini), `visualize` (inline Visualizer widget), or `publish` (interactive Swiss Pulse app on HeyGenverse). Do not guess.

Invocation context injected at render time: mode token is `$0`, content reference is `$ARGUMENTS`.

## Step 2: Load the mode workflow

Read the reference file for the resolved mode and follow its workflow end-to-end:

| Mode          | Workflow file                    |
| ------------- | -------------------------------- |
| `diagram`     | `references/mode-diagram.md`     |
| `infographic` | `references/mode-infographic.md` |
| `visualize`   | `references/mode-visualize.md`   |
| `publish`     | `references/mode-publish.md`     |

Read the file on every invocation — do not execute from memory — so any updates to the workflow are applied.

## Step 3: Acquire the content (shared across modes)

All four modes accept content from the same sources. Resolve the content target in this priority order:

1. If `$ARGUMENTS` contains a URL → retrieve via `web_fetch`. If blocked (429/403), fall back to `web_search` with key phrases to get the content from search snippets.
2. If `$ARGUMENTS` points to an uploaded file → read from `/mnt/user-data/uploads/` using `pdfplumber` for PDF, `python-docx` for DOCX, `pandas` for CSV/TSV, direct read for TXT/MD/HTML.
3. If `$ARGUMENTS` is inline text → use it directly.
4. Else scan the current conversation for a referenced source (uploaded file, URL previously shared, meeting transcript at `/mnt/transcripts/`, pasted text) and use that.

Summarize to core structure if the content exceeds 3,000 words for modes that pipe text into an LLM (`infographic`) or 5,000 words for modes that assemble visuals client-side (`diagram`, `visualize`, `publish`).

## Step 4: Execute the loaded workflow

Follow the steps in the loaded workflow file exactly. Do not substitute tools, colors, typography, or output formats across modes.

## Non-Negotiable Rules

- Never respond with a plain-text summary instead of the requested visual output.
- Never swap output format across modes (e.g., do not emit Excalidraw when `mode=publish` was requested).
- Never skip reading the mode-specific workflow file — every mode has non-obvious tool contracts and design constraints.
- Never use colors outside each mode's palette (Excalidraw: 2–3 neutrals; Swiss Pulse modes: black/white + #0066FF only).

## Error Handling

- **Mode unresolved** → execute Step 1.3 and ask the user.
- **Missing workflow file** → stop and report the missing path (`references/mode-<mode>.md`).
- **Missing tool integration** (`Excalidraw:*`, `visualize:*`, `HeyGenverse:*`) → report the specific missing integration and ask whether to proceed with an alternative mode.
- **Missing `GEMINI_API_KEY`** (mode `infographic` only) → stop and ask for the key before continuing.
- **Content acquisition fails** (empty, unreadable, blocked URL) → report the specific failure and request a different source.
