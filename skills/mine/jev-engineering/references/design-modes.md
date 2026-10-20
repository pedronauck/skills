# Designing with Jev: the three modes, the archetype, the POC

The naive picture is "send a sentence, get a label". Every serious use of Jev is one of three modes, or a combination, and the first design decision is which.

## Mode 1: the whole decision in one state, several questions in one call

`state` takes JSON up to 32k tokens. What goes in is the item **plus everything the decision needs to see**: the taxonomy with descriptions, the 20 neighbouring items with title and date, the list of open obligations, the goals, a table of candidates, a batch of items to judge together. On top of that, several questions in the same request: "which node?", "if none, which is closest?", "does it update one of the earlier items, and which?", "does it close an open obligation?", "does it advance a goal?".

Do not descend a tree level by level because "the list is long" when the list fits (a Choice takes up to 255 options and the state carries the descriptions); when it does not fit, use the hierarchical selection contract in `mechanisms.md`. Do not cap candidates at six out of fear of context, and do not treat "global" facts (chains, aggregates, open lists) as invisible when code can put exactly that into the state.

The limit that matters: everything the decision needs, **nothing it does not**. The docs say accuracy falls when the state grows with unrelated detail; in one integration 20 candidates sharing a state shifted probabilities by 0.12 on average. Filter in code first, and measure batch against single on a sample (see `state.md`).

## Mode 2: a question bank turns judgment into a number, a diagnosis or a selection

One text, hundreds of typed questions, each with its rubric, weight and dimension. Jev answers each with a probability; **code** aggregates into a score, a ranking, a diagnosis or a choice. The text is not classified; it is measured against an instrument. Examples of the shape: 334 criteria in 12 dimensions over a startup application; 21 editorial criteria plus 70 voice criteria over a generated script; 30 political-signal questions over a social post; a catalogue of code-review checks with literal counter-examples.

What it demands: questions independent of each other (they travel together), an explicit rubric per question (the model is literal), aggregation in code with a confidence gate and published coverage. Weights and thresholds are human calibration; without a labeled set the score is a diagnosis, not a measure.

## Mode 3: multi-stage classification with a state machine

One classification leads to the next. States and transitions are code, predicates are Jev, each state has its own gate and its own labeled set, and only survivors pay the expensive step. Shapes: triage → judge → relate → close over a chat export; screen → judge posts → group needs over a forum corpus; regime → sector → task over a regulatory feed; triage skill → evaluate items → follow-up round over a code diff. Compound error is why the gate per state matters (five steps at 90 % give 59 % end to end); calibrated probabilities are what make the chain viable.

## Combine them

The modes combine when the job needs it, and many jobs need only one. A memory assistant used all three: code assembles the slice that enters the state (mode 1), Jev answers nine questions per unit (mode 2), code stores the edges with the question hash and decides the next stage (mode 3). A tender screener needed only mode 2 in a single call. Add a mode when a measured gap asks for it, not by default.

## Checklist before designing anything with Jev

1. What am I sending in pieces that would fit whole in a 32k state?
2. Which bank of weighted questions would turn this judgment into a score, a ranking or a selection?
3. Which chain of gated stages avoids paying the expensive step for everything?
4. What is arithmetic, date, count or transition, and therefore code?
5. Where is the labeled set for each stage?
6. What in the state is a distractor, and what is an instruction disguised as data?

## Pick the closest archetype

`use-cases.md` catalogues the shapes that have been built: artifact evaluation loops, diagnostic banks, stream → units → relations, two-record fit, locate → classify → cite → verify, corpus atlases, rule packs for review, retrieval judges in hooks, signal streams with quantification, agent control loops, extraction by selection, feed → entity → task routing. Start from the one whose loop matches yours; borrow mechanisms from `mechanisms.md`; decide which tools carry the rest from `tooling.md`.

## A POC in a day

1. **One decision, one hundred items.** Pick the repeated judgment and a sample you can read yourself. Write the state builder for it (`state.md`).
2. **Five to thirty questions in a file.** Guard, polarity, abstention, criteria per option (`questions.md`). Version it.
3. **Run it with the skeleton.** `assets/poc_skeleton.py` runs a question map over a JSONL of items with cache and prints the table: distribution per question, mean confidence, cost, latency. Read the table before touching anything.
4. **Aggregate in code.** Score, tiers or routing (`aggregation-and-gates.md`). Keep raw answers; change thresholds without re-running.
5. **Label thirty items.** Compare. If a positive is missing, look at the vocabulary of the criteria and the state before touching a threshold. If a negative passes, add a counter-example to the criteria and a regression case.
6. **Write the numbers down** as what they are: one sample, one rubric version, one route. Cost per item, latency, coverage, what failed.

From POC to product is another discipline: `reliability.md` (statuses, budget, cache), `evaluation.md` (regression, gold, shadow), and the transport notes. Nothing in the POC has to change shape to get there if the state builder, the question file and the aggregation were already code.
