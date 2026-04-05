# Drizzle Relations & Relational Queries

Comprehensive reference for defining relations and using the relational queries API.

---

## Overview

Drizzle has two query APIs:

| API                             | Use Case                             | N+1 Safe |
| ------------------------------- | ------------------------------------ | -------- |
| **SQL-like** (`db.select()...`) | Complex queries, joins, aggregations | Manual   |
| **Relational** (`db.query...`)  | Nested data, simple CRUD             | Yes      |

Relations are **application-level** (not database constraints). They enable the relational queries API.

---

## Defining Relations

### Imports

```typescript
import { relations } from "drizzle-orm";
import { pgTable, uuid, text, timestamp, integer } from "drizzle-orm/pg-core";
```

---

## One-to-Many

A user has many posts. A post belongs to one user.

```typescript
// Tables
export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  name: text("name").notNull(),
});

export const posts = pgTable("posts", {
  id: uuid("id").primaryKey().defaultRandom(),
  title: text("title").notNull(),
  authorId: uuid("author_id")
    .notNull()
    .references(() => users.id),
});

// Relations
export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
}));
```

### Query Examples

```typescript
// Get user with all their posts
const userWithPosts = await db.query.users.findFirst({
  where: eq(users.id, userId),
  with: { posts: true },
});

// Get post with author
const postWithAuthor = await db.query.posts.findFirst({
  where: eq(posts.id, postId),
  with: { author: true },
});
```

---

## One-to-One

A user has one profile. A profile belongs to one user.

```typescript
// Tables
export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  email: text("email").notNull(),
});

export const profiles = pgTable("profiles", {
  id: uuid("id").primaryKey().defaultRandom(),
  userId: uuid("user_id")
    .notNull()
    .unique()
    .references(() => users.id),
  bio: text("bio"),
  avatarUrl: text("avatar_url"),
});

// Relations
export const usersRelations = relations(users, ({ one }) => ({
  profile: one(profiles),
}));

export const profilesRelations = relations(profiles, ({ one }) => ({
  user: one(users, {
    fields: [profiles.userId],
    references: [users.id],
  }),
}));
```

### Query Examples

```typescript
// Get user with profile
const userWithProfile = await db.query.users.findFirst({
  where: eq(users.id, userId),
  with: { profile: true },
});

// Get profile with user
const profileWithUser = await db.query.profiles.findFirst({
  where: eq(profiles.userId, userId),
  with: { user: true },
});
```

---

## Many-to-Many

Users belong to many groups. Groups have many users.

```typescript
// Tables
export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  name: text("name").notNull(),
});

export const groups = pgTable("groups", {
  id: uuid("id").primaryKey().defaultRandom(),
  name: text("name").notNull(),
});

// Junction table
export const usersToGroups = pgTable(
  "users_to_groups",
  {
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    groupId: uuid("group_id")
      .notNull()
      .references(() => groups.id, { onDelete: "cascade" }),
    joinedAt: timestamp("joined_at").notNull().defaultNow(),
    role: text("role").notNull().default("member"),
  },
  table => [primaryKey({ columns: [table.userId, table.groupId] })]
);

// Relations
export const usersRelations = relations(users, ({ many }) => ({
  usersToGroups: many(usersToGroups),
}));

export const groupsRelations = relations(groups, ({ many }) => ({
  usersToGroups: many(usersToGroups),
}));

export const usersToGroupsRelations = relations(usersToGroups, ({ one }) => ({
  user: one(users, {
    fields: [usersToGroups.userId],
    references: [users.id],
  }),
  group: one(groups, {
    fields: [usersToGroups.groupId],
    references: [groups.id],
  }),
}));
```

### Query Examples

```typescript
// Get user with all groups
const userWithGroups = await db.query.users.findFirst({
  where: eq(users.id, userId),
  with: {
    usersToGroups: {
      with: { group: true },
    },
  },
});

// Flatten the result
const groups = userWithGroups?.usersToGroups.map(utg => ({
  ...utg.group,
  joinedAt: utg.joinedAt,
  role: utg.role,
}));

// Get group with all members
const groupWithMembers = await db.query.groups.findFirst({
  where: eq(groups.id, groupId),
  with: {
    usersToGroups: {
      with: { user: true },
    },
  },
});
```

