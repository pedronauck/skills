---
name: hetzner-server
description: Create and manage Hetzner Cloud servers. Use when creating VPS/cloud servers, managing Hetzner infrastructure, or setting up dev/remote servers. Requires hcloud CLI.
---

# Hetzner Server Management

Create and manage Hetzner Cloud servers using the `hcloud` CLI.

## Prerequisites

- `hcloud` CLI installed (via mise: `hcloud = "latest"`)
- Authenticated: `hcloud context create <name>` with API token from https://console.hetzner.cloud

## Cloud Firewalls

Reusable firewall profiles applied at server creation. Firewalls can be swapped on running servers — use `apply-to-resource` / `remove-from-resource`.

| Firewall  | Rules                                       | Use case                                                       |
| --------- | ------------------------------------------- | -------------------------------------------------------------- |
| `ts-ssh`  | UDP 41641 (Tailscale) + TCP 22 (SSH)        | Dev boxes — initial setup, swap to `ts-only` after `tsonlyssh` |
| `ts-only` | UDP 41641 (Tailscale)                       | Tailscale-only access, no public ports                         |
| `ts-web`  | UDP 41641 (Tailscale) + TCP 80,443 (HTTP/S) | Servers accepting public web traffic                           |

### Swapping firewalls on a running server

```bash
hcloud firewall remove-from-resource ts-ssh --type server --server dev
hcloud firewall apply-to-resource ts-only --type server --server dev
```

## Quick Reference

### Create a server

```bash
# Prefer ARM (best value)
hcloud server create \
  --name dev \
  --type cax21 \
  --image ubuntu-24.04 \
  --location nbg1 \
  --ssh-key connorads \
  --ssh-key connor@penguin \
  --firewall ts-ssh

# x86 fallback
hcloud server create \
  --name dev \
  --type cpx21 \
  --image ubuntu-24.04 \
  --location nbg1 \
  --ssh-key connorads \
  --ssh-key connor@penguin \
  --firewall ts-ssh

# IPv6-only (saves ~$0.60/month on IPv4)
hcloud server create \
  --name dev \
  --type cax21 \
  --image ubuntu-24.04 \
  --location nbg1 \
  --ssh-key connorads \
  --ssh-key connor@penguin \
  --firewall ts-ssh \
  --without-ipv4
```

### With user-data (auto-run install script)

```bash
# Use heredoc - process substitution <(echo '...') escapes the shebang incorrectly
hcloud server create \
  --name dev \
  --type cax21 \
  --image ubuntu-24.04 \
  --location nbg1 \
  --ssh-key connorads \
  --ssh-key connor@penguin \
  --firewall ts-ssh \
  --user-data-from-file - <<'EOF'
#!/bin/bash
curl -fsSL https://raw.githubusercontent.com/connorads/dotfiles/master/install.sh | bash
EOF
```

The dotfiles installation takes ~5 minutes. To monitor progress:

```bash
# Quick status check
ssh connor@$(hcloud server ip dev) "cloud-init status"

# View recent installation logs
ssh connor@$(hcloud server ip dev) "sudo journalctl -u cloud-final -n 50 --no-pager"

# Follow installation in real-time
ssh connor@$(hcloud server ip dev) "sudo journalctl -u cloud-final -f"

# Check if tools are installed
ssh connor@$(hcloud server ip dev) "which zsh mise && echo \$SHELL"
```

### With swap (recommended for production)

Ubuntu cloud images don't include swap by default. Add swap via cloud-init at creation:

```bash
# Create server with 16GB swap (1:1 ratio for 16GB RAM server)
hcloud server create \
  --name dev \
  --type cax33 \
  --image ubuntu-24.04 \
  --location nbg1 \
  --ssh-key connorads \
  --ssh-key connor@penguin \
  --firewall ts-ssh \
  --user-data-from-file - <<'EOF'
#cloud-config
swap:
  filename: /swapfile
  size: 16G
  maxsize: 16G
EOF
```

**Recommended swap sizes:**

- 4GB RAM → 4-8GB swap
- 8GB RAM → 8GB swap
- 16GB+ RAM → 16GB swap (1:1 ratio)

**Add swap to existing server:**

