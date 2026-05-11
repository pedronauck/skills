# Build Hooks and Programmatic API Reference

## Table of Contents
- [Build Hooks Overview](#build-hooks-overview)
- [Hook Execution Order](#hook-execution-order)
- [Hook Definitions](#hook-definitions)
- [Hook Usage Patterns](#hook-usage-patterns)
- [Programmatic API](#programmatic-api)
- [Full Programmatic Example](#full-programmatic-example)

## Build Hooks Overview

Hooks can be specified as:
1. **Inline function** (JS/TS config only)
2. **Path to file** (any config format): `"./myHook.js"`
3. **Module id**: `"my-hook-package"`

Hook files must export function as `default`:
```javascript
// myHook.js
exports.default = async function(context) {
  // your code
};
```

## Hook Execution Order

```
beforeBuild        → Dependencies install/rebuild
  ↓
beforePack         → Before packing app
  ↓
afterExtract       → After Electron binary extracted to output
  ↓
afterPack          → After pack (before signing and distributable format)
  ↓
[code signing]
  ↓
afterSign          → After signing (before distributable format)
  ↓
artifactBuildStarted → Distributable artifact build starts
  ↓
[build distributable: NSIS, DMG, etc.]
  ↓
artifactBuildCompleted → Individual artifact build done
  ↓
afterAllArtifactBuild → ALL artifacts done (can return extra files to publish)
```

Platform-specific hooks:
- `appxManifestCreated` → After AppX manifest created, before packing .appx
- `msiProjectCreated` → After MSI project created, before packing .msi

## Hook Definitions

### beforeBuild
```typescript
beforeBuild?: (context: BeforeBuildContext) => Promise<boolean | void> | boolean | void;

interface BeforeBuildContext {
  appDir: string;
  electronVersion: string;
  arch: Arch;
  platform: Platform;
}
```
Runs before dependencies install/rebuild (when `npmRebuild: true`). Return `false` to skip dependency install.

### beforePack
```typescript
beforePack?: (context: PackContext) => Promise<void> | void;

interface PackContext {
  outDir: string;
  appOutDir: string;
  packager: PlatformPackager;
  electronPlatformName: string;
  arch: Arch;
  targets: Target[];
}
```

### afterExtract
Same signature as `beforePack`. Runs after Electron binary extracted to output directory.

### afterPack
Same signature as `beforePack`. Runs after pack but before distributable format and signing.

### afterSign
Same signature as `beforePack`. Runs after code signing but before distributable format.

### artifactBuildStarted
```typescript
artifactBuildStarted?: (context: ArtifactBuildStarted) => Promise<void> | void;

interface ArtifactBuildStarted {
  targetPresentableName: string;
  file: string;
  arch: Arch | null;
}
```

### artifactBuildCompleted
```typescript
artifactBuildCompleted?: (context: ArtifactCreated) => Promise<void> | void;

interface ArtifactCreated {
  file: string;
  target: Target | null;
  arch: Arch | null;
  safeArtifactName: string | null;
  packager: PlatformPackager;
  isWriteUpdateInfo: boolean;
  updateInfo: any;
}
```

### afterAllArtifactBuild
```typescript
afterAllArtifactBuild?: (result: BuildResult) => Promise<string[]> | string[];

interface BuildResult {
  outDir: string;
  artifactPaths: string[];
  platformToTargets: Map<Platform, Map<string, Target>>;
  configuration: Configuration;
}
```
Can return additional file paths to publish.

### onNodeModuleFile
```typescript
onNodeModuleFile?: (file: string) => boolean | void;
```
Runs on each node module file. Return `true` to force include, `false` to force exclude, or `void` for default behavior.

### electronDist
```typescript
electronDist?: (options: PrepareApplicationStageDirectoryOptions) => string;
```
Returns path to custom Electron build or folder of zips. Zip pattern: `electron-v${version}-${platformName}-${arch}.zip`.

## Hook Usage Patterns

### Inline (JS/TS config)
```javascript
module.exports = {
  afterSign: async (context) => {
    if (context.electronPlatformName === "darwin") {
      await notarize(context);
    }
  },
  beforeBuild: async (context) => {
    const { appDir, electronVersion, arch } = context;
    await electronRebuild.rebuild({ buildPath: appDir, electronVersion, arch });
    return false; // Skip default rebuild
  },
  afterAllArtifactBuild: (result) => {
    return ["/path/to/additional/file"]; // Extra files to publish
  },
};
```

### File path (YAML/JSON config)
```yaml
# electron-builder.yml
beforePack: "./scripts/before-pack.js"
afterSign: "./scripts/notarize.js"
afterAllArtifactBuild: "./scripts/after-build.js"
```

```javascript
// scripts/notarize.js
const { notarize } = require("@electron/notarize");

exports.default = async function notarizing(context) {
  const { electronPlatformName, appOutDir } = context;
  if (electronPlatformName !== "darwin") return;

  const appName = context.packager.appInfo.productFilename;
  return await notarize({
    appBundleId: "com.example.myapp",
    appPath: `${appOutDir}/${appName}.app`,
    appleId: process.env.APPLE_ID,
    appleIdPassword: process.env.APPLE_APP_SPECIFIC_PASSWORD,
    teamId: process.env.APPLE_TEAM_ID,
  });
};
```

## Programmatic API

### Installation
```bash
pnpm add electron-builder -D
```

### Basic usage
```typescript
import { build, Platform } from "electron-builder";

await build({
  targets: Platform.MAC.createTarget(),
  config: {
    appId: "com.example.myapp",
    mac: { target: "dmg" },
  },
});
```

### Platform targets
```typescript
// Single platform
Platform.MAC.createTarget()
Platform.WINDOWS.createTarget()
Platform.LINUX.createTarget()

// Specific targets
Platform.MAC.createTarget("dmg")
Platform.WINDOWS.createTarget("nsis", Arch.x64, Arch.ia32)

// Multiple platforms
Platform.MAC.createTarget().concat(Platform.WINDOWS.createTarget())
```

### Build options
```typescript
interface PackagerOptions {
  targets?: Map<Platform, Map<Arch, string[]>>;
  config?: Configuration | string;   // Config object or path to config file
  projectDir?: string;
  effectiveOptionComputed?: (options: any) => Promise<boolean>;
  prepackaged?: string;              // Path to prepackaged app
}
```

## Full Programmatic Example

```javascript
const builder = require("electron-builder");
const Platform = builder.Platform;

/** @type {import('electron-builder').Configuration} */
const options = {
  protocols: {
    name: "Deeplink Example",
    schemes: ["deeplink"],
  },
  compression: "normal",
  removePackageScripts: true,

  afterSign: async (context) => {
    if (context.electronPlatformName === "darwin") {
      await notarizeMac(context);
    }
  },
  beforeBuild: async (context) => {
    const { appDir, electronVersion, arch } = context;
    await electronRebuild.rebuild({ buildPath: appDir, electronVersion, arch });
    return false;
  },

  directories: {
    output: "dist/artifacts",
    buildResources: "installer/resources",
  },
  files: ["out"],
  extraFiles: [
    { from: "build/Release", to: "native-addons", filter: "*.node" },
  ],

  win: { target: "nsis" },
  nsis: {
    deleteAppDataOnUninstall: true,
    include: "installer/win/nsis-installer.nsh",
  },

  mac: {
    target: "dmg",
    hardenedRuntime: true,
    gatekeeperAssess: true,
    extendInfo: {
      NSAppleEventsUsageDescription: "Let me use Apple Events.",
      NSCameraUsageDescription: "Let me use the camera.",
    },
  },
  dmg: {
    background: "installer/mac/dmg-background.png",
    iconSize: 100,
    contents: [
      { x: 255, y: 85, type: "file" },
      { x: 253, y: 325, type: "link", path: "/Applications" },
    ],
    window: { width: 500, height: 500 },
  },

  linux: {
    desktop: {
      StartupNotify: "false",
      Encoding: "UTF-8",
      MimeType: "x-scheme-handler/deeplink",
    },
    target: ["AppImage", "rpm", "deb"],
  },
  deb: {
    priority: "optional",
    afterInstall: "installer/linux/after-install.tpl",
  },
};

builder
  .build({ targets: Platform.MAC.createTarget(), config: options })
  .then((result) => console.log(JSON.stringify(result)))
  .catch((error) => console.error(error));
```
