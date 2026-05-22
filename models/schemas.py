from pydantic import BaseModel, Field
from typing import List, Optional


class FileInfo(BaseModel):
    """Represents a single important file in the repo."""
    path: str = Field(description="Relative path from repo root")
    reason: str = Field(description="Why this file is important")
    language: str = Field(description="Programming language e.g. Python, TypeScript")


class RepoMap(BaseModel):
    """Output of Agent 1 (Explorer). A structured map of the repository."""
    repo_name: str = Field(description="Name of the repository")
    repo_url: str = Field(description="Original GitHub URL")
    local_path: str = Field(description="Absolute path to cloned repo on disk")
    languages: List[str] = Field(description="Languages detected e.g. ['Python', 'TypeScript']")
    directory_tree: str = Field(description="Formatted text tree of the directory")
    key_files: List[FileInfo] = Field(
        description="Top 10 most important files for the analyst to read"
    )
    entry_points: List[str] = Field(
        description="Likely entry points e.g. main.py, src/index.js, app.py"
    )
    has_tests: bool = Field(description="Whether a tests/ or __tests__/ directory exists")
    has_docker: bool = Field(description="Whether a Dockerfile or docker-compose.yml exists")


class ApiEndpoint(BaseModel):
    """A single API route found in the codebase."""
    method: str = Field(description="HTTP method: GET, POST, PUT, DELETE etc.")
    path: str = Field(description="Route path e.g. /api/users/:id")
    description: str = Field(description="What this endpoint does")


class ArchitectureReport(BaseModel):
    """Output of Agent 2 (Analyst). Deep understanding of the codebase."""
    project_name: str
    one_line_description: str = Field(
        description="One sentence: what does this project do?"
    )
    detailed_description: str = Field(
        description="2-3 paragraph description of what the project does and why"
    )
    architecture_pattern: str = Field(
        description="e.g. MVC, Microservices, Monolith, Serverless, REST API"
    )
    tech_stack: List[str] = Field(
        description="All frameworks and major libraries used"
    )
    api_endpoints: List[ApiEndpoint] = Field(
        default_factory=list,
        description="All discovered API endpoints. Empty list if not a web app."
    )
    database_info: Optional[str] = Field(
        default=None,
        description="Database used e.g. PostgreSQL with SQLAlchemy ORM. None if no DB."
    )
    environment_variables: List[str] = Field(
        default_factory=list,
        description="All env vars the project needs e.g. DATABASE_URL, JWT_SECRET"
    )
    installation_steps: List[str] = Field(
        description="Exact commands to install and run the project"
    )
    key_features: List[str] = Field(
        description="3-6 bullet points of main features"
    )
    contributing_notes: Optional[str] = Field(
        default=None,
        description="Any notes from CONTRIBUTING.md or code comments about how to contribute"
    )