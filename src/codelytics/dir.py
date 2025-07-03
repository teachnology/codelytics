import pathlib
import subprocess


class Dir:
    """
    Analyse directory structure and git repository information.

    This class provides methods to analyse directories, check if they are git
    repositories, count commits, iterate through files, and count files by type.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to the directory to analyse

    Raises
    ------
    FileNotFoundError
        If the specified directory does not exist
    NotADirectoryError
        If the specified path is not a directory
    """

    def __init__(self, path):
        """
        Initialise Dir object with a directory path.

        Parameters
        ----------
        path : str or pathlib.Path
            Path to the directory to analyse

        Raises
        ------
        FileNotFoundError
            If the specified directory does not exist
        NotADirectoryError
            If the specified path is not a directory
        """
        self.path = pathlib.Path(path)

        if not self.path.exists():
            raise FileNotFoundError(f"Directory does not exist: {self.path}")

        if not self.path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {self.path}")

    def is_repo(self):
        """
        Check if the directory is a git repository.

        Returns
        -------
        bool
            True if directory is a git repository, False otherwise
        """
        git_dir = self.path / ".git"
        return git_dir.exists() and git_dir.is_dir()

    def n_commits(self, ref="HEAD"):
        """
        Get the number of commits in the git repository.

        Parameters
        ----------
        ref : str, default 'HEAD'
            Git reference to count commits from. Can be 'HEAD' for current
            branch or '--all' for all branches.

        Returns
        -------
        int
            Number of commits in the repository

        Raises
        ------
        RuntimeError
            If the directory is not a git repository or git command fails
        """
        if not self.is_repo():
            raise RuntimeError("Directory is not a git repository")

        try:
            result = subprocess.run(
                ["git", "rev-list", "--count", ref],
                cwd=self.path,
                capture_output=True,
                text=True,
                check=True,
            )
            return int(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get commit count: {e}")
        except FileNotFoundError:
            raise RuntimeError("Git command not found")

    def __iter__(self):
        """
        Iterate recursively through all files in the directory.

        Yields
        ------
        pathlib.Path
            Path object for each file found recursively
        """
        for file_path in self.path.rglob("*"):
            if file_path.is_file():
                yield file_path

    def iter_files(self, suffix=None):
        """
        Iterate recursively through files with optional suffix filter.

        Parameters
        ----------
        suffix : str, optional
            File extension to filter by (without the dot). If None, behaves
            the same as __iter__ and yields all files.

        Yields
        ------
        pathlib.Path
            Path object for each file found recursively, optionally filtered by suffix
        """
        if suffix is None:
            # Same behaviour as __iter__
            yield from self
        else:
            # Ensure suffix starts with dot
            if not suffix.startswith("."):
                suffix = "." + suffix

            for file_path in self:
                if file_path.suffix == suffix:
                    yield file_path

    def n_files(self, suffix=None):
        """
        Count the number of files in the directory.

        Parameters
        ----------
        suffix : str, optional
            File extension to filter by (without the dot).
            If None, counts all files.

        Returns
        -------
        int
            Number of files matching the criteria
        """
        return sum(1 for _ in self.iter_files(suffix))
