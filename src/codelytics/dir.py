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

    def extract(self, content_type):
        """
        Extract and merge content from all files in the directory.

        Extracts content from Python files, Jupyter notebooks, and Markdown files
        based on the specified content type.

        Parameters
        ----------
        content_type : str
            Type of content to extract. Options are:
            - 'code': Extract Python code from .py files and code cells from .ipynb files
            - 'markdown': Extract content from .md files and markdown cells from .ipynb files

        Returns
        -------
        str
            All content of the specified type merged together as a single string.
            Each file's content is separated by double newlines.
            Returns empty string if no files found or content type not recognized.
        """
        if content_type not in ["code", "markdown"]:
            return ""

        content_parts = []

        for file_path in self:
            try:
                if content_type == "code":
                    # Extract Python code
                    if file_path.suffix == ".py":
                        content = file_path.read_text(encoding="utf-8")
                        if content.strip():
                            content_parts.append(content)

                    elif file_path.suffix == ".ipynb":
                        try:
                            from .notebook import Notebook  # Assuming relative import

                            nb = Notebook(file_path)
                            code_content = nb.extract("code")
                            if code_content.strip():
                                content_parts.append(code_content)
                        except Exception:
                            # Skip notebooks that can't be parsed
                            continue

                elif content_type == "markdown":
                    # Extract Markdown content
                    if file_path.suffix == ".md":
                        content = file_path.read_text(encoding="utf-8")
                        if content.strip():
                            content_parts.append(content)

                    elif file_path.suffix == ".ipynb":
                        try:
                            from .notebook import Notebook  # Assuming relative import

                            nb = Notebook(file_path)
                            markdown_content = nb.extract("markdown")
                            if markdown_content.strip():
                                content_parts.append(markdown_content)
                        except Exception:
                            # Skip notebooks that can't be parsed
                            continue

            except (UnicodeDecodeError, PermissionError):
                # Skip files that can't be read
                continue

        return "\n\n".join(content_parts)
