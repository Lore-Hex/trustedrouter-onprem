"""TrustedRouter first-party provider tests."""

from exp.cli.providers.trustedrouter import (
    CATALOG_PROVIDER,
    HOSTED_GATEWAY_API_KEY_ENV,
    HOSTED_GATEWAY_DEFAULT_BASE_URL,
    SETUP_PICKER_LABEL,
    SETUP_PICKER_NAME,
    hosted_connection,
    hosted_credential_binding,
)


def test_trustedrouter_identity_is_canonical() -> None:
    """The product exposes one stable first-party hosted provider identity."""
    assert SETUP_PICKER_NAME == "trustedrouter"
    assert SETUP_PICKER_LABEL == "TrustedRouter"
    assert CATALOG_PROVIDER == "trustedrouter"
    assert HOSTED_GATEWAY_API_KEY_ENV == "TRUSTEDROUTER_API_KEY"
    assert HOSTED_GATEWAY_DEFAULT_BASE_URL == "https://api.trustedrouter.com/v1"


def test_trustedrouter_connection_cannot_carry_an_operator_origin() -> None:
    """The native provider leaves its attested production origin in the adapter."""
    connection = hosted_connection()

    assert connection.name == "trustedrouter"
    assert connection.provider == "trustedrouter"
    assert connection.api_key_env == "TRUSTEDROUTER_API_KEY"
    assert connection.base_url is None


def test_trustedrouter_credential_is_bound_to_provider_identity() -> None:
    """A stored key cannot be replayed into another provider connection."""
    connection = hosted_connection()
    binding = hosted_credential_binding()

    assert binding.provider == "trustedrouter"
    assert binding.endpoint_sha256 == connection.catalog_config().identity_sha256()