---

## Self-Referential

A category can have a parent category and child categories.

```typescript
import { AnyPgColumn } from "drizzle-orm/pg-core";

export const categories = pgTable("categories", {
  id: uuid("id").primaryKey().defaultRandom(),
  name: text("name").notNull(),
  parentId: uuid("parent_id").references((): AnyPgColumn => categories.id),
});

export const categoriesRelations = relations(categories, ({ one, many }) => ({
  parent: one(categories, {
    fields: [categories.parentId],
    references: [categories.id],
    relationName: "parent",
  }),
  children: many(categories, {
    relationName: "parent",
  }),
}));
```

### Query Examples

```typescript
// Get category with parent and children
const category = await db.query.categories.findFirst({
  where: eq(categories.id, categoryId),
  with: {
    parent: true,
    children: true,
  },
});

// Get full tree (recursive CTE needed for deep trees)
const rootCategories = await db.query.categories.findMany({
  where: isNull(categories.parentId),
  with: {
    children: {
      with: {
        children: true, // 2 levels deep
      },
    },
  },
});
```

---

## Relational Queries API

### Setup

```typescript
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

const client = postgres(process.env.DATABASE_URL!);
export const db = drizzle(client, { schema }); // Pass schema!
```

### findMany

```typescript
// All users
const allUsers = await db.query.users.findMany();

// With filter
const activeUsers = await db.query.users.findMany({
  where: eq(users.status, "active"),
});

// With ordering
const sortedUsers = await db.query.users.findMany({
  orderBy: [desc(users.createdAt)],
});

// With pagination
const page = await db.query.users.findMany({
  limit: 20,
  offset: 40,
});
```

### findFirst

```typescript
// First matching
const user = await db.query.users.findFirst({
  where: eq(users.email, email),
});

// Returns undefined if not found
if (!user) {
  throw new NotFoundError();
}
```

### With Relations

```typescript
// Single relation
const userWithPosts = await db.query.users.findFirst({
  where: eq(users.id, userId),
  with: { posts: true },
});

// Multiple relations
const userWithAll = await db.query.users.findFirst({
  where: eq(users.id, userId),
  with: {
    posts: true,
    profile: true,
    usersToGroups: {
      with: { group: true },
    },
  },
});

// Nested relations
const postWithAll = await db.query.posts.findFirst({
  where: eq(posts.id, postId),
  with: {
    author: {
      with: { profile: true },
    },
    comments: {
      with: { author: true },
    },
  },
});
```

### Filtering Relations

```typescript
const userWithRecentPosts = await db.query.users.findFirst({
  where: eq(users.id, userId),
  with: {
    posts: {
      where: gt(posts.createdAt, oneWeekAgo),
      orderBy: [desc(posts.createdAt)],
      limit: 10,
    },
  },
});
```

### Selecting Columns

```typescript
// Select specific columns
const userBasic = await db.query.users.findFirst({
  columns: {
    id: true,
    email: true,
    // name: false  (excluded by default when using columns)
  },
});

// Exclude columns
const userWithoutPassword = await db.query.users.findFirst({
  columns: {
    password: false,
  },
});

// Select columns on relations
const userWithPostTitles = await db.query.users.findFirst({
  columns: { id: true, name: true },
  with: {
    posts: {
      columns: { id: true, title: true },
    },
  },
});
```

### Custom Extras

```typescript
// Add computed fields
const usersWithPostCount = await db.query.users.findMany({
  extras: {
    postCount: sql<number>`(
      SELECT count(*) FROM posts WHERE posts.author_id = users.id
    )`.as("post_count"),
  },
});
```

---

## Complex Examples

### Blog with Full Relations

