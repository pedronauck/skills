# Electron Development Patterns & Best Practices

This document contains comprehensive patterns, guidelines, and best practices for building production-grade Electron applications.

## Table of Contents

1. [Process Architecture](#process-architecture)
2. [Security Configuration](#security-configuration)
3. [IPC Communication](#ipc-communication)
4. [Preload Scripts](#preload-scripts)
5. [Native Modules](#native-modules)
6. [Build Configuration](#build-configuration)
7. [Window Management](#window-management)
8. [Error Handling](#error-handling)
9. [Performance Optimization](#performance-optimization)
10. [Common Pitfalls](#common-pitfalls)

---

## Process Architecture

### Main Process (Node.js Context)

The main process is the entry point of your Electron application and runs in a Node.js environment.

**Responsibilities:**
- Window creation and lifecycle management
- File system and database operations
- IPC message handling
- Application-level events and menus
- Native integrations (tray, notifications, etc.)
- System-level operations

**Key Guidelines:**

```typescript
import { app, BrowserWindow } from "electron";
import path from "path";

// Always wait for app ready before creating windows
app.whenReady().then(() => {
  createWindow();

  // macOS: Re-create window when dock icon is clicked
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Clean up on all windows closed (except macOS)
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

// Handle graceful shutdown
app.on("before-quit", () => {
  // Clean up resources, close database connections, etc.
});
```

### Renderer Process (Frontend Context)

The renderer process handles the user interface and runs in a sandboxed browser context.

**Key Rules:**
- Renders UI using web technologies (React, Vue, etc.)
- Communicates with main process via IPC only
- Never has direct access to Node.js APIs
- Cannot access the file system directly
- Must use preload script for any Node.js functionality

### Preload Script (Security Layer)

The preload script is the **only authorized bridge** between renderer and main processes.

**Purpose:**
- Expose a controlled API to the renderer
- Validate and whitelist IPC channels
- Act as a security boundary

---

## Security Configuration

### Mandatory webPreferences Settings

Always configure `BrowserWindow` with these security settings:

```typescript
import { BrowserWindow } from "electron";
import path from "path";

const mainWindow = new BrowserWindow({
  width: 1200,
  height: 800,
  webPreferences: {
    preload: path.join(__dirname, "preload.js"),
    contextIsolation: true,        // REQUIRED - isolates preload from renderer
    enableRemoteModule: false,     // REQUIRED - disables dangerous remote module
    sandbox: true,                 // REQUIRED - enables sandbox mode
    nodeIntegration: false,        // REQUIRED - no Node.js in renderer
    webSecurity: true,             // Enables same-origin policy
    allowRunningInsecureContent: false,
    experimentalFeatures: false,
  },
});
```

### Security Checklist

- [ ] `contextIsolation: true` - Prevents prototype pollution attacks
- [ ] `nodeIntegration: false` - No direct Node.js access in renderer
- [ ] `sandbox: true` - Chromium sandbox enabled
- [ ] `enableRemoteModule: false` - Remote module disabled
- [ ] `webSecurity: true` - Same-origin policy enabled
- [ ] IPC channels whitelisted in preload
- [ ] All IPC arguments validated in main process
- [ ] No secrets exposed to renderer

### Content Security Policy

```typescript
mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
  callback({
    responseHeaders: {
      ...details.responseHeaders,
      "Content-Security-Policy": [
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
      ],
    },
  });
});
```

---

## IPC Communication

### Type-Safe IPC Pattern

**Define IPC Types:**

```typescript
// shared/ipc-types.ts
export interface IPCChannels {
  "db:query": { args: { sql: string; params?: unknown[] }; result: unknown[] };
  "db:insert": { args: { table: string; data: Record<string, unknown> }; result: { id: number } };
  "file:read": { args: { path: string }; result: string };
  "file:write": { args: { path: string; content: string }; result: boolean };
  "app:close": { args: undefined; result: void };
}

export type IPCChannel = keyof IPCChannels;
```

**Main Process Handlers:**

```typescript
// main/ipc-handlers.ts
import { ipcMain } from "electron";
import { IPCChannels } from "../shared/ipc-types";

// Type-safe handler registration
function registerHandler<K extends keyof IPCChannels>(
  channel: K,
  handler: (args: IPCChannels[K]["args"]) => Promise<IPCChannels[K]["result"]>
) {
  ipcMain.handle(channel, async (event, args) => {
    // Always validate input
    return handler(args);
  });
}

registerHandler("db:query", async ({ sql, params }) => {
  if (typeof sql !== "string") {
    throw new TypeError("SQL must be a string");
  }
  // Execute query...
  return [];
});

registerHandler("file:write", async ({ path, content }) => {
  if (typeof path !== "string" || typeof content !== "string") {
    throw new TypeError("Path and content must be strings");
  }
  // Validate path is within allowed directory
  if (!isPathAllowed(path)) {
    throw new Error("Access denied");
  }
  // Write file...
  return true;
});
```

**Preload Script:**

```typescript
// preload/index.ts
import { contextBridge, ipcRenderer } from "electron";
import type { IPCChannel, IPCChannels } from "../shared/ipc-types";

// Whitelist of allowed channels
const VALID_CHANNELS: IPCChannel[] = [
  "db:query",
  "db:insert",
  "file:read",
  "file:write",
  "app:close",
];

contextBridge.exposeInMainWorld("electronAPI", {
  invoke: async <K extends IPCChannel>(
    channel: K,
    args: IPCChannels[K]["args"]
  ): Promise<IPCChannels[K]["result"]> => {
    if (!VALID_CHANNELS.includes(channel)) {
      throw new Error(`Invalid IPC channel: ${channel}`);
    }
    return ipcRenderer.invoke(channel, args);
  },
});
```

**Renderer Usage:**

```typescript
// renderer/api.ts
declare global {
  interface Window {
    electronAPI: {
      invoke: <K extends IPCChannel>(
        channel: K,
        args: IPCChannels[K]["args"]
      ) => Promise<IPCChannels[K]["result"]>;
    };
  }
}

// Usage in React component
async function saveFile(path: string, content: string) {
  const success = await window.electronAPI.invoke("file:write", { path, content });
  return success;
}
```

### One-Way Communication (Events)

```typescript
// Main to Renderer
mainWindow.webContents.send("update:progress", { percent: 50 });

// Preload
contextBridge.exposeInMainWorld("electronAPI", {
  onProgress: (callback: (data: { percent: number }) => void) => {
    ipcRenderer.on("update:progress", (event, data) => callback(data));
  },
  removeProgressListener: () => {
    ipcRenderer.removeAllListeners("update:progress");
  },
});
```

---

## Preload Scripts

### Complete Preload Example

```typescript
import { contextBridge, ipcRenderer } from "electron";

// Define all valid channels
const INVOKE_CHANNELS = [
  "db:query",
  "db:insert",
  "file:read",
  "file:write",
  "app:getVersion",
  "app:close",
] as const;

const EVENT_CHANNELS = [
  "update:progress",
  "notification:new",
] as const;

type InvokeChannel = (typeof INVOKE_CHANNELS)[number];
type EventChannel = (typeof EVENT_CHANNELS)[number];

// Validation helpers
function isValidInvokeChannel(channel: string): channel is InvokeChannel {
  return INVOKE_CHANNELS.includes(channel as InvokeChannel);
}

function isValidEventChannel(channel: string): channel is EventChannel {
  return EVENT_CHANNELS.includes(channel as EventChannel);
}

// Expose API to renderer
contextBridge.exposeInMainWorld("electronAPI", {
  // Two-way communication
  invoke: async (channel: string, args?: unknown) => {
    if (!isValidInvokeChannel(channel)) {
      throw new Error(`Invalid IPC channel: ${channel}`);
    }
    return ipcRenderer.invoke(channel, args);
  },

  // One-way: main to renderer
  on: (channel: string, callback: (...args: unknown[]) => void) => {
    if (!isValidEventChannel(channel)) {
      throw new Error(`Invalid event channel: ${channel}`);
    }
    const subscription = (event: Electron.IpcRendererEvent, ...args: unknown[]) => {
      callback(...args);
    };
    ipcRenderer.on(channel, subscription);
    return () => {
      ipcRenderer.removeListener(channel, subscription);
    };
  },

  // One-way: renderer to main (no response)
  send: (channel: string, args?: unknown) => {
    if (!isValidInvokeChannel(channel)) {
      throw new Error(`Invalid IPC channel: ${channel}`);
    }
    ipcRenderer.send(channel, args);
  },
});
```

---

## Native Modules

### Handling Native Dependencies

Native modules (like `better-sqlite3`) require special handling:

**1. Exclude from Bundler:**

```typescript
// electron-vite.config.ts
export default defineConfig({
  main: {
    build: {
      rollupOptions: {
        external: [
          "better-sqlite3",
          "node-pty",
          // Add other native modules here
        ],
      },
    },
  },
});
```

**2. Include in Build:**

```json
// electron-builder.json
{
  "extraResources": [
    {
      "from": "node_modules/better-sqlite3",
      "to": "node_modules/better-sqlite3"
    }
  ]
}
```

**3. Dynamic Import in Main Process:**

```typescript
// Use dynamic import to load native modules
async function loadDatabase() {
  const Database = await import("better-sqlite3");
  return new Database.default("app.db");
}
```

**4. Rebuild for Electron:**

```bash
npx @electron/rebuild
```

---

## Build Configuration

### electron-vite.config.ts

```typescript
import { defineConfig, externalizeDepsPlugin } from "electron-vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  main: {
    plugins: [externalizeDepsPlugin()],
    build: {
      outDir: "dist/main",
      rollupOptions: {
        external: ["better-sqlite3"],
      },
    },
    resolve: {
      alias: {
        "@main": path.resolve(__dirname, "src/main"),
        "@shared": path.resolve(__dirname, "src/shared"),
      },
    },
  },
  preload: {
    plugins: [externalizeDepsPlugin()],
    build: {
      outDir: "dist/preload",
    },
  },
  renderer: {
    root: "src/renderer",
    plugins: [react()],
    build: {
      outDir: "dist/renderer",
      rollupOptions: {
        input: path.resolve(__dirname, "src/renderer/index.html"),
        output: {
          manualChunks: {
            vendor: ["react", "react-dom"],
          },
        },
      },
    },
    resolve: {
      alias: {
        "@renderer": path.resolve(__dirname, "src/renderer"),
        "@shared": path.resolve(__dirname, "src/shared"),
      },
    },
  },
});
```

### electron-builder.json

```json
{
  "appId": "com.yourcompany.app",
  "productName": "Your App",
  "directories": {
    "output": "release"
  },
  "files": [
    "dist/**/*",
    "package.json"
  ],
  "extraResources": [
    {
      "from": "resources/",
      "to": "resources/"
    }
  ],
  "mac": {
    "target": ["dmg", "zip"],
    "category": "public.app-category.developer-tools",
    "hardenedRuntime": true,
    "gatekeeperAssess": false,
    "entitlements": "build/entitlements.mac.plist",
    "entitlementsInherit": "build/entitlements.mac.plist"
  },
  "win": {
    "target": ["nsis", "portable"]
  },
  "linux": {
    "target": ["AppImage", "deb"]
  }
}
```

---

## Window Management

### Creating Windows

```typescript
import { BrowserWindow, shell } from "electron";
import path from "path";

function createWindow(): BrowserWindow {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    show: false, // Don't show until ready
    webPreferences: {
      preload: path.join(__dirname, "../preload/index.js"),
      contextIsolation: true,
      sandbox: true,
      nodeIntegration: false,
    },
  });

  // Show when ready to prevent visual flash
  mainWindow.on("ready-to-show", () => {
    mainWindow.show();
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith("https://")) {
      shell.openExternal(url);
    }
    return { action: "deny" };
  });

  // Load content
  if (process.env.ELECTRON_RENDERER_URL) {
    mainWindow.loadURL(process.env.ELECTRON_RENDERER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, "../renderer/index.html"));
  }

  return mainWindow;
}
```

### Window State Persistence

```typescript
import { app, BrowserWindow, screen } from "electron";
import Store from "electron-store";

interface WindowState {
  x?: number;
  y?: number;
  width: number;
  height: number;
  isMaximized: boolean;
}

const store = new Store<{ windowState: WindowState }>();

function getWindowState(): WindowState {
  const defaults = { width: 1200, height: 800, isMaximized: false };
  const state = store.get("windowState", defaults);

  // Validate position is on a visible screen
  const displays = screen.getAllDisplays();
  const isVisible = displays.some((display) => {
    return (
      state.x !== undefined &&
      state.y !== undefined &&
      state.x >= display.bounds.x &&
      state.y >= display.bounds.y &&
      state.x < display.bounds.x + display.bounds.width &&
      state.y < display.bounds.y + display.bounds.height
    );
  });

  if (!isVisible) {
    delete state.x;
    delete state.y;
  }

  return state;
}

function saveWindowState(window: BrowserWindow): void {
  const bounds = window.getBounds();
  store.set("windowState", {
    ...bounds,
    isMaximized: window.isMaximized(),
  });
}
```

---

## Error Handling

### Global Error Handling

```typescript
// main/error-handler.ts
import { app, dialog } from "electron";

export function setupErrorHandling(): void {
  // Handle uncaught exceptions
  process.on("uncaughtException", (error) => {
    console.error("Uncaught Exception:", error);
    dialog.showErrorBox("Unexpected Error", error.message);
  });

  // Handle unhandled promise rejections
  process.on("unhandledRejection", (reason, promise) => {
    console.error("Unhandled Rejection at:", promise, "reason:", reason);
  });

  // Handle renderer crashes
  app.on("render-process-gone", (event, webContents, details) => {
    console.error("Renderer process gone:", details.reason);
    if (details.reason === "crashed") {
      // Optionally restart the renderer
    }
  });

  // Handle GPU process crashes
  app.on("child-process-gone", (event, details) => {
    console.error("Child process gone:", details.type, details.reason);
  });
}
```

### IPC Error Handling

```typescript
// Wrap IPC handlers with error handling
function createSafeHandler<T, R>(
  handler: (args: T) => Promise<R>
): (event: Electron.IpcMainInvokeEvent, args: T) => Promise<R> {
  return async (event, args) => {
    try {
      return await handler(args);
    } catch (error) {
      console.error("IPC Handler Error:", error);
      throw error; // Re-throw to propagate to renderer
    }
  };
}

ipcMain.handle("file:read", createSafeHandler(async ({ path }) => {
  // Handler implementation
}));
```

---

## Performance Optimization

### Lazy Loading Windows

```typescript
let settingsWindow: BrowserWindow | null = null;

function getSettingsWindow(): BrowserWindow {
  if (settingsWindow && !settingsWindow.isDestroyed()) {
    return settingsWindow;
  }

  settingsWindow = new BrowserWindow({
    width: 600,
    height: 400,
    show: false,
    parent: mainWindow,
    modal: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      sandbox: true,
      nodeIntegration: false,
    },
  });

  settingsWindow.on("closed", () => {
    settingsWindow = null;
  });

  return settingsWindow;
}
```

### Resource Cleanup

```typescript
mainWindow.on("closed", () => {
  // Clean up any subscriptions, listeners, etc.
  cleanup();
  mainWindow = null;
});

app.on("before-quit", async () => {
  // Close database connections
  await db.close();

  // Cancel pending operations
  pendingOperations.forEach((op) => op.cancel());
});
```

---

## Common Pitfalls

### Never Do This

```typescript
// 1. Exposing entire Node.js API
contextBridge.exposeInMainWorld("require", require);

// 2. Not validating IPC messages
ipcMain.handle("dangerous", (event, data) => {
  fs.writeFileSync(data.path, data.content); // Path traversal vulnerability!
});

// 3. Using __dirname in renderer (doesn't exist)
const imagePath = `${__dirname}/images/logo.png`;

// 4. Trusting renderer input without validation
ipcMain.handle("db:query", (event, { sql }) => {
  return db.exec(sql); // SQL injection!
});

// 5. Storing secrets in renderer
localStorage.setItem("apiKey", "secret-key"); // Accessible to any script!
```

### Do This Instead

```typescript
// 1. Whitelist specific channels
contextBridge.exposeInMainWorld("electronAPI", {
  invoke: (channel: string, args: unknown) => {
    const validChannels = ["safe:channel"];
    if (!validChannels.includes(channel)) {
      throw new Error("Invalid channel");
    }
    return ipcRenderer.invoke(channel, args);
  },
});

// 2. Validate all arguments thoroughly
ipcMain.handle("file:write", async (event, { path, content }) => {
  if (typeof path !== "string" || typeof content !== "string") {
    throw new TypeError("Invalid arguments");
  }
  if (!path.startsWith(app.getPath("userData"))) {
    throw new Error("Path not allowed");
  }
  return fs.promises.writeFile(path, content);
});

// 3. Use proper asset paths
// In renderer, use import or public folder
import logo from "./images/logo.png";

// 4. Use parameterized queries
ipcMain.handle("db:query", (event, { sql, params }) => {
  return db.prepare(sql).all(params);
});

// 5. Keep secrets in main process
// main/secrets.ts
const API_KEY = process.env.API_KEY;
ipcMain.handle("api:call", async (event, { endpoint }) => {
  return fetch(endpoint, { headers: { Authorization: `Bearer ${API_KEY}` } });
});
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| White screen in production | Incorrect asset paths | Use `base: './'` in Vite config, verify build output |
| Native module fails to load | Not rebuilt for Electron | Run `npx @electron/rebuild` |
| IPC not working | Preload not loaded or channel not whitelisted | Verify preload path is correct, check channel whitelist |
| HMR not working | Dev server URL not set | Run with `-w` flag, check VITE_DEV_SERVER_URL |
| Context isolation errors | Accessing Node.js in renderer | Use preload script to expose APIs |
| App crashes on startup | Unhandled promise rejection | Add proper error handling, check main process logs |
| File not found in production | Using development paths | Use `app.getPath()` and proper resource paths |
| Window state not persisting | Not saving on close | Add `close` event listener to save state |

---

## Quick Reference

### Development Commands

```bash
# Start development
pnpm run dev

# Build for production
pnpm run build

# Package application
pnpm run package

# Rebuild native modules
npx @electron/rebuild

# Type check
pnpm run typecheck
```

### Essential Paths

```typescript
import { app } from "electron";

// User data directory (persists across updates)
app.getPath("userData"); // ~/Library/Application Support/YourApp

// Application directory
app.getAppPath();

// Executable path
app.getPath("exe");

// Temp directory
app.getPath("temp");

// Resources path (for packaged app)
process.resourcesPath;
```
