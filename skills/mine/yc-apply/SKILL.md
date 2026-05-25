---
name: yc-apply
description: Guides a founder through the full Y Combinator batch application end-to-end. A 10-phase workflow that captures the live YC form, profiles the founders, stress-tests the idea via an embedded grill loop, runs a mandatory 5-agent parallel external research pass on the startup, drafts every form field with anti-pattern and accepted-example checks, produces founder-video bullet notes (no script), runs a final adversarial gate, generates paste-ready submission answers, unlocks an interview-prep simulator after invite, and supports reapplicant delta tracking and post-decision post-mortems. Writes a documented markdown trail under a user-chosen workspace. Use when a founder wants to prepare a YC batch application, build their founder video, drill mock YC interview questions, or reapply with delta evidence. Don't use for pitch-deck design unrelated to YC, generic startup advice without applying, or post-funding work.
---

# YC Apply

A founder-facing workflow that drives a Y Combinator batch application from blank workspace to paste-ready answers. The skill is the engine; the founder's data lives in a separate workspace they own and version. The body of this file is a dispatcher — load-bearing detail lives in `references/`. Inline content here is a tripwire, not the contract.

## Bundled Path Rule

Two distinct roots are in play and must never be confused:

- `<skill-dir>` — the directory that contains this `SKILL.md` (the bundled engine: `references/`, `assets/`, `scripts/`). Resolve it once at the start of a session (e.g. the absolute path of the directory holding this file).
- `<workspace>` — the founder's external application directory (resolved per the Invocation section). All founder data is written here.

Every `references/…`, `assets/…`, and `scripts/…` path in this file is **relative to `<skill-dir>`, never to `<workspace>` or the current working directory**. Because the agent often runs shell commands with the CWD set to `<workspace>`, always expand bundled helpers to an absolute path before invoking them: write `<skill-dir>/scripts/bootstrap-workspace.sh <workspace>`, not bare `scripts/bootstrap-workspace.sh`. The same applies to reading bundled files: read `<skill-dir>/references/partner-signals.md`. When a row or step below says `scripts/X` or `references/X`, treat it as `<skill-dir>/scripts/X` / `<skill-dir>/references/X`.

## Required Reading Router

Match the phase you are running to the row. Read the listed file in full **before** producing any output for that phase. The reference is load-bearing; the inline summaries in this SKILL.md are tripwires only.

| Phase / Trigger                                              | MUST read                                       |
| ------------------------------------------------------------ | ----------------------------------------------- |
| Any phase (background context on what YC partners look for)  | `references/partner-signals.md`                 |
| Phase 2 idea-stress-test, Phase 4 drafting any high-stakes field | `references/seven-pitch-questions.md`       |
| Phase 4 drafts of any field, Phase 6 final adversarial gate  | `references/anti-patterns.md`                   |
| Phase 4 drafting (every high-stakes field)                   | `references/accepted-examples.md`               |
| Phase 5 founder-video                                        | `references/video-spec.md`                      |
| Phase 8 interview-prep                                       | `references/interview-playbook.md`              |
| Phase 0 detects reapplicant, Phase 4 "what changed" draft, Phase 9 post-mortem | `references/reapplicant-playbook.md` |

## Reference Index

- `references/partner-signals.md` — what YC partners explicitly look for in written answers, the founder video, and the interview. The "20-second skim" reader model, the Dalton story-shape heuristic, Sam Altman's four evaluation questions.
- `references/seven-pitch-questions.md` — Michael Seibel's Seven Pitch Questions, Jared Friedman's Idea Quality Score, the Email Test. The pre-flight checklist every founder must pass before drafting.
- `references/anti-patterns.md` — buzzword list, Catherine Cross's 10-item "never say" list, behavioral red flags. Used by `scripts/buzzword-scan.sh` and by every grill loop.
- `references/accepted-examples.md` — verbatim accepted answers and videos: Anja Health W22, Embark Trucks W16, Hera (4-attempt case), Static EV (reapp case), Nalify S25, Razorpay. Reference rubric, never invent.
- `references/video-spec.md` — the founder-video rules (≤60s, all founders on camera, bullet notes not script, splice OK), full accepted-video transcripts.
- `references/interview-playbook.md` — 10-minute interview signals, inverted-pyramid rule, "I don't like your idea" adversarial probe, mock-interview format, demo-readiness, co-founder choreography.
- `references/reapplicant-playbook.md` — delta-doc pattern, how to surface "what changed since last application," explicit feedback-engagement rule.

