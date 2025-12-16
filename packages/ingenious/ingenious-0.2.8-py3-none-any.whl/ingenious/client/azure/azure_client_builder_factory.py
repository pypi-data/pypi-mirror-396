"""Azure Client Factory for building various Azure service clients.

This module provides a centralized factory for creating Azure service clients
with appropriate authentication methods based on configuration. It uses
builder classes from the builder subpackage to construct clients.
"""

from typing import Any, Optional

import pyodbc
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobClient, BlobServiceClient
from openai import AzureOpenAI

from ingenious.common.enums import AuthenticationMethod
from ingenious.config.models import (
    AzureSearchSettings,
    AzureSqlSettings,
    CosmosSettings,
    FileStorageContainerSettings,
    ModelSettings,
)

# Import builder classes directly for backward compatibility
from .builder.blob_client import BlobClientBuilder, BlobServiceClientBuilder
from .builder.cosmos_client import CosmosClientBuilder
from .builder.openai_chat_completions_client import AzureOpenAIChatCompletionClientBuilder
from .builder.openai_client import AzureOpenAIClientBuilder
from .builder.openai_client_async import AsyncAzureOpenAIClientBuilder
from .builder.search_client import AzureSearchClientBuilder
from .builder.sql_client import AzureSqlClientBuilder, AzureSqlClientBuilderWithAuth

# Optional SDK availability flags
try:
    from azure.cosmos import CosmosClient  # noqa: F401

    HAS_COSMOS = True
except ImportError:
    HAS_COSMOS = False

try:
    from azure.search.documents import SearchClient  # noqa: F401

    HAS_SEARCH = True
except ImportError:
    HAS_SEARCH = False


