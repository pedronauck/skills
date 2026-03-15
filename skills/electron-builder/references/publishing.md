# Publishing Reference

## Table of Contents
- [Publish CLI Flags](#publish-cli-flags)
- [Auto Publish Rules](#auto-publish-rules)
- [GitHub Releases](#github-releases)
- [Amazon S3](#amazon-s3)
- [Generic Server](#generic-server)
- [DigitalOcean Spaces](#digitalocean-spaces)
- [Keygen](#keygen)
- [Bitbucket](#bitbucket)
- [Snap Store](#snap-store)
- [GitLab](#gitlab)
- [Multiple Publishers](#multiple-publishers)
- [Release Channels](#release-channels)

## Publish CLI Flags

```bash
electron-builder --publish <value>
# or: electron-builder -p <value>
```

| Value | Description |
|---|---|
| `onTag` | Publish only on tag push |
| `onTagOrDraft` | Publish on tag push or if draft release exists |
| `always` | Always publish |
| `never` | Never publish |

### Publish subcommand (upload existing artifacts)
```bash
electron-builder publish -f dist/*.exe -c electron-builder.yml
```

## Auto Publish Rules

If you don't specify `--publish`:
1. CI server detected → `onTagOrDraft`
2. CI detects tag push → `onTag`
3. npm script named `release` → `always`

```json
{
  "scripts": {
    "release": "electron-builder"
  }
}
```
Running `pnpm release` will draft and publish automatically.

## GitHub Releases

Requires `GH_TOKEN` environment variable (personal access token with `repo` scope).

Generate at: https://github.com/settings/tokens/new

### Config
```yaml
publish:
  provider: github
  owner: myorg          # Auto-detected from repository
  repo: myapp           # Auto-detected from repository
  releaseType: draft    # "draft" | "prerelease" | "release"
  private: false        # Set true for private repo auto-update
```

### Recommended workflow
1. Draft a new release on GitHub. Tag = `v${version}` (e.g. `v1.0.0`)
2. Push commits — CI updates draft artifacts
3. When ready, publish the release. GitHub tags latest commit.

### Repository detection order
1. `repository` field in package.json
2. CI env vars: `TRAVIS_REPO_SLUG`, `APPVEYOR_REPO_NAME`, `CIRCLE_PROJECT_USERNAME/CIRCLE_PROJECT_REPONAME`
3. `.git/config` origin URL

### GitHub-specific options
| Property | Default | Description |
|---|---|---|
| `releaseType` | `"draft"` | Release type. Also settable via `EP_DRAFT=true` or `EP_PRE_RELEASE=true` env vars |
| `channel` | `"latest"` | Update channel name |
| `private` | `false` | Use private GitHub auto-update provider |
| `host` | `"github.com"` | Host for GitHub Enterprise |
| `protocol` | `"https"` | Only `https` supported |
| `tagNamePrefix` | `"v"` | Prefix before version in tag (e.g. `v` in `v1.2.3`) |

## Amazon S3

Requires AWS credentials via:
- Env vars: `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`
- Shared credentials: `~/.aws/credentials`
- Config file: `~/.aws/config` (also set `AWS_SDK_LOAD_CONFIG=1`)

### Config
```yaml
publish:
  provider: s3
  bucket: my-bucket-name
  region: us-east-1       # Optional, auto-detected
  acl: public-read        # "public-read" | "private" | null
  path: /releases/${channel}  # Supports macros
  channel: latest
```

### S3-specific options
| Property | Default | Description |
|---|---|---|
| `bucket` | **required** | S3 bucket name |
| `region` | auto | AWS region |
| `acl` | `"public-read"` | Object ACL. Set `null` to not add. |
| `storageClass` | `"STANDARD"` | S3 storage class |
| `encryption` | — | Server-side encryption: `"AES256"` or `"aws:kms"` |
| `accelerate` | `false` | Use S3 Transfer Acceleration endpoint |
| `path` | `"/"` | Directory path within bucket |
| `channel` | `"latest"` | Update channel |
| `endpoint` | — | Custom S3 endpoint (for MinIO, etc.) |

### Continuous deployment workflow (S3)
1. CI publishes on each commit: `"dist": "electron-builder --publish always"`
2. Dev version: `1.9.0-snapshot` → publishes `snapshot.yml`
3. Release: Change to `1.9.0`, push, tag
4. Post-release: Bump to `1.10.0-snapshot`

## Generic Server

Host files on any HTTP(S) server. **You must upload files manually.**

```yaml
publish:
  provider: generic
  url: https://example.com/releases
  channel: latest
```

| Property | Default | Description |
|---|---|---|
| `url` | **required** | Base URL |
| `channel` | `"latest"` | Channel name |
| `useMultipleRangeRequest` | `true` | Use HTTP Range requests for differential download |

Upload these files to the server:
- The installer/app artifacts
- `latest.yml` / `latest-mac.yml` / `latest-linux.yml`

## DigitalOcean Spaces

Same as S3 but with `provider: spaces`:

```yaml
publish:
  provider: spaces
  name: my-space-name
  region: nyc3
```

Requires `DO_KEY_ID` and `DO_SECRET_KEY` env vars.

## Keygen

```yaml
publish:
  provider: keygen
  account: "your-keygen-account-uuid"
  product: "your-keygen-product-uuid"
  channel: stable   # "stable" | "rc" | "beta" | "alpha" | "dev"
```

Requires `KEYGEN_TOKEN` env var.

## Bitbucket

```yaml
publish:
  provider: bitbucket
  owner: myorg
  slug: myrepo
```

Requires `BITBUCKET_TOKEN` env var (app password converted to Basic auth token):
```typescript
const token = `Basic ${Buffer.from(`${owner}:${appPassword}`).toString("base64")}`;
```

## Snap Store

```yaml
publish:
  provider: snapStore
  channels:
    - stable
    - edge
```

Requires `SNAP_TOKEN` env var.

## GitLab

```yaml
publish:
  provider: gitlab
  projectId: 12345
```

Requires `GITLAB_TOKEN` env var.

## Multiple Publishers

Specify an array of publish configs:
```yaml
publish:
  - provider: github
  - provider: s3
    bucket: my-bucket
    publishAutoUpdate: false  # Only first provider needed for auto-update metadata
```

`publishAutoUpdate` defaults to `true`. Set to `false` on secondary providers to skip uploading metadata files (auto-update only uses the first provider).

## Release Channels

Version determines channel automatically:
- `1.0.0` → `latest` channel
- `1.0.0-beta.1` → `beta` channel
- `1.0.0-alpha.1` → `alpha` channel

Config option to generate update files for ALL channels:
```yaml
generateUpdatesFilesForAllChannels: true
```

To detect update channel automatically:
```yaml
detectUpdateChannel: true   # Default
```

Channel can also be set explicitly per-provider:
```yaml
publish:
  provider: github
  channel: beta
```

Users on `beta` channel receive both `beta` and `latest` updates. Users on `latest` only receive `latest`.
