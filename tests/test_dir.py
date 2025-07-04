import pathlib
import subprocess

import pytest

from codelytics import Dir


@pytest.fixture
def dir():
    path = pathlib.Path(__file__).parent / "data" / "project01"
    return Dir(path=path)


@pytest.fixture
def repo(tmp_path):
    # Initialise git repo
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Create and commit a file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    subprocess.run(
        ["git", "add", "test.txt"], cwd=tmp_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    return Dir(tmp_path)


class TestDirInitialisation:
    def test_valid_directory(self, dir):
        assert dir.path == pathlib.Path(__file__).parent / "data" / "project01"

    def test_with_pathlib_object(self, tmp_path):
        dir = Dir(tmp_path)
        assert dir.path == tmp_path

    def test_nonexistent_directory(self):
        with pytest.raises(FileNotFoundError):
            Dir("/nonexistent/directory/somewhere")

    def test_file_not_directory(self, tmp_path):
        temp_file = tmp_path / "test_file.txt"
        temp_file.write_text("content")
        with pytest.raises(NotADirectoryError):
            Dir(temp_file)


class TestGitRepository:
    def test_is_repo_true(self, repo, dir):
        assert repo.is_repo()

    def test_is_repo_false(self, dir):
        assert not dir.is_repo()

    def test_commits_in_repo(self, repo):
        assert repo.n_commits() == 1
        assert repo.n_commits("HEAD") == 1
        assert repo.n_commits("--all") == 1

    def test_commits_all_branches(self, repo):
        # Create a new branch and commit
        subprocess.run(
            ["git", "checkout", "-b", "feature"],
            cwd=repo.path,
            check=True,
            capture_output=True,
        )
        test_file2 = repo.path / "test2.txt"
        test_file2.write_text("test content 2")
        subprocess.run(
            ["git", "add", "test2.txt"], cwd=repo.path, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Feature commit"],
            cwd=repo.path,
            check=True,
            capture_output=True,
        )

        # Current branch (feature) has 2 commits
        assert repo.n_commits("HEAD") == 2
        # All branches should have 2 commits total
        assert repo.n_commits("--all") == 2

    def test_commits_non_repo(self, tmp_path):
        dir = Dir(tmp_path)
        with pytest.raises(RuntimeError):
            dir.n_commits()
        with pytest.raises(RuntimeError):
            dir.n_commits("--all")


class TestFileIteration:
    def test_iter_empty_directory(self, tmp_path):
        dir = Dir(tmp_path)
        assert len(list(dir)) == 0

    def test_iter_with_files(self, dir):
        files = list(dir)

        assert len(files) > 0
        # Check that we get Path objects
        assert all(isinstance(f, pathlib.Path) for f in files)
        # Check that all returned items are files
        assert all(f.is_file() for f in files)

    def test_iter_files_with_suffix_py(self, dir):
        py_files = list(dir.iter_files("py"))

        # All files should have .py extension
        assert all(f.suffix == ".py" for f in py_files)
        assert len(py_files) == 4

    def test_iter_files_with_suffix_md(self, dir):
        md_files = list(dir.iter_files(suffix=".md"))

        # All files should have .md extension
        assert all(f.suffix == ".md" for f in md_files)
        assert len(md_files) == 1

    def test_iter_files_no_matches(self, dir):
        weird_files = list(dir.iter_files(suffix="weird"))

        assert len(weird_files) == 0

    def test_iter_files_empty_directory(self, tmp_path):
        dir = Dir(tmp_path)
        files = list(dir.iter_files("py"))
        assert len(files) == 0
        # Test with None suffix as well
        files_none = list(dir.iter_files(suffix=None))
        assert len(files_none) == 0


class TestFileCounting:
    def test_files_all(self, dir):
        total_files = dir.n_files()

        assert total_files > 0  # avoid precise number because of tmp files
        # Should match iterator count
        assert total_files == len(list(dir))

    def test_files_with_suffix(self, dir):
        assert dir.n_files("py") == 4
        assert dir.n_files(".py") == 4
        assert dir.n_files("md") == 1

    def test_files_empty_directory(self, tmp_path):
        dir = Dir(tmp_path)
        assert dir.n_files() == 0
        assert dir.n_files("py") == 0

    def test_files_nonexistent_suffix(self, dir):
        assert dir.n_files("xyz") == 0
