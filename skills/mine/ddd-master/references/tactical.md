# Tactical building blocks

Load when Step 4 runs, or when the user named aggregate, value object, entity, domain event, repository, factory, domain service, or invariant. Definitions and exceptions live here; the eleven-step design walk stays in `SKILL.md`.

## Classification tests

| Kind | Test | Equality |
| --- | --- | --- |
| **Entity** | Identity through a lifecycle; two instances with the same attributes and different ids are different | By identity |
| **Value object** | Care about attributes and logic, not identity; wholly replaceable | By all components; immutable; operations return new instances |
| **Aggregate root** | Own invariants and a global lifecycle; the only entry for writes that span the cluster | By identity; the only type a repository accepts |
| **Domain service** | Significant process that is not a natural responsibility of an entity or value object | Contract stated in the ubiquitous language |
| **Domain event** | Something domain experts care about that *happened* | Immutable; past-tense name; timestamp; involved identities |

A Route may mention a City (entity reference) and stay a value object. VO vs entity is context-relative — the same notion can be a VO in one context and an entity in another.

## Consistency boundary

An **aggregate** is a cluster of entities and value objects with one root. External objects hold references to the root only. Apply consistency synchronously inside the boundary; asynchronously across it.

A properly designed aggregate can be modified in any way the business requires with invariants consistent in a **single transaction**. One aggregate instance per transaction.

**True invariant, not relationship.** Draw the boundary around rules that must hold whenever anything in the group changes. "Has-a" graphs and "cannot delete X if Y exists" are false invariants — they produce large clusters and optimistic-concurrency collapse.

**Small.** Prefer a root plus the minimum attributes that must stay consistent. A common shape is a single root with value-typed properties. Signal of too-large: parallel writes collide on one record, or a query for one field loads the graph.

**Reference other aggregates by identity** (`OrderId`, not an `Order` pointer). Pointers tempt same-transaction edits and eager-load the foreign graph. Application (or domain) service looks up dependents *before* invoking the command. The aggregate opens no repository. Interior entity ids are local to the aggregate.

## Whose job — transactional vs eventual

A rule that spans aggregates is not expected to be up to date at all times.

If the *acting user* must see both sides consistent in this use case, keep one transactional boundary (without growing a large cluster) or record an ADR exception.

If it is another user or the system, register a domain event on A; a subscriber in another transaction loads B and applies a command; retry on contention; compensate or report when retries exhaust.

## Domain events — publication order

1. Command succeeds and state changes.
2. Root **registers** the event on an unpublished list. Publish nothing from inside the command.
3. Repository / unit of work publishes only if save succeeds.
4. Handlers live in the application layer. They may update another aggregate or emit an **integration event** (cross-process, only after persist).

Failed command → domain error, no event.

Command = imperative verb, one handler, rejectable. Event = past-tense fact, zero-to-n handlers.

Register events on the **root**. Immediate static `DomainEvents.Raise` couples tests and can publish before persist fails.

Default: publish after successful save of **one** root. Dispatch-before-commit on a shared unit of work (eShop / Bogard) is a disclosed exception — record an ADR; it hides lock cost and breaks when persistence cannot span aggregates.

## Repository

For each aggregate type that needs **global write access**, one collection-like port on the **root type only**. Add/remove encapsulate the store; selection uses ubiquitous-language criteria; return a fully instantiated aggregate.

Query interior entities through the root, not a child repository. Persistence model (ORM tables) ≠ domain entity; ORM types stay in infrastructure behind the port.

Implementation may be SQL, filesystem, API, or memory — the purpose is persistence. Cache may decorate the port; cache is not the pattern. Presenters transform use-case output; they do not couple to the loaded cluster.

Repository is **gated**, not mandatory. Query-side or event-sourced designs may skip a write repository. Overloaded finder methods are a signal to split a query path (logical CQRS), not to stuff reads into the command port.

## Factory and domain service

**Factory** when creating a consistent aggregate or a large value object would leak internals or skip invariants. Simple roots may use a constructor that validates. Client never `new`s interior parts of a complex graph.

**Domain service** when forcing the operation onto a root would distort it (lookup of dependents, routing). Prefer the application service to resolve, or pass the domain service into the command. An operation that is a natural responsibility of the root or a value object stays there.

## Encapsulation

Name operations by effect in the ubiquitous language. No public setters. Collections exposed read-only. Updates only via root methods. Application handlers do not `new` a child and push it into a public collection.

Layered isolation (domain depends on nothing above) is a constraint on implementation, not a step in drawing a boundary.

## Aggregate Design Canvas (optional artifact)

Nine fields when the user asked to document an aggregate or Step 4 size/conflict is ambiguous: name + lifespan; description + boundary tradeoffs; state transitions; enforced invariants; corrective policies; handled commands; created events; throughput (rate × clients → conflict); size (event growth × lifetime).

Completion is the Step 4 *Done when:* list, not a pretty board. Too many transitions → split process. Naive transitions → anemic. Many corrective policies → logic pushed out. Infinite lifetime → scope to a period.

## Allowed deviations (ADR, not defaults)

Vernon: batch-create of independent new roots in one transaction if semantically equal to repeated singles; no messaging mechanism plus user–aggregate affinity; mandated two-phase commit — still prefer one local instance per transaction; direct references for query performance, weighed against size.

Treat the four rules as defaults. Document each break.

## Language-agnostic restatements (not house style)

Identity equality for entities; component equality + immutability for value objects; unpublished-event list on the root; a marker that "this type is a root." Skip `OwnsOne`, MediatR, Spring `@DomainEvents`, and seedwork class listings as implied stack.
