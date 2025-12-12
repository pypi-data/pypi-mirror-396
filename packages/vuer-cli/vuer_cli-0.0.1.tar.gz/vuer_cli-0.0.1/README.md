# Vuer Hub Environment Manager

Vuer HUB and the vuer command line tool enable you to manage, version-control, and distribute physical simulation environments the same way you manage software packages.

## Overview

The CLI maintains a local environment list in `vuer.json`.

**Commands:**
- `sync` - pull all included environments
- `add` - add an environment to the vuer.json
- `remove` - remove an environment
- `upgrade` - upgrade environments

**Environment Commands:**
- `envs-create` – create a workspace for an environment
- `envs-publish` - publish an environment to the workspace
- `envs-pull` – download an environment by `environmentId`
- `envs-push` – upload a packaged environment

## Installation

```bash
pip install vuer-cli
```

## Environment Variables

| Variable          | Required | Description                                                              |
|-------------------|----------|--------------------------------------------------------------------------|
| `VUER_AUTH_TOKEN` | ✅        | JWT token used for all authenticated requests                            |
| `VUER_HUB`        | ❌        | Base URL of the Vuer Hub API backend (defaults to `https://hub.vuer.ai/api`) |

```bash
export VUER_AUTH_TOKEN="your-jwt-token"
export VUER_HUB="https://hub.vuer.ai/api"
```

## Usage Overview

```bash
# Sync all environments
vuer sync

# Add an environment
vuer add --command.env <environmentId>

# Pull an environment
vuer envs-pull --command.id <environmentId>

# Push an environment
vuer envs-push --command.file ./build/my-env.zip --command.name demo-env --command.version 1.2.3
```

## Push Command

Upload a packaged environment:

```bash
vuer envs-push \
  --command.file ./build/my-env.zip \
  --command.name demo-env \
  --command.version 1.2.3 \
  --command.description "Demo package" \
  --command.env-type isaac \
  --command.visibility PUBLIC \
  --command.push-timeout 600
```

### Push Flags

| Flag                            | Required | Description                                                |
|---------------------------------|----------|------------------------------------------------------------|
| `--command.file PATH`           | ✅        | Path to the package file (zip/tar/etc.)                    |
| `--command.name NAME`           | ✅        | Environment name without spaces                            |
| `--command.version SEMVER`      | ✅        | Semver-compliant version string (`1.2.3`, `2.0.0-beta`, …) |
| `--command.description TEXT`    | ❌        | Optional text                                              |
| `--command.env-type TYPE`       | ❌        | Example: `isaac`, `mujoco`                                 |
| `--command.visibility VIS`      | ❌        | `PUBLIC` (default), `PRIVATE`, or `ORG_MEMBERS`            |
| `--command.push-timeout SECONDS`| ❌        | Request timeout in seconds (default: 300)                  |

## Pull Command

Download an environment by ID:

```bash
vuer envs-pull \
  --command.id 252454509945688064 \
  --command.output ./downloads \
  --command.filename demo-env.zip \
  --command.timeout 600
```

If `--command.filename` is omitted, the tool will try to derive the original filename
from the server's `Content-Disposition` header. Files are stored under the `downloads/` directory by default.

### Pull Flags

| Flag                       | Required | Description                                 |
|----------------------------|----------|---------------------------------------------|
| `--command.id ENV_ID`      | ✅        | Target environment's `environmentId`        |
| `--command.output DIR`     | ❌        | Destination directory (default `downloads`) |
| `--command.filename NAME`  | ❌        | Override for the saved filename             |
| `--command.timeout SECONDS`| ❌        | Request timeout in seconds (default: 300)   |

## Hub Configuration

You can also configure Hub settings via CLI options:

```bash
vuer sync --hub.url https://custom-hub.example.com/api --hub.auth-token your-token
```

## Error Handling

All network and file-system errors are surfaced as readable messages (prefixed
with `[ERROR]`). Typical causes:

- Invalid JWT → ensure `VUER_AUTH_TOKEN` is set and not expired.
- Missing backend endpoint → ensure `VUER_HUB` is set.
- Duplicate name/version on `push` → server enforces `(name, versionId)` uniqueness.
- Missing file path on `push` or invalid target directory on `pull`.
- Timeout errors → increase `--command.push-timeout` or `--command.timeout` for large files.

## Development

1. Clone the main repository and navigate into the CLI folder.
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Run the CLI locally using `vuer ...`.

### Running with uv

Use `uv run` to execute the CLI without installing it globally:

```bash
# Create a new environment workspace
uv run vuer envs-create --command.name my-environment

# Pull an environment by ID
uv run vuer envs-pull --command.id 252454509945688064 --command.output ./downloads

# Push an environment package
uv run vuer envs-push \
  --command.file ./build/my-env.zip \
  --command.name demo-env \
  --command.version 1.2.3 \
  --command.description "Demo package" \
  --command.env-type isaac \
  --command.visibility PUBLIC

# Sync all environments in vuer.json
uv run vuer sync

# Add an environment to vuer.json
uv run vuer add --command.env <environmentId>
```
