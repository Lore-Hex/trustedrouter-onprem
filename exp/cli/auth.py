"""TrustedRouter authentication for the TrustedRouterOnPrem CLI."""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from getpass import getpass
from pathlib import Path

import typer
from rich.console import Console

from exp.cli.providers.sync import sync_account_models
from exp.cli.providers.trustedrouter import (
    HOSTED_GATEWAY_API_KEY_ENV,
    hosted_connection,
    hosted_credential_binding,
)
from exp.cli.shared.options import ROOT_OPTION
from exp.cli.shared.theme import EXP_THEME
from exp.common.auth import ProviderAuthStore
from exp.common.config import ARTIFACT_DIR
from exp.common.models import ProviderConnectionAuthoringError
from exp.runtime.models.providers import ProviderListingError, ProviderModelLister


def run_login(
    *,
    console: Console,
    environment: Mapping[str, str] | None = None,
    store: ProviderAuthStore | None = None,
    read_key: Callable[[str], str | None] = getpass,
    root: Path | None = None,
    lister: ProviderModelLister | None = None,
) -> None:
    """Authenticate the CLI with a TrustedRouter API key.

    Args:
        console: Terminal receiving progress and recovery messages.
        environment: Optional process environment containing ``TRUSTEDROUTER_API_KEY``.
        store: Optional credential store, primarily for deterministic tests.
        read_key: Masked reader used when no environment credential is set.
        root: Local ``.exp`` root receiving the synchronized provider catalog.
        lister: Optional account model-listing seam used by deterministic tests.

    Raises:
        typer.Abort: The operator cancels or provides an empty fallback key.
        ValueError: The credential store cannot safely persist the key.
    """
    connection = hosted_connection()
    source = os.environ if environment is None else environment
    key = source.get(HOSTED_GATEWAY_API_KEY_ENV, "").strip() or None
    if key is None:
        console.print("[dim]TrustedRouter API key[/dim]")
        try:
            key = read_key("TrustedRouter API key (hidden, empty line cancels): ")
        except (EOFError, KeyboardInterrupt):
            raise typer.Abort from None
    if key is None or not key.strip():
        raise typer.Abort

    try:
        sync_account_models(
            Path(ARTIFACT_DIR) if root is None else root,
            connection=connection,
            api_key=key,
            console=console,
            lister=lister,
        )
    except (ProviderConnectionAuthoringError, ProviderListingError) as exc:
        raise typer.BadParameter(
            f"TrustedRouter authentication succeeded, but model synchronization failed: {exc}"
        ) from None
    auth_store = store if store is not None else ProviderAuthStore()
    auth_store.put(
        connection.name,
        key,
        binding=hosted_credential_binding(),
    )
    console.print("[green]Logged in to TrustedRouter.[/green]")


def login(root: Path = ROOT_OPTION) -> None:
    """Save a TrustedRouter credential and synchronize account models."""
    run_login(console=Console(theme=EXP_THEME), environment=os.environ, root=root)
