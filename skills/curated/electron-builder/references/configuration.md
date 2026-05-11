# electron-builder Configuration Reference

## Table of Contents
- [Config File Locations](#config-file-locations)
- [Core Properties](#core-properties)
- [Directories](#directories)
- [Files and Content](#files-and-content)
- [File Patterns and Macros](#file-patterns-and-macros)
- [Native Dependencies](#native-dependencies)
- [Electron Fuses](#electron-fuses)
- [Build Version Management](#build-version-management)
- [Icons](#icons)

## Config File Locations

Config can live in any of these (checked in order):
1. `package.json` under `"build"` key
2. `electron-builder.yml` (default, recommended)
3. `electron-builder.json` / `.json5` / `.toml`
4. `electron-builder.config.js` / `.ts` (exported config or function)
5. CLI: `--config <path>`

**Warning**: Do NOT name JS config `electron-builder.js` — conflicts with the package name.

For TOML support, install: `pnpm add toml -D`

Env file `electron-builder.env` in current dir is supported (CLI only).

### YAML example (electron-builder.yml)
```yaml
appId: com.example.myapp
productName: My App
directories:
  output: dist
  buildResources: build
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
```

### JS/TS example (electron-builder.config.js)
```js
/** @type {import('electron-builder').Configuration} */
module.exports = {
  appId: "com.example.myapp",
  productName: "My App",
  files: ["out"],
  mac: { target: "dmg" },
  win: { target: "nsis" },
  linux: { target: ["AppImage", "deb"] },
};
```

## Core Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `appId` | string | `com.electron.${name}` | CFBundleIdentifier (macOS), AUMID (Windows NSIS). **Do not change once published.** |
| `productName` | string | package.json name | Display name, allows spaces/special chars |
| `copyright` | string | `Copyright © year ${author}` | Human-readable copyright |
| `compression` | `"store"` \| `"normal"` \| `"maximum"` | `"normal"` | Use `store` for fast test builds |
| `asar` | boolean \| AsarOptions | `true` | Pack source into asar archive |
| `asarUnpack` | string \| string[] | — | Glob patterns for files to unpack from asar |
| `extraMetadata` | any | — | Inject properties into `package.json` |
| `removePackageKeywords` | boolean | `true` | Remove `keywords` from package.json |
| `forceCodeSigning` | boolean | `false` | Fail build if app is not signed |
| `electronLanguages` | string[] | — | Limit languages included in Electron |
| `concurrency` | object | — | [Experimental] Concurrent build config |

## Directories

Set via `directories` key:

```yaml
directories:
  output: dist/artifacts    # Build output (default: "dist")
  buildResources: build     # Build resources like icons (default: "build")
  app: .                    # Application directory (default: ".")
```

## Files and Content

### `files` — Application source files
```yaml
files:
  - "out/**/*"
  - "package.json"
  - "!**/*.map"           # Exclude source maps
  - "!**/node_modules/*/{CHANGELOG.md,README.md}"
```

Default files pattern includes everything except:
- Build resources directory
- Hidden files (`.dot`)
- Standard non-runtime files (README, CHANGELOG, etc.)
- `node_modules/.bin`

### `extraFiles` — Copied outside asar
```yaml
extraFiles:
  - from: "build/Release"
    to: "native-addons"
    filter: "*.node"
```

### `extraResources` — Copied to resources directory
```yaml
extraResources:
  - from: "assets/"
    to: "assets"
    filter: ["**/*", "!*.psd"]
```

Both accept `string | FileSet | Array<string | FileSet>`.

FileSet format:
```typescript
interface FileSet {
  from?: string;   // Source (relative to project)
  to?: string;     // Destination (relative to app content)
  filter?: string | string[];  // Glob patterns
}
```

## File Patterns and Macros

### Pattern syntax
- `*` — 0+ chars in single path portion
- `**` — 0+ directories (globstar)
- `?` — 1 character
- `[...]` — character range
- `!(pattern|pattern)` — negation
- `!doNotCopyMe${/*}` — exclude directory AND contents (not just files)

### Macros (usable in file patterns, artifactName, publish URLs)
| Macro | Expands to |
|---|---|
| `${arch}` | `ia32`, `x64`, `arm64`, `armv7l` |
| `${os}` | `mac`, `linux`, `win` |
| `${platform}` | `darwin`, `linux`, `win32` |
| `${name}` | package.json name |
| `${productName}` | Sanitized product name |
| `${version}` | package.json version |
| `${channel}` | Prerelease component (e.g. `beta`) |
| `${ext}` | Target extension |
| `${env.ENV_NAME}` | Any environment variable |

### Artifact name template
```yaml
artifactName: "${productName}-${version}-${arch}.${ext}"
```

## Native Dependencies

| Property | Type | Default | Description |
|---|---|---|---|
| `npmRebuild` | boolean | `true` | Rebuild native deps before packaging |
| `nodeGypRebuild` | boolean | `false` | Run `node-gyp rebuild` before packaging |
| `nativeRebuilder` | `"legacy"` \| `"sequential"` \| `"parallel"` | `"sequential"` | Rebuilder strategy |
| `buildDependenciesFromSource` | boolean | `false` | Build native deps from source |
| `npmArgs` | string \| string[] | — | Extra args for `npm install` of native deps |

**Tip**: Use `electron-builder node-gyp-rebuild` instead of npm for configuring electron headers.

## Electron Fuses

Configure via `electronFuses` key:
```yaml
electronFuses:
  RunAsNode: false
  EnableCookieEncryption: true
  EnableNodeOptionsEnvironmentVariable: false
  EnableNodeCliInspectArguments: false
  EnableEmbeddedAsarIntegrityValidation: true
  OnlyLoadAppFromAsar: true
```

Reference: https://github.com/electron/fuses

## Build Version Management

| Property | Description |
|---|---|
| `buildVersion` | Maps to `CFBundleVersion` (macOS), `FileVersion` (Windows). Defaults to `version`. |
| `buildNumber` | Maps to `--iteration` for FPM (Linux). Falls back to CI env vars: `BUILD_NUMBER`, `TRAVIS_BUILD_NUMBER`, `APPVEYOR_BUILD_NUMBER`, `CIRCLE_BUILD_NUM`, `BUILD_BUILDNUMBER`, `CI_PIPELINE_IID`. |

If `buildVersion` undefined but `buildNumber` is set: `buildVersion = version.buildNumber`.

## Icons

Place in `buildResources` directory (default: `build/`):

### macOS
- `icon.icon` (preferred, Apple Icon Composer — needs Xcode 26+ on macOS 15+)
- `icon.icns` (legacy, copied to bundle via CFBundleIconFile)
- `icon.png` (at least 512x512)
- `background.png` / `background@2x.png` for DMG

### Windows
- `icon.ico` or `icon.png` (at least 256x256)

### Linux
- Auto-generated from macOS icns or `icon.png`
- Or manually: `build/icons/256x256.png` (sizes: 16, 32, 48, 64, 128, 256, 512)
