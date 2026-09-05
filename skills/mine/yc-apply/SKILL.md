---
name: yc-apply
description: Prepare, review, and package Y Combinator application answers and founder-video notes using the live form and verified founder facts. Use for a YC application, requested interview practice, or reapplication; not general fundraising or unrelated decks.
disable-model-invocation: true
---

# YC Apply

Complete the requested application task using the founder's facts and the current YC form. Work can start with one answer, a review, video notes, a submission pack, or reapplication; it need not traverse every coaching phase.

## Workspace and context

Keep founder data in the separate workspace they chose. Resolve `--workspace`/`--resume`, `YC_APPLY_WORKSPACE`, or an existing `00_meta.md`; ask only when no unambiguous location is known. `<skill-dir>` is this skill's directory, not the workspace. Create the authorized workspace with `scripts/bootstrap-workspace.sh`; preserve existing files and resume instead of overwriting them.

Use the existing layout: `00_meta.md`, `01_form-spec.md`, founder/narrative notes, optional `04_research/`, `05_drafts/`, `06_video/`, `06_gate.md`, optional `07_interview/`, `08_final/`, and milestone journal. These are artifact locations, not prerequisites for every task. Legacy `--phase` numbers may select the corresponding task; they no longer impose a sequential gate.

Capture/verify the live form in `01_form-spec.md` for a full application or submission check. Bundled batch forms are dated snapshots, not current authority. A single-answer edit can use the supplied field and limit without a full form-research pass.

## Choose the work

- **Draft or improve answers:** reuse known facts, batch missing factual questions, and ask a focused follow-up for a consequential ambiguity. Start from a concrete draft when the founder requested drafting. Use matching `references/partner-signals.md`, `references/seven-pitch-questions.md`, and `references/accepted-examples.md` sections when helpful; no compulsory seven-question interview, score threshold, Email Test, or accepted-example quota.
- **Research:** investigate unresolved claims that affect the answer. Use applicable `assets/research-*.md` outlines and bounded native explorers only when independent questions justify them. No five-slice prerequisite. Record evidence and uncertainty; a legitimately inapplicable regulatory slice may be `N/A` without an invented URL.
- **Review:** apply the relevant `references/anti-patterns.md` guidance. `scripts/buzzword-scan.sh` suggests clarity candidates; a technical word is not itself a defect. No journal entry is required for every intentional word. Preserve truthful meaning, exact field limits, and the founder's voice.
- **Founder video:** read `references/video-spec.md` and verify current application instructions. Preserve its time/participant/content requirements; use concise talking notes by default. An explicit request for a script is sufficient authorization to draft one; explain the natural-delivery tradeoff without requiring a magic confirmation phrase.
- **Interview:** use `references/interview-playbook.md` for requested practice. Mark the actual interview stage only after a confirmed invite; practice does not imply an invitation. Choose drills for weak answers, with optional timers; no personality performance or fixed rehearsal quota.
- **Reapplication/post-mortem:** use `references/reapplicant-playbook.md` for confirmed changes since the prior application. Do not auto-launch a rejection interview or scaffold another batch unless requested.

## Packaging and submission readiness

For a requested final pack, collect the accepted answers in `08_final/SUBMIT.md` in current form order. Record the founder's review and the material readiness checks in `06_gate.md`:

```text
form_current: pass
required_fields_complete: pass
claims_verified: pass
video_conforms: pass
founder_reviewed: pass
```

Use `video_conforms: not_required` only when the current form truly requires no video. A missing/failed item remains an explicit gap; optional research, coaching, and scoring cannot block otherwise ready answers. `scripts/phase-status.sh <workspace> --submission` checks the record and artifacts; it cannot independently prove the truth of a founder claim or the live form's requirements.

The pack is for founder review/use. Actual submission, emails to others, uploads, or disclosure of transcripts require explicit authorization. Preserve existing authorization without asking twice. Never invent metrics, customers, evidence, founder consent, or successful submission. Inspect a selected coding transcript for private data and current upload limits before staging it; do not explore unrelated conversation history.

Use `scripts/journal-append.sh` for meaningful decisions/handoffs, not every answer or phase. `scripts/phase-status.sh <workspace>` is an advisory progress inventory, not an instruction to restart completed work. An optional `--strict` buzzword scan may support a specifically requested lexical audit; it is never proof of application quality.
