"""Dulwich-based tape file repository implementation."""

from __future__ import annotations

import io
import logging
from pathlib import Path

from dulwich.objects import Blob, Tree
from dulwich.repo import Repo

from supertape.core.file.api import TapeFile
from supertape.core.file.load import file_load
from supertape.core.file.save import file_save
from supertape.core.repository.api import (
    RepositoryInfo,
    TapeFileRepository,
    TapeFileRepositoryObserver,
    TapeVersion,
)

logger = logging.getLogger(__name__)


class RepositoryError(Exception):
    """Exception raised for repository errors."""

    pass


class DulwichRepository(TapeFileRepository):
    """Dulwich-based tape file repository implementation.

    Stores tape files as .k7 binary files in a git repository using pure Python.
    Each add/remove operation creates an automatic commit.
    Uses Dulwich for pure Python git integration (no external git binary required).
    """

    def __init__(self, repository_dir: str | None, observers: list[TapeFileRepositoryObserver]) -> None:
        """Initialize Dulwich repository.

        Args:
            repository_dir: Directory to store .k7 files, or None for default (~/.supertape/tapes)
            observers: List of observers to notify on repository changes

        Raises:
            RepositoryError: If dulwich is not installed or repository initialization fails
        """
        self.repository_dir: Path = (
            Path(repository_dir) if repository_dir else Path.home() / ".supertape" / "tapes"
        )
        self.observers: list[TapeFileRepositoryObserver] = observers

        # Create repository directory if it doesn't exist
        self.repository_dir.mkdir(parents=True, exist_ok=True)

        # Ensure git repository is initialized
        self._ensure_git_repo()

    def __str__(self) -> str:
        """String representation of the repository."""
        return f"DulwichRepository at {self.repository_dir}"

    def _ensure_git_repo(self) -> None:
        """Ensure git repository is initialized using Dulwich.

        Creates a new git repository if one doesn't exist.
        Raises RepositoryError if dulwich is not available.
        """
        git_dir = self.repository_dir / ".git"

        if not git_dir.exists():
            try:
                # Initialize new git repository using Dulwich
                Repo.init(str(self.repository_dir))
                logger.info(f"Initialized git repository at {self.repository_dir}")

                # Create .gitignore file
                gitignore = self.repository_dir / ".gitignore"
                if not gitignore.exists():
                    gitignore.write_text("__pycache__/\n*.pyc\n")

                    # Add and commit .gitignore
                    repo = Repo(str(self.repository_dir))
                    worktree = repo.get_worktree()
                    worktree.stage([b".gitignore"])
                    worktree.commit(
                        b"Initial commit: Add .gitignore",
                        committer=b"Supertape <supertape@local>",
                        author=b"Supertape <supertape@local>",
                    )

            except ImportError as e:
                raise RepositoryError(
                    "Dulwich is not installed.\n" "Please install it: pip install dulwich"
                ) from e
            except (OSError, PermissionError) as e:
                raise RepositoryError(f"Failed to initialize git repository: {e}") from e

    def _get_file_path(self, tape: TapeFile) -> Path:
        """Get the file path for a tape file.

        Args:
            tape: TapeFile to get path for

        Returns:
            Path where the tape file should be stored (.k7 extension)
        """
        # Sanitize filename: keep alphanumeric, spaces, hyphens, underscores
        # Normalize to uppercase for case-insensitive storage (CSAVEM format)
        safe_name: str = "".join(c for c in tape.fname.upper() if c.isalnum() or c in (" ", "-", "_")).strip()
        if not safe_name:
            safe_name = f"tape_{id(tape)}"

        return self.repository_dir / f"{safe_name}.k7"

    def add_tape_file(self, file: TapeFile) -> None:
        """Add a tape file to the repository.

        If a file with the same name already exists, it will be replaced.
        Each operation creates a new git commit.

        Args:
            file: TapeFile to add to the repository

        Raises:
            RepositoryError: If git operations fail
        """
        file_path: Path = self._get_file_path(file)

        # Check if file already exists
        is_update: bool = file_path.exists()

        try:
            # Write .k7 file (overwriting if it exists)
            file_save(str(file_path), file)

            # Add to git and commit using Dulwich
            repo = Repo(str(self.repository_dir))
            worktree = repo.get_worktree()

            # Stage the file (relative path as bytes)
            relative_path = file_path.relative_to(self.repository_dir)
            worktree.stage([str(relative_path).encode("utf-8")])

            # Commit with appropriate message
            action: str = "Update" if is_update else "Add"
            commit_msg = f"{action} tape file: {file.fname}".encode()
            author = b"Supertape <supertape@local>"
            worktree.commit(commit_msg, committer=author, author=author)

            logger.info(f"{action}d tape file: {file.fname} -> {file_path.name}")

            # Notify observers
            for observer in self.observers:
                observer.file_added(file)

        except (OSError, PermissionError, ValueError, KeyError) as e:
            # Rollback: remove file if commit failed and it was a new addition
            if not is_update and file_path.exists():
                file_path.unlink()
            raise RepositoryError(f"Failed to add tape file: {e}") from e

    def remove_tape_file(self, file: TapeFile | str) -> None:
        """Remove a tape file from the repository.

        Args:
            file: Either a TapeFile object to remove, or a string filename.
                  If a TapeFile is provided, both name and content must match.
                  If a string is provided, the first file matching that name (case-insensitive) is removed.

        Raises:
            RepositoryError: If git operations fail
        """
        # Determine if we're matching by name only or by full object
        match_by_name_only = isinstance(file, str)
        target_fname = file if isinstance(file, str) else file.fname

        # Find and remove the file
        for k7_file in self.repository_dir.glob("*.k7"):
            try:
                existing_tape: TapeFile = file_load(str(k7_file))

                # Case-insensitive comparison for filename
                if existing_tape.fname.upper() == target_fname.upper():
                    # If matching by name only, we found our file
                    # If matching by full object, also check content equality
                    if match_by_name_only or existing_tape == file:
                        try:
                            # Remove file from filesystem
                            k7_file.unlink()

                            # Stage deletion and commit using Dulwich
                            repo = Repo(str(self.repository_dir))
                            worktree = repo.get_worktree()
                            relative_path = k7_file.relative_to(self.repository_dir)
                            worktree.stage([str(relative_path).encode("utf-8")])

                            commit_msg = f"Remove tape file: {target_fname}".encode()
                            author = b"Supertape <supertape@local>"
                            worktree.commit(commit_msg, committer=author, author=author)

                            logger.info(f"Removed tape file: {target_fname} ({k7_file.name})")

                            # Notify observers with the actual file that was removed
                            for observer in self.observers:
                                observer.file_removed(existing_tape)

                            return

                        except (OSError, PermissionError, ValueError, KeyError) as e:
                            raise RepositoryError(f"Failed to remove tape file: {e}") from e

            except (ValueError, OSError) as e:
                # Skip corrupted files
                logger.warning(f"Skipping corrupted file {k7_file}: {e}")
                continue

    def _validate_commit_hash(self, commit_hash: str) -> None:
        """Validate commit hash format and existence.

        Args:
            commit_hash: 40-character SHA-1 hex string

        Raises:
            RepositoryError: If format is invalid or commit doesn't exist
        """
        # Check length
        if len(commit_hash) != 40:
            raise RepositoryError(
                f"Invalid commit hash format: expected 40 characters, got {len(commit_hash)}"
            )

        # Check all characters are hex digits
        if not all(c in "0123456789abcdefABCDEF" for c in commit_hash):
            raise RepositoryError("Invalid commit hash format: contains non-hex characters")

        # Check commit exists in repository
        # Git hashes are case-insensitive, normalize to lowercase
        try:
            repo = Repo(str(self.repository_dir))
            _ = repo[commit_hash.lower().encode()]  # Will raise KeyError if commit doesn't exist
        except KeyError as e:
            raise RepositoryError(f"Commit hash not found in repository: {commit_hash}") from e
        except (OSError, ValueError) as e:
            raise RepositoryError(f"Failed to validate commit hash: {e}") from e

    def _walk_tree_at_commit(self, version_id: str | None) -> dict[bytes, bytes]:
        """Get all .k7 file entries from git tree at specified commit.

        Args:
            version_id: Git commit hash, or None for HEAD

        Returns:
            Dict mapping filename (bytes) to blob_id (bytes)

        Raises:
            RepositoryError: If tree walking fails
        """
        try:
            repo = Repo(str(self.repository_dir))

            # Get commit hash
            # Git hashes are case-insensitive, normalize to lowercase
            if version_id is None:
                commit_hash_bytes = repo.head()
            else:
                commit_hash_bytes = version_id.lower().encode()

            # Access commit and tree
            commit = repo[commit_hash_bytes]
            tree: Tree = repo[commit.tree]  # type: ignore[attr-defined, assignment]

            # Collect .k7 files
            tree_entries: dict[bytes, bytes] = {}
            for name, _mode, sha in tree.iteritems():
                if name.endswith(b".k7"):
                    tree_entries[name] = sha

            return tree_entries

        except (OSError, KeyError, ValueError, AttributeError) as e:
            version_desc = version_id if version_id else "HEAD"
            raise RepositoryError(f"Failed to walk tree at {version_desc}: {e}") from e

    def _load_files_from_tree_entries(self, repo: Repo, tree_entries: dict[bytes, bytes]) -> list[TapeFile]:
        """Load TapeFile objects from tree entries.

        Args:
            repo: Dulwich repository instance
            tree_entries: Dict mapping filename (bytes) to blob_id (bytes)

        Returns:
            List of successfully loaded TapeFile objects

        Raises:
            Does not raise on individual file errors - corrupted files are skipped with warnings
        """
        tapes: list[TapeFile] = []

        for filename_bytes, blob_id in tree_entries.items():
            try:
                # Get blob from repository
                blob: Blob = repo[blob_id]  # type: ignore[assignment]

                # Create BytesIO from blob data
                blob_stream = io.BytesIO(blob.data)

                # Load TapeFile
                tape_file = file_load(blob_stream)
                tapes.append(tape_file)

            except (ValueError, OSError) as e:
                # Skip corrupted files with warning
                filename_str = filename_bytes.decode("utf-8", errors="replace")
                logger.warning(f"Skipping corrupted file {filename_str}: {e}")
                continue

        return tapes

    def get_tape_files(self, version_id: str | None = None) -> list[TapeFile]:
        """Get all tape files from the repository.

        Args:
            version_id: Optional git commit hash. If provided, returns files
                       as they existed at that commit. If None, returns current files at HEAD.

        Returns:
            List of TapeFile objects

        Raises:
            RepositoryError: If version_id is invalid or git operations fail
        """
        try:
            # Validate version_id if provided
            if version_id is not None:
                self._validate_commit_hash(version_id)

            # Get repository instance
            repo = Repo(str(self.repository_dir))

            # Get tree entries at specified commit (or HEAD if None)
            tree_entries = self._walk_tree_at_commit(version_id)

            # Load and return TapeFile objects
            return self._load_files_from_tree_entries(repo, tree_entries)

        except RepositoryError:
            # Re-raise repository errors as-is
            raise
        except (OSError, KeyError, ValueError) as e:
            version_desc = version_id if version_id else "HEAD"
            raise RepositoryError(f"Failed to retrieve tape files at {version_desc}: {e}") from e

    def get_tape_file(self, filename: str, version_id: str | None = None) -> TapeFile:
        """Get a specific tape file from the repository.

        Args:
            filename: The tape filename to retrieve (case-insensitive)
            version_id: Optional git commit hash. If provided, returns the file
                       as it existed at that commit. If None, returns current file at HEAD.

        Returns:
            TapeFile object matching the filename

        Raises:
            FileNotFoundError: If file with the specified filename doesn't exist
            RepositoryError: If version_id is invalid or git operations fail
        """
        try:
            # Validate version_id if provided
            if version_id is not None:
                self._validate_commit_hash(version_id)

            # Get all files at the specified version (or HEAD)
            all_files = self.get_tape_files(version_id=version_id)

            # Find file by name (case-insensitive)
            for tape_file in all_files:
                if tape_file.fname.upper() == filename.upper():
                    return tape_file

            # File not found
            version_desc = f" at version {version_id}" if version_id else ""
            raise FileNotFoundError(f"Tape file '{filename}' not found in repository{version_desc}")

        except FileNotFoundError:
            raise
        except RepositoryError:
            raise
        except (OSError, KeyError, ValueError) as e:
            version_desc = version_id if version_id else "HEAD"
            raise RepositoryError(f"Failed to retrieve tape file '{filename}' at {version_desc}: {e}") from e

    def add_observer(self, observer: TapeFileRepositoryObserver) -> None:
        """Add an observer to watch repository events.

        Args:
            observer: Observer to add
        """
        self.observers.append(observer)

    def remove_observer(self, observer: TapeFileRepositoryObserver) -> None:
        """Remove an observer from watching repository events.

        Args:
            observer: Observer to remove
        """
        self.observers.remove(observer)

    def get_repository_info(self) -> RepositoryInfo:
        """Get information about the repository.

        Returns:
            RepositoryInfo object containing:
            - file_count: Number of .k7 files in the repository
            - path: Repository storage path (absolute)
            - type: Repository type ("git")
            - storage_size: Total size of stored .k7 files in bytes
        """
        k7_files = list(self.repository_dir.glob("*.k7"))
        file_count = len(k7_files)

        # Calculate total storage size
        storage_size = sum(k7_file.stat().st_size for k7_file in k7_files)

        return RepositoryInfo(
            file_count=file_count,
            path=str(self.repository_dir.absolute()),
            type="git",  # Still "git" since we're using git format
            storage_size=storage_size,
        )

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
        try:
            # Sanitize filename: keep alphanumeric, spaces, hyphens, underscores
            # Normalize to uppercase for case-insensitive lookup (CSAVEM format)
            safe_name: str = "".join(
                c for c in filename.upper() if c.isalnum() or c in (" ", "-", "_")
            ).strip()
            if not safe_name:
                safe_name = filename  # Fallback to original if all chars were removed

            # Construct file path
            relative_path = Path(f"{safe_name}.k7")
            path_bytes = str(relative_path).encode("utf-8")

            # Access git repository
            repo = Repo(str(self.repository_dir))

            # Walk history filtering by this file path
            walker = repo.get_walker(paths=[path_bytes])

            versions: list[TapeVersion] = []

            for entry in walker:
                commit = entry.commit

                # Extract metadata
                version_id = commit.id.decode("ascii")  # Dulwich stores hash as ASCII bytes
                commit_message = commit.message.decode("utf-8").strip()
                timestamp = commit.commit_time

                try:
                    # Check if file exists in this commit's tree
                    tree: Tree = repo[commit.tree]  # type: ignore[assignment]
                    mode, blob_id = tree.lookup_path(repo.__getitem__, path_bytes)

                    # File exists - create version entry
                    version = TapeVersion(
                        version_id=version_id,
                        commit_message=commit_message,
                        timestamp=timestamp,
                        is_deleted=False,
                    )
                    versions.append(version)

                except KeyError:
                    # File doesn't exist in this commit's tree
                    # This happens on removal commits
                    if "Remove tape file:" in commit_message:
                        version = TapeVersion(
                            version_id=version_id,
                            commit_message=commit_message,
                            timestamp=timestamp,
                            is_deleted=True,
                        )
                        versions.append(version)
                    # Otherwise, skip (file not yet added in this commit)

            return versions

        except (OSError, KeyError, ValueError, AttributeError, UnicodeDecodeError) as e:
            raise RepositoryError(f"Failed to get version history for '{filename}': {e}") from e
