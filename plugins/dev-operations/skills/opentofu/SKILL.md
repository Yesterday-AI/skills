---
name: opentofu
description: Manage infrastructure via OpenTofu (Terraform fork). Use when: provisioning servers, DNS, or cloud resources. Covers: init, plan, apply, destroy, import.
metadata:
  author: EmmettTheDoc
  version: "1.0"
  category: ops
compatibility: Requires `tofu` CLI.
---

# OpenTofu Skill 🥚

Infrastructure as Code using OpenTofu.

## When to Use

✅ **USE this skill when:**
- Creating/modifying cloud resources (Servers, DNS, S3)
- Managing stateful infrastructure
- Reviewing `.tf` files

❌ **DON'T use this skill when:**
- Configuring OS internals (use `ssh` or `ansible`)
- Running one-off scripts
- Managing Kubernetes resources inside a cluster (use `kubectl` / `helm`)

## Workflow

### 1. Init
Always run init first to download providers/modules.
```bash
tofu init
```

### 2. Plan (Dry Run)
Check what will happen. **Mandatory** before apply.
```bash
tofu plan -out=tfplan
```

### 3. Apply
Execute the changes.
```bash
tofu apply tfplan
```

### 4. Format
Keep code clean.
```bash
tofu fmt -recursive
```

## Best Practices

- **State:** Never commit `.tfstate` files. Use remote state (S3/Consul) or local state in `.gitignore`.
- **Secrets:** Never hardcode secrets. Use `variable "token" {}` and pass via `TF_VAR_token` environment variable.
- **Locking:** Ensure state locking works to prevent race conditions.

## Common Providers

### Hetzner Cloud (`hcloud`)
```hcl
provider "hcloud" {
  token = var.hcloud_token
}
resource "hcloud_server" "web" { ... }
```

### Hetzner DNS
Note: Use `hcloud_zone` and `hcloud_zone_rrset` resources within the `hcloud` provider for DNS management.

## Troubleshooting

- **Lock Error:** `tofu force-unlock <LOCK_ID>` (Use with extreme caution!)
- **State Drift:** `tofu refresh`
