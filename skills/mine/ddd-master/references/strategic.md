# Strategic design

Load when Step 3 runs, or when the user named ubiquitous language, subdomain, bounded context, context map, or a relationship pattern. Pattern catalog and canvas fields live here; the seven-step workflow stays in `SKILL.md`.

## Problem space vs solution space

**Subdomains** are discovered facts about the business (knowledge areas that already exist in the organization).

**Bounded contexts** are designed software boundaries — an internally consistent language and model.

A subdomain may split into several contexts (different owners, dialects, or rates of change). Several subdomains may share one context when integration cost exceeds the benefit of separation.

Default: one core domain + one bounded context. Extra contexts appear when a polyseme, purpose split, team split, or external system forces a boundary.

A bounded context is conceptual first — not a microservice, module, or package. 1:1, 1:n, and n:1 mappings to deployables are all valid. Map deployables after the context map exists.

## Ubiquitous language

The language *is* the model. Same term, one meaning, from expert talk through code.

A compromise name for a polyseme hides a missing context. Invent missing concepts when the current words cannot carry a numeric scenario.

**UL is locked** when: a short glossary exists for that context; an expert (or the named counterpart) can walk one concrete scenario without translation; class and module names match the glossary.

Continuous integration inside a live context: merge often, automated tests, relentlessly exercise the language so the model does not fragment.

## Context map

Brownfield recipe (Avanscoperta): (1) detect models, (2) make boundaries explicit, (3) draw relationships, (4) mark upstream/downstream, (5) categorize, (6) decorate risks.

Greenfield: purpose + boundaries; add ACL to external vendors; leave collaboration patterns as "to-be-determined" until collaboration exists.

Map the surroundings, not the company. Small maps for explicit questions. Upstream/downstream is political influence, not call direction. Line thickness is communication bandwidth.

Evans order: map existing terrain; take up transformations later.

Artifact: mermaid or bullet edges. Each edge states direction + one primary pattern name. Abbreviations (OHS, ACL, CF, …) are optional.

## Team relationships (know) vs contact patterns (decide)

Three team relationships: mutually dependent, upstream-downstream, free.

### Relationship decision tree

| Trigger | Pattern |
| --- | --- |
| Shared fate; must ship together; bandwidth exists | **Partnership** |
| Small shared model both sides can continuously integrate | **Shared Kernel** (keep small; growth ⇒ merge contexts) |
| Upstream can succeed alone; downstream can negotiate into the backlog | **Customer/Supplier** |
| Upstream will not accommodate; translation cost not justified | **Conformist** |
| Upstream will not accommodate; own model must stay clean (legacy/vendor) | **Anticorruption Layer** |
| Many clients need the same capability | **Open Host Service**, stabilize with **Published Language** |
| Integration benefit < cost | **Separate Ways** |
| No coherent model or boundaries | Draw a **Big Ball of Mud** contour; contain leakage with ACL on the outside; skip rich modeling inside |

OHS and Published Language commonly pair. Downstream of an OHS is Conformist or ACL.

Cost allocation: ACL spends code; Partnership and Customer/Supplier spend process. Assign Partnership or Shared Kernel only after checking communication bandwidth.

## Bounded Context Canvas — required vs disclosed

Required cells (Step 3 *Done when:*):

- Name (enters the ubiquitous language)
- Purpose (one or two sentences)
- UL terms
- Inbound or outbound messages (command / query / event) + collaborators

Disclosed cells: strategic classification (core/supporting/generic), domain roles, assumptions, verification metrics, open questions, Wardley evolution, business-model role.

Fill order when the user asked for the full canvas: name → purpose → classification → domain roles → messages + collaborators + relationship → UL → business decisions → assumptions → metrics → open questions.

## Context Mapper / CML

Machine-readable maps, legal pattern combos, generators. Optional formalization after a map exists. Not a required step. FEATURE / APPLICATION / SYSTEM / TEAM types are a tool interpretation — disclose only when the user asked for CML.

## Anti-patterns (positive form)

- Build several models with explicit maps; skip the enterprise-wide unified model.
- Classify subdomains and design contexts as two passes.
- Start from language and purpose; add tactical types after a context exists.
- Split a polyseme; skip the compromise term.
- Map neighbors the work touches; skip the giant company map.
- Apply rich modeling outside a Big Ball of Mud, behind an ACL.
