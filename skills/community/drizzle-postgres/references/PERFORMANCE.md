# Performance Optimization

Comprehensive reference for PostgreSQL and Drizzle ORM performance optimization.

---

## Indexing Strategies

### B-Tree Indexes (Default)

Best for: equality, range queries, sorting, LIKE with left anchor.

```sql
-- Single column
CREATE INDEX users_email_idx ON users(email);

-- Composite (order matters!)
CREATE INDEX orders_user_date_idx ON orders(user_id, created_at DESC);

-- Unique
CREATE UNIQUE INDEX users_email_unique ON users(email);
```

**In Drizzle:**

```typescript
export const users = pgTable(
  "users",
  {
    email: text("email").notNull(),
    createdAt: timestamp("created_at").notNull(),
  },
  table => [index("users_email_idx").on(table.email), index("users_created_idx").on(table.createdAt)]
);
```

### Partial Indexes

Index only rows matching a condition:

```sql
-- Index only active users
CREATE INDEX active_users_email_idx ON users(email)
WHERE deleted_at IS NULL;

-- Index only pending orders
CREATE INDEX pending_orders_idx ON orders(created_at)
WHERE status = 'pending';
```

**Benefits:** Smaller size, faster updates, more efficient queries.

**In Drizzle:**

```typescript
}, (table) => [
  index('active_users_idx')
    .on(table.email)
    .where(sql`deleted_at IS NULL`),
]);
```

### Covering Indexes (INCLUDE)

Include columns for index-only scans:

```sql
CREATE INDEX orders_user_idx ON orders(user_id)
INCLUDE (status, total);

-- This query uses index-only scan (no table access)
SELECT status, total FROM orders WHERE user_id = 123;
```

### GIN Indexes for JSONB

| Class                 | Size   | Operators      | Best For      |
| --------------------- | ------ | -------------- | ------------- |
| `jsonb_ops` (default) | 60-80% | @>, ?, ?\|, ?& | Key existence |
| `jsonb_path_ops`      | 20-30% | @> only        | Containment   |

```sql
-- Default (supports key existence)
CREATE INDEX data_gin_idx ON events USING gin(data);

-- Smaller, faster for containment only
CREATE INDEX data_gin_path_idx ON events USING gin(data jsonb_path_ops);
```

### Expression Indexes

Index computed values:

```sql
-- Case-insensitive search
CREATE INDEX users_email_lower_idx ON users(lower(email));

-- Date extraction
CREATE INDEX orders_month_idx ON orders(date_trunc('month', created_at));

-- JSONB field
CREATE INDEX events_type_idx ON events((data->>'type'));
```

**Important:** Query must match expression exactly.

```sql
-- Uses index
SELECT * FROM users WHERE lower(email) = 'user@example.com';

-- Does NOT use index
SELECT * FROM users WHERE email = 'USER@example.com';
```

---

## Query Optimization

### EXPLAIN ANALYZE

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE user_id = '123' AND status = 'pending';
```

| Option  | Description                      |
| ------- | -------------------------------- |
| ANALYZE | Execute query, show actual times |
| BUFFERS | Show buffer/cache hits and reads |
| COSTS   | Show planner estimates           |
| TIMING  | Show per-node timing             |

### Reading Query Plans

**Key metrics:**

- `actual time`: Startup..total time in ms
- `rows`: Estimated vs actual row count
- `loops`: Number of iterations
- `Buffers: shared hit/read`: Cache hits vs disk reads

**Problem indicators:**

- Large discrepancy between estimated and actual rows
- High `shared read` (cold cache, missing indexes)
- Seq Scan on large tables
- Nested Loop with high loop count

### Example Analysis

```sql
-- Bad plan
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE user_id = '123' AND status = 'pending';

-- Seq Scan on orders (cost=0.00..50000.00)
--   Filter: (user_id = '123' AND status = 'pending')
--   Rows Removed by Filter: 999000
--   Buffers: shared hit=10000 read=40000

