# Deploying to Vercel

> Source: `src/content/docs/connect/vercel.mdx`
> Canonical URL: https://rivet.dev/docs/connect/vercel
> Description: Deploy your RivetKit app to Vercel.

---
## Steps

### Prerequisites

- [Vercel account](https://vercel.com/)
- Your RivetKit app
  - If you don't have one, see the [Quickstart](/docs/actors/quickstart) page or our [Examples](https://github.com/rivet-dev/rivet/tree/main/examples)
- Access to the [Rivet Cloud](https://dashboard.rivet.dev/) or a [self-hosted Rivet Engine](/docs/general/self-hosting)

### Prepare Your Application

Make sure your project is configured correctly for Vercel deployment.

### Next.js

Your Next.js project should have the following structure:

- `src/app/api/rivet/[...all]/route.ts`: RivetKit route handler
- `src/actors.ts`: Actor definitions and registry

See the [Next.js quickstart](/docs/actors/quickstart/next-js) or the [Next.js example](https://github.com/rivet-dev/rivet/tree/main/examples/next-js) to get started.

### Hono

Your Hono project needs:

1. A `vercel.json` file with the Hono framework specified:

```json vercel.json
{
  "framework": "hono"
}
```

2. Your server file must import from `"hono"` for Vercel to recognize the framework:

```ts src/server.ts @nocheck
// You MUST import from "hono" for Vercel to detect this as a Hono app
import { Hono } from "hono";
import { registry } from "./actors.ts";

const app = new Hono();
app.all("/api/rivet/*", (c) => registry.handler(c.req.raw));
export default app;
```

3. Use `.ts` file extensions in imports and configure your `tsconfig.json`:

```json tsconfig.json
{
  "compilerOptions": {
    "allowImportingTsExtensions": true,
    "rewriteRelativeImportExtensions": true
  }
}
```

See the [Hello World example](https://github.com/rivet-dev/rivet/tree/main/examples/hello-world) for a complete example.

For more details on Hono deployments, see [Vercel's Hono documentation](https://vercel.com/docs/frameworks/backend/hono).

### Other

Vercel currently supports Next.js and Hono frameworks for RivetKit deployments.

For other frameworks, consider deploying to [Railway](/docs/connect/railway), [Kubernetes](/docs/connect/kubernetes), or another platform.

### Deploy to Vercel

1. Connect your GitHub repository to Vercel
2. Vercel will deploy your app

### Configure Preview Deployments (Recommended)

Add a GitHub action to automatically create isolated Rivet namespaces for each PR:

1. Add these secrets to your GitHub repository:
   - `RIVET_CLOUD_TOKEN`: Get from [Rivet Dashboard](https://dashboard.rivet.dev) → Settings → Advanced → Cloud API Tokens
   - `VERCEL_TOKEN`: Get from [Vercel Account Settings](https://vercel.com/account/tokens)

2. Create `.github/workflows/rivet-preview.yml`:

```yaml
name: Rivet Preview

on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches: [main]

concurrency:
  group: rivet-preview-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

jobs:
  rivet-preview:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - uses: rivet-dev/preview-namespace-action@v1
        with:
          platform: vercel
          rivet-token: ${{ secrets.RIVET_CLOUD_TOKEN }}
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
```

## Troubleshooting

```
Error: ENOENT: no such file or directory, mkdir '.../rivetkit/.../state'
```

**Cause:** The `RIVET_ENDPOINT` environment variable is not configured. RivetKit falls back to the file system driver, which fails in Vercel's read-only serverless environment.

**Solution:** Ensure `RIVET_ENDPOINT` is set with your Rivet endpoint using the URL auth format:

```
RIVET_ENDPOINT=https://my-namespace:sk_****@api.rivet.dev
```

If using the [preview-namespace-action](https://github.com/rivet-dev/preview-namespace-action), this is configured automatically.

The `/api/rivet/metadata` endpoint returns data but `clientEndpoint`, `clientNamespace`, and `clientToken` are missing.

**Cause:** The `RIVET_PUBLIC_ENDPOINT` environment variable is not configured. This tells the metadata endpoint what connection info to provide to clients.

**Solution:** Set `RIVET_PUBLIC_ENDPOINT` with the publishable token (for client access):

```
RIVET_PUBLIC_ENDPOINT=https://my-namespace:pk_****@api.rivet.dev
```

If using the [preview-namespace-action](https://github.com/rivet-dev/preview-namespace-action), this is configured automatically.

Rivet fails to connect to your Vercel deployment with a 401 error mentioning "Authentication Required".

**Cause:** [Vercel Deployment Protection](https://vercel.com/docs/security/deployment-protection) is blocking requests from Rivet.

**Solution:**

1. Create a bypass secret in your Vercel project settings
2. In Rivet, go to **Settings > Providers**
3. Click the three dots on your provider and select **Edit**
4. Click **Add Header** and add `x-vercel-protection-bypass` with your bypass secret

If using the [preview-namespace-action](https://github.com/rivet-dev/preview-namespace-action), this is configured automatically.

_Source doc path: /docs/connect/vercel_