## Invocation

Founder calls `/yc-apply` with optional flags. The skill autodetects state and resumes where it left off.

```
/yc-apply                            # autodetect: workspace + phase
/yc-apply --new                      # bootstrap fresh workspace
/yc-apply --workspace ~/apps/acme    # explicit path override
/yc-apply --phase 4                  # jump to phase
/yc-apply --resume ~/apps/acme       # resume specific workspace
/yc-apply --force-submit             # bypass Phase 6 gate (logs warning)
```

Workspace resolution order:
1. `--workspace` flag.
2. `$YC_APPLY_WORKSPACE` env var.
3. Current working directory if it contains `00_meta.md`.
4. Prompt the founder to choose: bootstrap new, resume by path, or cancel.

## Workspace Layout

The skill is the engine; the workspace is the artifact. The founder owns and may version the workspace. Bootstrap creates this exact tree.

```
<workspace>/
├── 00_meta.md                         # batch, deadline, company-slug, status
├── 01_form-spec.md                    # canonical form (operated on, never bundled)
├── 02_founder-profile.md              # founders, cool-things, hardest-built
├── 03_idea-narrative.md               # Seven Pitch Questions + Idea Quality Score + Email Test
├── 04_research/                       # 5-agent parallel external research
│   ├── 01_founder-footprint.md
│   ├── 02_competitive-landscape.md
│   ├── 03_market-tam.md
│   ├── 04_regulatory-context.md
│   ├── 05_traction-signals.md
│   └── summary.md
├── 04_reapplicant-delta.md            # only if Phase 0 marked reapplicant
├── 05_drafts/                         # one .md per form field, versioned
├── 06_video/
│   ├── notes.md                       # bullet talking notes (always)
│   └── script.md                      # only if founder explicitly opts in
├── 06_gate.md                         # Phase 6 result: the 10 checks + RESULT: PASS|FORCE-SUBMIT
├── 07_interview/                      # only after invite (Phase 8)
├── 08_final/                          # paste-ready locked answers
├── 09_journal.md                      # milestone log
└── 10_post-mortem.md                  # only after rejection (Phase 9)
```

## Phase Map

Ten phases, idempotent. The skill detects the current phase from workspace state via `<skill-dir>/scripts/phase-status.sh` and offers to resume there.

| # | Phase                | Definition of done                                                                                       |
|---|----------------------|----------------------------------------------------------------------------------------------------------|
| 0 | bootstrap            | Workspace exists; `00_meta.md` has real `batch`/`company_slug`/`target_deadline`/`reapplicant` values (no `{{}}`); `01_form-spec.md` captured. |
| 1 | founder-profile      | Every founder has cool-things + hardest-thing-built logged; no `{{}}` left; named versioned section; grill loops journaled. |
| 2 | idea-stress-test     | Seven Pitch Questions answered; numeric Idea Quality Score ≥6/10 avg w/ weakest dim addressed; Email Test logged.|
| 3 | external-research    | All 5 slice files + `04_research/summary.md` present; each slice has a Findings section and ≥1 real URL.  |
| 4 | drafts               | A draft per high-stakes field in `05_drafts/` (count ≥ `[HIGH]` fields); fields grilled; coding-agent session staged. |
| 5 | founder-video        | `06_video/notes.md` exists; estimated ≤60s; founders named with credentials.                            |
| 6 | pre-submit-gate      | `06_gate.md` written with all 10 boxes `[x]` and `RESULT: PASS` (or `FORCE-SUBMIT`); final adversarial grill logged. |
| 7 | submission-pack      | Gate passed; `08_final/SUBMIT.md` populated with paste-ready answers.                                    |
| 8 | interview-prep       | Unlocked only after operator confirms interview invite. Mock drills journaled.                          |
| 9 | post-mortem          | Auto-prompted after rejection; lessons + next-batch reapplicant scaffolding written.                    |

