# Drizzle + PostgreSQL Quick Reference

---

## Schema Definition

### Column Types

```typescript
import { pgTable, uuid, text, varchar, integer, bigint, boolean,
  timestamp, date, numeric, json, jsonb, pgEnum, serial } from 'drizzle-orm/pg-core';

// Primary Keys
id: uuid('id').primaryKey().defaultRandom(),           // UUIDv4
id: uuid('id').primaryKey().default(sql`uuidv7()`),    // UUIDv7 (PG18+)
id: integer('id').primaryKey().generatedAlwaysAsIdentity(),  // Identity
id: serial('id').primaryKey(),                          // Serial (legacy)

// Strings
name: text('name').notNull(),
email: varchar('email', { length: 255 }).unique(),

// Numbers
age: integer('age'),
price: numeric('price', { precision: 10, scale: 2 }),
count: bigint('count', { mode: 'number' }),

// Boolean
active: boolean('active').default(true),

// Timestamps
createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
updatedAt: timestamp('updated_at', { withTimezone: true }).$onUpdate(() => new Date()),

// JSON
data: jsonb('data').$type<{ key: string }>(),

// Arrays
tags: text('tags').array(),
```

### Constraints

```typescript
email: text('email').notNull().unique(),
status: text('status').notNull().default('pending'),
price: numeric('price').check(sql`price > 0`),

// Foreign Key
authorId: uuid('author_id').references(() => users.id, { onDelete: 'cascade' }),
```

### Indexes

```typescript
}, (table) => [
  index('idx_name').on(table.column),                    // B-tree
  uniqueIndex('idx_unique').on(table.column),            // Unique
  index('idx_composite').on(table.col1, table.col2),     // Composite
  index('idx_partial').on(table.col).where(sql`...`),    // Partial
]);
```

### Enums

```typescript
export const statusEnum = pgEnum('status', ['pending', 'active', 'archived']);
status: statusEnum('status').default('pending'),
```

---

## Relations

```typescript
import { relations } from "drizzle-orm";

// One-to-Many
export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
}));

// Many-to-Many (via junction table)
export const usersToGroupsRelations = relations(usersToGroups, ({ one }) => ({
  user: one(users, { fields: [usersToGroups.userId], references: [users.id] }),
  group: one(groups, { fields: [usersToGroups.groupId], references: [groups.id] }),
}));
```

---

## Type Inference

```typescript
import type { InferSelectModel, InferInsertModel } from "drizzle-orm";

type User = InferSelectModel<typeof users>;
type NewUser = InferInsertModel<typeof users>;
```

---

## Query Operators

```typescript
import {
  eq,
  ne,
  gt,
  gte,
  lt,
  lte,
  like,
  ilike,
  inArray,
  isNull,
  isNotNull,
  and,
  or,
  not,
  between,
  sql,
} from "drizzle-orm";

eq(col, value); // =
ne(col, value); // <>
gt(col, value); // >
gte(col, value); // >=
lt(col, value); // <
lte(col, value); // <=
like(col, "%pat%"); // LIKE
ilike(col, "%pat%"); // ILIKE (case-insensitive)
inArray(col, [1, 2, 3]); // IN
isNull(col); // IS NULL
isNotNull(col); // IS NOT NULL
between(col, a, b); // BETWEEN
and(cond1, cond2); // AND
or(cond1, cond2); // OR
not(cond); // NOT
```

---

## Select Queries

```typescript
// Basic
await db.select().from(users);
await db.select({ id: users.id }).from(users);

// Where
await db.select().from(users).where(eq(users.id, id));

// Conditional filters (undefined skips condition)
await db
  .select()
  .from(users)
  .where(and(eq(users.active, true), term ? ilike(users.name, `%${term}%`) : undefined));

// Order, Limit, Offset
await db.select().from(users).orderBy(desc(users.createdAt)).limit(20).offset(40);

// Join
await db.select().from(users).leftJoin(posts, eq(posts.authorId, users.id));
```

---

## Relational Queries

