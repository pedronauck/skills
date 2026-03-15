# Drizzle Query Patterns

Comprehensive reference for querying PostgreSQL with Drizzle ORM.

---

## Query Operators

### Imports

```typescript
import {
  eq, // =
  ne, // <>
  gt, // >
  gte, // >=
  lt, // <
  lte, // <=
  like, // LIKE (case-sensitive)
  ilike, // ILIKE (case-insensitive)
  notLike,
  notIlike,
  inArray, // IN
  notInArray, // NOT IN
  isNull,
  isNotNull,
  between,
  notBetween,
  and,
  or,
  not,
  exists,
  notExists,
  arrayContains,
  arrayContained,
  arrayOverlaps,
  sql,
} from "drizzle-orm";
```

---

## Select Queries

### Basic Select

```typescript
// All columns
const allUsers = await db.select().from(users);

// Specific columns
const emails = await db
  .select({
    id: users.id,
    email: users.email,
  })
  .from(users);

// With alias
const result = await db
  .select({
    identifier: users.id,
    mail: users.email,
  })
  .from(users);
```

### Where Clause

```typescript
// Single condition
const user = await db.select().from(users).where(eq(users.id, userId));

// Multiple conditions (AND)
const activeAdmins = await db
  .select()
  .from(users)
  .where(and(eq(users.status, "active"), eq(users.role, "admin")));

// OR conditions
const flaggedUsers = await db
  .select()
  .from(users)
  .where(or(eq(users.status, "suspended"), gt(users.warningCount, 3)));

// Complex nested conditions
const result = await db
  .select()
  .from(users)
  .where(and(eq(users.status, "active"), or(eq(users.role, "admin"), gt(users.score, 100))));
```

### Comparison Operators

```typescript
// Equality
.where(eq(users.status, 'active'))

// Not equal
.where(ne(users.status, 'deleted'))

// Greater than / less than
.where(gt(users.age, 18))
.where(gte(users.age, 18))
.where(lt(users.age, 65))
.where(lte(users.age, 65))

// Between
.where(between(users.age, 18, 65))
.where(notBetween(products.price, 0, 10))

// Null checks
.where(isNull(users.deletedAt))
.where(isNotNull(users.verifiedAt))

// IN / NOT IN
.where(inArray(users.status, ['active', 'pending']))
.where(notInArray(users.role, ['banned', 'suspended']))
```

### Pattern Matching

```typescript
// Case-sensitive LIKE
.where(like(users.name, 'John%'))      // Starts with
.where(like(users.name, '%Smith'))     // Ends with
.where(like(users.name, '%John%'))     // Contains

// Case-insensitive ILIKE
.where(ilike(users.email, '%@gmail.com'))

// Negated
.where(notLike(users.name, 'Test%'))
.where(notIlike(users.email, '%spam%'))
```

### Conditional Filters

Build dynamic queries by passing `undefined` to skip conditions:

```typescript
interface Filters {
  search?: string;
  categoryId?: string;
  minPrice?: number;
  maxPrice?: number;
}

async function getPosts(filters: Filters) {
  return db
    .select()
    .from(posts)
    .where(
      and(
        eq(posts.published, true),
        filters.search ? ilike(posts.title, `%${filters.search}%`) : undefined,
        filters.categoryId ? eq(posts.categoryId, filters.categoryId) : undefined,
        filters.minPrice ? gte(posts.price, filters.minPrice) : undefined,
        filters.maxPrice ? lte(posts.price, filters.maxPrice) : undefined
      )
    );
}
```

---

## Ordering & Pagination

### Order By

```typescript
import { asc, desc } from 'drizzle-orm';

// Single column
const newest = await db
  .select()
  .from(posts)
  .orderBy(desc(posts.createdAt));

// Multiple columns
const sorted = await db
  .select()
  .from(users)
  .orderBy(asc(users.lastName), asc(users.firstName));

// Nulls handling
.orderBy(sql`${users.name} NULLS LAST`)
```

### Limit & Offset

```typescript
// Basic pagination
const page1 = await db.select().from(posts).orderBy(desc(posts.createdAt)).limit(20).offset(0);

// Page helper
async function getPage(page: number, pageSize: number = 20) {
  return db
    .select()
    .from(posts)
    .orderBy(desc(posts.createdAt))
    .limit(pageSize)
    .offset((page - 1) * pageSize);
}
```

### Cursor-Based Pagination (Better Performance)

```typescript
async function getPostsAfter(cursor?: string, limit = 20) {
  return db
    .select()
    .from(posts)
    .where(cursor ? lt(posts.id, cursor) : undefined)
    .orderBy(desc(posts.id))
    .limit(limit);
}
```

---

## Joins

### Left Join

