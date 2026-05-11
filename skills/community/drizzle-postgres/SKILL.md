---
name: drizzle-postgres
description: |
  PostgreSQL and Drizzle ORM best practices. Triggers on: PostgreSQL, Postgres, Drizzle, database,
  schema, tables, columns, indexes, queries, migrations, ORM, relations, joins, transactions, SQL,
  drizzle-kit, connection pooling, N+1, JSONB, RLS.

  Use when: writing database schemas, queries, migrations, or any database-related code.
  Proactively apply when creating APIs, backends, or data models.
---

# PostgreSQL + Drizzle ORM

Type-safe database applications with PostgreSQL 18 and Drizzle ORM.

## Essential Commands

```bash
npx drizzle-kit generate   # Generate migration from schema changes
npx drizzle-kit migrate    # Apply pending migrations
npx drizzle-kit push       # Push schema directly (dev only!)
npx drizzle-kit studio     # Open database browser
```

## Quick Decision Trees

### "How do I model this relationship?"

```
Relationship type?
├─ One-to-many (user has posts)     → FK on "many" side + relations()
├─ Many-to-many (posts have tags)   → Junction table + relations()
├─ One-to-one (user has profile)    → FK with unique constraint
└─ Self-referential (comments)      → FK to same table
```

### "Why is my query slow?"

```
Slow query?
├─ Missing index on WHERE/JOIN columns  → Add index
├─ N+1 queries in loop                  → Use relational queries API
├─ Full table scan                      → EXPLAIN ANALYZE, add index
├─ Large result set                     → Add pagination (limit/offset)
└─ Connection overhead                  → Enable connection pooling
```

### "Which drizzle-kit command?"

```
What do I need?
├─ Schema changed, need SQL migration   → drizzle-kit generate
├─ Apply migrations to database         → drizzle-kit migrate
├─ Quick dev iteration (no migration)   → drizzle-kit push
└─ Browse/edit data visually            → drizzle-kit studio
```

## Directory Structure

```
src/db/
├── schema/
│   ├── index.ts          # Re-export all tables
│   ├── users.ts          # Table + relations
│   └── posts.ts          # Table + relations
├── db.ts                 # Connection with pooling
└── migrate.ts            # Migration runner
drizzle/
└── migrations/           # Generated SQL files
drizzle.config.ts         # drizzle-kit config
```

## Schema Patterns

### Basic Table with Timestamps

```typescript
export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  email: varchar("email", { length: 255 }).notNull().unique(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});
```

### Foreign Key with Index

```typescript
export const posts = pgTable(
  "posts",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id),
    title: varchar("title", { length: 255 }).notNull(),
  },
  (table) => [
    index("posts_user_id_idx").on(table.userId), // ALWAYS index FKs
  ],
);
```

### Relations

```typescript
export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, { fields: [posts.userId], references: [users.id] }),
}));
```

## Query Patterns

### Relational Query (Avoid N+1)

```typescript
// ✓ Single query with nested data
const usersWithPosts = await db.query.users.findMany({
  with: { posts: true },
});
```

### Filtered Query

```typescript
const activeUsers = await db
  .select()
  .from(users)
  .where(eq(users.status, "active"));
```

### Transaction

```typescript
await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values({ email }).returning();
  await tx.insert(profiles).values({ userId: user.id });
});
```

## Performance Checklist

| Priority | Check                                  | Impact                             |
| -------- | -------------------------------------- | ---------------------------------- |
| CRITICAL | Index all foreign keys                 | Prevents full table scans on JOINs |
| CRITICAL | Use relational queries for nested data | Avoids N+1                         |
| HIGH     | Connection pooling in production       | Reduces connection overhead        |
| HIGH     | `EXPLAIN ANALYZE` slow queries         | Identifies missing indexes         |
| MEDIUM   | Partial indexes for filtered subsets   | Smaller, faster indexes            |
| MEDIUM   | UUIDv7 for PKs (PG18+)                 | Better index locality              |

## Anti-Patterns (CRITICAL)

| Anti-Pattern             | Problem                    | Fix                                       |
| ------------------------ | -------------------------- | ----------------------------------------- |
| **No FK index**          | Slow JOINs, full scans     | Add index on every FK column              |
| **N+1 in loops**         | Query per row              | Use `with:` relational queries            |
| **No pooling**           | Connection per request     | Use `@neondatabase/serverless` or similar |
| **`push` in prod**       | Data loss risk             | Always use `generate` + `migrate`         |
| **Storing JSON as text** | No validation, bad queries | Use `jsonb()` column type                 |

## Reference Documentation

| File                                                   | Purpose                          |
| ------------------------------------------------------ | -------------------------------- |
| [references/SCHEMA.md](references/SCHEMA.md)           | Column types, constraints        |
| [references/QUERIES.md](references/QUERIES.md)         | Operators, joins, aggregations   |
| [references/RELATIONS.md](references/RELATIONS.md)     | One-to-many, many-to-many        |
| [references/MIGRATIONS.md](references/MIGRATIONS.md)   | drizzle-kit workflows            |
| [references/POSTGRES.md](references/POSTGRES.md)       | PG18 features, RLS, partitioning |
| [references/PERFORMANCE.md](references/PERFORMANCE.md) | Indexing, optimization           |
| [references/CHEATSHEET.md](references/CHEATSHEET.md)   | Quick reference                  |

## Resources

### Drizzle ORM

- **Official Documentation**: https://orm.drizzle.team
- **GitHub Repository**: https://github.com/drizzle-team/drizzle-orm
- **Drizzle Kit (Migrations)**: https://orm.drizzle.team/kit-docs/overview

### PostgreSQL

- **Official Documentation**: https://www.postgresql.org/docs/
- **SQL Commands Reference**: https://www.postgresql.org/docs/current/sql-commands.html
- **Performance Tips**: https://www.postgresql.org/docs/current/performance-tips.html
- **Index Types**: https://www.postgresql.org/docs/current/indexes-types.html
- **JSON Functions**: https://www.postgresql.org/docs/current/functions-json.html
- **Row Level Security**: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
