import os, shutil, tempfile
from pathlib import Path
from crewai.tools import tool
import git
from dotenv import load_dotenv

load_dotenv()

# Files and folders to always skip
SKIP_DIRS = {
    '.git', 'node_modules', '__pycache__', '.venv', 'venv',
    'env', '.env', 'dist', 'build', '.next', '.nuxt',
    'vendor', 'bower_components', 'target', '.idea', '.vscode'
}
SKIP_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
    '.woff', '.woff2', '.ttf', '.eot', '.mp4', '.mp3',
    '.zip', '.tar', '.gz', '.pdf', '.pyc', '.pyo',
    '.class', '.jar', '.lock'  # skip lock files
}
SKIP_FILES = {
    'package-lock.json', 'yarn.lock', 'poetry.lock',
    'Pipfile.lock', '.DS_Store'
}


@tool("Clone GitHub Repository")
def clone_repository(repo_url: str) -> str:
    """
    Clone a GitHub repository to a local temporary directory.
    Input: a full GitHub URL like https://github.com/owner/repo
    Returns: the absolute local path where the repo was cloned.
    """
    try:
        base_dir = os.getenv("TEMP_REPO_DIR", "./tmp_repos")
        os.makedirs(base_dir, exist_ok=True)

        # Extract repo name from URL
        repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        clone_path = os.path.abspath(os.path.join(base_dir, repo_name))

        # Remove existing clone if present
        if os.path.exists(clone_path):
            shutil.rmtree(clone_path)

        # Clone (with auth token if available)
        token = os.getenv("GITHUB_TOKEN")
        if token and "github.com" in repo_url:
            auth_url = repo_url.replace(
                "https://", f"https://{token}@"
            )
        else:
            auth_url = repo_url

        git.Repo.clone_from(auth_url, clone_path, depth=1)  # depth=1 = fast shallow clone
        return clone_path

    except git.GitCommandError as e:
        return f"ERROR cloning repo: {str(e)}"
    except Exception as e:
        return f"ERROR: {str(e)}"


@tool("Map Directory Tree")
def map_directory_tree(repo_path: str) -> str:
    """
    Walk a cloned repository and return a formatted directory tree.
    Input: absolute path to the cloned repo.
    Returns: a text tree showing files and directories, skipping noise.
    """
    try:
        lines = []
        root = Path(repo_path)

        def walk(path: Path, prefix: str = "", depth: int = 0):
            if depth > 4:  # don't go deeper than 4 levels
                return
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
            for i, item in enumerate(items):
                if item.name in SKIP_DIRS or item.name in SKIP_FILES:
                    continue
                if item.suffix in SKIP_EXTENSIONS:
                    continue
                connector = "└── " if i == len(items) - 1 else "├── "
                if item.is_dir():
                    lines.append(f"{prefix}{connector}{item.name}/")
                    extension = "    " if i == len(items) - 1 else "│   "
                    walk(item, prefix + extension, depth + 1)
                else:
                    size = item.stat().st_size
                    size_str = f"{size // 1024}KB" if size > 1024 else f"{size}B"
                    lines.append(f"{prefix}{connector}{item.name} ({size_str})")

        lines.append(f"{root.name}/")
        walk(root)
        return "\n".join(lines)

    except Exception as e:
        return f"ERROR mapping tree: {str(e)}"