---
name: drizzle-orm
description: Expert guide for Drizzle ORM best practices, including schema definitions, queries, mutations, transactions, migrations, and performance optimization. Use when working with Drizzle ORM, database schemas, queries, or migrations.
allowed-tools: Read, Grep, Glob
---

# Drizzle ORM Developer Guide

This skill provides guidelines, patterns, and best practices for working with Drizzle ORM in this project.

## Quick Start

For detailed development guidelines, patterns, and code examples, refer to [references/patterns.md](references/patterns.md).

## Core Philosophy

- **Type-Safe by Default**: Leverage TypeScript and Drizzle's type inference to catch database errors at compile time
- **Performance First**: Use prepared statements and query optimization techniques
- **SQL Transparency**: Keep SQL queries readable and avoid over-abstraction
- **Minimal Overhead**: Drizzle is a thin layer - use it accordingly without unnecessary complexity

## Common Tasks

### Schema Definition

Organize schemas by domain in separate files. Use fluent constraint chaining and add indexes for frequently queried columns.

```typescript
export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});
```

### Type Exports

Always export table types for use in your application:

```typescript
export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
```

### Prepared Statements

Use prepared statements for frequently executed queries for extreme performance benefits:

```typescript
export const getUserById = db
  .select()
  .from(users)
  .where(eq(users.id, sql.placeholder('id')))
  .prepare();

// Usage
const user = await getUserById.execute({ id: userId });
```

### Transactions

Use transactions for multi-step operations to maintain data consistency:

```typescript
return db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values(userData).returning();
  const [profile] = await tx.insert(profiles).values({ userId: user.id, ...profileData }).returning();
  return { user, profile };
});
```

## Migration Commands

**CRITICAL**: Always use package scripts for migrations. Never call `drizzle-kit` directly.

- Backend: `pnpm run db:generate` (generates migration)
- Backend: `pnpm run db:migrate` (applies migrations)
- Landing: `pnpm run db:generate` (generates migration)
- Landing: `pnpm run db:migrate` (applies migrations)

## Code Organization

```
db/
  index.ts           (Drizzle client initialization)
  schema/
    users.ts         (User table & relations)
    posts.ts         (Post table & relations)
  queries/
    users.ts         (User query functions)
    posts.ts         (Post query functions)
  migrations/        (Auto-generated migration files)
```

## Common Pitfalls to Avoid

1. **Missing Indexes**: Always index columns used in WHERE, JOIN, and ORDER BY clauses
2. **Unbounded Queries**: Always use `limit()` and `offset()` for user-facing queries
3. **Unsafe Raw SQL**: Never concatenate user input into raw SQL - use `sql.placeholder()`
4. **N+1 Queries**: Use eager loading with `with()` or batch queries
5. **Missing Transactions**: Wrap multi-step operations in transactions

## Validation Checklist

Before finishing a task involving Drizzle ORM:

- [ ] Check schema definitions have proper indexes for queried columns
- [ ] Verify prepared statements are used for repeated queries
- [ ] Ensure transactions wrap multi-step operations
- [ ] Use package scripts for migrations (never call drizzle-kit directly)
- [ ] Run type checks (`pnpm run typecheck`) and tests (`pnpm run test`)

For detailed rules and code examples, consult [references/patterns.md](references/patterns.md).