```typescript
const usersWithPosts = await db.select().from(users).leftJoin(posts, eq(posts.authorId, users.id));

// Result type: { users: User, posts: Post | null }[]
```

### Inner Join

```typescript
const usersWithPosts = await db.select().from(users).innerJoin(posts, eq(posts.authorId, users.id));

// Only users who have posts
```

### Right Join

```typescript
const postsWithUsers = await db.select().from(posts).rightJoin(users, eq(posts.authorId, users.id));
```

### Full Join

```typescript
const all = await db.select().from(users).fullJoin(posts, eq(posts.authorId, users.id));
```

### Multiple Joins

```typescript
const fullData = await db
  .select({
    order: orders,
    user: users,
    product: products,
  })
  .from(orders)
  .leftJoin(users, eq(orders.userId, users.id))
  .leftJoin(products, eq(orders.productId, products.id));
```

### Join with Selected Columns

```typescript
const result = await db
  .select({
    userName: users.name,
    userEmail: users.email,
    postTitle: posts.title,
    postDate: posts.createdAt,
  })
  .from(users)
  .innerJoin(posts, eq(posts.authorId, users.id));
```

---

## Aggregations

### Imports

```typescript
import { count, sum, avg, min, max, countDistinct } from "drizzle-orm";
```

### Basic Aggregates

```typescript
// Count all rows
const [{ total }] = await db.select({ total: count() }).from(users);

// Count with condition
const [{ activeCount }] = await db.select({ activeCount: count() }).from(users).where(eq(users.status, "active"));

// Count distinct
const [{ uniqueAuthors }] = await db.select({ uniqueAuthors: countDistinct(posts.authorId) }).from(posts);

// Sum
const [{ totalRevenue }] = await db.select({ totalRevenue: sum(orders.amount) }).from(orders);

// Average
const [{ avgPrice }] = await db.select({ avgPrice: avg(products.price) }).from(products);

// Min / Max
const [{ cheapest, expensive }] = await db
  .select({
    cheapest: min(products.price),
    expensive: max(products.price),
  })
  .from(products);
```

### Group By

```typescript
const postsByAuthor = await db
  .select({
    authorId: posts.authorId,
    postCount: count(),
    totalViews: sum(posts.views),
  })
  .from(posts)
  .groupBy(posts.authorId);
```

### Having

```typescript
const prolificAuthors = await db
  .select({
    authorId: posts.authorId,
    postCount: count(),
  })
  .from(posts)
  .groupBy(posts.authorId)
  .having(gt(count(), 10));
```

### Group By with Join

```typescript
const authorStats = await db
  .select({
    authorName: users.name,
    postCount: count(posts.id),
    totalViews: sum(posts.views),
  })
  .from(users)
  .leftJoin(posts, eq(posts.authorId, users.id))
  .groupBy(users.id, users.name);
```

---

## Subqueries

### Subquery in FROM

```typescript
const subquery = db
  .select({
    authorId: posts.authorId,
    postCount: sql<number>`count(*)`.as("post_count"),
  })
  .from(posts)
  .groupBy(posts.authorId)
  .as("author_stats");

const usersWithStats = await db
  .select({
    user: users,
    postCount: subquery.postCount,
  })
  .from(users)
  .leftJoin(subquery, eq(users.id, subquery.authorId));
```

### Subquery in WHERE (EXISTS)

```typescript
// Users who have at least one post
const usersWithPosts = await db
  .select()
  .from(users)
  .where(exists(db.select().from(posts).where(eq(posts.authorId, users.id))));

// Users who have NO posts
const usersWithoutPosts = await db
  .select()
  .from(users)
  .where(notExists(db.select().from(posts).where(eq(posts.authorId, users.id))));
```

### Scalar Subquery

```typescript
const postsWithAuthorCount = await db
  .select({
    post: posts,
    authorPostCount: db.select({ count: count() }).from(posts).where(eq(posts.authorId, posts.authorId)),
  })
  .from(posts);
```

---

## Insert Operations

### Single Insert

```typescript
const [newUser] = await db
  .insert(users)
  .values({
    email: "user@example.com",
    name: "John Doe",
  })
  .returning();
```

### Multiple Insert

```typescript
const newUsers = await db
  .insert(users)
  .values([
    { email: "user1@example.com", name: "User 1" },
    { email: "user2@example.com", name: "User 2" },
    { email: "user3@example.com", name: "User 3" },
  ])
  .returning();
```

### Upsert (On Conflict)

```typescript
// Update on conflict
await db
  .insert(users)
  .values({ email: "user@example.com", name: "John" })
  .onConflictDoUpdate({
    target: users.email,
    set: {
      name: "John Updated",
      updatedAt: new Date(),
    },
  });

// Ignore on conflict
await db.insert(users).values({ email: "user@example.com", name: "John" }).onConflictDoNothing();

// Composite key conflict
await db
  .insert(usersToGroups)
  .values({ userId, groupId })
  .onConflictDoNothing({
    target: [usersToGroups.userId, usersToGroups.groupId],
  });
```

