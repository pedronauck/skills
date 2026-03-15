# Electron Production Build & Release Patterns

This document provides enterprise-grade best practices for building, signing, releasing, and distributing Electron applications with emphasis on security, reliability, performance, and user trust.

## Quick Reference

1. **Build Configuration**: For electron-vite production config, bundle optimization, and pre-build checks.
2. **Code Signing**: Platform-specific signing for Windows (EV certificates), macOS (Developer ID + notarization), and Linux (GPG).
3. **Auto-Updates**: electron-updater configuration, staged rollouts, and update testing.
4. **Release Workflows**: GitHub Actions CI/CD pipelines for multi-platform builds.
5. **Distribution**: GitHub Releases, Cloudflare R2, or private server hosting.

## Core Principles

- **Security First**: All production builds must be code-signed; macOS builds must be notarized.
- **Pre-Build Verification**: Always run `pnpm audit`, `pnpm run typecheck`, `pnpm run lint`, and `pnpm run test` before builds.
- **Semantic Versioning**: Follow SemVer strictly (MAJOR.MINOR.PATCH).
- **Staged Rollouts**: Release to a percentage of users first, then expand gradually.

## Build Strategy

### Pre-Build Checklist

Before every production build:

1. Check dependencies for vulnerabilities: `pnpm audit`
2. Verify code quality: `pnpm run typecheck && pnpm run lint`
3. Run test suite: `pnpm run test && pnpm run test:e2e`
4. Check bundle size: `pnpm run build:analyzer`
5. Verify environment configuration

### Production Build Optimization

- Remove all `console.log` and `debugger` statements
- Tree-shake unused dependencies
- Split vendor chunks (React, UI libraries)
- Compress images and assets
- Lazy load non-critical modules
- Disable source maps for distribution (ship separately if needed)
- Use production-mode build flags

### Target Bundle Sizes

| Component        | Target   |
|------------------|----------|
| Main process     | < 2 MB   |
| Renderer         | < 5 MB   |
| Total package    | < 150 MB |
| Install size     | < 250 MB |

## Code Signing

### Windows (EV Certificate Required)

Microsoft requires Extended Validation (EV) certificates since June 2023.

**Recommended**: Use cloud-based signing (DigiCert KeyLocker or Azure Trusted Signing).

**Never use self-signed certificates for distribution.**

#### Windows Configuration Example

```yaml
# electron-builder.yml
win:
  sign: ./scripts/sign-windows.js
  signingHashAlgorithms:
    - sha256
  certificateSubjectName: "Your Company Name"
  publisherName: "Your Company Name"
```

```javascript
// scripts/sign-windows.js (DigiCert KeyLocker example)
const { execSync } = require("child_process");

exports.default = async function (config) {
  const filePath = config.path;

  execSync(`smctl sign --keypair-alias=${process.env.DIGICERT_KEYPAIR_ALIAS} \
    --certificate=${process.env.DIGICERT_CERTIFICATE_FINGERPRINT} \
    --input="${filePath}"`, { stdio: "inherit" });
};
```

### macOS (Developer ID + Notarization)

Two-step process:
1. **Code Signing**: Uses Developer ID Certificate
2. **Notarization**: Apple scans for malware (required for distribution)

Key requirements:
- `hardenedRuntime: true` in electron-builder config
- Valid entitlements.mac.plist
- APPLE_TEAM_ID, APPLE_ID, and APPLE_APP_SPECIFIC_PASSWORD environment variables

#### macOS Configuration Example

```yaml
# electron-builder.yml
mac:
  hardenedRuntime: true
  gatekeeperAssess: false
  entitlements: build/entitlements.mac.plist
  entitlementsInherit: build/entitlements.mac.plist
  notarize:
    teamId: ${env.APPLE_TEAM_ID}
```

```xml
<!-- build/entitlements.mac.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>com.apple.security.cs.allow-jit</key>
  <true/>
  <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
  <true/>
  <key>com.apple.security.cs.disable-library-validation</key>
  <true/>
  <key>com.apple.security.automation.apple-events</key>
  <true/>
</dict>
</plist>
```