```typescript
// Must pass schema to drizzle()
const db = drizzle(client, { schema });

// Find many
await db.query.users.findMany();
await db.query.users.findMany({
  where: eq(users.active, true),
  orderBy: [desc(users.createdAt)],
  limit: 20,
});

// Find first
await db.query.users.findFirst({
  where: eq(users.id, id),
});

// With relations
await db.query.users.findFirst({
  where: eq(users.id, id),
  with: {
    posts: true,
    profile: true,
  },
});

// Nested relations with filters
await db.query.users.findFirst({
  with: {
    posts: {
      where: eq(posts.published, true),
      orderBy: [desc(posts.createdAt)],
      limit: 10,
      with: { comments: true },
    },
  },
});

// Select specific columns
await db.query.users.findFirst({
  columns: { id: true, email: true },
  with: {
    posts: { columns: { title: true } },
  },
});
```

---

## Insert

```typescript
// Single
const [user] = await db.insert(users).values({ email, name }).returning();

// Multiple
await db.insert(users).values([
  { email: "a@b.com", name: "A" },
  { email: "b@b.com", name: "B" },
]);

// Upsert
await db.insert(users).values({ email, name }).onConflictDoUpdate({
  target: users.email,
  set: { name },
});

// Ignore conflict
await db.insert(users).values({ email, name }).onConflictDoNothing();
```

---

## Update

```typescript
await db.update(users).set({ status: "active" }).where(eq(users.id, id));

// With returning
const [updated] = await db.update(users).set({ status: "active" }).where(eq(users.id, id)).returning();

// Increment
await db
  .update(posts)
  .set({ views: sql`${posts.views} + 1` })
  .where(eq(posts.id, id));
```

---

## Delete

```typescript
await db.delete(users).where(eq(users.id, id));

const [deleted] = await db.delete(users).where(eq(users.id, id)).returning();
```

---

## Transactions

```typescript
await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values({ ... }).returning();
  await tx.insert(profiles).values({ userId: user.id });
  return user;
});

// Rollback
await db.transaction(async (tx) => {
  await tx.insert(users).values({ ... });
  if (condition) tx.rollback();  // Throws
});
```

---

## Aggregations

```typescript
import { count, sum, avg, min, max } from 'drizzle-orm';

// Count
const [{ total }] = await db.select({ total: count() }).from(users);

// Group by
await db.select({
  authorId: posts.authorId,
  postCount: count(),
}).from(posts).groupBy(posts.authorId);

// Having
.having(gt(count(), 10));
```

---

## Prepared Statements

```typescript
const getUser = db
  .select()
  .from(users)
  .where(eq(users.id, sql.placeholder("id")))
  .prepare("get_user");

const user = await getUser.execute({ id });
```

---

## drizzle-kit Commands

```bash
npx drizzle-kit generate   # Generate migration from schema
npx drizzle-kit migrate    # Apply migrations
npx drizzle-kit push       # Push schema directly (dev)
npx drizzle-kit pull       # Introspect existing DB
npx drizzle-kit studio     # Open Drizzle Studio
npx drizzle-kit check      # Verify migrations
```

---

## drizzle.config.ts

```typescript
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
});
```

---

## Connection Setup

### postgres.js (Recommended)

```typescript
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

const client = postgres(process.env.DATABASE_URL!);
export const db = drizzle(client, { schema });
```

### node-postgres

```typescript
import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import * as schema from "./schema";

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
export const db = drizzle(pool, { schema });
```

---

## Error Codes

| Code  | Name                  | Description         |
| ----- | --------------------- | ------------------- |
| 23505 | unique_violation      | Duplicate key       |
| 23503 | foreign_key_violation | FK constraint       |
| 23502 | not_null_violation    | NULL in NOT NULL    |
| 23514 | check_violation       | CHECK constraint    |
| 42P01 | undefined_table       | Table doesn't exist |

---

## PostgreSQL 18 Features

| Feature           | Syntax                       |
| ----------------- | ---------------------------- |
| UUIDv7            | `SELECT uuidv7();`           |
| Async I/O         | `SET io_method = 'worker';`  |
| Skip Scan         | Automatic for B-tree         |
| RETURNING OLD/NEW | `RETURNING OLD.col, NEW.col` |

---

## Quick Tips

1. **Use UUIDv7** over UUIDv4 for better index performance
2. **Use relational queries** to avoid N+1
3. **Add indexes** on foreign keys and frequently filtered columns
4. **Use partial indexes** for filtered subsets
5. **Use prepared statements** for repeated queries
6. **Set `shared_buffers`** to 25% of RAM
7. **Use `EXPLAIN ANALYZE`** to debug slow queries
8. **Use transactions** for related operations
9. **Use connection pooling** in production
10. **Run `generate` not `push`** for production migrations