```bash
# Create 16GB swap file
ssh connor@$(hcloud server ip dev) "sudo fallocate -l 16G /swapfile && \
  sudo chmod 600 /swapfile && \
  sudo mkswap /swapfile && \
  sudo swapon /swapfile && \
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab"

# Verify swap is active
ssh connor@$(hcloud server ip dev) "free -h"
```

### Common commands

```bash
# List servers
hcloud server list

# Get server IP
hcloud server ip dev

# SSH to server
ssh connor@$(hcloud server ip dev)

# Delete server
hcloud server delete dev

# Power operations
hcloud server poweroff dev
hcloud server poweron dev
hcloud server reboot dev

# Rebuild (reinstall OS, keeps IP)
hcloud server rebuild dev --image ubuntu-24.04
```

### Server types (commonly used)

Prices in USD for EU regions (US regions ~20% higher):

| Type  | Arch | vCPU | RAM  | Disk  | ~USD/mo |
| ----- | ---- | ---- | ---- | ----- | ------- |
| cax11 | ARM  | 2    | 4GB  | 40GB  | $4.50   |
| cax21 | ARM  | 4    | 8GB  | 80GB  | $8      |
| cax31 | ARM  | 8    | 16GB | 160GB | $16     |
| cpx21 | x86  | 3    | 4GB  | 80GB  | $9      |
| cpx31 | x86  | 4    | 8GB  | 160GB | $18     |

Full list: `hcloud server-type list`

### Locations

| ID   | City        | Country |
| ---- | ----------- | ------- |
| fsn1 | Falkenstein | DE      |
| nbg1 | Nuremberg   | DE      |
| hel1 | Helsinki    | FI      |
| ash  | Ashburn     | US      |
| hil  | Hillsboro   | US      |
| sin  | Singapore   | SG      |

### SSH keys

```bash
# List keys
hcloud ssh-key list

# Add a key
hcloud ssh-key create --name mykey --public-key-from-file ~/.ssh/id_ed25519.pub
```

### Images

```bash
# List system images
hcloud image list --type system

# ARM images
hcloud image list --type system --architecture arm
```

## Cloning GitHub repos (SSH agent forwarding)

Use the `<name>-agent` SSH host (which has agent forwarding enabled) to clone private repos without copying keys to the server. If you hit host key errors, add GitHub's host key first.

```bash
# First time only: add GitHub's host key
ssh dev "ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null"

# Confirm forwarded agent is visible
ssh dev-agent "ssh-add -l"

# Clone with agent forwarding (use -agent suffix)
ssh dev-agent "mkdir -p ~/git && cd ~/git && git clone git@github.com:you/repo.git"

# Clone specific branch
ssh dev-agent "mkdir -p ~/git && cd ~/git && git clone git@github.com:you/repo.git && cd repo && git checkout branch-name"

# Push/pull with agent forwarding
ssh dev-agent "cd repo && git push"
```

For interactive sessions (e.g., lazygit):

```bash
ssh dev-agent
# Then on server: git clone/push/pull works with forwarded agent
```

## Post-creation setup

After creating a server, **always** clear any old host keys for that IP (Hetzner reuses IPs):

```bash
ssh-keygen -R $(hcloud server ip dev) 2>/dev/null
ssh-keyscan $(hcloud server ip dev) >> ~/.ssh/known_hosts 2>/dev/null
```

Then generate/update SSH config entries:

```bash
hcssh              # update ~/.ssh/config with all Hetzner servers
hcssh --dry-run    # preview without writing
```

This creates two Host entries per server inside a managed block (`# BEGIN/END hetzner-managed`):

- `<name>` — no agent forwarding (safe for AI agents)
- `<name>-agent` — with agent forwarding (for git push/pull to GitHub)

Run `hcssh` again after creating/deleting servers to keep SSH config in sync.
This enables VS Code Remote-SSH to show the server in the dropdown.

## Optional: Restrict SSH to Tailscale only

After `ts up` and confirming SSH works via Tailscale (`ts ssh connor@dev`), run `tsonlyssh` on the server to remove public port 22 from UFW. This leaves SSH accessible only via the Tailscale interface.

Fallback: Hetzner Cloud Console VNC if locked out.

## Notes

- ARM (cax\*) servers are best value for dev work
- IPv6-only saves money but requires Tailscale/cloudflared for access from IPv4 networks
- User-data runs as root on first boot
- The dotfiles install.sh handles creating user `connor`, installing Nix, home-manager, and mise tools
