# Implementation pitfalls

Load when a "DDD" sample is offered as the model, a loop is about to emit aggregates from chat history, CQRS or Event Sourcing appears as the default, or model and code have drifted. Empirical overlay; building-block definitions stay in `tactical.md`.

## Refuse tag-as-proof

Keyword-tagged GitHub "DDD" is mostly noise (78.7% of 11,742 candidates failed semantic validation; `in:readme ddd` 94.9%). A liberal classifier still accepted incomplete structure.

25.3% of *verified* DDD repos record no explicit business domain — they describe Clean Architecture, not the business.

Inspect for invariants on aggregate roots, immutable value objects, and repository *interfaces*. Missing those: write "DDD-in-name-only" and model from experts. Skip cloning a starred starter as the model.

*Done when:* at least one write path enforces a named business rule inside a domain type, or the sample is rejected.

## Demand a domain in the docs

When README or spec describes an architecture style but not the business, write a ubiquitous-language glossary before generating tactical types.

*Done when:* every proposed bounded context names a business capability (`Orders`), not a layer (`CleanArchitecture`).

## Prefer layered or clean first

Literature over-weights microservices (44% of SLR studies). Verified OSS DDD is mostly Layered (28.9%) and Clean (22.8%); Microservices is 2.56%.

**Simplified CQRS** (Microsoft Learn): two logical models, *one* database, so queries are not trapped behind aggregate boundaries. Event Sourcing is optional and unused in that guide.

CQS is method-level (return *or* mutate). CQRS is two objects/layers. Evolved CQRS+ES is a later option when reads cannot be answered without breaking a write-side boundary.

*Done when:* the command side still has a rich model, and any read side is justified by a named query that the write model cannot answer.

Event Sourcing is a storage choice, not a discovery outcome. Discovery events are business facts.

## Size by immediate invariant

Agents grow an aggregate until every rule is atomic. Prefer a fine-grained root + eventual consistency via events (Richardson: `OrderCreated` → credit reserve → `CreditReserved` / `CreditLimitExceeded`).

One transaction creates or updates **one** aggregate. Inter-aggregate refs are identities.

2PC and cross-service SQL joins are the wrong consistency tool. Name the compensating path.

*Done when:* the aggregate loads for a single use case without another context's history, and the leftover rule has an event + subscriber.

## Model, then deploy

Each service's logic is **one or more** aggregates. "One microservice per aggregate" and LLM-proposed fine contexts that operations cannot split both fail.

Group aggregates into a bounded context; deploy that context as a module first; extract a process when team or release cadence requires it.

Prompting frameworks over-split (Access Control vs Identity) when the prompt says "question any context that seems too large" and never says "merge when coupling is operationally tight."

*Done when:* a context map exists and each deployable owns ≥1 aggregate, not 1:1.

## Halt generation at bounded-context proposals

Eisenreich & Wagner five-step chat: (1) UL, (2) simulated Event Storming, (3) bounded contexts, (4) aggregates/invariants, (5) technical architecture. Steps 1–3 produced usable discussion artifacts; accumulated errors made 4–5 impractical.

Terms go generic or artificial; event coverage misses operational edges; contexts over-fine; architecture dumps are shallow PlantUML. Automation can *reduce* the stakeholder collaboration DDD exists to create.

Use the model as a sparring partner through glossary / events / BC *proposals*. Refine each step against the named counterpart. Reuse accepted domain decisions; resolve material uncertainty before turning a new proposal into aggregate or hexagon files.

JDomInO: Copilot on raw source reproduces surface structure and violates aggregate boundaries, VO immutability, and event publication. Context files are not reliably obeyed. Treat sync as a check the agent *does*, not a toolchain the skill requires.

*Done when:* new or changed context boundaries are supported by domain evidence; existing accepted contexts need no new approval round.

## Check model–code sync

Model–code divergence and boundary leakage are the recurring technical root cause. Unidirectional codegen severs the link. Generic reverse-engineering recovers classes, not roots.

For each changed aggregate root, the named invariant exists in code *and* in the living model (glossary, canvas, or equivalent).

*Done when:* changed invariants agree between code and the living model; conceptual model entries need not map one-to-one to types.

## Move the rule

Industrial leftover (EMSE Spring backend): anemic objects, duplicated use-case services, god repository (>3000 LOC) with query-as-business-logic, DTO conversion oscillating between controller and service, tests re-testing unencapsulated rules.

Repair: put the invariant on the entity or value object; name application services with a verb (`ApproveLoan`, not `LoanService`); keep the unit of work on the application service; clients call domain objects, not DAOs.

Guardian rule: a service class carries a verb; periodic reviews push logic back into entities.

*Done when:* a unit test constructs the domain type and the rule fails without a framework.

## Isolate, then parity

Refactoring DDD into an active codebase: work behind an ACL / isolated module; reach feature parity; then switch. Keep framework idioms (Evans: don't fight the framework). Size the refactor to codebase, experience, commitments, and budget. Pilot one context before a whole-system rewrite.

Onboarding and learnability are the lowest scores even when teams accept the change. Progressive-disclose tactical blocks; first pass is UL + contexts + one core aggregate.

## Name a domain counterpart

When evidence cannot resolve a material language decision, identify the domain counterpart who can answer. Continue independent, evidenced work while that question is pending. Guardian failure mode: a tech-led model that editors do not own; business people "going native."

*Done when:* a counterpart can accept or reject UL terms.

## Disclosed, not default

- Cloud management groups named after bounded contexts (AWS OUs / Azure MGs) with explicit network allow-lists — only when designing those controls.
- Context Mapper and JDomInO as optional tooling, not required installs.
- Microsoft Learn class names and eShopOnContainers structure — decisions transfer; types do not.
- Zhang et al. mining study is a protocol; cite the *claim* (gap is primary), not a prevalence number.