## Embedded Grill Loop

Phases 1, 2, 4 (high-stakes fields), and 6 all use the same relentless interview format. Run it as discrete rounds, one question at a time. Do not batch questions; do not move on until the round resolves.

Each round:
1. **Question** — one sharp, specific question targeting the weakest part of the current answer.
2. **Founder answer** — wait for it. Never answer on the founder's behalf.
3. **Critique** — name what is vague, unverifiable, buzzword-laden, or unsupported (cross-check `references/anti-patterns.md`).
4. **Recommendation** — propose a concrete sharper answer so the founder can react to a draft, not a void.
5. **Decision** — founder accepts, edits, or rejects. Record the resolved answer.

Stop conditions for a field/topic (all must hold):
- The first sentence passes the 20-second skim test (a reader reproduces the core claim from it alone).
- `<skill-dir>/scripts/buzzword-scan.sh` returns 0 hits on the draft, or each hit is journaled with a rationale.
- Every numeric or named-customer claim is defensible if Googled live.
- No adjective-only founder claims remain.

Cap a single field at ~6 rounds; if it has not converged, journal the sticking point and move on rather than looping forever. Log a one-line outcome per field via `<skill-dir>/scripts/journal-append.sh` (e.g. "Phase 4 competitors field resolved in 4 rounds").

## Procedures

### Step 1: Resolve workspace and detect phase

1. Resolve `<skill-dir>` (the directory containing this SKILL.md) per the Bundled Path Rule. Parse flags. If `--new`, run `<skill-dir>/scripts/bootstrap-workspace.sh <path>` (mutating helper) and proceed to Phase 0.
2. Otherwise, resolve workspace per the order above. If no candidate exists, ask the founder whether to bootstrap new, resume by path, or cancel — do not invent a default.
3. Run `<skill-dir>/scripts/phase-status.sh <workspace>` (read-only helper) and parse the current phase + completion checklist.
4. Announce the detected phase to the founder. Offer to resume there or override via `--phase`.

### Step 2: Phase 0 — Bootstrap

1. If `00_meta.md` does not exist, run `<skill-dir>/scripts/bootstrap-workspace.sh <workspace>` (mutating helper). It copies the `<skill-dir>/assets/template-*.md` files into the workspace and seeds `09_journal.md`.
2. Ask the founder for batch target (e.g., `S26`, `F26`), company-slug, target submission date. Write **real values** (no `{{PLACEHOLDER}}` left) into `00_meta.md` — `phase-status.sh` treats any remaining `{{` as "not done".
3. Ask: "Paste the live YC application form text from apply.ycombinator.com, OR confirm the bundled form spec for your batch is current." The live paste is the source of truth; the bundled spec is a fallback only. If confirmed, copy `<skill-dir>/assets/form-spec-summer-2026.md` (or the matching batch spec) to `<workspace>/01_form-spec.md`. If pasted, write the pasted text instead.
4. Ask: "Have you applied to YC before?" If yes, set `reapplicant: true` in `00_meta.md`, force paste of prior interview/rejection feedback, and create `04_reapplicant-delta.md`. **STOP. Read `references/reapplicant-playbook.md` in full before structuring the delta doc.**
5. Append milestone via `<skill-dir>/scripts/journal-append.sh <workspace> "Phase 0 bootstrap complete"` (mutating helper).

### Step 3: Phase 1 — Founder profile (embedded grill loop)

