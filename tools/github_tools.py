import os, json
from pathlib import Path
from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()

# Dependency files to look for
DEP_FILES = [
    "package.json", "requirements.txt", "pyproject.toml",
    "Pipfile", "go.mod", "Cargo.toml", "pom.xml",
    "build.gradle", "composer.json", "Gemfile"
]


@tool("Get Project Dependencies")
def get_dependencies(repo_path: str) -> str:
    """
    Scan a cloned repo for dependency files and extract library names.
    Input: absolute path to the cloned repo.
    Returns: JSON string with detected dependencies per ecosystem.
    """
    try:
        root = Path(repo_path)
        result = {}

        for dep_file in DEP_FILES:
            fpath = root / dep_file
            if not fpath.exists():
                continue

            content = fpath.read_text(encoding="utf-8", errors="replace")

            if dep_file == "package.json":
                try:
                    data = json.loads(content)
                    deps = list(data.get("dependencies", {}).keys())
                    dev_deps = list(data.get("devDependencies", {}).keys())
                    result["node"] = {"dependencies": deps, "devDependencies": dev_deps}
                except:
                    result["node"] = {"raw": content[:500]}

            elif dep_file == "requirements.txt":
                lines = [l.strip() for l in content.split("\n")
                         if l.strip() and not l.startswith("#")]
                result["python"] = lines

            elif dep_file in ("pyproject.toml", "Pipfile"):
                result["python_toml"] = content[:800]

            elif dep_file == "go.mod":
                result["go"] = content[:800]

            else:
                result[dep_file] = content[:500]

        if not result:
            return "No dependency files found."
        return json.dumps(result, indent=2)

    except Exception as e:
        return f"ERROR reading dependencies: {str(e)}"