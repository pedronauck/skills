---
name: stripe-subscriptions
description: Complete subscription billing system with Stripe integration, feature flags for plan gating, webhook handling, and billing portal.
---

# Stripe Subscriptions

Complete subscription billing system with Stripe integration, feature flags for plan gating, webhook handling, and billing portal.

## Prerequisites

Complete these recipes first (in order):

### Type-Safe Environment Configuration with better-env

Use better-env config modules for type-safe server/public env access, feature flags, and either-or credential constraints.

```bash
curl -H "Accept: text/markdown" https://fullstackrecipes.com/api/recipes/config-schema-setup
```

### Neon + Drizzle Setup

Connect a Next.js app to Neon Postgres using Drizzle ORM with optimized connection pooling for Vercel serverless functions.

```bash
curl -H "Accept: text/markdown" https://fullstackrecipes.com/api/recipes/neon-drizzle-setup
```

### Pino Logging Setup

Configure structured logging with Pino. Outputs human-readable colorized logs in development and structured JSON in production for log aggregation services.

```bash
curl -H "Accept: text/markdown" https://fullstackrecipes.com/api/recipes/pino-logging-setup
```

## Cookbook - Complete These Recipes in Order

### Feature Flags with Flags SDK

Implement feature flags using the Vercel Flags SDK with server-side evaluation, environment-based toggles, and Vercel Toolbar integration.

```bash
curl -H "Accept: text/markdown" https://fullstackrecipes.com/api/recipes/feature-flags-setup
```

### Stripe Subscriptions DB Sync

Complete subscription system with Stripe, Vercel Flags for plan configuration, webhook handling for syncing subscription state to Postgres, usage tracking, and billing portal integration.

```bash
curl -H "Accept: text/markdown" https://fullstackrecipes.com/api/recipes/stripe-sync
```
