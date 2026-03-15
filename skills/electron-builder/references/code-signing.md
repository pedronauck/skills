# Code Signing Reference

## Table of Contents
- [Environment Variables](#environment-variables)
- [macOS Code Signing](#macos-code-signing)
- [macOS Notarization](#macos-notarization)
- [Disabling macOS Signing](#disabling-macos-signing)
- [Windows Code Signing](#windows-code-signing)
- [Azure Trusted Signing (Windows)](#azure-trusted-signing-windows)
- [CI Server Setup](#ci-server-setup)
- [Signing Windows Apps on macOS/Linux](#signing-windows-apps-on-macoslinux)

## Environment Variables

| Env Name | Description |
|---|---|
| `CSC_LINK` | HTTPS link, base64-encoded data, `file://` link, or local path to `.p12`/`.pfx` certificate. `~/` supported. |
| `CSC_KEY_PASSWORD` | Password to decrypt the certificate in `CSC_LINK` |
| `CSC_NAME` | (macOS only) Certificate name from keychain. Useful on dev machine with multiple identities. |
| `CSC_IDENTITY_AUTO_DISCOVERY` | `true`/`false`. Default `true`. Auto-discover valid identity from keychain. |
| `CSC_KEYCHAIN` | Keychain name. Used if `CSC_LINK` not set. Defaults to system keychain. |
| `CSC_INSTALLER_LINK` | Certificate for PKG installer signing |
| `CSC_INSTALLER_KEY_PASSWORD` | Password for installer certificate |
| `WIN_CSC_LINK` | Windows-specific certificate (when cross-signing from macOS) |
| `WIN_CSC_KEY_PASSWORD` | Windows-specific certificate password |

## macOS Code Signing

Signing is automatic if configuration is correct. On a dev machine, a valid identity from your keychain is auto-used.

Default behavior by architecture:
- **ARM / Universal builds**: Ad-hoc signature applied by default (no identity needed)
- **Intel-only builds**: No signing by default

### Certificates needed
| Purpose | Certificate Type |
|---|---|
| Distribution outside App Store | `Developer ID Application:` |
| Distribution + Installer outside App Store | `Developer ID Application:` + `Developer ID Installer` |
| Mac App Store | `3rd Party Mac Developer Installer:` + `Apple Distribution` (or `3rd Party Mac Developer Application:`) |
| MAS Development testing | `Apple Development:` or `Mac Developer:` + provisioning profile |

### Exporting certificates
1. Open Keychain Access
2. Select `login` keychain > `My Certificates`
3. Cmd-click to select all needed certificates
4. Right-click > Export as `.p12`

Multiple certificates can be selected and exported together — all will be imported into temporary keychain on CI.

### Mac-specific config options
```yaml
mac:
  identity: "Developer ID Application: Company Name (TEAM_ID)"  # or null to skip, or "-" for ad-hoc
  hardenedRuntime: true           # Required for notarization
  gatekeeperAssess: false         # Skip Gatekeeper assessment
  entitlements: build/entitlements.mac.plist
  entitlementsInherit: build/entitlements.mac.plist
  signIgnore:                     # Glob patterns to skip signing
    - "*.provisionprofile"
  strictVerify: true              # Strict codesign verification
  type: distribution              # "distribution" | "development"
  timestamp: null                 # RFC 3161 timestamp server URL
```

## macOS Notarization

electron-builder supports notarization natively:

```yaml
mac:
  notarize: true    # Uses `notarytool` (requires Xcode 13+)
```

Or with explicit options:
```yaml
mac:
  notarize:
    teamId: "TEAM_ID"
```

Environment variables for notarization:
- `APPLE_ID` — Apple ID email
- `APPLE_APP_SPECIFIC_PASSWORD` — App-specific password
- `APPLE_TEAM_ID` — Team ID

Alternatively, use API key authentication:
- `APPLE_API_KEY` — Path to .p8 key file
- `APPLE_API_KEY_ID` — Key ID
- `APPLE_API_ISSUER` — Issuer ID

## Disabling macOS Signing

Option 1: Environment variable
```bash
export CSC_IDENTITY_AUTO_DISCOVERY=false
```

Option 2: Config
```yaml
mac:
  identity: null
```

Option 3: CLI
```bash
electron-builder -c.mac.identity=null
```

For ARM builds that need ad-hoc signing:
```yaml
mac:
  identity: "-"
```

## Windows Code Signing

Windows apps are dual code-signed (SHA1 + SHA256).

### Certificate types
| Type | Pros | Cons |
|---|---|---|
| **Code Signing Certificate** | Cheaper, exportable for CI | Shows warning until trust is built |
| **EV Code Signing Certificate** | Immediate trust, no warnings | Bound to USB dongle, can't export for CI |

For EV certificates, set:
```yaml
win:
  certificateSubjectName: "Your Company Name"
```

### Windows-specific config
```yaml
win:
  certificateFile: path/to/cert.pfx
  certificatePassword: ""                    # Or use CSC_KEY_PASSWORD env
  certificateSubjectName: ""                 # For EV certs
  certificateSha1: ""                        # Thumbprint
  signingHashAlgorithms:
    - sha256
  sign: "./custom-sign.js"                   # Custom sign script
  signDlls: false                            # Also sign DLLs
  signExts:                                  # Additional extensions to sign
    - ".dll"
    - ".exe"
```

## Azure Trusted Signing (Windows)

Microsoft's cloud code signing service. Config:

```yaml
win:
  azureSignOptions:
    publisherName: "CN=Your Company"         # Must match certificate CN exactly
    endpoint: "https://eus.codesigning.azure.net"
    certificateProfileName: "your-profile"
    codeSigningAccountName: "your-account"
```

Required environment variables (from Azure App Registration):
| Env Name | Description |
|---|---|
| `AZURE_TENANT_ID` | Azure AD Tenant ID |
| `AZURE_CLIENT_ID` | App Registration's Application (Client) ID |
| `AZURE_CLIENT_SECRET` | App Registration's Secret value |

Setup steps:
1. Create Azure Trusted Signing Account ([quickstart](https://learn.microsoft.com/en-us/azure/trusted-signing/quickstart))
2. Create App Registration in Azure Entra ID
3. Create a Secret for the App Registration
4. Assign "Trusted Signing Certificate Profile Signer" role to the App Registration

## CI Server Setup

1. Export certificate as `.p12`
2. Base64 encode: `base64 -i cert.p12 -o encoded.txt` (macOS) or `base64 cert.p12 > encoded.txt` (Linux)
3. Set `CSC_LINK` to the base64 string (or HTTPS URL to the file)
4. Set `CSC_KEY_PASSWORD` to the certificate password

**CI-specific notes**:
- Set vars in CI project settings, NOT in config files
- AppVeyor: Click lock icon to encrypt variables
- Windows: env var values limited to 8192 chars — re-export cert without full chain if too large
- Avoid special bash characters in passwords. Test with: `printf "%q\n" "<password>"`

## Signing Windows Apps on macOS/Linux

Use `WIN_CSC_LINK` and `WIN_CSC_KEY_PASSWORD` instead of `CSC_*` vars:

```bash
export WIN_CSC_LINK="base64-encoded-pfx-or-url"
export WIN_CSC_KEY_PASSWORD="password"
```

For EV certificates on Unix, see the [dedicated tutorial](https://www.electron.build/tutorials/code-signing-windows-apps-on-unix).
