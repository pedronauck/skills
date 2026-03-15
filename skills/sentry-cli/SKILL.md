---
name: sentry-cli
description: Guide for using the Sentry CLI to interact with Sentry from the command line. Use when the user asks about viewing issues, events, projects, organizations, making API calls, or authenticating with Sentry via CLI.
---

# Sentry CLI Usage Guide

Help users interact with Sentry from the command line using the `sentry` CLI.

## Prerequisites

The CLI must be installed and authenticated before use.

### Installation

```bash
curl https://cli.sentry.dev/install -fsS | bash

# Or install via npm/pnpm/bun
npm install -g sentry
```

### Authentication

```bash
sentry auth login
sentry auth login --token YOUR_SENTRY_API_TOKEN
sentry auth status
sentry auth logout
```

## Available Commands

### Auth

Authenticate with Sentry

#### `sentry auth login`

Authenticate with Sentry

**Flags:**
- `--token <value> - Authenticate using an API token instead of OAuth`
- `--timeout <value> - Timeout for OAuth flow in seconds (default: 900) - (default: "900")`

**Examples:**

```bash
# OAuth device flow (recommended)
sentry auth login

# Using an API token
sentry auth login --token YOUR_TOKEN
```

#### `sentry auth logout`

Log out of Sentry

**Examples:**

```bash
sentry auth logout
```

#### `sentry auth refresh`

Refresh your authentication token

**Flags:**
- `--json - Output result as JSON`
- `--force - Force refresh even if token is still valid`

**Examples:**

```bash
sentry auth refresh
```

#### `sentry auth status`

View authentication status

**Flags:**
- `--showToken - Show the stored token (masked by default)`

**Examples:**

```bash
sentry auth status
```

#### `sentry auth token`

Print the stored authentication token

### Org

Work with Sentry organizations

#### `sentry org list`

List organizations

**Flags:**
- `--limit <value> - Maximum number of organizations to list - (default: "30")`
- `--json - Output JSON`

**Examples:**

```bash
sentry org list

sentry org list --json
```

#### `sentry org view <org>`

View details of an organization

**Flags:**
- `--json - Output as JSON`
- `-w, --web - Open in browser`

**Examples:**

```bash
sentry org view <org-slug>

sentry org view my-org

sentry org view my-org -w
```

### Project

Work with Sentry projects

#### `sentry project list <org>`

List projects

**Flags:**
- `-n, --limit <value> - Maximum number of projects to list - (default: "30")`
- `--json - Output JSON`
- `-p, --platform <value> - Filter by platform (e.g., javascript, python)`

**Examples:**

```bash
# List all projects
sentry project list

# List projects in a specific organization
sentry project list <org-slug>

# Filter by platform
sentry project list --platform javascript
```

#### `sentry project view <project>`

View details of a project

**Flags:**
- `--org <value> - Organization slug`
- `--json - Output as JSON`
- `-w, --web - Open in browser`

**Examples:**

```bash
sentry project view <project-slug>

sentry project view frontend --org my-org

sentry project view frontend -w
```

### Issue

Manage Sentry issues

#### `sentry issue list <target>`

List issues in a project

**Flags:**
- `-q, --query <value> - Search query (Sentry search syntax)`
- `-n, --limit <value> - Maximum number of issues to return - (default: "10")`
- `-s, --sort <value> - Sort by: date, new, freq, user - (default: "date")`
- `--json - Output as JSON`

**Examples:**

```bash
# Explicit org and project
sentry issue list <org>/<project>

# All projects in an organization
sentry issue list <org>/

# Search for project across all accessible orgs
sentry issue list <project>

# Auto-detect from DSN or config
sentry issue list

# List issues in a specific project
sentry issue list my-org/frontend

sentry issue list my-org/

sentry issue list frontend

sentry issue list my-org/frontend --query "TypeError"

sentry issue list my-org/frontend --sort freq --limit 20

# Show only unresolved issues
sentry issue list my-org/frontend --query "is:unresolved"

# Show resolved issues
sentry issue list my-org/frontend --query "is:resolved"

# Combine with other search terms
sentry issue list my-org/frontend --query "is:unresolved TypeError"
```

#### `sentry issue explain <issue>`

Analyze an issue's root cause using Seer AI

**Flags:**
- `--json - Output as JSON`
- `--force - Force new analysis even if one exists`

**Examples:**

