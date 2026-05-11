# Platform Targets Reference

## Table of Contents
- [Default Targets](#default-targets)
- [Target Configuration](#target-configuration)
- [macOS Targets](#macos-targets)
- [Windows Targets](#windows-targets)
- [Linux Targets](#linux-targets)

## Default Targets

| Build Platform | Default Targets |
|---|---|
| macOS | DMG + ZIP (for Squirrel.Mac) |
| Windows | NSIS |
| Linux (from Windows/macOS) | Snap + AppImage (x64) |
| Linux (native) | Snap + AppImage (current arch) |

## Target Configuration

### CLI
```bash
electron-builder -mwl                          # All platforms
electron-builder --mac dmg --win nsis --linux AppImage deb
electron-builder --windows nsis:ia32            # Target with specific arch
electron-builder --linux deb tar.xz             # Multiple targets
```

### Config (electron-builder.yml)
```yaml
win:
  target:
    - target: nsis
      arch:
        - x64
        - ia32
mac:
  target:
    - target: dmg
      arch: universal
linux:
  target:
    - AppImage
    - deb
    - rpm
```

### TargetConfiguration object
```typescript
interface TargetConfiguration {
  target: string;    // Required: target name (e.g. "nsis", "dmg")
  arch?: string[];   // "x64" | "ia32" | "armv7l" | "arm64" | "universal"
}
```

---

## macOS Targets

### DMG
```yaml
dmg:
  background: build/dmg-background.png  # Background image
  backgroundColor: "#ffffff"            # Or solid color
  iconSize: 80
  iconTextSize: 12
  title: "${productName} ${version}"
  contents:                             # Icon positions
    - x: 130
      y: 220
      type: file                        # The app
    - x: 410
      y: 220
      type: link
      path: /Applications              # Alias to Applications
  window:
    x: 400
    y: 100
    width: 540
    height: 380
  sign: true                            # Sign the DMG itself
  writeUpdateInfo: true                 # Write auto-update info
```

### PKG (macOS installer)
```yaml
pkg:
  installLocation: /Applications
  allowAnywhere: true
  allowCurrentUserHome: true
  allowRootDirectory: true
  isRelocatable: false
  overwriteAction: upgrade
  scripts: build/pkg-scripts            # Pre/post install scripts
  license: build/license.txt
```

**Note**: PKG signing requires `INSTALLER ID` identity or `CSC_INSTALLER_LINK`/`CSC_INSTALLER_KEY_PASSWORD`.

### MAS (Mac App Store)
```yaml
mas:
  entitlements: build/entitlements.mas.plist
  entitlementsInherit: build/entitlements.mas.inherit.plist
  provisioningProfile: build/embedded.provisionprofile
  hardenedRuntime: false                # MAS doesn't use hardened runtime
  category: public.app-category.developer-tools
  type: distribution
```

Certificates needed:
- `3rd Party Mac Developer Installer:`
- `Apple Distribution` or `3rd Party Mac Developer Application:`

### macOS common options
```yaml
mac:
  category: public.app-category.developer-tools
  hardenedRuntime: true                  # Required for notarization
  darkModeSupport: true
  minimumSystemVersion: "10.15"
  extendInfo:                            # Extra Info.plist entries
    NSAppleEventsUsageDescription: "Let me use Apple Events."
    NSCameraUsageDescription: "Camera access needed."
  entitlements: build/entitlements.mac.plist
  entitlementsInherit: build/entitlements.mac.plist
  notarize: true
  binaries:                              # Extra binaries to sign
    - path/to/helper
  type: distribution                     # "distribution" | "development"
  mergeASARs: true                       # Merge x64+arm64 ASARs for universal
```

---

## Windows Targets

### NSIS (default)
```yaml
nsis:
  oneClick: true                         # Default. Set false for assisted installer.
  perMachine: false                      # Install for all users (requires admin)
  allowElevation: true                   # Allow requesting elevation (assisted only)
  allowToChangeInstallationDirectory: false  # Let user choose dir (assisted only)
  installerIcon: build/icon.ico
  uninstallerIcon: build/icon.ico
  installerHeader: build/header.bmp      # 150x57 (assisted only)
  installerHeaderIcon: build/icon.ico    # One-click header icon
  installerSidebar: build/sidebar.bmp    # 164x314 (assisted only)
  uninstallerSidebar: build/sidebar.bmp
  license: build/license.html            # Or .txt, .rtf
  createDesktopShortcut: true            # true | false | "always"
  createStartMenuShortcut: true
  shortcutName: "My App"
  deleteAppDataOnUninstall: false
  include: build/installer.nsh           # Custom NSIS script to include
  guid: null                             # Auto-generated from appId (don't change appId!)
  unicode: true                          # Default true
  runAfterFinish: true                   # Launch app after install
  menuCategory: false                    # Start menu subfolder
  artifactName: "${productName} Setup ${version}.${ext}"
  differentialPackage: true              # Delta updates
```

**GUID warning**: Do NOT change `appId` once app is deployed. A UUID v5 is generated from appId for registry keys.

### Custom NSIS script
Place `build/installer.nsh` with macros:
- `customHeader`, `preInit`, `customInit`, `customUnInit`
- `customInstall`, `customUnInstall`, `customRemoveFiles`
- `customInstallMode`, `customWelcomePage`, `customUnWelcomePage`
- `customUnInstallSection`

Available variables: `BUILD_RESOURCES_DIR`, `PROJECT_DIR`, `${isUpdated}`

```nsis
!macro customInstall
  File /oname=$PLUGINSDIR\extra.msi "${BUILD_RESOURCES_DIR}\extra.msi"
  ExecWait '"msiexec" /i "$PLUGINSDIR\extra.msi" /passive'
!macroend
```

### NSIS Web Installer
Set target to `nsis-web`. Auto-detects OS arch, downloads correct package. Customize with `nsisWeb` key (not `nsis`).

### Portable
```bash
electron-builder --win portable
```
Env vars available at runtime: `PORTABLE_EXECUTABLE_FILE`, `PORTABLE_EXECUTABLE_DIR`, `PORTABLE_EXECUTABLE_APP_FILENAME`

### MSI
```yaml
msi:
  oneClick: true
  perMachine: true
  runAfterFinish: true
  createDesktopShortcut: true
```

### AppX (Windows Store)
```yaml
appx:
  identityName: "Company.AppName"
  publisher: "CN=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
  publisherDisplayName: "Company Name"
  applicationId: "AppName"
  languages:
    - en-US
```

### Squirrel.Windows
**Not recommended** — no auto-update support with electron-updater. Use NSIS instead.

---

## Linux Targets

### Common Linux options
```yaml
linux:
  category: Development                  # Freedesktop category
  synopsis: "Short description"
  description: "Longer description"
  desktop:
    StartupNotify: "false"
    Encoding: "UTF-8"
    MimeType: "x-scheme-handler/myapp"
  icon: build/icons                      # Directory with size-named PNGs
  target:
    - AppImage
    - deb
    - rpm
    - snap
```

### AppImage
```yaml
appImage:
  license: build/license.txt
  artifactName: "${name}-${version}-${arch}.AppImage"
```
Auto-updatable. Self-contained, no installation needed.

### DEB (Debian/Ubuntu)
```yaml
deb:
  depends:                               # Package dependencies
    - libnotify4
    - libxtst6
  packageCategory: utils
  priority: optional
  afterInstall: build/after-install.sh
  afterRemove: build/after-remove.sh
  fpm:                                   # Extra FPM arguments
    - "--deb-no-default-config-files"
```

### RPM (Fedora/RHEL)
```yaml
rpm:
  depends:
    - libnotify
  fpm:
    - "--rpm-rpmbuild-define=_build_id_links none"
```

### Snap
```yaml
snap:
  confinement: strict                    # "strict" | "devmode" | "classic"
  grade: stable                          # "stable" | "devel"
  summary: "Short summary"
  plugs:
    - default
    - removable-media
  publish:
    provider: snapStore
    channels:
      - stable
```

### Flatpak
```yaml
flatpak:
  runtime: org.freedesktop.Platform
  runtimeVersion: "23.08"
  sdk: org.freedesktop.Sdk
  finishArgs:
    - "--share=ipc"
    - "--socket=x11"
    - "--socket=wayland"
    - "--socket=pulseaudio"
    - "--share=network"
```

### Pacman (Arch Linux)
Auto-updatable (beta). Configure under `pacman` key with same options as other Linux targets.
