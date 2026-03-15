# Drizzle ORM Patterns and Best Practices

This document contains comprehensive patterns, best practices, and guidelines for working with Drizzle ORM in this project.

## Table of Contents

1. [Schema Definition](#schema-definition)
2. [Type Exports](#type-exports)
3. [Relations](#relations)
4. [Queries](#queries)
5. [Prepared Statements](#prepared-statements)
6. [Transactions](#transactions)
7. [Migrations](#migrations)
8. [Performance Optimization](#performance-optimization)
9. [Common Pitfalls](#common-pitfalls)
10. [Code Organization](#code-organization)

---

## Schema Definition

### Basic Table Structure

Organize schemas by domain in separate files. Use fluent constraint chaining and add indexes for frequently queried columns.

```typescript
import { pgTable, uuid, varchar, timestamp, text, boolean, integer, index } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  name: varchar('name', { length: 255 }),
  avatarUrl: text('avatar_url'),
  isActive: boolean('is_active').default(true).notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
}, (table) => ({
  emailIdx: index('users_email_idx').on(table.email),
  createdAtIdx: index('users_created_at_idx').on(table.createdAt),
}));
```

### Column Types Reference

```typescript
// UUIDs (preferred for primary keys)
id: uuid('id').primaryKey().defaultRandom(),

// Strings
email: varchar('email', { length: 255 }).notNull().unique(),
description: text('description'),

// Numbers
count: integer('count').default(0).notNull(),
price: decimal('price', { precision: 10, scale: 2 }),

// Booleans
isActive: boolean('is_active').default(true).notNull(),

// Timestamps
createdAt: timestamp('created_at').defaultNow().notNull(),
updatedAt: timestamp('updated_at').defaultNow().notNull().$onUpdate(() => new Date()),
deletedAt: timestamp('deleted_at'),

// JSON
metadata: jsonb('metadata').$type<{ key: string; value: unknown }>(),

// Enums
status: pgEnum('status', ['pending', 'active', 'completed']),
```

### Indexes

Always add indexes for:
- Columns used in WHERE clauses
- Columns used in JOIN conditions
- Columns used in ORDER BY clauses
- Foreign key columns

```typescript
export const posts = pgTable('posts', {
  id: uuid('id').primaryKey().defaultRandom(),
  authorId: uuid('author_id').notNull().references(() => users.id),
  title: varchar('title', { length: 255 }).notNull(),
  status: varchar('status', { length: 50 }).notNull(),
  publishedAt: timestamp('published_at'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
}, (table) => ({
  authorIdIdx: index('posts_author_id_idx').on(table.authorId),
  statusIdx: index('posts_status_idx').on(table.status),
  publishedAtIdx: index('posts_published_at_idx').on(table.publishedAt),
  // Composite index for common query patterns
  authorStatusIdx: index('posts_author_status_idx').on(table.authorId, table.status),
}));
```

---

## Type Exports

Always export table types for use in your application:

```typescript
// Infer select type (for reading from DB)
export type User = typeof users.$inferSelect;

// Infer insert type (for inserting into DB)
export type NewUser = typeof users.$inferInsert;

// Partial update type
export type UserUpdate = Partial<Omit<NewUser, 'id' | 'createdAt'>>;
```

### Using Types in Functions

```typescript
import type { User, NewUser, UserUpdate } from './schema/users';

async function createUser(data: NewUser): Promise<User> {
  const [user] = await db.insert(users).values(data).returning();
  return user;
}

async function updateUser(id: string, data: UserUpdate): Promise<User | undefined> {
  const [user] = await db
    .update(users)
    .set({ ...data, updatedAt: new Date() })
    .where(eq(users.id, id))
    .returning();
  return user;
}
```

---

## Relations

Define relations separately from table definitions for better organization:

```typescript
import { relations } from 'drizzle-orm';

export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
  comments: many(comments),
}));

export const postsRelations = relations(posts, ({ one, many }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
  comments: many(comments),
}));

export const commentsRelations = relations(comments, ({ one }) => ({
  author: one(users, {
    fields: [comments.authorId],
    references: [users.id],
  }),
  post: one(posts, {
    fields: [comments.postId],
    references: [posts.id],
  }),
}));
```

---

## Queries

### Basic Select

```typescript
import { eq, and, or, gt, lt, like, inArray, isNull } from 'drizzle-orm';

// Simple select
const allUsers = await db.select().from(users);

// With conditions
const activeUsers = await db
  .select()
  .from(users)
  .where(eq(users.isActive, true));

// Multiple conditions
const filteredUsers = await db
  .select()
  .from(users)
  .where(
    and(
      eq(users.isActive, true),
      gt(users.createdAt, new Date('2024-01-01'))
    )
  );

// Select specific columns
const userEmails = await db
  .select({ id: users.id, email: users.email })
  .from(users);
```

### Joins

```typescript
// Inner join
const postsWithAuthors = await db
  .select({
    post: posts,
    author: users,
  })
  .from(posts)
  .innerJoin(users, eq(posts.authorId, users.id));

// Left join
const usersWithPosts = await db
  .select({
    user: users,
    post: posts,
  })
  .from(users)
  .leftJoin(posts, eq(users.id, posts.authorId));
```

### Query with Relations (Eager Loading)

```typescript
// Using the query API for eager loading
const usersWithRelations = await db.query.users.findMany({
  with: {
    posts: {
      with: {
        comments: true,
      },
    },
  },
});

// With filtering
const activeUsersWithPosts = await db.query.users.findMany({
  where: eq(users.isActive, true),
  with: {
    posts: {
      where: eq(posts.status, 'published'),
    },
  },
});
```

### Pagination

```typescript
// Always use limit and offset for user-facing queries
const pageSize = 20;
const page = 1;

const paginatedPosts = await db
  .select()
  .from(posts)
  .where(eq(posts.status, 'published'))
  .orderBy(desc(posts.createdAt))
  .limit(pageSize)
  .offset((page - 1) * pageSize);

// Get total count for pagination
const [{ count }] = await db
  .select({ count: sql<number>`count(*)` })
  .from(posts)
  .where(eq(posts.status, 'published'));
```

### Aggregations

```typescript
import { sql, count, sum, avg, min, max } from 'drizzle-orm';

// Count
const [{ total }] = await db
  .select({ total: count() })
  .from(users)
  .where(eq(users.isActive, true));

// Group by with aggregation
const postsByAuthor = await db
  .select({
    authorId: posts.authorId,
    postCount: count(),
  })
  .from(posts)
  .groupBy(posts.authorId);
```

---

## Prepared Statements

Use prepared statements for frequently executed queries for extreme performance benefits:

```typescript
import { sql } from 'drizzle-orm';

// Prepared select
export const getUserById = db
  .select()
  .from(users)
  .where(eq(users.id, sql.placeholder('id')))
  .prepare('get_user_by_id');

// Usage
const user = await getUserById.execute({ id: userId });

// Prepared select with multiple placeholders
export const getUsersByStatus = db
  .select()
  .from(users)
  .where(
    and(
      eq(users.isActive, sql.placeholder('isActive')),
      gt(users.createdAt, sql.placeholder('since'))
    )
  )
  .limit(sql.placeholder('limit'))
  .prepare('get_users_by_status');

// Usage
const users = await getUsersByStatus.execute({
  isActive: true,
  since: new Date('2024-01-01'),
  limit: 10,
});

// Prepared insert
export const insertUser = db
  .insert(users)
  .values({
    email: sql.placeholder('email'),
    name: sql.placeholder('name'),
  })
  .returning()
  .prepare('insert_user');

// Usage
const [newUser] = await insertUser.execute({
  email: 'user@example.com',
  name: 'John Doe',
});
```

---

## Transactions

Use transactions for multi-step operations to maintain data consistency:

```typescript
// Basic transaction
const result = await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values(userData).returning();
  const [profile] = await tx
    .insert(profiles)
    .values({ userId: user.id, ...profileData })
    .returning();
  return { user, profile };
});

// Transaction with rollback on error
const result = await db.transaction(async (tx) => {
  try {
    const [order] = await tx.insert(orders).values(orderData).returning();

    // Insert order items
    await tx.insert(orderItems).values(
      items.map(item => ({ orderId: order.id, ...item }))
    );

    // Update inventory
    for (const item of items) {
      await tx
        .update(products)
        .set({
          stock: sql`${products.stock} - ${item.quantity}`
        })
        .where(eq(products.id, item.productId));
    }

    return order;
  } catch (error) {
    tx.rollback();
    throw error;
  }
});

// Nested transactions with savepoints
const result = await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values(userData).returning();

  await tx.transaction(async (nestedTx) => {
    // This creates a savepoint
    await nestedTx.insert(auditLogs).values({
      action: 'user_created',
      userId: user.id,
    });
  });

  return user;
});
```

---

## Migrations

**CRITICAL**: Always use package scripts for migrations. Never call `drizzle-kit` directly.

### Migration Commands

```bash
# Generate migration (creates SQL file from schema changes)
pnpm run db:generate

# Apply pending migrations
pnpm run db:migrate

# Push schema directly (development only - bypasses migrations)
pnpm run db:push

# View migration status
pnpm run db:status
```

### Drizzle Config Example

```typescript
// drizzle.config.ts
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/db/schema/*',
  out: './src/db/migrations',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
});
```

### Migration Best Practices

1. **Always generate migrations for schema changes** - Don't modify migration files manually
2. **Review generated SQL before applying** - Check the generated migration file
3. **Test migrations on a copy of production data** - Before applying to production
4. **Keep migrations small and focused** - One logical change per migration
5. **Never delete applied migrations** - They're part of the database history

---

## Performance Optimization

### Use Prepared Statements

```typescript
// GOOD: Prepared statement (compiled once, executed many times)
const getUser = db.select().from(users).where(eq(users.id, sql.placeholder('id'))).prepare();
await getUser.execute({ id: '123' });

// AVOID: Dynamic query (compiled every time)
await db.select().from(users).where(eq(users.id, '123'));
```

### Batch Operations

```typescript
// GOOD: Single batch insert
await db.insert(users).values([
  { email: 'user1@example.com' },
  { email: 'user2@example.com' },
  { email: 'user3@example.com' },
]);

// AVOID: Multiple individual inserts
for (const userData of usersData) {
  await db.insert(users).values(userData); // N+1 problem
}
```

### Selective Columns

```typescript
// GOOD: Select only needed columns
const userNames = await db
  .select({ id: users.id, name: users.name })
  .from(users);

// AVOID: Select all columns when only some are needed
const users = await db.select().from(users);
const userNames = users.map(u => ({ id: u.id, name: u.name }));
```

### Avoid N+1 Queries

```typescript
// GOOD: Use eager loading
const usersWithPosts = await db.query.users.findMany({
  with: { posts: true },
});

// GOOD: Use a join
const usersWithPosts = await db
  .select()
  .from(users)
  .leftJoin(posts, eq(users.id, posts.authorId));

// AVOID: N+1 pattern
const allUsers = await db.select().from(users);
for (const user of allUsers) {
  const userPosts = await db.select().from(posts).where(eq(posts.authorId, user.id));
  // Process...
}
```

### Use Indexes Effectively

```typescript
// Query that benefits from composite index
const results = await db
  .select()
  .from(posts)
  .where(
    and(
      eq(posts.authorId, authorId),
      eq(posts.status, 'published')
    )
  );

// Define composite index for this query pattern
// posts_author_status_idx ON (author_id, status)
```

---

## Common Pitfalls

### 1. Missing Indexes

```typescript
// BAD: No index on frequently queried column
const usersByEmail = await db
  .select()
  .from(users)
  .where(eq(users.email, email)); // Slow without index

// GOOD: Add index in schema definition
export const users = pgTable('users', {
  // ...columns
}, (table) => ({
  emailIdx: index('users_email_idx').on(table.email),
}));
```

### 2. Unbounded Queries

```typescript
// BAD: No limit - can return millions of rows
const allPosts = await db.select().from(posts);

// GOOD: Always use limit for user-facing queries
const posts = await db.select().from(posts).limit(100);
```

### 3. Unsafe Raw SQL

```typescript
// BAD: SQL injection vulnerability
const results = await db.execute(
  sql`SELECT * FROM users WHERE email = '${userInput}'`
);

// GOOD: Use parameterized queries
const results = await db.execute(
  sql`SELECT * FROM users WHERE email = ${userInput}`
);

// GOOD: Or use prepared statements
const getByEmail = db
  .select()
  .from(users)
  .where(eq(users.email, sql.placeholder('email')))
  .prepare();
await getByEmail.execute({ email: userInput });
```

### 4. N+1 Queries

See [Avoid N+1 Queries](#avoid-n1-queries) section above.

### 5. Missing Transactions

```typescript
// BAD: Multiple related operations without transaction
const [user] = await db.insert(users).values(userData).returning();
const [profile] = await db.insert(profiles).values({ userId: user.id }).returning();
// If profile insert fails, user is orphaned!

// GOOD: Use transaction for atomicity
const result = await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values(userData).returning();
  const [profile] = await tx.insert(profiles).values({ userId: user.id }).returning();
  return { user, profile };
});
```

### 6. Forgetting to Update `updatedAt`

```typescript
// BAD: updatedAt stays stale
await db.update(users).set({ name: newName }).where(eq(users.id, id));

// GOOD: Always update timestamp
await db
  .update(users)
  .set({ name: newName, updatedAt: new Date() })
  .where(eq(users.id, id));

// BETTER: Use $onUpdate in schema
updatedAt: timestamp('updated_at').defaultNow().notNull().$onUpdate(() => new Date()),
```

---

## Code Organization

### Recommended Directory Structure

```
db/
  index.ts           # Drizzle client initialization
  schema/
    index.ts         # Re-exports all schemas
    users.ts         # User table, types, and relations
    posts.ts         # Post table, types, and relations
    comments.ts      # Comment table, types, and relations
  queries/
    index.ts         # Re-exports all query modules
    users.ts         # User query functions and prepared statements
    posts.ts         # Post query functions and prepared statements
  migrations/        # Auto-generated migration files (don't edit manually)
```

### Schema File Template

```typescript
// db/schema/users.ts
import { pgTable, uuid, varchar, timestamp, boolean, index } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';
import { posts } from './posts';

// Table definition
export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  name: varchar('name', { length: 255 }),
  isActive: boolean('is_active').default(true).notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
}, (table) => ({
  emailIdx: index('users_email_idx').on(table.email),
}));

// Type exports
export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
export type UserUpdate = Partial<Omit<NewUser, 'id' | 'createdAt'>>;

// Relations
export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));
```

### Query File Template

```typescript
// db/queries/users.ts
import { eq, and, gt, sql } from 'drizzle-orm';
import { db } from '../index';
import { users, type User, type NewUser, type UserUpdate } from '../schema/users';

// Prepared statements
export const getUserById = db
  .select()
  .from(users)
  .where(eq(users.id, sql.placeholder('id')))
  .prepare('get_user_by_id');

export const getUserByEmail = db
  .select()
  .from(users)
  .where(eq(users.email, sql.placeholder('email')))
  .prepare('get_user_by_email');

// Query functions
export async function findUserById(id: string): Promise<User | undefined> {
  const [user] = await getUserById.execute({ id });
  return user;
}

export async function findUserByEmail(email: string): Promise<User | undefined> {
  const [user] = await getUserByEmail.execute({ email });
  return user;
}

export async function createUser(data: NewUser): Promise<User> {
  const [user] = await db.insert(users).values(data).returning();
  return user;
}

export async function updateUser(id: string, data: UserUpdate): Promise<User | undefined> {
  const [user] = await db
    .update(users)
    .set({ ...data, updatedAt: new Date() })
    .where(eq(users.id, id))
    .returning();
  return user;
}

export async function deleteUser(id: string): Promise<boolean> {
  const result = await db.delete(users).where(eq(users.id, id));
  return result.rowCount > 0;
}
```

---

## Validation Checklist

Before completing any task involving Drizzle ORM:

- [ ] Schema definitions have proper indexes for queried columns
- [ ] Types are exported using `$inferSelect` and `$inferInsert`
- [ ] Prepared statements are used for frequently executed queries
- [ ] Transactions wrap multi-step operations
- [ ] All user-facing queries use `limit()` for pagination
- [ ] No raw user input is concatenated into SQL
- [ ] N+1 query patterns are avoided (use eager loading or joins)
- [ ] `updatedAt` is updated on modifications
- [ ] Package scripts are used for migrations (never call drizzle-kit directly)
- [ ] Type checks pass (`pnpm run typecheck`)
- [ ] Tests pass (`pnpm run test`)
