---
name: ddd-master
description: "Assess DDD fit; discover domains with EventStorming, define language and bounded contexts, and design aggregates, value objects, events, and repositories. Excludes architecture-only audits, product specs, and CQRS/Event Sourcing catalogs."
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---

# DDD Master

Predictable process for applying **DDD**: verdict first, then grasp what happens, lock language and **bounded contexts**, then design one **aggregate** at a time.

Use the branch covering the changed model or decision. Reuse established language, context maps, and timelines; read adjacent references only when the change crosses their boundaries.

## Bundled Path Rule

Resolve bundled files relative to the directory that holds this `SKILL.md`. A path written `references/<name>` expands to `<ddd-master-dir>/references/<name>`.

## Branches

| When the task involves… | Read **in full** |
| --- | --- |
| Refusing DDD, anemic models, transaction script, slogan folders, CRUD, or legacy rewrite | `references/when-not.md` |
| EventStorming, event timelines, or grasping what happens before contexts exist | `references/discovery.md` |
| Ubiquitous language, subdomains, bounded contexts, context map, or context relationships | `references/strategic.md` |
| Aggregates, value objects, domain events, repositories, factories, or invariants | `references/tactical.md` |
| Rule density, repository FAQ, or Branas/Elemar practitioner checks | `references/practitioner.md` |
| CQRS-by-default, copying a "DDD" repo, LLM-generated aggregates, or model/code drift | `references/pitfalls.md` |

For a new or redesigned model, work through the relevant discovery, strategic, and tactical decisions. A narrow change inside an established context needs only its affected invariants and consumers. Downgrade-to-layers can use `architectural-analysis` when a structural audit is requested.

## Floor

1. Ground new context boundaries in the organization's knowledge areas; reuse the established map for local changes.
2. Treat **subdomain**, **bounded context**, and deployable as three objects.
3. One transaction updates one aggregate; other aggregates appear as identities.
4. Place every **invariant** on the root, value object, or domain service; repository methods only load, save, and search.
5. Register a past-tense **domain event** after a successful command; publish it after persist.
6. Treat a language change as a model change.

## Step 1: Verdict

Classify new or redesigned models before scaffolding. For a focused question or local fix, give the relevant rationale without a six-tag report.

1. Tag essential complexity (multi-step invariants that change together) or write "CRUD + syntax only."
2. Tag the subdomain **core**, supporting, or generic.
3. Flag slogan DDD: Evans vocabulary or layer folders without a collaboratively evolved model of rules.
4. If objects are data bags and services own the rules, name **transaction script** (or operations-over-records). Keep the DDD label off that design.
5. If the change sits inside a ball of mud, pick Bubble, Autonomous Bubble, or Open-host-over-ACL — when the request is a legacy rewrite, read `references/when-not.md` in full before choosing.
6. Tag each rule syntax, semantic, or production. Syntax may stay in the UI; semantic and production rules earn a model owner only on Proceed.

Record **Refuse**, **Downgrade**, or **Proceed**.

*Done when:* one verdict is written with the six tags above; Refuse and Downgrade emit no aggregate or repository types.

## Step 2: Grasp the domain

Run when the verdict is Proceed and no trusted event timeline exists. When the user asked for EventStorming or "what happens," read `references/discovery.md` in full.

1. List who knows the questions (code, APIs, logs) and who knows the answers (named humans). Absent answerers become a hotspot.
2. Hang past-tense domain events on one unbounded timeline. Prefer sentence names.
3. Sequence in time; walk backward from the end once; mark gaps as red hotspots.
4. Place a present-tense command and an actor immediately before each event, or a hotspot when the cause is unknown.
5. Dual-visualise disagreements. Ask money path, success metric, and missing-role questions; leave a hotspot when the answer is unknown.
6. Stop after events, commands, and hotspots unless the user asked for software-design depth. Yellow notes are aggregate *candidates* — Step 4 owns their rules.
7. Carve loosely coupled subdomain cuts and hand relationship types to Step 3.

