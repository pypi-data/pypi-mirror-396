"""Azure Blob Storage file repository implementation."""

from pathlib import Path

from azure.identity import (
    ClientSecretCredential,
    DefaultAzureCredential,
    ManagedIdentityCredential,
)
from azure.storage.blob import BlobServiceClient

from ingenious.common.enums import (
    AuthenticationMethod as file_storage_AuthenticationMethod,
)
from ingenious.config.models import FileStorageContainerSettings
from ingenious.config.settings import IngeniousSettings
from ingenious.core.structured_logging import get_logger
from ingenious.files.files_repository import IFileStorage

logger = get_logger(__name__)


class azure_FileStorageRepository(IFileStorage):
    """Azure Blob Storage implementation of the file storage interface.

    Provides file operations (read, write, delete, list) using Azure Blob Storage
    with support for multiple authentication methods including tokens, client secrets,
    managed identity, and default credentials.
    """

    def __init__(self, config: IngeniousSettings, fs_config: FileStorageContainerSettings):
        """Initialize Azure file storage repository with authentication.

        Args:
            config: The ingenious settings configuration.
            fs_config: File storage container configuration including authentication details.
        """
        self.config = config
        self.fs_config = fs_config
        self.url = fs_config.url
        self.token = fs_config.token
        self.client_id = fs_config.client_id
        self.container_name = fs_config.container_name
        self.authentication_method = fs_config.authentication_method

        # Check if token is actually a connection string
        if self.token and "DefaultEndpointsProtocol" in self.token:
            # Use connection string authentication
            self.blob_service_client = BlobServiceClient.from_connection_string(self.token)
        elif self.authentication_method == file_storage_AuthenticationMethod.TOKEN:
            self.blob_service_client = BlobServiceClient(
                account_url=self.url, credential=self.token
            )
        elif self.authentication_method == file_storage_AuthenticationMethod.CLIENT_ID_AND_SECRET:
            cred = ClientSecretCredential(
                tenant_id="",  # TODO: Add proper tenant_id from config
                client_id=self.client_id,
                client_secret=self.token,
            )
            self.blob_service_client = BlobServiceClient(account_url=self.url, credential=cred)
        elif self.authentication_method == file_storage_AuthenticationMethod.MSI:
            self.blob_service_client = BlobServiceClient(
                account_url=self.url,
                credential=ManagedIdentityCredential(client_id=self.client_id),
            )
            print("======")
            print(self.client_id, self.url)
        elif self.authentication_method == file_storage_AuthenticationMethod.DEFAULT_CREDENTIAL:
            self.blob_service_client = BlobServiceClient(
                account_url=self.url, credential=DefaultAzureCredential()
            )
        else:
            # If no authentication method matched, raise an error
            raise ValueError(
                f"Invalid authentication configuration. Token provided: {bool(self.token)}, "
                f"Authentication method: {self.authentication_method}"
            )

    async def write_file(self, contents: str, file_name: str, file_path: str) -> str:
        """Asynchronously writes the given contents to a file in Azure Blob Storage.

        Args:
            contents (str): The contents to write to the file.
            file_name (str): The name of the file to write.
            file_path (str): The path within the storage container where the file will be written.

        Raises:
            Exception: If there is an error during the upload process.

        Example:
            await write_file("Hello, World!", "example.txt", "path/to/directory")
        """
        try:
            path = Path(self.fs_config.path) / Path(file_path) / Path(file_name)
            # Create the container if it does not exist
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.container_name:
                container_client.create_container()

            # Create a blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=str(path)
            )

            # Upload the data
            blob_client.upload_blob(contents, overwrite=True)
            # print(f"Successfully uploaded {path} to container {self.container_name}.")
        except Exception as e:
            logger.error(f"Failed to upload {path} to container {self.container_name}: {e}")
            raise
        return str(path)

    async def read_file(self, file_name: str, file_path: str) -> str:
        """Download data from Azure Blob Storage.

        :param file_name: Name of the blob (file) to read.
        :param file_path: Path of the blob (file) to read.
        """
        try:
            path = Path(self.fs_config.path) / Path(file_path) / Path(file_name)
            print(path)
            # Create a blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=str(path)
            )

            # encoding param is necessary for readall() to return str, otherwise it returns bytes
            downloader = blob_client.download_blob(max_concurrency=1, encoding="UTF-8")
            data: str = downloader.readall()

            # print(f"Successfully downloaded {path} from container {self.container_name}.")
            return data
        except Exception as e:
            logger.error(f"Failed to download {path} from container {self.container_name}: {e}")
            raise

    async def delete_file(self, file_name: str, file_path: str) -> str:
        """Delete a blob from Azure Blob Storage.

        :param file_name: Name of the blob (file) to delete.
        :param file_path: Path of the blob (file) to delete.
        """
        try:
            path = Path(self.fs_config.path) / Path(file_path) / Path(file_name)
            # Create a blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=str(path)
            )

            # Delete the blob
            blob_client.delete_blob()
            # print(f"Successfully deleted {path} from container {self.container_name}.")
        except Exception as e:
            logger.error(f"Failed to delete {path} from container {self.container_name}: {e}")
            raise
        return str(path)

    async def list_files(self, file_path: str) -> str:
        """List blobs in an Azure Blob container based on a path.

        Returns only filenames (not full paths) for files directly in the specified path,
        matching the behavior of the local filesystem implementation.

        :param file_path: Path within the storage container to list blobs from.
        """
        try:
            path = Path(self.fs_config.path) / Path(file_path)
            prefix = str(path).replace(
                "\\", "/"
            )  # Ensure the path is in the correct format for Azure

            # Ensure prefix ends with / for proper directory listing
            if prefix and not prefix.endswith("/"):
                prefix += "/"

            # List blobs in the container with the specified prefix
            container_client = self.blob_service_client.get_container_client(self.container_name)

            # Extract filenames from blob paths (only direct children, not subdirectories)
            filenames = []
            for blob in container_client.list_blobs(name_starts_with=prefix):
                # Get the relative path after the prefix
                relative_path = blob.name[len(prefix) :]

                # Only include files directly in this directory (no slashes = not in subdirectory)
                if "/" not in relative_path and relative_path:
                    filenames.append(relative_path)

            # print(f"Files in container {self.container_name} with prefix {prefix}: {filenames}")
            return "\n".join(filenames)
        except Exception as e:
            logger.error(
                f"Failed to list blobs in container {self.container_name} with prefix {prefix}: {e}"
            )
            raise

    async def list_directories(self, file_path: str) -> list[str]:
        """List directories (blob prefixes) in an Azure Blob container.

        In blob storage, directories are virtual - they don't exist as actual objects.
        This method extracts unique directory names from blob paths.

        :param file_path: Path within the storage container to list directories from.
        :return: List of directory names.
        """
        prefix = ""
        try:
            path = Path(self.fs_config.path) / Path(file_path)
            prefix = str(path).replace("\\", "/")

            # Ensure prefix ends with / for proper directory listing
            if prefix and not prefix.endswith("/"):
                prefix += "/"

            # List blobs in the container with the specified prefix
            container_client = self.blob_service_client.get_container_client(self.container_name)

            # Extract unique directory names from blob paths
            directories: set[str] = set()
            for blob in container_client.list_blobs(name_starts_with=prefix):
                # Get the relative path after the prefix
                relative_path = blob.name[len(prefix) :]

                # If there's a slash, it means there's a subdirectory
                if "/" in relative_path:
                    # Get the first directory name
                    dir_name = relative_path.split("/")[0]
                    directories.add(dir_name)

            return sorted(list(directories))
        except Exception as e:
            logger.error(
                f"Failed to list directories in container {self.container_name} with prefix {prefix}: {e}"
            )
            return []

    async def check_if_file_exists(self, file_path: str, file_name: str) -> bool:
        """Check if a blob exists in an Azure Blob container.

        :param container_name: Name of the Azure Blob container.
        :param blob_name: Name of the blob (file) to check.
        :param connection_string: Connection string to Azure Storage account.
        :return: True if the blob exists, False otherwise.
        """
        try:
            path = Path(self.fs_config.path) / Path(file_path) / Path(file_name)
            # Create a blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=str(path)
            )
            exists: bool = blob_client.exists()
            # print(f"Blob {path} exists in container {self.container_name}: {exists}")
            return exists
        except Exception as e:
            logger.error(
                f"Failed to check if blob {path} exists in container {self.container_name}: {e}"
            )
            raise

    async def get_base_path(self) -> str:
        """Get the base path of the Azure Blob container.

        :return: Base path of the Azure Blob container.
        """
        return self.url + "/" + self.fs_config.path
