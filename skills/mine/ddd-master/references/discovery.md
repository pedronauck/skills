# Grasp the domain

Load when Step 2 runs, or when the user named EventStorming, "what happens," or a missing event timeline. Workshop catalogs live here; the agent-runnable sequence stays in `SKILL.md`.

## Skip / swap gate

**Discovery cannot be skipped.** EventStorming-the-tool can.

| Situation | Action |
| --- | --- |
| No trusted timeline; greenfield kickoff, brownfield discovery, multi-team program, alignment, or reteaming | Run Step 2 (EventStorming or an agent-synthesised timeline) |
| Recent EventStorm, Domain Storytelling, or Example Mapping exists | Keep that timeline; jump to the subdomain carve |
| User asked for Software Design EventStorming | Refuse the format — official mechanics are unfinished in the source corpus |
| Remote Big Picture from a template alone | Refuse; Big Picture needs facilitation, not a board file |

EventStorming is not a UML diagram, design doc, or deployment plan. A finished wall is a knowledge snapshot, not a spec.

## Family of formats

| Format | Job | Default for this skill? |
| --- | --- | --- |
| **Big Picture** | Whole line of business; candidate contexts; language collisions; core and bottleneck candidates | Yes — events-first discovery |
| **Process Modelling** | Shared notation for business + tech + UX | Only when Connect/flow is the ask |
| **Software Design** | Same flow plus moving parts and a stricter grammar | No — book incomplete; 90-minute kits exclude it |

Brandolini purposes (Improve / Envision / Explore / Design) are *why* a room gathers. They do not change the agent sequence.

Official spelling: **EventStorming** (one word).

## Colour legend (v1 freeze)

| Colour | Artifact | Tense / form |
| --- | --- | --- |
| Orange | Domain event | Past tense; prefer a sentence ("A product was added to a basket") |
| Blue | Command | Present tense; sits immediately before its event |
| (actor note) | Actor or external system | Who executes the command |
| Red | Hotspot | Gap, conflict, money path, missing role |
| Yellow | Aggregate *candidate* | Only if the user asked for software-design depth |

Views, errors, and Lucidchart "reactions" stay optional. Dual-visualise a disagreement — two notes, not a winner.

## What the agent does vs fakes

The agent **synthesises** a timeline from stakeholder text, handlers, event types, and logs, and **labels** uncertainty.

The agent **does not** claim it facilitated Big Picture. Humans own: 6–30 people in a room, infinite wall, live argument, "do both parties feel represented," throw-away-and-redo with other stakeholders, confirming language in experts' mouths.

The agent **may** brief a facilitator and **may** seed the wall with a first-pass event list from code.

Incompleteness is normal. Move on with hotspots. A complete model is not the *Done when:*.

## Facilitation invariants (for a human room)

Hang the first sticky. Guide; do not model. Ask: something missing; how this makes money; how the business evaluates success; for whom this event matters; whether a silent role should be in the room. Reverse time once. Interrupt long discussions; visualise both opinions. Timebox; after each box, move phase (events → causality → boundaries) even if the model feels incomplete. Photograph, then throw the model away and redo with other stakeholders when learning matters more than the artifact.

## Starter modelling backdrop

ddd-crew order (beginners' guide, *not* a linear SDLC): Understand → **Discover** → Decompose → Strategize → Connect → Organise → Define (Bounded Context Canvas) → Code (Aggregate Design Canvas).

This skill inlines Discover + the Decompose carve. Strategize / Connect / Define hand off to Step 3. Code hands off to Step 4.

Legal adaptations: start at Discover if the team models more easily than it strategises; on brownfield, start from the IT landscape; repeat Discover–Organise before Define.

Discovery events are business facts, not an event store.

## Core / generic / supporting during a storm

Ask "are we in the core?" as a hotspot if unanswered. Investment policy stays in Step 3 / `when-not.md`.