Skip the workshop *tool* when a recent EventStorm, Domain Storytelling, or Example Mapping already exists — keep the timeline artifact and continue at the carve. Reopen discovery only for gaps relevant to the requested change.

*Done when:* a sequenced past-tense timeline exists; every event has a command/actor or a hotspot; the roster or the gap is written.

## Step 3: Strategic design

Run when creating or changing context boundaries or language. When drawing contexts, locking language, or mapping relationships, read `references/strategic.md` in full.

1. Classify every named capability core / supporting / generic. Generic lists a buy-or-reuse candidate.
2. Hunt polysemes (Customer, Order, Account). Split the term across contexts or give it one meaning inside a named context.
3. Lock **ubiquitous language** per emerging context: glossary, one walked scenario, code names that match.
4. Design bounded contexts. Default: one core + one context. Split when language, purpose, owner, or use diverges. Name each context (the name enters the language).
5. Draw a context map of the *surroundings*. Each edge states direction (upstream/downstream, mutually dependent, or free) and one primary pattern. When choosing ACL, OHS, conformist, partnership, shared kernel, customer/supplier, published language, separate ways, or big ball of mud, read `references/strategic.md` in full and apply its decision tree.
6. Fill required canvas cells for each context the agent owns: name, purpose, UL terms, inbound or outbound messages.

*Done when:* every named area has a subdomain type; every in-scope context has name, purpose, and boundary; every neighboring edge has direction + pattern; required canvas cells are non-empty.

## Step 4: Design one aggregate

Run only for a bounded context labeled Domain Model. When designing building blocks, read `references/tactical.md` in full. When judging rule density or a repository FAQ, read `references/practitioner.md` in full.

1. Name the aggregate and its lifespan (billing period, sprint, or process-scoped).
2. List true invariants — rules that must hold after every successful command. Drop relationship-only and "cannot delete X if Y exists" false invariants.
3. Classify each concept: identity through change → entity; replaceable / equal by attributes → **value object**; own invariants and lifecycle → other aggregate referenced by id.
4. Draw the **consistency boundary**. Each insider names the invariant it shares with the root; each outsider is an id.
5. Choose the root and the write API. Commands are imperative; events are past tense. Pair them.
6. Place spanning invariants on the root. Local VO/entity rules stay local.
7. Load foreign aggregates in the application (or domain) service *before* the command. The aggregate opens no repository.
8. Label each cross-aggregate rule transactional or eventual and name whose job it is. Eventual: register a domain event; update the other aggregate in a later transaction.
9. Note size and conflict (command rate × concurrent clients; graph/event growth × lifetime). Split when insiders share no invariant.
10. One repository if the root needs global write access — it accepts only this root and loads/saves the whole cluster. Use a factory only when construction would leak interior types or skip invariants.

*Done when:* every mutation path goes through the root; foreign aggregates are ids; each value object is immutable and equal by components; events are past-tense, registered after success, published after persist; the repository — if any — accepts only this root; no repository method holds a business rule.

## Tripwires

- A package or topic tagged `ddd` offered as the model — inspect for invariants on roots and immutable value objects, or write "DDD-in-name-only" and model from experts. When copying a sample repo, read `references/pitfalls.md` in full.
- A multi-step prompt about to emit aggregates or hexagons from chat history — stop at glossary / event list / BC *proposals*; validate uncertain in-scope context proposals against domain evidence before generating their aggregates; reuse accepted boundaries. When the loop is an LLM generation, read `references/pitfalls.md` in full.
- A reach for an event store or a new microservice "to do DDD" — keep one write model and one database; split a query model only when a named read is blocked by aggregate constraints. When CQRS or Event Sourcing is proposed as the default, read `references/pitfalls.md` in full.
- A `*Service` about to own a new invariant — put the rule on the entity or value object; name the application service with a verb.
- Hexagonal ports chosen as proof of DDD — hexagonal + transaction script is a valid Downgrade; tactical DDD still requires a Domain Model inside the context.
