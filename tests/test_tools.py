import os, sys, pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.git_tools import clone_repository, map_directory_tree
from tools.file_tools import read_file_safe, write_file
from tools.github_tools import get_dependencies


def test_clone_public_repo():
    result = clone_repository.run("https://github.com/psf/requests")
    # Should return a path string, not an error
    assert "ERROR" not in result
    assert os.path.exists(result), f"Clone path does not exist: {result}"
    print(f"✓ Cloned to: {result}")


def test_map_tree(tmp_path):
    """Map a temp directory tree."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hi')")
    (tmp_path / "README.md").write_text("# Test")

    result = map_directory_tree.run(str(tmp_path))
    assert "main.py" in result
    assert "README.md" in result
    print("\n" + result)


def test_read_file_safe(tmp_path):
    """Read a small file and verify contents returned."""
    f = tmp_path / "hello.py"
    f.write_text("def hello():\n    return 'world'\n")

    result = read_file_safe.run(str(f))
    assert "hello" in result
    assert "ERROR" not in result


def test_write_file(tmp_path):
    """Write a file and verify it exists on disk."""
    output = tmp_path / "README.md"
    result = write_file.run(content="# Hello", output_path=str(output))
    assert "SUCCESS" in result
    assert output.read_text() == "# Hello"


def test_get_dependencies(tmp_path):
    """Detect dependencies from a fake repo."""
    (tmp_path / "requirements.txt").write_text("flask==3.0\nrequests==2.31\n")

    result = get_dependencies.run(str(tmp_path))
    assert "flask" in result
    assert "requests" in result