### Linux (GPG)

Sign release artifacts with GPG:
```bash
gpg --detach-sign -u YOUR_KEY_ID dist/packages/*.AppImage
gpg --detach-sign -u YOUR_KEY_ID dist/packages/*.deb
```

## Auto-Update Implementation

### electron-updater Configuration

Configure publish provider in electron-builder.yml:
```yaml
publish:
  provider: github
  owner: your-username
  repo: your-repo
  releaseType: release
```

### Main Process Auto-Update Setup

```typescript
// src/main/updater.ts
import { autoUpdater } from "electron-updater";
import { app, BrowserWindow } from "electron";

export function setupAutoUpdater(mainWindow: BrowserWindow) {
  autoUpdater.autoDownload = false;
  autoUpdater.autoInstallOnAppQuit = true;

  autoUpdater.on("update-available", (info) => {
    mainWindow.webContents.send("update-available", info);
  });

  autoUpdater.on("update-downloaded", (info) => {
    mainWindow.webContents.send("update-downloaded", info);
  });

  autoUpdater.on("error", (error) => {
    mainWindow.webContents.send("update-error", error.message);
  });

  // Check for updates every 4 hours
  setInterval(() => {
    autoUpdater.checkForUpdates();
  }, 4 * 60 * 60 * 1000);

  // Initial check after app is ready
  autoUpdater.checkForUpdates();
}

export function downloadUpdate() {
  autoUpdater.downloadUpdate();
}

export function installUpdate() {
  autoUpdater.quitAndInstall();
}
```

### Staged Rollout Strategy

Reduce risk by gradually rolling out updates:
- Day 1: 10% of users
- Day 2: 25% of users
- Day 3: 50% of users
- Day 4: 100% of users

**If issues detected**:
- Do NOT release same version again (users will ignore update)
- Release a higher version (e.g., 1.0.1 -> 1.0.2)
- Consider reverting to previous version if critical bug

### Staged Rollout Implementation

```yaml
# latest.yml (generated by electron-builder, can be modified for staged rollout)
version: 1.2.3
files:
  - url: YourApp-1.2.3.exe
    sha512: <hash>
    size: 123456789
path: YourApp-1.2.3.exe
sha512: <hash>
stagingPercentage: 10  # Only 10% of users get this update
releaseDate: "2024-01-15T10:00:00.000Z"
```

### Testing Auto-Update Locally

Create `dev-app-update.yml` in project root:
```yaml
provider: generic
url: http://localhost:8080/releases
```

Test with local server:
```bash
# Serve releases directory
npx http-server ./releases -p 8080

# Run app with dev update config
cross-env ELECTRON_IS_DEV=0 electron .
```

## Release Workflow

### Manual Release Checklist

Before creating release tag:
- [ ] Merge all PRs for this version
- [ ] Bump version in `package.json`
- [ ] Update `CHANGELOG.md`
- [ ] Run full test suite
- [ ] Run bundle analysis
- [ ] Test build locally
- [ ] Verify app starts and basic features work
- [ ] Test auto-update mechanism

### Creating a Release

```bash
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

GitHub Actions automatically handles:
1. Building for Windows, macOS, Linux
2. Code signing
3. Notarization (macOS)
4. Creating GitHub Release
5. Publishing artifacts

### GitHub Actions Release Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - "v*"

jobs:
  release:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [macos-latest, ubuntu-latest, windows-latest]

    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v2
        with:
          version: 9

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run checks
        run: |
          pnpm run typecheck
          pnpm run lint
          pnpm run test

      - name: Build and release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # macOS signing
          CSC_LINK: ${{ secrets.MAC_CERTS }}
          CSC_KEY_PASSWORD: ${{ secrets.MAC_CERTS_PASSWORD }}
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_APP_SPECIFIC_PASSWORD: ${{ secrets.APPLE_APP_SPECIFIC_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
          # Windows signing (DigiCert KeyLocker)
          DIGICERT_KEYPAIR_ALIAS: ${{ secrets.DIGICERT_KEYPAIR_ALIAS }}
          DIGICERT_CERTIFICATE_FINGERPRINT: ${{ secrets.DIGICERT_CERTIFICATE_FINGERPRINT }}
          SM_API_KEY: ${{ secrets.SM_API_KEY }}
        run: pnpm run build:release
```

