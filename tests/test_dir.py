import pathlib
import shutil
import subprocess

import pandas as pd
import pytest

import codelytics as cdl

PROJECT_DIR = pathlib.Path(__file__).parent / "data" / "project01"


@pytest.fixture
def dir():
    return cdl.Dir(path=PROJECT_DIR)


@pytest.fixture
def invalid_dir(tmp_path):
    """Create a Dir fixture with invalid Python by converting .txt to .py files."""
    # Copy entire project directory to tmp_path
    temp_project_dir = tmp_path / "project01"
    shutil.copytree(PROJECT_DIR, temp_project_dir)

    # Convert all .txt files to .py files in the temp directory
    for txt_file in temp_project_dir.rglob("*.txt"):
        txt_file.rename(txt_file.with_suffix(".py"))

    return cdl.Dir(temp_project_dir)


@pytest.fixture
def repo(tmp_path):
    test_file1 = tmp_path / "test.txt"
    test_file1.write_text("test content")

    test_file2 = tmp_path / "test2.txt"
    test_file2.write_text("test content 2")

    commands = [
        ["git", "init"],
        ["git", "checkout", "-b", "main"],
        ["git", "config", "user.email", "test_fake_user@example.com"],
        ["git", "config", "user.name", "Test User"],
        ["git", "add", "test.txt"],
        ["git", "commit", "-m", "Initial commit"],
        ["git", "checkout", "-b", "feature"],
        ["git", "add", "test2.txt"],
        ["git", "commit", "-m", "Feature commit"],
        ["git", "checkout", "main"],
    ]
    for cmd in commands:
        subprocess.run(cmd, cwd=tmp_path, check=True, capture_output=True)

    return cdl.Dir(tmp_path)


class TestInit:
    def test_valid_directory(self, dir):
        assert dir.path.exists() and dir.path.is_dir()

    def test_with_pathlib_object(self, tmp_path):
        dir = cdl.Dir(tmp_path)
        assert dir.path == tmp_path

    def test_nonexistent_directory(self):
        with pytest.raises(FileNotFoundError):
            cdl.Dir("/nonexistent/directory/somewhere")

    def test_file_not_directory(self, tmp_path):
        temp_file = tmp_path / "test_file.txt"
        temp_file.write_text("content")
        with pytest.raises(NotADirectoryError):
            cdl.Dir(temp_file)


class TestGitRepository:
    def test_is_repo_true(self, repo):
        assert repo.is_repo

    def test_is_repo_false(self, dir):
        assert not dir.is_repo

    def test_n_commits_in_repo(self, repo):
        assert repo.n_commits() == 1
        assert repo.n_commits("HEAD") == 1
        assert repo.n_commits("main") == 1
        assert repo.n_commits("--all") == 2
        assert repo.n_commits("feature") == 2

    def test_n_commits_non_repo(self, dir):
        with pytest.raises(RuntimeError):
            dir.n_commits()


class TestFileIteration:
    def test_iter_empty_directory(self, tmp_path):
        dir = cdl.Dir(tmp_path)

        assert len(dir) == len(list(dir)) == len(list(dir.iter_files(suffix=None))) == 0

    def test_iter_with_files(self, dir):
        files = list(dir)

        assert len(files) > 0
        assert all(isinstance(f, pathlib.Path) for f in files)
        assert all(f.is_file() for f in files)

    def test_iter_files_py(self, dir):
        py_files = list(dir.iter_files("py"))

        assert all(f.suffix == ".py" for f in py_files)
        assert len(py_files) > 0

    def test_iter_files_md(self, dir):
        md_files = list(dir.iter_files(suffix=".md"))

        assert all(f.suffix == ".md" for f in md_files)
        assert len(md_files) > 0

    def test_iter_files_ipynb(self, dir):
        ipynb_files = list(dir.iter_files("ipynb"))

        assert all(f.suffix == ".ipynb" for f in ipynb_files)
        assert len(ipynb_files) > 0

    def test_iter_files_no_matches(self, dir):
        weird_files = list(dir.iter_files(suffix="weirdsuffix"))

        assert len(weird_files) == 0


class TestFileCounting:
    def test_files_all(self, dir):
        total_files = dir.n_files()

        assert total_files > 0  # avoid precise number because of tmp files
        # Should match iterator count
        assert total_files == len(list(dir))

    def test_files_with_suffix(self, dir):
        assert dir.n_files("py") >= 7
        assert dir.n_files(".py") >= 7
        assert dir.n_files("md") == 1

    def test_files_empty_directory(self, tmp_path):
        dir = cdl.Dir(tmp_path)
        assert dir.n_files() == 0
        assert dir.n_files("py") == 0

    def test_files_nonexistent_suffix(self, dir):
        assert dir.n_files("xyz") == 0

    def test_invalid_dir(self, dir, invalid_dir):
        # Should not raise an error, but return empty content for invalid files
        assert invalid_dir.n_files("txt") == 0
        assert dir.n_files("txt") == 1
        assert invalid_dir.n_files("py") == dir.n_files("py") + 1


class TestExtract:
    def test_code(self, dir):
        code = dir.extract("code")
        assert isinstance(code, cdl.Py)
        assert len(code.content) > 0

        assert "print(1 + 2 + 3)" in code.content
        assert "# Walrus operator" in code.content
        assert "print(sh)" in code.content

    def test_markdown(self, dir):
        md = dir.extract("markdown")
        assert isinstance(md, cdl.TextAnalysis)
        assert len(md.texts) > 0

        assert "This is a readme file." in md.texts[0]
        assert "Let's analyse the data:" in md.texts[0]

    def test_invalid_content_type(self, dir):
        with pytest.raises(ValueError):
            dir.extract("invalid_type")


class TestExtractionInvalid:
    def test_invalid_py(self, invalid_dir):
        code = invalid_dir.extract("code")
        assert isinstance(code, cdl.Py)
        assert "a + b" not in code.content
        assert "# colon missing" not in code.content
        assert "Hello from a valid syntax function!" in code.content

        assert "def function_with_loop_and_conditions(numbers):" in code.content
        assert "x =+ 5" not in code.content
        assert "# Incorrect indentation" not in code.content

    def test_invalid_md(self, dir, invalid_dir):
        md_invalid = invalid_dir.extract("markdown")
        md_valid = dir.extract("markdown")
        assert md_invalid.texts == md_valid.texts


class TestStats:
    def test_stats(self, dir):
        stats = dir.stats()
        assert isinstance(stats, pd.Series)

        assert stats.loc["docstrings_non_ascii_total"] == 1

    def test_stats_keys(self, dir):
        stats = dir.stats()
        stats_nan = cdl.stats_nan(dir.path.name)

        assert stats_nan.index.equals(stats.index)