class AzureClientFactory:
    """Factory class for creating Azure service clients with proper authentication.

    This class provides a unified interface for creating various Azure service clients.
    """

    # OpenAI clients
    @staticmethod
    def create_openai_client(
        model_config: ModelSettings,
    ) -> AzureOpenAI:
        """Create an Azure OpenAI client from model configuration."""
        builder = AzureOpenAIClientBuilder(model_config)
        return builder.build()

    @staticmethod
    def create_openai_client_from_params(
        model: str,
        base_url: str,
        api_version: str,
        deployment: Optional[str] = None,
        api_key: Optional[str] = None,
        authentication_method: AuthenticationMethod = AuthenticationMethod.DEFAULT_CREDENTIAL,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> AzureOpenAI:
        """Create an Azure OpenAI client with direct parameters."""
        model_settings = ModelSettings(
            model=model,
            api_type="rest",
            base_url=base_url,
            api_version=api_version,
            deployment=deployment or model,
            api_key=api_key or "",
            authentication_method=authentication_method,
            client_id=client_id or "",
            client_secret=client_secret or "",
            tenant_id=tenant_id or "",
        )
        builder = AzureOpenAIClientBuilder(model_settings)
        return builder.build()

    @staticmethod
    def create_openai_chat_completion_client(
        model_config: ModelSettings,
    ) -> AzureOpenAIChatCompletionClient:
        """Create an Azure OpenAI Chat Completion client from model configuration."""
        builder = AzureOpenAIChatCompletionClientBuilder(model_config)
        return builder.build()

    @staticmethod
    def create_openai_chat_completion_client_from_params(
        model: str,
        base_url: str,
        api_version: str,
        deployment: Optional[str] = None,
        api_key: Optional[str] = None,
        authentication_method: AuthenticationMethod = AuthenticationMethod.DEFAULT_CREDENTIAL,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> AzureOpenAIChatCompletionClient:
        """Create an Azure OpenAI Chat Completion client with direct parameters."""
        model_settings = ModelSettings(
            model=model,
            api_type="rest",
            base_url=base_url,
            api_version=api_version,
            deployment=deployment or model,
            api_key=api_key or "",
            authentication_method=authentication_method,
            client_id=client_id or "",
            client_secret=client_secret or "",
            tenant_id=tenant_id or "",
        )
        builder = AzureOpenAIChatCompletionClientBuilder(model_settings)
        return builder.build()

    @staticmethod
    def create_async_openai_client(
        config: dict[str, Any],
        api_version: Optional[str] = None,
        **client_options: Any,
    ) -> Any:
        """Create an async Azure OpenAI client with direct parameters."""
        builder = AsyncAzureOpenAIClientBuilder.from_config(
            config=config,
            api_version=api_version,
            client_options=client_options,
        )
        return builder.build()

    # Blob storage clients
    @staticmethod
    def create_blob_service_client(
        file_storage_config: FileStorageContainerSettings,
    ) -> BlobServiceClient:
        """Create an Azure Blob Service client from file storage configuration."""
        builder = BlobServiceClientBuilder(file_storage_config)
        return builder.build()

    @staticmethod
    def create_blob_service_client_from_params(
        account_url: str,
        authentication_method: AuthenticationMethod = AuthenticationMethod.DEFAULT_CREDENTIAL,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
    ) -> BlobServiceClient:
        """Create an Azure Blob Service client with direct parameters."""
        file_storage_settings = FileStorageContainerSettings(
            enable=True,
            storage_type="azure",
            container_name="",
            path="./",
            add_sub_folders=True,
            url=account_url,
            client_id=client_id or "",
            token=token or "",
            authentication_method=authentication_method,
        )
        builder = BlobServiceClientBuilder(file_storage_settings)
        return builder.build()

    @staticmethod
    def create_blob_client(
        file_storage_config: FileStorageContainerSettings,
        container_name: str,
        blob_name: str,
    ) -> BlobClient:
        """Create an Azure Blob client from file storage configuration."""
        builder = BlobClientBuilder(file_storage_config, container_name, blob_name)
        return builder.build()

    @staticmethod
    def create_blob_client_from_params(
        account_url: str,
        blob_name: str,
        container_name: str,
        authentication_method: AuthenticationMethod = AuthenticationMethod.DEFAULT_CREDENTIAL,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
    ) -> BlobClient:
        """Create an Azure Blob client with direct parameters."""
        file_storage_settings = FileStorageContainerSettings(
            enable=True,
            storage_type="azure",
            container_name=container_name,
            path="./",
            add_sub_folders=True,
            url=account_url,
            client_id=client_id or "",
            token=token or "",
            authentication_method=authentication_method,
        )
        builder = BlobClientBuilder(file_storage_settings, container_name, blob_name)
        return builder.build()

    # Cosmos DB clients
    @staticmethod
    def create_cosmos_client(
        cosmos_config: CosmosSettings,
    ) -> Any:
        """Create an Azure Cosmos DB client."""
        if not HAS_COSMOS:
            raise ImportError(
                "azure-cosmos is required for Cosmos DB functionality. "
                "Install with: pip install azure-cosmos"
            )
        builder = CosmosClientBuilder(cosmos_config)
        return builder.build()

    # Search clients
    @staticmethod
    def create_search_client(search_config: AzureSearchSettings, index_name: str) -> Any:
        """Create an Azure Search client from search configuration."""
        if not HAS_SEARCH:
            raise ImportError(
                "azure-search-documents is required for Azure Search functionality. "
                "Install with: pip install azure-search-documents"
            )
        builder = AzureSearchClientBuilder(search_config, index_name)
        return builder.build()

    @staticmethod
    def create_async_search_client(
        index_name: str, config: dict[str, Any], **client_options: Any
    ) -> Any:
        """Create an async Azure Search client with direct parameters."""
        if not HAS_SEARCH:
            raise ImportError(
                "azure-search-documents is required for Azure Search functionality. "
                "Install with: pip install azure-search-documents"
            )
        from azure.search.documents.aio import SearchClient

        endpoint = config.get("endpoint")
        search_key = config.get("search_key")

        if not endpoint or not search_key:
            raise ValueError("Both 'endpoint' and 'search_key' must be provided in config")

        credential = AzureKeyCredential(search_key)
        return SearchClient(
            endpoint=endpoint, index_name=index_name, credential=credential, **client_options
        )

    @staticmethod
    def create_search_client_from_params(
        endpoint: str,
        index_name: str,
        api_key: str,
        service: Optional[str] = None,
        authentication_method: AuthenticationMethod = AuthenticationMethod.DEFAULT_CREDENTIAL,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> Any:
        """Create an Azure Search client with direct parameters."""
        if not HAS_SEARCH:
            raise ImportError(
                "azure-search-documents is required for Azure Search functionality. "
                "Install with: pip install azure-search-documents"
            )
        search_settings = AzureSearchSettings(
            service=service or "",
            endpoint=endpoint,
            key=api_key,
            client_id=client_id or "",
            client_secret=client_secret or "",
            tenant_id=tenant_id or "",
            authentication_method=authentication_method,
        )
        builder = AzureSearchClientBuilder(search_settings, index_name)
        return builder.build()

    # SQL clients
    @staticmethod
    def create_sql_client(
        sql_config: AzureSqlSettings,
    ) -> pyodbc.Connection:
        """Create an Azure SQL client from SQL configuration."""
        builder = AzureSqlClientBuilder(sql_config)
        return builder.build()

    @staticmethod
    def create_sql_client_from_params(
        database_name: str,
        connection_string: str,
        table_name: Optional[str] = None,
    ) -> pyodbc.Connection:
        """Create an Azure SQL client with direct parameters."""
        sql_settings = AzureSqlSettings(
            database_name=database_name,
            table_name=table_name or "",
            database_connection_string=connection_string,
        )
        builder = AzureSqlClientBuilder(sql_settings)
        return builder.build()

    @staticmethod
    def create_sql_client_with_auth(
        server: str,
        database: str,
        authentication_method: AuthenticationMethod = AuthenticationMethod.DEFAULT_CREDENTIAL,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> pyodbc.Connection:
        """Create an Azure SQL client with explicit authentication configuration."""
        builder = AzureSqlClientBuilderWithAuth(
            server=server,
            database=database,
            authentication_method=authentication_method,
            username=username,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
        )
        return builder.build()

    @staticmethod
    def create_sql_client_with_auth_from_params(
        server: str,
        database: str,
        authentication_method: AuthenticationMethod = AuthenticationMethod.DEFAULT_CREDENTIAL,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> pyodbc.Connection:
        """Create an Azure SQL client with explicit authentication configuration from direct parameters."""
        return AzureClientFactory.create_sql_client_with_auth(
            server=server,
            database=database,
            authentication_method=authentication_method,
            username=username,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
        )
