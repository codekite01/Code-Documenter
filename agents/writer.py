import os
from crewai import Agent, Task, LLM
from tools.file_tools import write_file
from models.schemas import RepoMap, ArchitectureReport
from dotenv import load_dotenv

load_dotenv()


gemini_llm = LLM(
    model=f"gemini/{os.getenv('MODEL_NAME', 'gemini-pro-latest')}",
    api_key=os.getenv("GOOGLE_API_KEY")
)


def create_writer_agent() -> Agent:
    return Agent(
        role="Technical Documentation Specialist",
        goal=(
            "Transform structured code analysis into a beautiful, comprehensive README.md "
            "that a new developer can follow to understand and run the project in under 10 minutes."
        ),
        backstory=(
            "You are a senior developer advocate who has written documentation for major "
            "open source projects. You write clearly, concisely, and with empathy for the "
            "reader. Your READMEs always have clear setup instructions, good examples, "
            "and are formatted beautifully in Markdown."
        ),
        tools=[write_file],
        llm=gemini_llm,  # <-- Wired specifically to Google
        max_iter=2,
        verbose=True,
    )


def create_write_task(
    agent: Agent,
    repo_map: RepoMap,
    arch_report: ArchitectureReport,
    output_path: str
) -> Task:

    # Build endpoint section if any were found
    endpoints_text = ""
    if arch_report.api_endpoints:
        ep_lines = "\n".join([
            f"- `{e.method} {e.path}` — {e.description}"
            for e in arch_report.api_endpoints
        ])
        endpoints_text = f"\nAPI Endpoints found:\n{ep_lines}\n"

    env_text = ""
    if arch_report.environment_variables:
        env_text = "Environment variables needed: " + ", ".join(
            arch_report.environment_variables
        )

    return Task(
        description=f"""
Write a comprehensive README.md for the project "{repo_map.repo_name}".

Here is everything the Analyst discovered about this project:

PROJECT OVERVIEW:
- Name: {arch_report.project_name}
- One-liner: {arch_report.one_line_description}
- Description: {arch_report.detailed_description}
- Architecture: {arch_report.architecture_pattern}
- Tech stack: {', '.join(arch_report.tech_stack)}

KEY FEATURES:
{chr(10).join(['- ' + f for f in arch_report.key_features])}

INSTALLATION STEPS:
{chr(10).join([f'{i+1}. {s}' for i, s in enumerate(arch_report.installation_steps)])}

{env_text}
{endpoints_text}

DATABASE: {arch_report.database_info or 'None detected'}
HAS TESTS: {repo_map.has_tests}
HAS DOCKER: {repo_map.has_docker}

Write the README in this order:
1. Title with emoji, one-liner, and shields.io badges for the main technologies
2. Brief description (2-3 paragraphs)
3. ✨ Features section (bullet list)
4. 🛠 Tech Stack section
5. 🚀 Getting Started (Prerequisites, Installation step-by-step with code blocks)
6. ⚙️ Environment Variables section (if any exist)
7. 📡 API Reference section (if endpoints were found, skip if none)
8. 🗂 Project Structure (show the directory tree)
9. 🧪 Running Tests section (if has_tests is true)
10. 🐳 Docker section (if has_docker is true)
11. 🤝 Contributing section
12. 📄 License section

Rules:
- Use proper Markdown: ## headers, ``` code blocks, | tables for API endpoints
- Every command must be in a code block with the language specified
- Don't make up information — only include what the Analyst found
- If a section has no data, skip it entirely
- Target audience: a developer seeing this project for the first time

When done writing the README content, use the 'Write File to Disk' tool to save it.
Call it with: content=, output_path="{output_path}"
""",
        expected_output=f"""
A confirmation that the README was successfully written to {output_path}.
The README should be comprehensive, well-formatted Markdown covering all
sections listed above.
""",
        agent=agent,
    )