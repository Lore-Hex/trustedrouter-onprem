"""Tests for TrustedRouter key authentication and model synchronization."""

from __future__ import annotations

import io
from pathlib import Path

import pytest
import typer
from rich.console import Console

from exp.cli import auth
from exp.cli.providers.trustedrouter import hosted_credential_binding
from exp.common.auth import ProviderAuthStore
from exp.common.models import DiscoveredModel, load_model_catalog
from exp.runtime.models.providers import ProviderEndpoint


class _AccountModelLister:
    """Return model identities visible to one deterministic TrustedRouter account."""

    def __init__(self, api_key: str) -> None:
        """Store the exact credential expected by the listing call."""
        self.api_key = api_key

    def list_models(self, endpoint: ProviderEndpoint) -> tuple[DiscoveredModel, ...]:
        """Verify the native provider endpoint and return two models."""
        assert endpoint == ProviderEndpoint(
            provider="trustedrouter",
            api_key=self.api_key,
            base_url=None,
        )
        return (
            DiscoveredModel(provider="trustedrouter", model="trustedrouter/auto"),
            DiscoveredModel(provider="trustedrouter", model="anthropic/claude-sonnet-4.8"),
        )


def test_login_uses_environment_key_without_printing_it(tmp_path: Path) -> None:
    """An environment credential is stored, synced, and absent from console output."""
    key = "sk-tr-v1-environment-key"
    transcript = io.StringIO()
    console = Console(file=transcript, force_terminal=True, no_color=True)
    store = ProviderAuthStore(tmp_path / "auth.json")
    root = tmp_path / ".exp"

    auth.run_login(
        console=console,
        environment={"TRUSTEDROUTER_API_KEY": key},
        store=store,
        root=root,
        lister=_AccountModelLister(key),
    )

    assert store.get("trustedrouter", binding=hosted_credential_binding()) == key
    catalog = load_model_catalog(root / "models.toml")
    assert catalog.connections["trustedrouter"].provider == "trustedrouter"
    assert {record.model for record in catalog.models.values()} == {
        "trustedrouter/auto",
        "anthropic/claude-sonnet-4.8",
    }
    assert {record.billing_source.value for record in catalog.models.values()} == {"host_managed"}
    assert key not in transcript.getvalue()
    assert "Synced TrustedRouter: 2 models." in transcript.getvalue()
    assert "Logged in to TrustedRouter." in transcript.getvalue()


def test_login_prompts_when_environment_key_is_missing(tmp_path: Path) -> None:
    """Interactive login accepts one hidden key and never echoes it."""
    key = "sk-tr-v1-pasted-key"
    transcript = io.StringIO()
    console = Console(file=transcript, force_terminal=True, no_color=True)
    store = ProviderAuthStore(tmp_path / "auth.json")

    auth.run_login(
        console=console,
        environment={},
        store=store,
        read_key=lambda _prompt: key,
        root=tmp_path / ".exp",
        lister=_AccountModelLister(key),
    )

    assert store.get("trustedrouter", binding=hosted_credential_binding()) == key
    assert key not in transcript.getvalue()


def test_login_aborts_on_empty_key(tmp_path: Path) -> None:
    """An empty prompt response leaves both catalog and credential store untouched."""
    store = ProviderAuthStore(tmp_path / "auth.json")
    root = tmp_path / ".exp"

    with pytest.raises(typer.Abort):
        auth.run_login(
            console=Console(file=io.StringIO(), no_color=True),
            environment={},
            store=store,
            read_key=lambda _prompt: None,
            root=root,
            lister=_AccountModelLister("unused"),
        )

    assert store.connection_ids() == ()
    assert not (root / "models.toml").exists()
