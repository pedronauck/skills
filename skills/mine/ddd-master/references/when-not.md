# When DDD is the wrong tool

Load when Step 1 must refuse, downgrade, or name an alternative. Companion to the Verdict checklist in `SKILL.md`.

## Three verdicts

| Verdict | Emit | Stop |
| --- | --- | --- |
| **Refuse** | The relevant complexity evidence and alternative name | Aggregate, repository, and "domain layer" types |
| **Downgrade** | Transaction script, operations-over-records, or layers-without-a-model | Evans vocabulary presented as proof of DDD |
| **Proceed** | Exit into Steps 2–4 | Only unresolved discovery or boundary decisions need further work |

## Essential complexity

A Domain Model pays an object-mapping tax. That tax is worth it only when object techniques organize *essential* complexity — multi-step invariants, calculations, and rules that change together.

CRUD + field-format checks are accidental complexity. Tag them syntax and Refuse tactical DDD.

Microsoft / Thoughtworks constraint: tactical design belongs on complex (or soon-to-be-complex) logic in a **core domain**.

## Core vs generic vs supporting

| Type | Investment | Default verdict |
| --- | --- | --- |
| **Core** | Differentiator; best people; custom model | Proceed if complexity is essential |
| **Supporting** | Necessary specialization; extend or buy-and-tweak | Refuse full tactical catalog; thin model only if rules are dense |
| **Generic** | Commodity | Buy, reuse, or transaction script |

The same capability flips type across companies (payments generic at a merchant, core at a payments firm). Name the type for *this* organization.

## Slogan DDD vs discipline

Lowercase **ddd** (Tune / Verraes): grasp the domain, agree a language, express shared models, separate contexts, evolve them.

Capital **DDD** adds Evans names, collaboration with domain experts, continuous evolution, and heavy investment only in core domains.

Folders named after domains, Clean Architecture layers, or `Aggregate` types *without* a collaboratively evolved model of rules are slogan DDD. Refuse capital scaffolding. Keep lowercase language work (ask, name, split terms).

## Anemic vs transaction script

**Anemic domain model** (Fowler): nouns, rich structure, almost no behavior; services compute and write back. Pays Domain Model cost for transaction-script benefits. An anti-pattern *when the design claims a Domain Model*.

**Transaction script**: one procedure per user–system interaction. Honest fit for simple applications. Prefer this name over "anemic DDD."

Heuristic: the more behavior in services, the more the model is robbed; all logic in services = robbed blind.

Dohna dissent (downgrade, not a green light): Entity + Operation Class in the *same domain package* can stay an honest operations-over-records design. Premature anemia-as-best-practice remains a smell. Functional separation of data and behavior is allowed — still not permission to call getter bags DDD.

Service layer may exist and stay *thin*: it directs domain objects and holds no business rules. Fat services that *are* the rules are either a named transaction script or refused DDD.

Clean Architecture / hexagonal without a behavior-rich model is layered CRUD. Hand isolation structure to `architectural-analysis`. Ports-and-adapters are not a Domain Model.

## Validation placement

| Kind | Meaning | Owner |
| --- | --- | --- |
| **Syntax** | Command is coherent (non-null, date not in the past) | UI *and* domain may both reject |
| **Semantic** | Command makes sense given current state | Domain consistency |
| **Production** | Heart of the system; changes state; emits events | Domain |

Syntax-only work is not a reason to start DDD. Semantic and production rules living *only* in a controller block Proceed.

## Legacy — tactics inside the mud disappoint

Refuse "add aggregates to the monolith as-is" and refuse big-bang legacy replacement as the DDD on-ramp. Pick one Evans strategy:

1. **Bubble context** — small bounded context behind an **anticorruption layer**; modest commitment; often temporary; umbilical / ACL-backed repository; no new database required.
2. **Autonomous bubble** — own data store; synchronizing ACL (batch or translated events); can run cut off; needs organizational commitment.
3. **Open-host over ACL** — stable published protocol for select legacy assets (especially generic/supporting). Once legacy is stable, not core, and reachable — leave it.
4. **Expanding a bubble** — co-evolve model and ACL; bring in only data the new model uses. An untranslated field is a bypass of the context, not a free DTO.

Translator rule: translate concepts. Business logic stays out of the translator. Matching numbers do not make two concepts the same.

*Done when (legacy):* strategy name, ACL style (umbilical vs synchronizing), and what happens to the bubble are written.

## Honest alternative names

- **Transaction script** — one procedure per interaction.
- **Operations-over-records** — verb functions over data; domain package optional.
- **Layers without a model** — UI/persistence isolation; `architectural-analysis`.
- **Lowercase ddd** — language and problem framing without Aggregate types.
