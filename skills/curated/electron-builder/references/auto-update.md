# Auto Update Reference (electron-updater)

## Table of Contents
- [Overview](#overview)
- [Auto-updatable Targets](#auto-updatable-targets)
- [Quick Setup](#quick-setup)
- [TypeScript ESM Import](#typescript-esm-import)
- [Custom Updater Instance](#custom-updater-instance)
- [Events](#events)
- [Debugging](#debugging)
- [Dev Testing](#dev-testing)
- [Staged Rollouts](#staged-rollouts)
- [Private GitHub Repos](#private-github-repos)
- [Compatibility](#compatibility)
- [UpdateInfo Interface](#updateinfo-interface)

## Overview

`electron-updater` provides auto-update with advantages over Electron's built-in autoUpdater:
- Linux support (not just macOS/Windows)
- Code signature validation on macOS AND Windows
- All metadata files produced/published automatically
- Download progress and staged rollouts on all platforms
- Multiple providers: GitHub Releases, S3, DigitalOcean Spaces, Keygen, generic HTTP(s)

## Auto-updatable Targets

| Platform | Targets |
|---|---|
| macOS | DMG |
| Linux | AppImage, DEB, Pacman (beta), RPM |
| Windows | NSIS |

**Important**:
- Squirrel.Windows is NOT supported for auto-update
- macOS apps MUST be code-signed for auto-update to work
- macOS default target `dmg+zip` already works (zip needed for Squirrel.Mac fallback)

## Quick Setup

1. Install electron-updater:
```bash
pnpm add electron-updater
```

2. Configure `publish` in electron-builder config (see [publishing.md](publishing.md))

3. Build your app — metadata `.yml` files are generated automatically

4. Import and use in main process:

```typescript
import electronUpdater, { type AppUpdater } from "electron-updater";

export function getAutoUpdater(): AppUpdater {
  // Workaround for ESM compatibility with CommonJS module
  // See: https://github.com/electron-userland/electron-builder/issues/7976
  const { autoUpdater } = electronUpdater;
  return autoUpdater;
}
```

5. Check for updates:
```typescript
const autoUpdater = getAutoUpdater();
autoUpdater.checkForUpdatesAndNotify();
```

**Do NOT call `setFeedURL()`** — electron-builder auto-creates `app-update.yml` in `resources/` at build time.

## TypeScript ESM Import

Due to CommonJS/ESM interop issues, use destructuring:

```typescript
// CORRECT - works with ESM
import electronUpdater, { type AppUpdater } from "electron-updater";
const { autoUpdater } = electronUpdater;

// WRONG - may fail with ESM
import { autoUpdater } from "electron-updater";
```

For CommonJS:
```javascript
const { autoUpdater } = require("electron-updater");
```

## Custom Updater Instance

For more control (auth headers, custom provider):

```typescript
import { NsisUpdater } from "electron-updater";
// Or: MacUpdater, AppImageUpdater, DebUpdater, RpmUpdater, PacmanUpdater

const options = {
  requestHeaders: {
    Authorization: "Bearer token"
  },
  provider: "generic" as const,
  url: "https://example.com/auto-updates"
};

const autoUpdater = new NsisUpdater(options);
autoUpdater.addAuthHeader(`Bearer ${token}`);
autoUpdater.checkForUpdatesAndNotify();
```

## Events

```typescript
autoUpdater.on("error", (error: Error) => {
  // Error while updating
});

autoUpdater.on("checking-for-update", () => {
  // Started checking for updates
});

autoUpdater.on("update-available", (info: UpdateInfo) => {
  // Update available. Downloaded automatically if autoDownload is true.
});

autoUpdater.on("update-not-available", (info: UpdateInfo) => {
  // No update available
});

autoUpdater.on("download-progress", (progress: ProgressInfo) => {
  // progress.bytesPerSecond, progress.percent, progress.total, progress.transferred
});

autoUpdater.on("update-downloaded", (info: UpdateDownloadedEvent) => {
  // Update downloaded, call autoUpdater.quitAndInstall() to apply
});
```

## Debugging

Set up logging with electron-log:
```typescript
import log from "electron-log";

autoUpdater.logger = log;
autoUpdater.logger.transports.file.level = "info";
```

### Common issue: "APPIMAGE env is not defined"
Workaround for development:
```typescript
import path from "path";
import { app } from "electron";

process.env.APPIMAGE = path.join(
  __dirname, "dist", `app_name-${app.getVersion()}.AppImage`
);
```

Better approach: Test auto-update with installed application. Use [Minio](https://min.io/) as local S3 server for testing.

## Dev Testing

Create `dev-app-update.yml` in project root matching your publish config (in YAML format):

```yaml
provider: generic
url: http://localhost:8080
```

Force dev mode:
```typescript
autoUpdater.forceDevUpdateConfig = true;
```

## Staged Rollouts

Control distribution percentage by editing `latest.yml` / `latest-mac.yml`:

```yaml
version: 1.1.0
path: TestApp Setup 1.1.0.exe
sha512: Dj51I0q8aPQ3ioaz9LMqGYujAYRbDNblAQbodDRXAMxmY6hsHqEl3F6SvhfJj5oPhcqdX1ldsgEvfMNXGUXBIw==
stagingPercentage: 10
```

Ships update to 10% of userbase.

**Critical**: To pull a broken staged release, you MUST increment the version number above the broken release — you can't re-release the same version since some users already have it.

## Private GitHub Repos

Set `GH_TOKEN` environment variable on user's machine and `private: true` in publish config:

```yaml
publish:
  provider: github
  private: true
```

**Limitations**:
- GitHub API rate limit: 5000 requests/user/hour
- Each update check uses up to 3 requests
- Not intended for all users — only for very special cases

## Compatibility

Set `electronUpdaterCompatibility` to control metadata format:

```yaml
electronUpdaterCompatibility: ">= 2.16"
```

| Version | Feature |
|---|---|
| `1.0.0` | `latest-mac.json` format |
| `2.15.0` | `path` field |
| `2.16.0` | `files` field |

Default: `>=2.15`. For new projects, use `>= 2.16`.

## UpdateInfo Interface

```typescript
interface UpdateInfo {
  readonly version: string;
  readonly files: UpdateFileInfo[];
  releaseDate: string;
  readonly minimumSystemVersion?: string;  // macOS: "23.1.0", Windows: "10.0.22631"
  readonly stagingPercentage?: number;     // 0-100
  releaseName?: string | null;
  releaseNotes?: string | ReleaseNoteInfo[] | null;  // Array if fullChangelog=true
  /** @deprecated */ readonly path: string;
  /** @deprecated */ readonly sha512: string;
}
```

Generated metadata files:
- `latest.yml` (Windows)
- `latest-mac.yml` (macOS)
- `latest-linux.yml` (Linux)
