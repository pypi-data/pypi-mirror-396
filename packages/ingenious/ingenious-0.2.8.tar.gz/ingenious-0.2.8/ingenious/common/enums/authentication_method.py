"""Authentication method enumeration for Azure services.

This enum is used across Ingenious to choose how SDK clients
authenticate to Azure services (Azure OpenAI, Azure AI Search,
Cosmos DB, Blob Storage, etc.).

Supported values (case-insensitive):

- DEFAULT_CREDENTIAL ("default_credential"):
    Uses `azure.identity.DefaultAzureCredential`. This aggregates multiple
    credential sources (environment variables, Managed Identity, VS Code/Az CLI
    sign-in, etc.) and is the safest default when no explicit method is set.

- TOKEN ("token"):
    Uses a raw key/token string for services that support it.

Examples:
            - Azure OpenAI API key (env: INGENIOUS_MODELS__N__API_KEY)
            - Azure AI Search admin/query key
                (env: INGENIOUS_AZURE_SEARCH_SERVICES__N__KEY)
            - Cosmos DB primary key
                (env: INGENIOUS_COSMOS_SERVICE__API_KEY)
            - Blob: SAS token or full connection string
                (env: INGENIOUS_FILE_STORAGE__...__TOKEN)

- MSI ("msi"):
    Uses `ManagedIdentityCredential`. If `client_id` is provided, a
    user-assigned identity is used; otherwise the system-assigned
    identity is used.

- CLIENT_ID_AND_SECRET ("client_id_and_secret"):
    Uses `ClientSecretCredential` (service principal). Requires `client_id`,
    `client_secret`, and `tenant_id`.

Defaults:
- If no authentication_method is specified for a service, Ingenious
    will default to DEFAULT_CREDENTIAL (which includes MSI if
    available) unless the service has a strong convention to use keys
    (e.g., Azure Search in some contexts).
"""

from enum import Enum
from typing import Any, Optional


class AuthenticationMethod(str, Enum):
    """Authentication methods for Azure services.

    Attributes:
        MSI (str): Managed Identity authentication.
        CLIENT_ID_AND_SECRET (str): Service principal with client secret.
        DEFAULT_CREDENTIAL (str): DefaultAzureCredential chain.
        TOKEN (str): Direct key/token authentication.
    """

    MSI = "msi"
    CLIENT_ID_AND_SECRET = "client_id_and_secret"
    DEFAULT_CREDENTIAL = "default_credential"
    TOKEN = "token"

    @classmethod
    def _missing_(cls, value: Any) -> Optional["AuthenticationMethod"]:
        """Handle case-insensitive enum lookups.

        Args:
            value (Any): Value to lookup.

        Returns:
            Optional[AuthenticationMethod]: Matched enum member or None.
        """
        if isinstance(value, str):
            # Try to find a match with case-insensitive comparison
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        # If no match found, return None (will raise ValueError)
        return None
