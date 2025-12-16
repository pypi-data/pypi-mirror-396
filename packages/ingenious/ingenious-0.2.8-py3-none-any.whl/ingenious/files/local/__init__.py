"""Local filesystem file repository implementation."""

from pathlib import Path

import aiofiles  # type: ignore

from ingenious.config.models import FileStorageContainerSettings
from ingenious.config.settings import IngeniousSettings
from ingenious.files.files_repository import IFileStorage


class local_FileStorageRepository(IFileStorage):
    """Local filesystem implementation of the file storage interface.

    Provides file operations (read, write, delete, list) using the local filesystem
    with async I/O support via aiofiles.
    """

    def __init__(self, config: IngeniousSettings, fs_config: FileStorageContainerSettings):
        """Initialize local file storage repository.

        Args:
            config: The ingenious settings configuration.
            fs_config: File storage container configuration including base path.
        """
        self.config = config
        self.fs_config = fs_config
        self.base_path = Path(fs_config.path)

    async def write_file(self, contents: str, file_name: str, file_path: str) -> str:
        """Write data to a local file.

        :param contents: Data to write to the file.
        :param file_name: Name of the file to create.
        :param file_path: Path to the file.
        """
        try:
            path = Path(self.fs_config.path) / Path(file_path) / Path(file_name)
            path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(path, "w") as f:
                await f.write(contents)
            # print(f"Successfully wrote {path}.")
            return f"Successfully wrote {path}"
        except Exception as e:
            error_msg = f"Failed to write {path}: {e}"
            print(error_msg)
            return error_msg

    async def read_file(self, file_name: str, file_path: str) -> str:
        """Read data from a local file.

        :param file_name: Name of the file to read.
        :param file_path: Path to the file.
        :return: Contents of the file.
        """
        try:
            path = Path(self.fs_config.path) / Path(file_path) / Path(file_name)
            async with aiofiles.open(path, "r") as f:
                contents = await f.read()
                # print(f"Successfully read {path}.")
                return str(contents)
        except Exception as e:
            error_msg = f"Failed to read {path}: {e}"
            print(error_msg)
            return ""

    async def delete_file(self, file_name: str, file_path: str) -> str:
        """Delete a local file.

        :param file_name: Name of the file to delete.
        :param file_path: Path to the file.
        """
        try:
            path = Path(self.fs_config.path) / Path(file_path) / Path(file_name)
            Path(path).unlink()
            # print(f"Successfully deleted {path}.")
            return f"Successfully deleted {path}"
        except Exception as e:
            error_msg = f"Failed to delete {path}: {e}"
            print(error_msg)
            return error_msg

    async def list_files(self, file_path: str) -> str:
        """List files in a local directory.

        Returns filenames as newline-delimited string, matching Azure blob storage format.

        :param file_path: Path to the directory.
        :return: Newline-delimited string of filenames.
        """
        try:
            path = Path(self.fs_config.path) / Path(file_path)
            files = [f.name for f in path.iterdir() if f.is_file()]
            return "\n".join(files)
        except Exception as e:
            error_msg = f"Failed to list files in {path}: {e}"
            print(error_msg)
            return ""

    async def list_directories(self, file_path: str) -> list[str]:
        """List directories in a local directory.

        :param file_path: Path to the directory.
        :return: List of directory names.
        """
        try:
            path = Path(self.fs_config.path) / Path(file_path)
            if not path.exists():
                return []
            directories = [f.name for f in path.iterdir() if f.is_dir()]
            return directories
        except Exception as e:
            print(f"Failed to list directories in {path}: {e}")
            return []

    async def check_if_file_exists(self, file_path: str, file_name: str) -> bool:
        """Check if a local file exists.

        :param file_path: Path to the file.
        :param file_name: Name of the file.
        :return: True if the file exists, False otherwise.
        """
        path = Path(self.fs_config.path) / Path(file_path) / Path(file_name)
        try:
            exists = path.exists()
            # print(f"File {file_name} exists in {path}: {exists}")
            return exists
        except Exception as e:
            print(f"Failed to check if {file_name} exists in {path}: {e}")
            return False

    async def get_base_path(self) -> str:
        """Get the base path of the local file storage.

        :return: Base path of the local file storage.
        """
        return str(self.base_path)
