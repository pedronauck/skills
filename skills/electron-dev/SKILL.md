---
name: electron-dev
description: Expert guide for Electron development with Electron Vite and Electron Builder. Use when developing Electron applications, working with main/renderer processes, IPC communication, preload scripts, security configuration, native module handling, or build/distribution setup.
allowed-tools: Read, Grep, Glob
---

# Electron Development Guide

This skill provides guidelines, patterns, and best practices for building production-grade Electron applications using Electron Vite and Electron Builder.

## Quick Start

1. **Core Rules**: For detailed Electron development patterns and guidelines, refer to `references/patterns.md` within this skill.
2. **Security**: Always enable `contextIsolation`, `sandbox`, and disable `nodeIntegration`.
3. **Architecture**: Main process handles Node.js operations; renderer focuses on UI; preload bridges them securely.

## Process Architecture

### Main Process (Node.js Context)

The main process handles:
- Window creation and lifecycle
- File system and database operations
- IPC message handling
- Application-level events

Key guidelines:
- Use `app.isReady()` before creating windows
- Clean up resources on `window.destroyed` event
- Handle graceful shutdown with `app.on('before-quit')`

### Renderer Process (Frontend Context)

The renderer process:
- Renders UI using web technologies (React, Vue, etc.)
- Communicates with main process via IPC only
- Never has direct access to Node.js APIs

### Preload Script (Security Layer)

The preload script is the **only bridge** between renderer and main:

```typescript
import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("electronAPI", {
  invoke: (channel: string, args?: unknown) => {
    const validChannels = ["db:query", "file:save", "app:close"];
    if (validChannels.includes(channel)) {
      return ipcRenderer.invoke(channel, args);
    }
    throw new Error(`Invalid IPC channel: ${channel}`);
  },
});
```

## Security Checklist

Always configure `webPreferences` with these settings:

```typescript
webPreferences: {
  preload: path.join(__dirname, 'preload.js'),
  contextIsolation: true,        // REQUIRED
  enableRemoteModule: false,     // REQUIRED
  sandbox: true,                 // REQUIRED
  nodeIntegration: false,        // REQUIRED
  webSecurity: true,
}
```

## IPC Communication

### Main Process Handler

```typescript
ipcMain.handle("db:insert", async (event, data: unknown) => {
  if (!isValidInsertData(data)) {
    throw new Error("Invalid data");
  }
  return db.insert(data);
});
```

### Security Rules

- Whitelist all IPC channels in preload script
- Validate all arguments in main process handlers
- Never trust user input from renderer
- Keep secrets in main process only

## Configuration

### electron-vite.config.ts

```typescript
import { defineConfig } from "electron-vite";

export default defineConfig({
  main: {
    build: {
      outDir: "dist/main",
      rollupOptions: {
        external: ["better-sqlite3", "native-module-name"],
      },
    },
  },
  preload: {
    build: { outDir: "dist/preload" },
  },
  renderer: {
    build: {
      outDir: "dist/renderer",
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ["react", "react-dom"],
          },
        },
      },
    },
  },
});
```

### Native Modules

For native modules like `better-sqlite3`:
1. Exclude from rollup in electron-vite config
2. Include in `extraResources` in Electron Builder config
3. Use dynamic imports in main process
4. Rebuild for Electron using `@electron/rebuild`

## Common Pitfalls

### Never Do This

```typescript
// Exposing entire Node.js API
contextBridge.exposeInMainWorld("require", require);

// Not validating IPC messages
ipcMain.handle("dangerous", (event, data) => {
  fs.writeFileSync(data.path, data.content);
});

// Using __dirname in renderer
const imagePath = `${__dirname}/images/logo.png`;
```

### Do This Instead

```typescript
// Whitelist specific channels
contextBridge.exposeInMainWorld("electronAPI", {
  invoke: (channel: string, args: unknown) => {
    if (!["safe:channel"].includes(channel)) throw new Error("Invalid");
    return ipcRenderer.invoke(channel, args);
  },
});

// Validate all arguments
ipcMain.handle("file:write", async (event, { path, content }) => {
  if (typeof path !== "string" || typeof content !== "string") {
    throw new TypeError("Invalid arguments");
  }
  // Safe to use
});
```

## Validation Checklist

Before finishing a task involving Electron:

- [ ] Security settings enabled (`contextIsolation`, `sandbox`, no `nodeIntegration`)
- [ ] IPC channels whitelisted in preload script
- [ ] All IPC arguments validated in main process
- [ ] Native modules excluded from bundler and included in extraResources
- [ ] Secrets kept in main process only (not exposed to renderer)
- [ ] Run type checks (`pnpm run typecheck`) and tests (`pnpm run test`)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| White screen in production | Check asset paths use `base: './'`, verify build output |
| Native module fails | Exclude from rollup, include in extraResources |
| IPC not working | Verify preload path, contextIsolation enabled, channel whitelisted |
| HMR not working | Run with `-w` flag, check VITE_DEV_SERVER_URL |

For detailed configuration examples and additional patterns, consult `references/patterns.md`.