```bash
sentry issue explain <issue-id>

# By numeric issue ID
sentry issue explain 123456789

# By short ID with org prefix
sentry issue explain my-org/MYPROJECT-ABC

# By project-suffix format
sentry issue explain myproject-G

# Force a fresh analysis
sentry issue explain 123456789 --force
```

#### `sentry issue plan <issue>`

Generate a solution plan using Seer AI

**Flags:**
- `--cause <value> - Root cause ID to plan (required if multiple causes exist)`
- `--json - Output as JSON`
- `--force - Force new plan even if one exists`

**Examples:**

```bash
sentry issue plan <issue-id>

# After running explain, create a plan
sentry issue plan 123456789

# Specify which root cause to plan for (if multiple were found)
sentry issue plan 123456789 --cause 0

# By short ID with org prefix
sentry issue plan my-org/MYPROJECT-ABC --cause 1

# By project-suffix format
sentry issue plan myproject-G --cause 0
```

#### `sentry issue view <issue>`

View details of a specific issue

**Flags:**
- `--json - Output as JSON`
- `-w, --web - Open in browser`
- `--spans <value> - Span tree depth limit (number, "all" for unlimited, "no" to disable) - (default: "3")`

**Examples:**

```bash
# By issue ID
sentry issue view <issue-id>

# By short ID
sentry issue view <short-id>

sentry issue view FRONT-ABC

sentry issue view FRONT-ABC -w
```

### Event

View Sentry events

#### `sentry event view <args...>`

View details of a specific event

**Flags:**
- `--json - Output as JSON`
- `-w, --web - Open in browser`
- `--spans <value> - Span tree depth limit (number, "all" for unlimited, "no" to disable) - (default: "3")`

**Examples:**

```bash
sentry event view <event-id>

sentry event view abc123def456

sentry event view abc123def456 -w
```

### Api

Make an authenticated API request

#### `sentry api <endpoint>`

Make an authenticated API request

**Flags:**
- `-X, --method <value> - The HTTP method for the request - (default: "GET")`
- `-F, --field <value>... - Add a typed parameter (key=value, key[sub]=value, key[]=value)`
- `-f, --raw-field <value>... - Add a string parameter without JSON parsing`
- `-H, --header <value>... - Add a HTTP request header in key:value format`
- `--input <value> - The file to use as body for the HTTP request (use "-" to read from standard input)`
- `-i, --include - Include HTTP response status line and headers in the output`
- `--silent - Do not print the response body`
- `--verbose - Include full HTTP request and response in the output`

**Examples:**

```bash
sentry api <endpoint> [options]

# List organizations
sentry api /organizations/

# Get a specific organization
sentry api /organizations/my-org/

# Get project details
sentry api /projects/my-org/my-project/

# Create a new project
sentry api /teams/my-org/my-team/projects/ \
  --method POST \
  --field name="New Project" \
  --field platform=javascript

# Update an issue status
sentry api /issues/123456789/ \
  --method PUT \
  --field status=resolved

# Assign an issue
sentry api /issues/123456789/ \
  --method PUT \
  --field assignedTo="user@example.com"

# Delete a project
sentry api /projects/my-org/my-project/ \
  --method DELETE

sentry api /organizations/ \
  --header "X-Custom-Header:value"

sentry api /organizations/ --include

# Get all issues (automatically follows pagination)
sentry api /projects/my-org/my-project/issues/ --paginate
```

### Cli

CLI-related commands

#### `sentry cli feedback <message...>`

Send feedback about the CLI

#### `sentry cli fix`

Diagnose and repair CLI database issues

**Flags:**
- `--dry-run - Show what would be fixed without making changes`

#### `sentry cli upgrade <version>`

Update the Sentry CLI to the latest version

**Flags:**
- `--check - Check for updates without installing`
- `--method <value> - Installation method to use (curl, npm, pnpm, bun, yarn)`

### Log

View Sentry logs

#### `sentry log list <target>`

List logs from a project

**Flags:**
- `-n, --limit <value> - Number of log entries (1-1000) - (default: "100")`
- `-q, --query <value> - Filter query (Sentry search syntax)`
- `-f, --follow <value> - Stream logs (optionally specify poll interval in seconds)`
- `--json - Output as JSON`

## Output Formats

### JSON Output

Most list and view commands support `--json` flag for JSON output, making it easy to integrate with other tools:

```bash
sentry org list --json | jq '.[] | .slug'
```

### Opening in Browser

View commands support `-w` or `--web` flag to open the resource in your browser:

```bash
sentry issue view PROJ-123 -w
```
