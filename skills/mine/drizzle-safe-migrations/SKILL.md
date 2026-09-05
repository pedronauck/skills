---
name: drizzle-safe-migrations
description: "Plan safe Drizzle backfills, enum/check/default changes, constraint tightening, migration ordering, and rollback. Excludes other ORMs, query optimization, and new-schema design."
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---
# Drizzle Safe Migrations

## Overview

Use this skill to run database migrations in a way that is auditable, deployment-safe, and consistent with Drizzle's migration model.

## Core Rules

- Generate schema migrations with the existing project script and package manager; `bun run db:generate` below is an example, not a required script name.
- Never hand-edit generated schema migration files.
- Generate data backfills as custom migrations (`bun run db:generate -- --custom --name <name>`) and edit only that custom SQL file.
- Apply data normalization before tightening constraints.
- Keep one-off data fixes in migration history, not as hidden runtime logic, unless an emergency hotfix requires temporary mitigation.

## Workflow

1. Classify the change:
   - `schema-only`: only column/table/index/default changes.
   - `data+schema`: old rows must be transformed before new constraints/defaults.
2. For `data+schema`, create custom migration first:
   - `bun run db:generate -- --custom --name <descriptive_name>`
   - Add idempotent backfill SQL.
3. Generate schema migration second:
   - `bun run db:generate`
4. Verify migration ordering in `drizzle/meta/_journal.json`:
   - backfill migration index must be lower than constraint-tightening migration index.
5. Verify generated SQL and snapshots:
   - backfill migration contains only intended data change.
   - schema migration contains constraint/default/type changes.
6. Run the owning migration suite against existing-data and fresh-install cases, plus required project gates. Reuse current evidence; unrelated backend suites are not an additional skill gate.
7. Record material rollout risks and recovery steps when applicable:
   - expected data transformations,
   - lock-risk areas,
   - rollback strategy.

## Backfill Requirements

- Use restrictive `WHERE` clauses.
- Prefer idempotent updates (`UPDATE ... WHERE status = 'legacy_value'`).
- Do not mix unrelated DDL/DML in the same migration.
- Keep SQL explicit and minimal.

## Constraint Tightening Pattern

When removing allowed values (enum/check):

1. Backfill existing rows to valid target value.
2. Update default to new value.
3. Tighten check/enum constraint.

For large tables or strict uptime targets, evaluate staged constraint validation supported by the actual database and driver. PostgreSQL `NOT VALID` / `VALIDATE CONSTRAINT` applies only to supported constraint kinds.

## Anti-Patterns

- Hand-editing generated schema migration files.
- Tightening constraints before backfilling existing data.
- Hiding one-time migration logic in app startup code without migration artifacts.
- Running migrations without validating order in the Drizzle journal.

## Reference

- See `references/production-playbook.md` for command templates and review checklists.
