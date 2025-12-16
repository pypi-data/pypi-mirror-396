from __future__ import annotations

from dataclasses import dataclass

from supertape.core.file.api import TapeFile


@dataclass(frozen=True)
class RepositoryInfo:
    """Repository information record."""

    file_count: int
    path: str
    type: str
    storage_size: int


@dataclass(frozen=True)
class TapeVersion:
    """Represents a specific version of a tape file from repository history.

    This class encapsulates metadata about the version that introduced or modified a file.
    To retrieve file content at a specific version, use get_tape_file(filename, version_id).

    Attributes:
        version_id: Unique version identifier (format depends on repository implementation)
        commit_message: The commit message (e.g., "Add tape file: HELLO")
        timestamp: Unix timestamp when the version was created (seconds since epoch)
        is_deleted: True if this version represents a file deletion
    """

    version_id: str
    commit_message: str
    timestamp: int
    is_deleted: bool


class TapeFileRepositoryObserver:
    """Observer interface for tape file repository events."""

    def file_added(self, file: TapeFile) -> None:
        """Called when a file is added to the repository."""
        pass

    def file_removed(self, file: TapeFile) -> None:
        """Called when a file is removed from the repository."""
        pass


class TapeFileRepository:
    """Abstract base class for tape file repositories."""

    def add_tape_file(self, file: TapeFile) -> None:
        """Add a tape file to the repository."""
        raise NotImplementedError

    def remove_tape_file(self, file: TapeFile | str) -> None:
        """Remove a tape file from the repository.

        Args:
            file: Either a TapeFile object to remove, or a string filename.
                  If a TapeFile is provided, both name and content must match.
                  If a string is provided, the first file matching that name (case-insensitive) is removed.
        """
        raise NotImplementedError

    def get_tape_files(self, version_id: str | None = None) -> list[TapeFile]:
        """Get all tape files from the repository.

        Args:
            version_id: Optional version identifier. If provided, returns files
                       as they existed at that version. If None, returns current files.
                       Format depends on repository implementation.

        Returns:
            List of TapeFile objects

        Raises:
            RepositoryError: If version_id is invalid or version doesn't exist
        """
        raise NotImplementedError

    def get_tape_file(self, filename: str, version_id: str | None = None) -> TapeFile:
        """Get a specific tape file from the repository.

        Args:
            filename: The tape filename to retrieve (case-insensitive)
            version_id: Optional version identifier. If provided, returns the file
                       as it existed at that version. If None, returns current file.
                       Format depends on repository implementation.

        Returns:
            TapeFile object matching the filename

        Raises:
            FileNotFoundError: If file with the specified filename doesn't exist
            RepositoryError: If version_id is invalid or version doesn't exist
        """
        raise NotImplementedError

    def add_observer(self, observer: TapeFileRepositoryObserver) -> None:
        """Add an observer to watch repository events."""
        raise NotImplementedError

    def remove_observer(self, observer: TapeFileRepositoryObserver) -> None:
        """Remove an observer from watching repository events."""
        raise NotImplementedError

    def get_repository_info(self) -> RepositoryInfo:
        """Get information about the repository.

        Returns:
            RepositoryInfo dictionary containing:
            - file_count: Number of files in the repository
            - path: Repository storage path
            - type: Repository type (e.g., "yaml")
            - storage_size: Total size of stored files in bytes
        """
        raise NotImplementedError

    def get_tape_file_versions(self, filename: str) -> list[TapeVersion]:
        """Get all historical versions of a tape file.

        Walks through the git history to find all commits that affected the
        specified tape file, ordered from newest to oldest.

        Args:
            filename: The original tape filename (not sanitized, as stored in
                      TapeFile.fname). The method will handle sanitization internally.

        Returns:
            List of TapeVersion objects, ordered from newest to oldest.
            Empty list if the file was never committed to the repository.

        Raises:
            RepositoryError: If git operations fail or history cannot be accessed.
        """
        raise NotImplementedError