**STOP. Read `references/partner-signals.md` in full before opening the grill loop.** That file is the contract for what YC reads in founder bios — the inline tripwires below are not the source of truth.

Gist tripwires for what the grill must extract per founder:
- One specific verifiable achievement (artifact, not adjective). Reject "dedicated / passionate / driven."
- The single hardest intellectually difficult thing the founder has built. Cannot be the current startup itself.
- The non-resume hack story (if not in the live form, capture it anyway — useful for the narrative).
- Concrete role on the team + 2-3 line backstory.

Procedure:
1. For each founder, run a relentless one-question-at-a-time interview. After every answer, ask the next sharpest question. Always recommend an answer per question (do not leave the founder to guess your direction). Mirror the `grill-me` pattern in this workspace.
2. Reject any answer with only adjectives. Reject any "cool thing" that is the founder's role at a job — push for shipped artifacts.
3. Write the grilled output to `02_founder-profile.md`, one section per founder, versioned (`### Alex Doe — v3`).
4. Append milestone via `<skill-dir>/scripts/journal-append.sh`.

### Step 4: Phase 2 — Idea stress-test (embedded grill loop)

**STOP. Read `references/seven-pitch-questions.md` in full before opening the grill loop.** It contains the Seibel Seven Pitch Questions, Friedman's Idea Quality Score formula, and the Email Test gate. Do not paraphrase the framework — embed it.

Procedure:
1. Walk the founder through Seibel's seven questions one at a time, in order: (1) what do you do? (2) market size — bottom-up preferred? (3) progress? (4) unique insight? (5) business model? (6) team? (7) what do you want?
2. After each answer, run the grill: probe for vagueness, buzzwords, missing concrete nouns. Recommend a sharpened version.
3. Score the idea on Friedman's four criteria (market size, founder-market fit, problem confidence, unique insight). If average <6 or any dim <4, force the founder to either strengthen that dim or write a paragraph naming the weakness.
4. Run the Email Test: skill drafts a two-sentence pitch; founder must email it to a smart non-technical friend and paste the friend's paraphrase back. Skip is not allowed; if friend unavailable, founder pastes a written read-back of the pitch from a stranger they trust.
5. Write to `03_idea-narrative.md`.

### Step 5: Phase 3 — External research (MANDATORY 5 parallel subagents)

This phase is gated. Drafts (Phase 4) cannot begin until Phase 3 completes. Skip is not allowed.

1. Read each research prompt template `assets/research-*.md` — one per slice (`research-founder-footprint.md`, `research-competitive-landscape.md`, `research-market-tam.md`, `research-regulatory-context.md`, `research-traction-signals.md`).
2. Compose 5 slice prompts. Each prompt MUST embed:
   - The slice question and primary scope.
   - The exact target file path: `<workspace>/04_research/0N_<slug>.md`.
   - Forbidden write paths (anything outside `04_research/`).
   - The output schema (six sections: Findings, Verbatim Quotes, Signal Strength, Risks, Open Questions, Evidence URLs).
3. **Dispatch all five Agent tool calls in a SINGLE message** (parallel by default in Claude Code). Use `subagent_type=general-purpose` for each. Wait for every call to complete. If the harness exposes no parallel Agent facility, fall back to running the five sequentially — never skip a slice.
4. **Web-tool fallback:** the slice prompts assume `WebSearch` + `WebFetch` are available. If a subagent reports those tools are unavailable, it must still write its file using what it can find (founder-provided links, local context), mark the gaps under Open Questions, and never fabricate URLs. A slice with zero real URLs fails validation (next step) and is re-dispatched or flagged to the founder.
5. Verify each output exists, contains all six sections, and cites at least one real URL (`<skill-dir>/scripts/phase-status.sh <workspace>` confirms the Phase 3 invariant mechanically). Re-dispatch any slice that failed validation.
6. Synthesize `04_research/summary.md` parent-authored. Sections: Research Question, Slice Findings (one per agent), Convergences, Divergences, Risks & Open Questions, Recommended Next Steps for the application.
7. Append milestone via `<skill-dir>/scripts/journal-append.sh`.

