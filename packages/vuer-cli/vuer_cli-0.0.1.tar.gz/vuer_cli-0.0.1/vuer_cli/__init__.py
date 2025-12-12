"""Vuer CLI - Environment Manager for Vuer Hub."""

import os
from dataclasses import dataclass
from typing import Optional

from params_proto import proto


# -- Configuration with environment variable defaults --

@proto.prefix
class Hub:
    """Vuer Hub connection settings."""
    url: str = os.environ.get("VUER_HUB", "https://hub.vuer.ai/api")  # Base URL of the Vuer Hub API
    auth_token: str = os.environ.get("VUER_AUTH_TOKEN", "")  # JWT token for authentication


# -- Subcommand dataclasses for top-level commands --

@dataclass
class Sync:
    """Pull all included environments from vuer.json."""
    output: str = "downloads"  # Destination directory for downloaded environments
    timeout: int = 300  # Request timeout in seconds


@dataclass
class Add:
    """Add an environment to vuer.json."""
    env: str = ""  # Environment ID to add
    name: Optional[str] = None  # Optional name for the environment
    version: str = "latest"  # Version to track


@dataclass
class Remove:
    """Remove an environment from vuer.json."""
    env: str = ""  # Environment ID to remove


@dataclass
class Upgrade:
    """Upgrade environments in vuer.json."""
    env: Optional[str] = None  # Specific environment ID to upgrade (all if not specified)
    version: Optional[str] = None  # New version to set


# -- Subcommand dataclasses for `vuer envs` --

@dataclass
class EnvsCreate:
    """Create a workspace for a new environment."""
    name: str = ""  # Environment name (slug format, no spaces)
    timeout: int = 300  # Request timeout in seconds


@dataclass
class EnvsPublish:
    """Publish a new version of an environment."""
    env_id: str = ""  # Environment ID to publish to
    file: str = ""  # Path to the package file (zip/tar/etc.)
    version: str = ""  # Semver-compliant version string
    description: str = ""  # Optional description
    env_type: str = ""  # Environment type (isaac, mujoco, etc.)
    visibility: str = "PUBLIC"  # Visibility (PUBLIC, PRIVATE, ORG_MEMBERS)
    timeout: int = 300  # Request timeout in seconds


@dataclass
class EnvsPull:
    """Download an environment by ID."""
    id: str = ""  # Environment ID to download
    output: str = "downloads"  # Destination directory
    filename: Optional[str] = None  # Override for saved filename
    version: Optional[str] = None  # Specific version to download
    timeout: int = 300  # Request timeout in seconds


@dataclass
class EnvsPush:
    """Upload a packaged environment (creates env if needed, then publishes)."""
    file: str = ""  # Path to the package file (zip/tar/etc.)
    name: str = ""  # Environment name without spaces
    version: str = ""  # Semver-compliant version string
    description: str = ""  # Optional description
    env_type: str = ""  # Environment type (isaac, mujoco, etc.)
    visibility: str = "PUBLIC"  # Visibility (PUBLIC, PRIVATE, ORG_MEMBERS)
    push_timeout: int = 300  # Request timeout in seconds


@proto.cli(prog="vuer")
def entrypoint(
    command: Sync | Add | Remove | Upgrade | EnvsCreate | EnvsPublish | EnvsPull | EnvsPush,
):
    """Vuer Hub Environment Manager.

    Manage, version-control, and distribute physical simulation environments.

    Commands:
        sync          Pull all included environments from vuer.json
        add           Add an environment to vuer.json
        remove        Remove an environment from vuer.json
        upgrade       Upgrade environments in vuer.json
        envs-create   Create a workspace for an environment
        envs-publish  Publish an environment version
        envs-pull     Download an environment by ID
        envs-push     Upload a packaged environment

    Environment Variables:
        VUER_HUB         Base URL of the Vuer Hub API (default: https://hub.vuer.ai/api)
        VUER_AUTH_TOKEN  JWT token for authentication
    """
    # Dispatch based on command type
    pass
