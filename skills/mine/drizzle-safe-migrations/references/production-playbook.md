# Drizzle Production Migration Playbook

## Decision Tree

- If no existing data can violate new constraints: use generated schema migration only.
- If existing data may violate new constraints: use custom backfill migration first, then generated schema migration.

## Command Sequence

```bash
# 1) Create custom backfill migration
bun run db:generate -- --custom --name <backfill_name>

# 2) Edit generated custom file in drizzle/
# Example: drizzle/0014_<backfill_name>.sql

# 3) Generate schema migration
bun run db:generate
```

## Example Backfill SQL

```sql
UPDATE "tasks"
SET "status" = 'pending'
WHERE "status" = 'saved';
```

## Migration Review Checklist

- Backfill migration is ordered before schema-tightening migration.
- Custom migration changes only the intended rows.
- Schema migration removes legacy values from constraints/enums.
- Defaults reflect the new target value.
- `drizzle/meta/_journal.json` and snapshots are present.

## Deployment Checklist

- Confirm backups/snapshots are available.
- Apply migrations in order in staging first.
- Validate row counts before and after backfill.
- Run app smoke checks after migration.

## Rollback Strategy

- Prefer forward-fix migrations instead of editing old migration files.
- If rollback is necessary, add a new migration that reintroduces valid compatibility states.
