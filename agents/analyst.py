import os
from crewai import Agent, Task, LLM
from tools.file_tools import read_file_safe
from tools.github_tools import get_dependencies
from models.schemas import RepoMap, ArchitectureReport
from dotenv import load_dotenv

load_dotenv()

gemini_llm = LLM(
    model=f"gemini/{os.getenv('MODEL_NAME', 'gemini-pro-latest')}",
    api_key=os.getenv("GOOGLE_API_KEY")
)


def create_analyst_agent() -> Agent:
    return Agent(
        role="Software Architecture Expert",
        goal=(
            "Read the key source files of a repository and produce a deep, accurate "
            "understanding of what the project does, how it works architecturally, "
            "what its API looks like, and how someone would set it up and run it."
        ),
        backstory=(
            "You are a principal engineer with expertise in reading and reverse-engineering "
            "codebases. You can read 10 files and understand an entire system. You always "
            "look for: the main entry point, how data flows through the system, what "
            "external services it depends on, and what a new developer would need to know."
        ),
        tools=[read_file_safe, get_dependencies],
        llm=gemini_llm,  # <-- Wired specifically to Google
        max_iter=4,
        verbose=True,
    )


def create_analyse_task(agent: Agent, repo_map: RepoMap) -> Task:
    # Build a list of file paths for the agent to read
    file_list = "\n".join([
        f"- {f.path} ({f.language}): {f.reason}"
        for f in repo_map.key_files
    ])

    return Task(
        description=f"""
You are analysing the repository: {repo_map.repo_name}
Local path: {repo_map.local_path}
Languages detected: {', '.join(repo_map.languages)}

The Explorer agent has identified these key files for you to read:
{file_list}

Your job:
1. Use the 'Read File Safely' tool to read each key file above.
   Pass the FULL absolute path: {repo_map.local_path}/
2. After reading all files, use 'Get Project Dependencies' on {repo_map.local_path}
3. Synthesise everything you've read into a complete ArchitectureReport.

When looking for API endpoints, look for patterns like:
  - Python: @app.route, @router.get, @app.get, @blueprint.route
  - Node/Express: app.get(, router.post(, app.use(
  - Next.js: files in /pages/api/ or /app/api/

For environment variables, look in: .env.example, config files, README, source code.
For installation steps, look in: README.md, Makefile, package.json scripts, Dockerfile.
""",
        expected_output="""
A complete ArchitectureReport JSON object with all fields filled in accurately
based on what you actually read in the files. Do not guess — only report
what you found in the source code.
""",
        agent=agent,
        output_pydantic=ArchitectureReport,
    )