## Distribution Options

### GitHub Releases (Recommended)

- Free and reliable
- Built-in auto-update support
- Version management
- Release notes

### Cloudflare R2

S3-compatible storage with R2 endpoint. Configure environment variables:
- R2_BUCKET_NAME
- R2_ACCOUNT_ID
- R2_ACCESS_KEY_ID
- R2_SECRET_ACCESS_KEY
- UPDATE_FEED_URL

```yaml
# electron-builder.yml for R2
publish:
  provider: s3
  bucket: ${env.R2_BUCKET_NAME}
  endpoint: https://${env.R2_ACCOUNT_ID}.r2.cloudflarestorage.com
  acl: public-read
```

### Private Server (Generic HTTP)

Requires serving `latest.yml`, `latest-mac.yml`, and all artifacts via HTTPS.

```yaml
# electron-builder.yml for private server
publish:
  provider: generic
  url: https://your-server.com/releases
  channel: latest
```

## Security Checklist

Before release, verify:
- [ ] Dependencies audited (`pnpm audit`)
- [ ] No hardcoded secrets in code
- [ ] IPC channels validated
- [ ] CSP properly configured
- [ ] Context isolation enabled
- [ ] Node integration disabled in renderer
- [ ] Sandbox enabled for all windows
- [ ] Auto-update tested end-to-end
- [ ] Code signing certificates valid
- [ ] macOS app notarized
- [ ] All communications over HTTPS
- [ ] No sensitive data in logs or error messages

### Secure Electron Configuration

```typescript
// src/main/index.ts
const mainWindow = new BrowserWindow({
  webPreferences: {
    nodeIntegration: false,
    contextIsolation: true,
    sandbox: true,
    webSecurity: true,
    preload: path.join(__dirname, "preload.js"),
  },
});

// CSP Header
mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
  callback({
    responseHeaders: {
      ...details.responseHeaders,
      "Content-Security-Policy": [
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
      ],
    },
  });
});
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Auto-update not triggering | Verify `latest.yml` exists, check GitHub releases config |
| Code signing fails | Renew certificate, verify fingerprint |
| Windows SmartScreen warning | Distribute widely, file with Microsoft for reputation |
| macOS "cannot verify developer" | Re-notarize, check team ID and certificate |
| Large app download | Analyze with `ANALYZE=true pnpm run build`, enable compression |
| Blank screen in production | Use relative paths (`base: './'`), verify build output |

### Common Notarization Issues

```bash
# Check notarization status
xcrun notarytool log <submission-id> --apple-id $APPLE_ID --password $APPLE_APP_SPECIFIC_PASSWORD --team-id $APPLE_TEAM_ID

# Staple notarization ticket
xcrun stapler staple "YourApp.app"

# Verify notarization
spctl -a -vvv -t install "YourApp.app"
```

### Debug Auto-Update

```typescript
// Enable verbose logging
import log from "electron-log";
import { autoUpdater } from "electron-updater";

autoUpdater.logger = log;
autoUpdater.logger.transports.file.level = "debug";
```

## Validation Checklist

Before finishing a task involving Electron releases:

- [ ] Pre-build checks pass (audit, typecheck, lint, test)
- [ ] Bundle sizes within targets
- [ ] Code signing configured for all platforms
- [ ] macOS notarization configured
- [ ] Auto-update mechanism implemented and tested
- [ ] Staged rollout strategy defined
- [ ] Security checklist completed
- [ ] Release notes prepared