### Step 6: Phase 4 — Drafts (per-field grill loop for high-stakes fields)

**STOP. Read `references/accepted-examples.md` and `references/anti-patterns.md` in full before opening any draft loop.** Examples seed the founder's mental model; anti-patterns drive the rewrite gate. Inline tripwires below are not substitutes.

Gist tripwires the per-field loop must enforce:
- First sentence carries full informational load (Graham's 20-sec skim test).
- No buzzwords. No "platform" / "AI-powered" / "revolutionizing" / "leveraging" / "ecosystem" / "no competitors" / "in stealth" / "need funding to start" / "some users."
- No adjectives without verifiable artifacts.
- Inverted-pyramid structure: conclusion first, proof after.

High-stakes fields (run full grill loop on each):
- 50-character company description.
- "What is your company going to make?" (3-sentence template from `accepted-examples.md`).
- Founder bios (one per founder).
- "Why did you pick this idea?" / domain expertise.
- "Who are your competitors? What do you understand that they don't?"
- "How will you make money?" with bottom-up TAM.
- "Other ideas you considered."
- (Reapplicant only) "What changed since last application?"

Low-stakes fields (skip grill, just validate):
- Yes/no boxes (cofounder search, revenue, users, fundraising, legal entity).
- Location (use the post-YC city format).
- Tech stack (require: include AI models + AI coding tools per the S26 form).
- Company URL, demo URL, login credentials.

Per-field procedure:
1. Read field intent from `references/partner-signals.md` + accepted examples from `references/accepted-examples.md`.
2. Present the question to the founder verbatim from `01_form-spec.md`.
3. Surface 2-3 verbatim accepted examples from the matching field.
4. Founder writes first draft.
5. Run `<skill-dir>/scripts/buzzword-scan.sh <draft-file>` (read-only helper). For every hit, present the bad → good rewrite pair from `references/anti-patterns.md`.
6. Run the embedded grill loop: one adversarial question at a time, with a recommended answer; tighten the draft each round.
7. When draft passes both the buzzword scan and the grill, save versioned in `05_drafts/<field>.md`.

Coding-agent session sub-step (Summer 2026 experimental field):
1. Ask the founder where coding-agent transcripts live (e.g., `~/.claude/projects/`, cursor exports). Optionally glob to list candidates with size + date.
2. Score top 3 candidates on: technical complexity, ownership demonstration, problem-solving narrative, real product progress. Surface scores; founder picks one.
3. Validate: ≤25 MB, `.md` or `.txt`. If oversize, ask the founder to trim or pick another.
4. Skill drafts a one-paragraph context blurb (what the problem was, what the transcript demonstrates). Stage selected file + blurb in `05_drafts/coding-session/`.

### Step 7: Phase 5 — Founder video

**STOP. Read `references/video-spec.md` in full before producing notes or a script.** It contains the ≤60s rule, the "all founders on camera" rule, the anti-script doctrine, and full accepted-video transcripts (Anja Health W22, Embark Trucks W16).

1. Compose bullet talking notes per founder (3-5 bullets each: name + 2-3 credential anchors + one traction stat or insight). Total budget ≤60s.
2. Show estimated speaking duration per bullet (~3 seconds per bullet by default).
3. Write to `06_video/notes.md`.
4. If — and only if — the founder explicitly opts in by saying "yes, draft a script for me," produce `06_video/script.md` with a strong header warning that reading verbatim is a YC anti-pattern (cite `video-spec.md`).
5. Refuse to produce a script otherwise, even on indirect requests.

### Step 8: Phase 6 — Pre-submit adversarial gate (10-check)

**STOP. Read `references/anti-patterns.md` and `references/partner-signals.md` in full before opening the final grill.** This phase is the last filter before paste-ready answers; it must combine the buzzword scan, the story compile, and the partner-style adversarial probes.

The 10-check gate. ALL must pass to unlock Phase 7. The result is recorded in a real artifact, `<workspace>/06_gate.md`, which `phase-status.sh` reads — a check is not "done" until it is recorded there.

Procedure:
1. Run each check below against the workspace. Several have a deterministic helper: run `<skill-dir>/scripts/buzzword-scan.sh <workspace>/05_drafts` for check 7 and re-run `<skill-dir>/scripts/phase-status.sh <workspace>` to confirm checks 1-6/9 mechanically.
2. Write `<workspace>/06_gate.md` containing the checklist below with each box marked `[x]` only when its evidence exists, plus a final line `RESULT: PASS` when all ten are `[x]`. Leave unchecked boxes `[ ]` for any that fail — `phase-status.sh` treats any remaining `[ ]` as "gate not passed".
3. If the founder invokes `--force-submit` with unmet checks, still write `06_gate.md` but mark the final line `RESULT: FORCE-SUBMIT`, list the unmet checks explicitly, and append a warning to `09_journal.md` via the journal helper.

```
[ ]  1. 01_form-spec.md exists and is current.
[ ]  2. 02_founder-profile.md complete: cool-things + hardest-built per founder.
[ ]  3. 03_idea-narrative.md: Idea Quality Score ≥6 avg AND weakest dim addressed in writing.
[ ]  4. Email Test paraphrase logged in 09_journal.md (with friend's paraphrase verbatim).
[ ]  5. 04_research/summary.md exists; 5 slice files present; each cites ≥1 real URL.
[ ]  6. Every high-stakes form field from 01_form-spec.md has a draft in 05_drafts/.
[ ]  7. scripts/buzzword-scan.sh returns 0 hits across 05_drafts/ OR every hit has a journaled rationale.
[ ]  8. Dalton-story compile passes: skill writes "This is the story of N founders, who X, working on Y for Z, currently at W, because V." Founder confirms the story is accurate from the drafts alone.
[ ]  9. 06_video/notes.md exists; ≤60s estimate; all founders named with credentials; demo content absent.
[ ] 10. Phase 6 final adversarial grill logged in 09_journal.md. Drills must include: "I don't like your idea, what else have you got?" probe response; "What's the single biggest current risk?" probe response; and one numeric claim fact-check.
RESULT: PASS|FORCE-SUBMIT
```

Final adversarial grill: walk the founder through Sam Altman's four-question filter (see `references/partner-signals.md`) and the "I don't like your idea" probe. Score the responses for formidable-but-not-defensive posture. If any answer is robotic, scripted, or denies all challenges, force a rewrite.

### Step 9: Phase 7 — Submission pack

1. **Refuse to enter Phase 7 unless `<workspace>/06_gate.md` exists with `RESULT: PASS` (or `RESULT: FORCE-SUBMIT`).** Confirm via `<skill-dir>/scripts/phase-status.sh <workspace>` showing Phase 6 checked. If the gate is unmet, return to Phase 6.
2. Read every `05_drafts/<field>.md`. For each field, copy the final version (last `### v`) to `08_final/<field>.md`.
3. Generate `08_final/SUBMIT.md` — a single document with each form field heading + the paste-ready answer underneath, in the exact order from `01_form-spec.md`. The founder pastes from here into apply.ycombinator.com.
4. Append milestone via `<skill-dir>/scripts/journal-append.sh`.

### Step 10: Phase 8 — Interview prep (only after invite)

Refuse to enter Phase 8 unless `00_meta.md` has `interview_invited: true` written by the founder.

**STOP. Read `references/interview-playbook.md` in full before running drills.** It contains the 10-minute interview signals, the inverted-pyramid 10-second rule, the "I don't like your idea" probe simulator, co-founder choreography, demo-readiness mandates, and "what not to say" lines.

Run, in order:
1. The 5-question rapid-fire drill (10-second visible timer per answer): what are you building, what's your progress, what's your unique insight, how will you get the first 1000 customers, who are your competitors and why are you different.
2. The "I don't like your idea, what else have you got?" probe simulator. Score the response: zero defensiveness, genuine curiosity ("why do you think it won't work?"), credible alternative on tap.
3. Co-founder choreography check: enforce written pre-division of questions by area (CEO: business/market; CTO: technical/team), no interruptions, no real-time contradictions.
4. Metric cheat-sheet generator: list every numeric claim in the application; for each, the source/verification (partners may Google-check live).
5. Demo-readiness check (24h before): "Is the product loaded in a browser tab? Can you screen-share in <10s if asked?"
6. Send a pre-interview note: "Walk in with a real smile and full attention. Partners read earnest energy as positive; flat scripted energy as negative."

Save all drill outputs to `07_interview/`.

### Step 11: Phase 9 — Post-mortem (auto-prompt on rejection)

If `00_meta.md` has `decision: rejected`, the next `/yc-apply` invocation auto-opens Phase 9. If `decision: accepted`, Phase 9 is skipped.

1. Ask the founder to paste the rejection feedback verbatim.
2. Walk the lessons: what did partners flag? What is unaddressable? What is addressable in the next 3 months?
3. Build `10_post-mortem.md` and seed a `04_reapplicant-delta.md` for the next batch (which the next workspace's Phase 0 will inherit).

## Gist tripwires (operating-level)

These tripwires are not the contract; the references are. If any tripwire fires, follow the STOP directive for that phase before continuing.

- **Skim test.** Each first sentence in `05_drafts/*.md` must let a reader reproduce the answer's core claim. If not, rewrite.
- **Buzzword scan.** `scripts/buzzword-scan.sh` returns 0 hits or every hit is journaled with rationale.
- **Story compile.** The Dalton story must be reconstructable from the drafts alone. If not, the founder has not told a story yet.
- **Honesty audit.** Every numeric or named-customer claim is defensible if a partner Googles it on the call.
- **Anti-script doctrine.** Founder video stays as bullets. Script only on explicit opt-in with warning.

## Anti-patterns

Behaviors the skill must refuse, regardless of founder pressure:

- Writing a verbatim founder-video script without an explicit opt-in.
- Submitting drafts (Phase 7) without Phase 3 external research complete.
- Bypassing the buzzword scan or fabricating its result.
- Producing application answers without surfacing accepted examples from `references/accepted-examples.md`.
- Coaching personality, "earnestness," or "banana mindset" — those are interview-room signals a written tool cannot reliably train.
- Cold-outreach to YC partners. The only documented exception is a recommendation from a YC-portfolio-company founder (see `partner-signals.md`).
- Recommending another accelerator as a path into YC.

## When NOT to use

- Pitch-deck design unrelated to a YC application — use a dedicated deck skill.
- Generic startup advice without the founder intending to apply.
- Post-Series-A fundraising or hiring work.
- AI tools / models comparison without a YC application context.

## Error Handling

- **Workspace ambiguous (no clear candidate):** ask the founder explicitly; never assume current directory.
- **`scripts/bootstrap-workspace.sh` fails on permission or existing files:** report the error and ask whether to overwrite, choose another path, or abort.
- **A subagent in Phase 3 returns malformed output:** re-dispatch only that slice with stricter instructions; never synthesize the missing slice.
- **`scripts/buzzword-scan.sh` returns hits the founder insists are intentional:** require a one-line rationale in `09_journal.md` per hit; never silently allow.
- **Phase 6 gate fails:** write `06_gate.md` with the failing checks left as `[ ]` and no `RESULT: PASS`; refuse to enter Phase 7. Only `--force-submit` (recorded as `RESULT: FORCE-SUBMIT` + a journal warning) bypasses it.
- **Coding-agent session export oversize (>25 MB):** ask the founder to trim or pick another file; do not attempt to compress automatically.
- **Live YC form differs significantly from bundled spec:** trust the paste, not the bundle; warn the founder and update `01_form-spec.md` from the paste.
