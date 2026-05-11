---
name: electron-release
description: Expert guide for Electron production builds, code signing, notarization, auto-updates, and release workflows. Use when building, packaging, or releasing Electron applications, configuring electron-builder, setting up CI/CD pipelines for desktop app distribution, or implementing auto-update mechanisms.
allowed-tools: Read, Grep, Glob, Bash
---

# Electron Production Build & Release Guide

This skill provides enterprise-grade best practices for building, signing, releasing, and distributing Electron applications with emphasis on security, reliability, performance, and user trust.

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

### macOS (Developer ID + Notarization)

Two-step process:
1. **Code Signing**: Uses Developer ID Certificate
2. **Notarization**: Apple scans for malware (required for distribution)

Key requirements:
- `hardenedRuntime: true` in electron-builder config
- Valid entitlements.mac.plist
- APPLE_TEAM_ID, APPLE_ID, and APPLE_APP_SPECIFIC_PASSWORD environment variables

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

### Testing Auto-Update Locally

Use `dev-app-update.yml` for local testing. Test the full update cycle before releasing.

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

### Private Server (Generic HTTP)

Requires serving `latest.yml`, `latest-mac.yml`, and all artifacts via HTTPS.

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

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Auto-update not triggering | Verify `latest.yml` exists, check GitHub releases config |
| Code signing fails | Renew certificate, verify fingerprint |
| Windows SmartScreen warning | Distribute widely, file with Microsoft for reputation |
| macOS "cannot verify developer" | Re-notarize, check team ID and certificate |
| Large app download | Analyze with `ANALYZE=true pnpm run build`, enable compression |
| Blank screen in production | Use relative paths (`base: './'`), verify build output |

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

For detailed configuration examples, code samples, and GitHub Actions workflows, refer to `references/patterns.md`.
