"""TrustedRouter connection metadata for the on-premises gateway."""

from __future__ import annotations

from exp.common.auth import StoredCredentialBinding
from exp.common.models import ProviderConnection

SETUP_PICKER_NAME = "trustedrouter"
SETUP_PICKER_LABEL = "TrustedRouter"
CATALOG_PROVIDER = "trustedrouter"
HOSTED_GATEWAY_DEFAULT_BASE_URL = "https://api.trustedrouter.com/v1"
HOSTED_GATEWAY_API_KEY_ENV = "TRUSTEDROUTER_API_KEY"


def hosted_connection() -> ProviderConnection:
    """Return the canonical secret-free TrustedRouter connection."""
    return ProviderConnection(
        name=SETUP_PICKER_NAME,
        provider=CATALOG_PROVIDER,
        api_key_env=HOSTED_GATEWAY_API_KEY_ENV,
    )


def hosted_credential_binding() -> StoredCredentialBinding:
    """Bind a stored key to the canonical TrustedRouter endpoint identity."""
    connection = hosted_connection()
    return StoredCredentialBinding(
        provider=connection.provider,
        endpoint_sha256=connection.catalog_config().identity_sha256(),
    )