### Insert from Select

```typescript
await db.insert(archivedPosts).select().from(posts).where(lt(posts.createdAt, oneYearAgo));
```

---

## Update Operations

### Basic Update

```typescript
await db.update(users).set({ status: "active" }).where(eq(users.id, userId));
```

### Update with Returning

```typescript
const [updated] = await db
  .update(users)
  .set({
    status: "active",
    updatedAt: new Date(),
  })
  .where(eq(users.id, userId))
  .returning();
```

### Increment/Decrement

```typescript
// Increment
await db
  .update(posts)
  .set({ views: sql`${posts.views} + 1` })
  .where(eq(posts.id, postId));

// Decrement with floor
await db
  .update(products)
  .set({ stock: sql`GREATEST(${products.stock} - 1, 0)` })
  .where(eq(products.id, productId));
```

### Conditional Update

```typescript
await db
  .update(users)
  .set({
    status: sql`CASE WHEN ${users.score} > 100 THEN 'gold' ELSE 'silver' END`,
  })
  .where(eq(users.role, "member"));
```

---

## Delete Operations

### Basic Delete

```typescript
await db.delete(users).where(eq(users.id, userId));
```

### Delete with Returning

```typescript
const [deleted] = await db.delete(users).where(eq(users.id, userId)).returning();
```

### Soft Delete

```typescript
await db.update(users).set({ deletedAt: new Date() }).where(eq(users.id, userId));
```

### Delete with Subquery

```typescript
// Delete inactive users who have no posts
await db
  .delete(users)
  .where(and(eq(users.status, "inactive"), notExists(db.select().from(posts).where(eq(posts.authorId, users.id)))));
```

---

## Raw SQL

### SQL Template

```typescript
import { sql } from 'drizzle-orm';

// In select
const result = await db
  .select({
    id: users.id,
    fullName: sql<string>`${users.firstName} || ' ' || ${users.lastName}`,
  })
  .from(users);

// In where
.where(sql`${users.email} ~* ${pattern}`)  // PostgreSQL regex

// Typed raw query
const users = await db.execute<{ id: string; name: string }>(
  sql`SELECT id, name FROM users WHERE status = 'active'`
);
```

### SQL Operators

```typescript
// JSON operators
.where(sql`${events.data}->>'type' = 'purchase'`)
.where(sql`${events.data} @> '{"status": "active"}'::jsonb`)

// Array operators
.where(sql`${posts.tags} @> ARRAY['typescript']`)

// Full-text search
.where(sql`to_tsvector('english', ${posts.content}) @@ plainto_tsquery('english', ${searchTerm})`)
```

---

## Prepared Statements

Improve performance by preparing queries once:

```typescript
// Prepare
const getUserById = db
  .select()
  .from(users)
  .where(eq(users.id, sql.placeholder("id")))
  .prepare("get_user_by_id");

// Execute multiple times
const user1 = await getUserById.execute({ id: "uuid-1" });
const user2 = await getUserById.execute({ id: "uuid-2" });

// Prepared insert
const createUser = db
  .insert(users)
  .values({
    email: sql.placeholder("email"),
    name: sql.placeholder("name"),
  })
  .returning()
  .prepare("create_user");

const newUser = await createUser.execute({
  email: "user@example.com",
  name: "John",
});
```

---

## Transactions

### Basic Transaction

```typescript
const result = await db.transaction(async tx => {
  const [user] = await tx.insert(users).values({ email, name }).returning();
  await tx.insert(profiles).values({ userId: user.id, bio: "" });
  return user;
});
```

### Nested Transactions (Savepoints)

```typescript
await db.transaction(async (tx) => {
  await tx.insert(users).values({ ... });

  try {
    await tx.transaction(async (tx2) => {
      // Creates savepoint
      await tx2.insert(riskyTable).values({ ... });
      // If this throws, only tx2 is rolled back
    });
  } catch (e) {
    // Handle savepoint rollback
  }

  // Outer transaction continues
  await tx.insert(logs).values({ ... });
});
```

### Rollback

```typescript
await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values({ ... }).returning();

  const balance = await checkBalance(user.id);
  if (balance < 0) {
    tx.rollback();  // Throws to abort entire transaction
  }

  await tx.insert(orders).values({ userId: user.id, ... });
});
```

### Transaction Isolation

```typescript
await db.transaction(
  async tx => {
    // ...
  },
  {
    isolationLevel: "serializable", // read committed, repeatable read, serializable
    accessMode: "read write", // read only, read write
  }
);
```
