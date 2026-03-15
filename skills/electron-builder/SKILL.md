---
name: electron-builder
description: |
  Comprehensive guide for electron-builder (v26.x) packaging, code signing, auto-updates,
  and release workflows. Use when: (1) configuring electron-builder builds (electron-builder.yml
  or config.js/ts), (2) setting up macOS/Windows code signing or notarization, (3) implementing
  auto-updates with electron-updater, (4) publishing to GitHub Releases, S3, or generic servers,
  (5) configuring platform targets (NSIS, DMG, AppImage, Snap, PKG, MSI), (6) working with
  build hooks (beforePack, afterSign, afterAllArtifactBuild), or (7) using the programmatic API.
  Triggers on: electron-builder, electron-updater, code signing, notarize, NSIS, DMG, AppImage,
  auto-update, publish releases, build hooks, electron packaging, electron distribution.
---

# electron-builder

Docs: https://www.electron.build (v26.8.x)
Repo: https://github.com/electron-userland/electron-builder

## Quick Start

Install:
```bash
pnpm add electron-builder -D
pnpm add electron-updater  # If using auto-updates
```

Minimal config (`electron-builder.yml`):
```yaml
appId: com.example.myapp
productName: My App
files:
  - "out/**/*"
  - "package.json"
mac:
  target: dmg
  category: public.app-category.developer-tools
win:
  target: nsis
linux:
  target:
    - AppImage
    - deb
publish:
  provider: github
```

Build scripts in `package.json`:
```json
{
  "scripts": {
    "build:mac": "electron-builder --mac",
    "build:win": "electron-builder --win",
    "build:linux": "electron-builder --linux",
    "build:all": "electron-builder -mwl",
    "release": "electron-builder --publish always"
  }
}
```

## CLI Reference

```bash
electron-builder                    # Build for current platform
electron-builder -mwl              # Build for all platforms
electron-builder --mac dmg         # macOS DMG only
electron-builder --win nsis:ia32   # Windows NSIS 32-bit
electron-builder --linux deb tar.xz
electron-builder --dir             # Unpacked dir (test builds)
electron-builder -p always         # Build and publish

# Architecture flags
--x64  --ia32  --armv7l  --arm64  --universal

# CLI config overrides
-c.extraMetadata.foo=bar
-c.mac.identity=null
-c.nsis.unicode=false

# Publish existing artifacts
electron-builder publish -f dist/*.exe -c electron-builder.yml
```

Publish flag values: `onTag` | `onTagOrDraft` | `always` | `never`

## Configuration

Config locations (checked in order):
1. `package.json` > `"build"` key
2. `electron-builder.yml` (default, recommended)
3. `electron-builder.json` / `.json5` / `.toml`
4. `electron-builder.config.js` / `.ts`
5. CLI: `--config <path>`

**Do NOT name JS config `electron-builder.js`** — conflicts with package name.

For full configuration options, file patterns, macros, icons, and directory settings:
See [references/configuration.md](references/configuration.md)

### Essential Config Properties

| Property | Default | Description |
|---|---|---|
| `appId` | `com.electron.${name}` | **Do not change once deployed.** Used as bundle ID (macOS) and AUMID (Windows). |
| `productName` | package.json name | Display name (allows spaces) |
| `compression` | `"normal"` | `"store"` for fast test builds, `"maximum"` for release |
| `asar` | `true` | Pack source into asar archive |
| `files` | auto | Glob patterns for app source files |
| `extraFiles` | — | Files copied outside asar (e.g. native addons) |
| `extraResources` | — | Files copied to resources directory |
| `forceCodeSigning` | `false` | Fail build if not signed |

### File Macros

Available in `artifactName`, file patterns, and publish URLs:
`${arch}`, `${os}`, `${platform}`, `${name}`, `${productName}`, `${version}`, `${channel}`, `${ext}`, `${env.VAR_NAME}`

## Default Targets

