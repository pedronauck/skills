# Practitioner checks (Branas / Elemar)

Load when judging **rule density**, answering a repository FAQ, or applying organization-level DDD after Step 1 already produced Proceed. Portuguese teaching distilled to English leading words. Ubiquitous language stays required in `SKILL.md`; the 2024 anti-romantic warning lives only here.

## Organization, not project

"I apply DDD on my project" is the wrong sentence. DDD applies to the organization's knowledge structure. E-commerce is not one domain — logistics, sales, payments, invoices are subdomains of the company.

Subdomains already exist; the team does not invent them. Sectors of a firm are usually 1:1 with subdomains (core / supporting / generic). Each subdomain *converts* to a bounded context in the solution space.

Same term for different things, or different terms for the same thing, is a subdomain-split signal.

Strategic modeling exists so some subdomains can be *not implemented* (buy a vendor).

## Start with less

A bounded context is not a microservice. A context may live inside one project.

Splitting a tightly coupled knowledge area replaces in-process calls with network, retries, and circuit breakers. Default: start with less; decompose later. Start from a business area; split when an aggregate clearly decomposes.

*Done when (split proposed):* either the split is refused or a resilience cost is accepted in writing.

## Density, not size — per bounded context

After the strategic cut, pick a design strategy **inside each** bounded context.

| Density signal | Strategy |
| --- | --- |
| Payroll, accounting, legal, fiscal; rules that vary by customer / state / city; frequently changing isolated rules | **Domain Model** (tactical DDD) |
| CRUD, blog, post/comment, 1:1 entity↔table↔repository, no reusable isolated rules | **Transaction Script** |

Size is irrelevant. Putting a Domain Model on a simple domain is bureaucratic. "Always use DDD because we teach DDD" is false.

One size does not fit all: one context may be transaction script, another Domain Model. Tactical DDD *is* Domain Model — objects used to distribute complexity — not a philosophy.

Anemic (behavior in a service, data in DTOs) is a **strategy label**, not an insult. Detect the split; enrich only when the density gate already selected Domain Model.

Hexagonal architecture admits transaction script. Clean Architecture and tactical DDD require a Domain Model. Hexagonal ports are not proof of DDD.

AI does not change the density gate.

## Value object as first tactical move

Creating the team's own types is the first move toward a Domain Model. A value object replaces a primitive (or a set of them) with a constructor-gated instance. Identified by value; immutable; changing a phone/email/money value replaces the instance.

Prefer extracting a value object over a new entity when the concept is independently reusable and unit-testable. Validate at construction, not on the DTO.

Hotel sketch: reservation = entity (lifecycle, cancellation); guest name/email/document, stay interval, coordinates = value objects inside the aggregate. Persistence unwraps `email.value` and rebuilds `new Email(...)`.

## Small aggregates (examples)

Aggregate = cluster of entities + value objects that must stay consistent; repository loads/saves the cluster as a whole. Root is the only operation entry.

Loan that embeds Customer or Invoice forces every address change or invoice payment through the loan root — split and relate by identity.

Order + line items travel together; financing + installments travel together. Store the customer id on financing; skip lazy-loading Customer.

If aggregates are not obvious, the model is table replicas and the team will open one repository per entity.

Do not mutate multiple aggregates in one client action. The only transactional guarantee is inside the repository save; otherwise move to events.

A recalled "~70% single-entity aggregates" figure is a warning against giant clusters, not a quota. Branas does not commit the source.

## Repository FAQ

| Ask | Do |
| --- | --- |
| May business rules live in the repository? | No. Persist only. Rules live on entities, value objects, and domain services. |
| What may the repository accept? | The aggregate root / cluster. One repository per aggregate. |
| Partial graph on a mutation path? | Forbidden — skips invariance. Split the aggregate or open a query path. |
| Save semantics? | All-or-nothing for the cluster. |
| Persistence model vs domain? | ORM tables stay in infrastructure behind the port. DAO talks to tables; repository talks to domain objects. |
| Backend other than SQL? | API, filesystem, or memory is fine if the purpose is persistence. |
| Cache? | Decorator. Not the pattern's job. |
| Presenter coupled to the loaded aggregate? | Presenter transforms use-case output (JSON/CSV/PDF). |
| Library in the domain layer? | Fine (math, string, UUID) until it touches an external resource — then invert and adapter. |
| Fat finder API? | Signal to split a query model (logical CQRS), not to keep stuffing reads into the command repository. |

Elemar sometimes calls the repository a domain service. English *Done when:* uses **persistence port on the aggregate** — load/save/search only.

## Ubiquitous language — dissent (do not promote)

2019 Live #17: ubiquitous language is the agreement between experts and developers; a model is a selective abstraction.

2024 short: DDD is "extremely technical and practical"; ubiquitous language is "always good" but not the definition.

Keep the vocabulary-alignment *Done when:* in Step 3. Use this file to stop the agent from treating renamed classes as completion.

Elemar live #52 auto-captions are badly garbled. Cite Branas restatements, not isolated Elemar ASR tokens.