-- After adding index
-- Index Scan using orders_user_status_idx
--   Index Cond: (user_id = '123' AND status = 'pending')
--   Buffers: shared hit=10
```

---

## Drizzle Query Optimization

### Prepared Statements

```typescript
// Prepare once
const getUserById = db
  .select()
  .from(users)
  .where(eq(users.id, sql.placeholder("id")))
  .prepare("get_user_by_id");

// Execute many times (reuses plan)
const user1 = await getUserById.execute({ id: "uuid-1" });
const user2 = await getUserById.execute({ id: "uuid-2" });
```

### Avoid N+1 Queries

**Bad (N+1):**

```typescript
const posts = await db.select().from(posts);
for (const post of posts) {
  const author = await db.select().from(users).where(eq(users.id, post.authorId));
  // N+1 queries!
}
```

**Good (Relational Query):**

```typescript
const posts = await db.query.posts.findMany({
  with: { author: true },
});
// Single query with JOIN
```

**Good (Manual Join):**

```typescript
const posts = await db.select().from(posts).leftJoin(users, eq(posts.authorId, users.id));
```

### Select Only Needed Columns

```typescript
// Bad - selects all columns
const users = await db.select().from(users);

// Good - selects only needed columns
const users = await db.select({ id: users.id, email: users.email }).from(users);

// With relational queries
const users = await db.query.users.findMany({
  columns: { id: true, email: true },
});
```

### Batch Operations

```typescript
// Bad - individual inserts
for (const user of users) {
  await db.insert(usersTable).values(user);
}

// Good - batch insert
await db.insert(usersTable).values(users);

// For very large batches, chunk them
const BATCH_SIZE = 1000;
for (let i = 0; i < users.length; i += BATCH_SIZE) {
  await db.insert(usersTable).values(users.slice(i, i + BATCH_SIZE));
}
```

### Use Transactions for Multiple Operations

```typescript
// Bad - multiple round trips
const user = await db.insert(users).values({ ... }).returning();
const profile = await db.insert(profiles).values({ userId: user.id });

// Good - single transaction
await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values({ ... }).returning();
  await tx.insert(profiles).values({ userId: user.id });
});
```

---

## Connection Pooling

### Why Pool?

Each PostgreSQL connection uses ~10MB RAM. PgBouncer connections use ~2KB.

### PgBouncer Configuration

```ini
[databases]
myapp = host=localhost port=5432 dbname=myapp

[pgbouncer]
listen_port = 6432
listen_addr = 0.0.0.0
auth_type = scram-sha-256
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
min_pool_size = 10
reserve_pool_size = 5
```

### Pooling Modes

| Mode        | Connection Release     | Use Case            |
| ----------- | ---------------------- | ------------------- |
| Session     | After disconnect       | Legacy apps         |
| Transaction | After each transaction | Most applications   |
| Statement   | After each statement   | Simple queries only |

### Transaction Pooling Limitations

- No `SET SESSION` (use `SET LOCAL`)
- No `PREPARE` without config
- Temp tables must be created/dropped in same transaction

### Drizzle with postgres.js

postgres.js has built-in connection pooling:

```typescript
import postgres from "postgres";

const client = postgres(process.env.DATABASE_URL!, {
  max: 20, // Max connections
  idle_timeout: 30, // Close idle connections after 30s
  connect_timeout: 10, // Connection timeout
});
```

### Drizzle with node-postgres Pool

```typescript
import { Pool } from "pg";
import { drizzle } from "drizzle-orm/node-postgres";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 10000,
});

const db = drizzle(pool, { schema });
```

---

## Caching Strategies

### Query Result Caching

```typescript
import { Redis } from "ioredis";

const redis = new Redis();

async function getCachedUser(userId: string) {
  const cacheKey = `user:${userId}`;

  // Try cache first
  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  // Query database
  const user = await db.query.users.findFirst({
    where: eq(users.id, userId),
  });

  // Cache result
  if (user) {
    await redis.setex(cacheKey, 3600, JSON.stringify(user));
  }

  return user;
}
```

### Cache Invalidation

```typescript
// Invalidate on update
async function updateUser(userId: string, data: Partial<User>) {
  await db.update(users).set(data).where(eq(users.id, userId));
  await redis.del(`user:${userId}`);
}
```

---

## Pagination Best Practices

### Offset-Based (Simple, Slow for Large Offsets)

```typescript
async function getPage(page: number, pageSize = 20) {
  return db
    .select()
    .from(posts)
    .orderBy(desc(posts.createdAt))
    .limit(pageSize)
    .offset((page - 1) * pageSize);
}
```

### Cursor-Based (Better Performance)

```typescript
async function getPostsAfter(cursor?: string, limit = 20) {
  return db
    .select()
    .from(posts)
    .where(cursor ? lt(posts.id, cursor) : undefined)
    .orderBy(desc(posts.id))
    .limit(limit);
}