| Platform | Default |
|---|---|
| macOS | DMG + ZIP |
| Windows | NSIS |
| Linux (cross) | Snap + AppImage (x64) |
| Linux (native) | Snap + AppImage (current arch) |

## Code Signing

Signing is automatic when configured. Core environment variables:

| Env | Description |
|---|---|
| `CSC_LINK` | Certificate path/URL/base64 (.p12/.pfx) |
| `CSC_KEY_PASSWORD` | Certificate password |
| `CSC_IDENTITY_AUTO_DISCOVERY` | `true`/`false` (macOS keychain auto-discovery) |
| `WIN_CSC_LINK` | Windows cert (when cross-signing from macOS) |
| `WIN_CSC_KEY_PASSWORD` | Windows cert password |

### macOS: Disable signing
```bash
export CSC_IDENTITY_AUTO_DISCOVERY=false
# Or in config: mac.identity: null
# For ad-hoc (ARM): mac.identity: "-"
```

### macOS: Notarization
```yaml
mac:
  hardenedRuntime: true
  notarize: true    # or { teamId: "TEAM_ID" }
```
Requires `APPLE_ID`, `APPLE_APP_SPECIFIC_PASSWORD`, `APPLE_TEAM_ID` env vars.

### Windows: Azure Trusted Signing
```yaml
win:
  azureSignOptions:
    publisherName: "CN=Your Company"
    endpoint: "https://eus.codesigning.azure.net"
    certificateProfileName: "your-profile"
    codeSigningAccountName: "your-account"
```
Requires `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`.

For complete code signing reference (CI setup, certificates, EV certs, cross-platform):
See [references/code-signing.md](references/code-signing.md)

## Auto Update (electron-updater)

### Minimal setup
```typescript
// main process
import electronUpdater, { type AppUpdater } from "electron-updater";

export function getAutoUpdater(): AppUpdater {
  const { autoUpdater } = electronUpdater;
  return autoUpdater;
}

const autoUpdater = getAutoUpdater();
autoUpdater.checkForUpdatesAndNotify();
```

**Do NOT call `setFeedURL()`** — `app-update.yml` is auto-generated at build time.

### ESM Import (required workaround)
```typescript
// CORRECT
import electronUpdater from "electron-updater";
const { autoUpdater } = electronUpdater;

// WRONG (may fail with ESM)
import { autoUpdater } from "electron-updater";
```

### Auto-updatable targets
- macOS: DMG
- Windows: NSIS
- Linux: AppImage, DEB, Pacman (beta), RPM

**macOS apps MUST be signed** for auto-update. **Squirrel.Windows NOT supported.**

### Events
```typescript
autoUpdater.on("error", (err) => {});
autoUpdater.on("checking-for-update", () => {});
autoUpdater.on("update-available", (info) => {});
autoUpdater.on("update-not-available", (info) => {});
autoUpdater.on("download-progress", (progress) => {
  // .bytesPerSecond, .percent, .total, .transferred
});
autoUpdater.on("update-downloaded", (info) => {
  autoUpdater.quitAndInstall();
});
```

### Debugging
```typescript
import log from "electron-log";
autoUpdater.logger = log;
autoUpdater.logger.transports.file.level = "info";
```

For staged rollouts, custom updater instances, private repos, dev testing:
See [references/auto-update.md](references/auto-update.md)

## Publishing

### Quick GitHub Releases setup
```yaml
publish:
  provider: github
  releaseType: draft
```
Set `GH_TOKEN` env var (personal access token with `repo` scope).

### Quick S3 setup
```yaml
publish:
  provider: s3
  bucket: my-bucket-name
```
Set `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`.

### Quick Generic Server setup
```yaml
publish:
  provider: generic
  url: https://example.com/releases
```
Upload artifacts + `latest.yml` manually.

### Publish CLI behavior
| Condition | Default behavior |
|---|---|
| CI detected | `onTagOrDraft` |
| CI + tag pushed | `onTag` |
| npm script `release` | `always` |

