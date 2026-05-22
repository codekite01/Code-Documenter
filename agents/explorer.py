import os
from crewai import Agent, Task, LLM
from tools.git_tools import clone_repository, map_directory_tree
from tools.github_tools import get_dependencies
from models.schemas import RepoMap
from dotenv import load_dotenv

load_dotenv()


gemini_llm = LLM(
    
    model=f"gemini/{os.getenv('MODEL_NAME', 'gemini-1.5-flash')}",
    api_key=os.getenv("GOOGLE_API_KEY")
)

def create_explorer_agent() -> Agent:
    return Agent(
        role="Senior Repository Analyst",
        goal=(
            "Thoroughly map any GitHub repository's structure, identify the technology "
            "stack, entry points, and most important files for further analysis. "
            "Produce a complete, structured map that another agent can use without "
            "needing to explore the repo themselves."
        ),
        backstory=(
            "You are an expert software architect with 15 years of experience reading "
            "codebases across dozens of languages and frameworks. You can instantly "
            "identify what a project does, how it's organized, and which files matter "
            "most — just from directory structure and file names."
        ),
        tools=[clone_repository, map_directory_tree, get_dependencies],
        llm=gemini_llm,  # <-- Wired specifically to Google
        max_iter=5,
        max_rpm=4,
        verbose=True,
    )


def create_explore_task(agent: Agent, repo_url: str) -> Task:
    return Task(
        description=f"""
Analyze the GitHub repository at: {repo_url}

Follow these steps in order:
1. Use the 'Clone GitHub Repository' tool to clone the repo locally.
2. Use the 'Map Directory Tree' tool on the returned local path to get the file tree.
3. Use the 'Get Project Dependencies' tool to identify all libraries and frameworks.
4. Based on the tree and dependencies, identify:
   - The tech stack (languages, frameworks, databases)
   - The top 10 most important files (entry points, main modules, config files)
   - The likely entry points for the application
   - Whether the project has tests or Docker configuration

Be systematic. Do not guess — base your analysis on what the tools return.
""",
        expected_output="""
A complete RepoMap JSON object with:
- repo_name: the repository name
- repo_url: the original URL
- local_path: where it was cloned
- languages: list of detected languages
- directory_tree: the full tree string from the tool
- key_files: list of up to 10 FileInfo objects (path, reason, language)
- entry_points: list of entry point file paths
- has_tests: true/false
- has_docker: true/false
""",
        agent=agent,
        output_pydantic=RepoMap,
    )