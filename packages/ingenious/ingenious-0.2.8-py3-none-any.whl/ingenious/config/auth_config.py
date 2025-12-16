"""Authentication configuration utilities for Ingenious.

Provides authentication helpers for validating credentials, managing auth methods,
and integrating with various authentication providers (Azure, Basic Auth, JWT).
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Mapping, Optional, Union

from ingenious.common.enums import AuthenticationMethod

if TYPE_CHECKING:
    pass


def _get(obj: object, *names: str) -> str | None:
    """Get a value from an object or mapping by trying multiple attribute names.

    Args:
        obj: The object or mapping to search.
        *names: Attribute or key names to try in order.

    Returns:
        The first non-None value found as string, or None if all are None or not present.
    """
    if obj is None:
        return None
    if isinstance(obj, Mapping):
        for n in names:
            if n in obj and obj[n] is not None:
                val = obj[n]
                return str(val) if val is not None else None
        return None
    for n in names:
        val = getattr(obj, n, None)
        if val is not None:
            return str(val)
    return None


class AzureAuthConfig:
    """Centralized authentication configuration for Azure client builders.

    Attributes:
        authentication_method: The authentication method to use.
        api_key: API key for token-based authentication.
        client_id: Azure client ID for service principal or MSI.
        client_secret: Azure client secret for service principal authentication.
        tenant_id: Azure tenant ID for service principal authentication.
        endpoint: Azure service endpoint URL.
        openai_key: Alias for api_key (for Azure OpenAI compatibility).
        openai_endpoint: Alias for endpoint (for Azure OpenAI compatibility).
        api_version: Optional API version string.
    """

    # Declare instance attributes for mypy
    authentication_method: AuthenticationMethod
    api_key: Optional[str]
    client_id: Optional[str]
    client_secret: Optional[str]
    tenant_id: Optional[str]
    endpoint: Optional[str]
    openai_key: Optional[str]
    openai_endpoint: Optional[str]
    api_version: Optional[str]

    def __init__(
        self,
        authentication_method: AuthenticationMethod = AuthenticationMethod.DEFAULT_CREDENTIAL,
        api_key: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        """Initialize Azure authentication configuration.

        Args:
            authentication_method: The authentication method to use.
            api_key: API key for token-based authentication.
            client_id: Azure client ID for service principal or MSI.
            client_secret: Azure client secret for service principal.
            tenant_id: Azure tenant ID for service principal.
            endpoint: Azure service endpoint URL.
        """
        # Use object.__setattr__ to avoid Pydantic attribute guards when this
        # initializer is (intentionally) called with a Pydantic model instance.
        object.__setattr__(self, "authentication_method", authentication_method)
        object.__setattr__(self, "api_key", api_key)
        object.__setattr__(self, "client_id", client_id)
        object.__setattr__(self, "client_secret", client_secret)
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "endpoint", endpoint)

        # Optional AOAI specifics
        object.__setattr__(self, "openai_key", api_key if api_key else None)
        object.__setattr__(self, "openai_endpoint", endpoint if endpoint else None)

        # Optional API version if present in config
        object.__setattr__(self, "api_version", None)

    @classmethod
    def default_credential(cls) -> "AzureAuthConfig":
        """Create authentication config using default Azure credential.

        Returns:
            AzureAuthConfig instance configured for default credential authentication.
        """
        return cls(authentication_method=AuthenticationMethod.DEFAULT_CREDENTIAL)

    @classmethod
    def _infer_auth_method(
        cls,
        client_id: Optional[str],
        client_secret: Optional[str],
        tenant_id: Optional[str],
        api_key: Optional[str],
        explicit: Optional[AuthenticationMethod],
    ) -> AuthenticationMethod:
        """Infer authentication method from available credentials.

        Precedence: SPN > MSI (with client_id) > API key > Default
        """
        if client_id and client_secret and tenant_id:
            return AuthenticationMethod.CLIENT_ID_AND_SECRET
        if client_id and not client_secret and not tenant_id:
            return AuthenticationMethod.MSI
        if api_key:
            method = AuthenticationMethod.TOKEN
        else:
            method = AuthenticationMethod.DEFAULT_CREDENTIAL

        # Respect explicit method unless it would demote SPN
        if isinstance(explicit, AuthenticationMethod):
            return explicit
        return method

    @classmethod
    def _parse_explicit_method(cls, value: object) -> Optional[AuthenticationMethod]:
        """Parse explicit authentication method from config value."""
        if isinstance(value, str):
            try:
                return AuthenticationMethod[value]
            except Exception:
                return None
        return value if isinstance(value, AuthenticationMethod) else None

    @classmethod
    def from_config(cls, config: object) -> "AzureAuthConfig":
        """Create authentication config from a configuration object or mapping.

        Args:
            config: Configuration object or mapping containing authentication settings.

        Returns:
            AzureAuthConfig instance inferred from the configuration.
        """
        # Aliases for API key
        api_key = _get(config, "api_key", "key", "search_key", "openai_key", "token")
        if api_key is not None:
            api_key = str(api_key)

        # Endpoint aliases
        endpoint = _get(config, "endpoint", "base_url", "url", "openai_endpoint")

        # AAD/SPN/MSI credentials
        client_id = _get(config, "client_id")
        client_secret = _get(config, "client_secret")
        tenant_id = _get(config, "tenant_id")

        # Optional explicit method and API version
        explicit = cls._parse_explicit_method(_get(config, "authentication_method"))
        api_version = _get(config, "openai_version", "api_version")

        method = cls._infer_auth_method(client_id, client_secret, tenant_id, api_key, explicit)

        inst = cls(
            authentication_method=method,
            api_key=api_key,
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            endpoint=endpoint,
        )
        # Set optional fields via object.__setattr__ to be safe on all instances
        object.__setattr__(inst, "openai_key", api_key)
        object.__setattr__(inst, "openai_endpoint", endpoint)
        object.__setattr__(inst, "api_version", str(api_version) if api_version else None)
        return inst

    def validate_for_method(self) -> None:
        """Validate that required fields are present for the selected authentication method.

        Raises:
            ValueError: If required fields are missing for the authentication method.
        """
        if self.authentication_method == AuthenticationMethod.TOKEN:
            if not self.api_key:
                raise ValueError("API key is required for TOKEN authentication.")
        elif self.authentication_method == AuthenticationMethod.CLIENT_ID_AND_SECRET:
            if not (self.client_id and self.client_secret and self.tenant_id):
                raise ValueError(
                    "CLIENT_ID_AND_SECRET requires client_id, client_secret, and tenant_id."
                )
        # MSI/DEFAULT have no additional required fields.

    # -------------------------- Async helpers --------------------------

    def _is_spn_auth(self) -> bool:
        """Check if using service principal authentication with all required fields."""
        return (
            self.authentication_method == AuthenticationMethod.CLIENT_ID_AND_SECRET
            and bool(self.tenant_id)
            and bool(self.client_id)
            and bool(self.client_secret)
        )

    def _is_msi_auth(self) -> bool:
        """Check if using managed identity authentication."""
        return self.authentication_method == AuthenticationMethod.MSI and bool(self.client_id)

    def _try_sync_token_provider(self, scope: str) -> Optional[Callable[[], str]]:
        """Try to create a sync token provider using azure.identity."""
        try:
            from azure.identity import ClientSecretCredential as SyncClientSecretCredential
            from azure.identity import DefaultAzureCredential as SyncDefaultAzureCredential
            from azure.identity import (
                ManagedIdentityCredential as SyncManagedIdentityCredential,
            )
            from azure.identity import (
                get_bearer_token_provider as get_sync_bearer_token_provider,
            )

            cred: Union[
                SyncClientSecretCredential,
                SyncManagedIdentityCredential,
                SyncDefaultAzureCredential,
            ]
            if self._is_spn_auth():
                cred = SyncClientSecretCredential(
                    tenant_id=str(self.tenant_id),
                    client_id=str(self.client_id),
                    client_secret=str(self.client_secret),
                )
            elif self._is_msi_auth():
                cred = SyncManagedIdentityCredential(client_id=str(self.client_id))
            else:
                cred = SyncDefaultAzureCredential(exclude_interactive_browser_credential=True)
            provider: Callable[[], str] | None = get_sync_bearer_token_provider(cred, scope)
            return provider
        except Exception:
            return None  # nosec B110 - intentional fallback to async path

    def _create_aio_token_provider(self, scope: str) -> Callable[[], Coroutine[Any, Any, str]]:
        """Create an async token provider using azure.identity.aio."""
        from azure.identity.aio import ClientSecretCredential as AioClientSecretCredential
        from azure.identity.aio import DefaultAzureCredential as AioDefaultAzureCredential
        from azure.identity.aio import (
            ManagedIdentityCredential as AioManagedIdentityCredential,
        )
        from azure.identity.aio import (
            get_bearer_token_provider as get_aio_bearer_token_provider,
        )

        aio_cred: Union[
            AioClientSecretCredential,
            AioManagedIdentityCredential,
            AioDefaultAzureCredential,
        ]
        if self._is_spn_auth():
            aio_cred = AioClientSecretCredential(
                tenant_id=str(self.tenant_id),
                client_id=str(self.client_id),
                client_secret=str(self.client_secret),
            )
        elif self._is_msi_auth():
            aio_cred = AioManagedIdentityCredential(client_id=str(self.client_id))
        else:
            aio_cred = AioDefaultAzureCredential(exclude_interactive_browser_credential=True)
        result: Callable[[], Coroutine[Any, Any, str]] = get_aio_bearer_token_provider(
            aio_cred, scope
        )
        return result

    def to_openai_async_token_provider_or_none(
        self,
        scope: str,
    ) -> Optional[Callable[[], str]]:
        """Return a synchronous callable that yields a bearer token string.

        Args:
            scope: The OAuth2 scope for the token request.

        Returns:
            A synchronous callable that returns a bearer token string for passing as
            azure_ad_token_provider to openai.AsyncAzureOpenAI, or None if key-based
            authentication should be used instead.
        """
        # If explicit key path, don't build a provider.
        if self.authentication_method == AuthenticationMethod.TOKEN and self.api_key:
            return None

        # Try sync azure.identity first
        sync_provider = self._try_sync_token_provider(scope)
        if sync_provider is not None:
            return sync_provider

        # Fall back to aio path and wrap in a sync callable
        try:
            aio_provider = self._create_aio_token_provider(scope)
        except Exception as e:  # pragma: no cover
            raise ImportError(
                "Async Azure OpenAI with AAD requires 'azure-identity'. "
                "Install with: pip install azure-identity"
            ) from e

        def _sync_provider() -> str:
            coro = aio_provider()
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    new_loop = asyncio.new_event_loop()
                    try:
                        result: str = new_loop.run_until_complete(coro)
                        return result
                    finally:
                        new_loop.close()
                result = loop.run_until_complete(coro)
                return result
            except RuntimeError:
                result = asyncio.run(coro)
                return result

        return _sync_provider
