# Spec Quality Markers

Use these markers to assess the requested review, not to add an approval stage. Scope and affected boundaries always apply. Interface definitions, persistent-data rationale, ownership decisions, and safety invariants apply only where the design changes them. A missing applicable contract is a review finding; an explicit request to review the saved draft is sufficient to proceed. Ask first only when missing scope makes a useful review impossible.

## Marker 1: Scope / MVP Boundary Statement

The spec opens with an explicit boundary in plain language: which work composes the current
change, which follow-up work is deferred, and which features are intentionally out of scope.
A reader should be able to tell what is and is not being built without inference.

## Marker 2: Architectural Boundaries & Affected Components

A first-class section names which modules, packages, services, layers, routes, or shared
helpers may own the change. It explicitly calls out forbidden cross-layer dependencies,
wrapper bypasses, or coupling hazards when they matter.

## Marker 3: Concrete Interface / Contract Definitions

Critical interfaces, types, schemas, request/response payloads, or API contracts are shown
concretely, not waved at in prose. If a contract is still in flux, the spec says so
explicitly instead of pretending the shape is final.

## Marker 4: Data-Model & Migration Rationale

Any new or changed persistent data — columns, fields, indexes, constraints, enums,
backfills, config keys, or stored formats — is listed with its purpose, nullability/defaults,
and rollout implications (migration order, backward compatibility, data backfill). If no
persistence change is needed, the spec says why.

## Marker 5: Ownership & Pattern Decisions

For every new piece of state, data flow, cache, view-model, form, or filter concern, the spec
names the owning layer and the chosen pattern: local vs shared state, who loads/owns data,
reuse of an existing helper vs a new one, and canonical primitives vs inline copies. The point
is that the spec has made the decision, not deferred it to implementation guesswork.

## Marker 6: Safety / Verification Invariants Numbered

Security-sensitive, permission-sensitive, migration-sensitive, cache-sensitive, or
concurrency-sensitive behavior is spelled out as a numbered invariant list rather than loose
prose. The spec also names the verification surface that proves those invariants (unit /
integration / end-to-end / contract / lint / build).

Record material gaps and their consequence in the findings. Do not abort for inapplicable headings.