// Usage
const page1 = await getPostsAfter(undefined, 20);
const lastId = page1[page1.length - 1]?.id;
const page2 = await getPostsAfter(lastId, 20);
```

### Keyset Pagination (Most Efficient)

```typescript
async function getPostsAfter(cursor?: { createdAt: Date; id: string }, limit = 20) {
  return db
    .select()
    .from(posts)
    .where(
      cursor
        ? or(lt(posts.createdAt, cursor.createdAt), and(eq(posts.createdAt, cursor.createdAt), lt(posts.id, cursor.id)))
        : undefined
    )
    .orderBy(desc(posts.createdAt), desc(posts.id))
    .limit(limit);
}
```

---

## Bulk Operations

### Bulk Insert

```typescript
// Insert many rows efficiently
await db.insert(events).values(
  items.map(item => ({
    type: item.type,
    data: item.data,
    createdAt: new Date(),
  }))
);
```

### Bulk Update with CASE

```typescript
// Update multiple rows with different values
await db.execute(sql`
  UPDATE products
  SET price = CASE id
    ${sql.join(
      updates.map(u => sql`WHEN ${u.id} THEN ${u.price}`),
      sql` `
    )}
  END
  WHERE id IN ${sql`(${sql.join(
    updates.map(u => u.id),
    sql`, `
  )})`}
`);
```

### Bulk Upsert

```typescript
await db
  .insert(products)
  .values(products)
  .onConflictDoUpdate({
    target: products.sku,
    set: {
      price: sql`excluded.price`,
      updatedAt: new Date(),
    },
  });
```

---

## Performance Checklist

### PostgreSQL Configuration

- [ ] Set `shared_buffers` to 25% of RAM
- [ ] Set `effective_cache_size` to 50-75% of RAM
- [ ] Configure `work_mem` based on workload (OLTP: 4-16MB, OLAP: 64-256MB)
- [ ] Enable `io_method = worker` (PostgreSQL 18)
- [ ] Tune `io_workers` (~1/4 of CPU cores)

### Indexing

- [ ] Create indexes for foreign keys
- [ ] Use partial indexes for filtered subsets
- [ ] Use covering indexes for hot queries
- [ ] Use GIN with `jsonb_path_ops` for JSONB containment
- [ ] Monitor unused indexes and remove them

### Queries

- [ ] Use `EXPLAIN (ANALYZE, BUFFERS)` for optimization
- [ ] Use prepared statements for repeated queries
- [ ] Use relational queries API to avoid N+1
- [ ] Select only needed columns
- [ ] Use cursor-based pagination for large datasets

### Application

- [ ] Use connection pooling
- [ ] Batch insert/update operations
- [ ] Cache frequently accessed data
- [ ] Use transactions appropriately

### Maintenance

- [ ] Ensure autovacuum is configured
- [ ] Run `ANALYZE` after bulk data changes
- [ ] Monitor table/index bloat
- [ ] Reindex periodically (CONCURRENTLY)

---

## Monitoring Queries

### Slow Queries

```sql
-- Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1 second
```

### pg_stat_statements

```sql
-- Enable extension
CREATE EXTENSION pg_stat_statements;

-- Top queries by time
SELECT
  query,
  calls,
  mean_exec_time,
  total_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

### Index Efficiency

```sql
-- Index usage vs table size
SELECT
  t.tablename,
  pg_size_pretty(pg_table_size(t.tablename::regclass)) AS table_size,
  indexname,
  pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
  idx_scan AS scans
FROM pg_tables t
JOIN pg_stat_user_indexes i ON t.tablename = i.relname
WHERE t.schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```