```typescript
// Schema
export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  name: text("name").notNull(),
  email: text("email").notNull().unique(),
});

export const posts = pgTable("posts", {
  id: uuid("id").primaryKey().defaultRandom(),
  title: text("title").notNull(),
  content: text("content").notNull(),
  authorId: uuid("author_id")
    .notNull()
    .references(() => users.id),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const comments = pgTable("comments", {
  id: uuid("id").primaryKey().defaultRandom(),
  content: text("content").notNull(),
  postId: uuid("post_id")
    .notNull()
    .references(() => posts.id),
  authorId: uuid("author_id")
    .notNull()
    .references(() => users.id),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const likes = pgTable(
  "likes",
  {
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id),
    postId: uuid("post_id")
      .notNull()
      .references(() => posts.id),
  },
  table => [primaryKey({ columns: [table.userId, table.postId] })]
);

// Relations
export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
  comments: many(comments),
  likes: many(likes),
}));

export const postsRelations = relations(posts, ({ one, many }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
  comments: many(comments),
  likes: many(likes),
}));

export const commentsRelations = relations(comments, ({ one }) => ({
  post: one(posts, {
    fields: [comments.postId],
    references: [posts.id],
  }),
  author: one(users, {
    fields: [comments.authorId],
    references: [users.id],
  }),
}));

export const likesRelations = relations(likes, ({ one }) => ({
  user: one(users, {
    fields: [likes.userId],
    references: [users.id],
  }),
  post: one(posts, {
    fields: [likes.postId],
    references: [posts.id],
  }),
}));
```

### Query Full Post

```typescript
const fullPost = await db.query.posts.findFirst({
  where: eq(posts.id, postId),
  with: {
    author: {
      columns: { id: true, name: true },
    },
    comments: {
      orderBy: [desc(comments.createdAt)],
      with: {
        author: {
          columns: { id: true, name: true },
        },
      },
    },
    likes: {
      with: {
        user: {
          columns: { id: true, name: true },
        },
      },
    },
  },
});

// Result structure:
// {
//   id, title, content, authorId, createdAt,
//   author: { id, name },
//   comments: [{ id, content, createdAt, author: { id, name } }],
//   likes: [{ userId, postId, user: { id, name } }],
// }
```

### Feed Query

```typescript
const feed = await db.query.posts.findMany({
  where: eq(posts.published, true),
  orderBy: [desc(posts.createdAt)],
  limit: 20,
  columns: {
    id: true,
    title: true,
    createdAt: true,
  },
  with: {
    author: {
      columns: { id: true, name: true },
    },
  },
  extras: {
    commentCount: sql<number>`(
      SELECT count(*) FROM comments WHERE comments.post_id = posts.id
    )`.as("comment_count"),
    likeCount: sql<number>`(
      SELECT count(*) FROM likes WHERE likes.post_id = posts.id
    )`.as("like_count"),
  },
});
```

---

## Type Inference

### Basic Types

```typescript
import type { InferSelectModel, InferInsertModel } from "drizzle-orm";

type User = InferSelectModel<typeof users>;
type NewUser = InferInsertModel<typeof users>;
```

### Query Result Types

```typescript
// Type from a specific query result
type UserWithPosts = Awaited<
  ReturnType<
    typeof db.query.users.findFirst<{
      with: { posts: true };
    }>
  >
>;

// Or infer from actual query
const getUser = async (id: string) => {
  return db.query.users.findFirst({
    where: eq(users.id, id),
    with: { posts: true },
  });
};

type UserWithPosts = NonNullable<Awaited<ReturnType<typeof getUser>>>;
```

### Partial Select Types

```typescript
const result = await db
  .select({
    id: users.id,
    email: users.email,
  })
  .from(users);

type UserBasic = (typeof result)[number];
// { id: string; email: string }
```

---

## Relations vs Joins

### When to Use Relations (Relational Queries)

- Simple CRUD operations
- Fetching nested/hierarchical data
- When you want automatic N+1 prevention
- When the result should be nested objects

### When to Use Joins (SQL-like Queries)

- Complex aggregations
- Filtering based on related data
- Custom column selection across tables
- Performance-critical queries with specific needs

### Example Comparison

```typescript
// Relational - nested result
const userWithPosts = await db.query.users.findFirst({
  where: eq(users.id, userId),
  with: { posts: true },
});
// { id, name, posts: [{ id, title }, ...] }

// Join - flat result
const userWithPosts = await db
  .select()
  .from(users)
  .leftJoin(posts, eq(posts.authorId, users.id))
  .where(eq(users.id, userId));
// [{ users: { id, name }, posts: { id, title } | null }, ...]
```
