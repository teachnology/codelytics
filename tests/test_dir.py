import pathlib
import subprocess

import pytest

import codelytics


@pytest.fixture
def dir():
    return codelytics.Dir(path=pathlib.Path(__file__).parent / "data" / "project01")


@pytest.fixture
def repo(tmp_path):
    test_file1 = tmp_path / "test.txt"
    test_file1.write_text("test content")

    test_file2 = tmp_path / "test2.txt"
    test_file2.write_text("test content 2")

    commands = [
        ["git", "init"],
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

    return codelytics.Dir(tmp_path)


class TestInit:
    def test_valid_directory(self, dir):
        assert dir.path.exists() and dir.path.is_dir()

    def test_with_pathlib_object(self, tmp_path):
        dir = codelytics.Dir(tmp_path)
        assert dir.path == tmp_path

    def test_nonexistent_directory(self):
        with pytest.raises(FileNotFoundError):
            codelytics.Dir("/nonexistent/directory/somewhere")

    def test_file_not_directory(self, tmp_path):
        temp_file = tmp_path / "test_file.txt"
        temp_file.write_text("content")
        with pytest.raises(NotADirectoryError):
            codelytics.Dir(temp_file)


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
        dir = codelytics.Dir(tmp_path)

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
        assert dir.n_files("py") == 9
        assert dir.n_files(".py") == 9
        assert dir.n_files("md") == 1

    def test_files_empty_directory(self, tmp_path):
        dir = codelytics.Dir(tmp_path)
        assert dir.n_files() == 0
        assert dir.n_files("py") == 0

    def test_files_nonexistent_suffix(self, dir):
        assert dir.n_files("xyz") == 0


class TestExtract:
    def test_extract_code(self, dir):
        code = dir.extract("code")
        assert isinstance(code, codelytics.Py)
        assert len(code.content) > 0

        assert 'return "world"  # inline comment' in code.content
        assert "total_sum = sum([1, 2, 3])  # 'total_sum' included" in code.content
        assert "print(sh)" in code.content

    def test_extract_markdown(self, dir):
        md = dir.extract("markdown")
        assert isinstance(md, codelytics.TextAnalysis)
        assert len(md.texts) > 0

        assert "This is a readme file." in md.texts[0]
        assert "Let's analyze the data:" in md.texts[0]