### Release Channels
Version determines channel: `1.0.0` = `latest`, `1.0.0-beta.1` = `beta`

For all publishers (Bitbucket, GitLab, Keygen, Snap Store, Spaces), workflows, and advanced config:
See [references/publishing.md](references/publishing.md)

## Platform Target Configuration

### macOS
```yaml
mac:
  category: public.app-category.developer-tools
  hardenedRuntime: true
  darkModeSupport: true
  target: dmg
  entitlements: build/entitlements.mac.plist
  notarize: true
```

### Windows (NSIS)
```yaml
nsis:
  oneClick: true              # false for assisted installer
  perMachine: false
  allowToChangeInstallationDirectory: false
  createDesktopShortcut: true
  deleteAppDataOnUninstall: false
  include: build/installer.nsh  # Custom NSIS script
  differentialPackage: true
```

### Linux
```yaml
linux:
  category: Development
  desktop:
    MimeType: "x-scheme-handler/myapp"
  target:
    - AppImage
    - deb
    - snap
```

For all target options (DMG, PKG, MAS, MSI, AppX, Snap, Flatpak, portable, custom NSIS scripts):
See [references/platform-targets.md](references/platform-targets.md)

## Build Hooks

Execution order:
```
beforeBuild → beforePack → afterExtract → afterPack → [signing] →
afterSign → artifactBuildStarted → [build] → artifactBuildCompleted →
afterAllArtifactBuild
```

### Inline (JS/TS config)
```javascript
module.exports = {
  afterSign: async (context) => {
    if (context.electronPlatformName === "darwin") {
      await notarize(context);
    }
  },
  afterAllArtifactBuild: (result) => {
    return ["/path/to/extra/file"];  // Additional files to publish
  },
};
```

### File reference (YAML config)
```yaml
beforePack: "./scripts/before-pack.js"
afterSign: "./scripts/notarize.js"
```

```javascript
// scripts/notarize.js
exports.default = async function(context) {
  // context: { outDir, appOutDir, packager, electronPlatformName, arch, targets }
};
```

For all hooks, context interfaces, and programmatic API:
See [references/hooks-and-programmatic.md](references/hooks-and-programmatic.md)

## Common Patterns

### Multi-platform CI build
```yaml
# GitHub Actions pattern
mac:
  target:
    - target: dmg
      arch: [x64, arm64]
win:
  target:
    - target: nsis
      arch: [x64, ia32]
linux:
  target:
    - target: AppImage
      arch: [x64, arm64]
    - target: deb
      arch: [x64, arm64]
publish:
  provider: github
```

### Complete config with auto-update and signing
```yaml
appId: com.example.myapp
productName: My App
copyright: Copyright 2024 Example Inc.
asar: true
compression: normal
forceCodeSigning: true

directories:
  output: dist
  buildResources: build

files:
  - "out/**/*"
  - "package.json"

mac:
  target: [dmg, zip]
  hardenedRuntime: true
  notarize: true
  category: public.app-category.developer-tools

win:
  target: nsis

nsis:
  oneClick: false
  perMachine: false
  allowToChangeInstallationDirectory: true

linux:
  target: [AppImage, deb]
  category: Development

publish:
  provider: github

electronUpdaterCompatibility: ">= 2.16"
```

## Gotchas

1. **Never change `appId`** after release — NSIS uses it for registry GUID
2. **macOS signing required** for auto-update to work
3. **ESM import workaround** needed for electron-updater in TypeScript
4. **Don't call `setFeedURL()`** — `app-update.yml` is auto-generated
5. **Squirrel.Windows** not supported by electron-updater — use NSIS
6. **Windows env var limit** 8192 chars — re-export cert without chain if too large
7. **`electron-builder.js`** conflicts with package name — use different filename
8. Set `app.setAppUserModelId(appId)` in main process for Windows notifications
