import os
from crewai import Crew, Process
from agents.explorer import create_explorer_agent, create_explore_task
from agents.analyst  import create_analyst_agent, create_analyse_task
from agents.writer   import create_writer_agent, create_write_task
from models.schemas  import RepoMap, ArchitectureReport
from dotenv import load_dotenv

load_dotenv()


def run_documenter(repo_url: str, output_path: str = "./output/README.md") -> str:
    """
    Run the full multi-agent pipeline.

    Args:
        repo_url:    GitHub repository URL to document
        output_path: Where to save the generated README.md

    Returns:
        Path to the generated README file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # ── Step 1: Create all agents ──────────────────────
    explorer_agent = create_explorer_agent()
    analyst_agent  = create_analyst_agent()
    writer_agent   = create_writer_agent()

    # ── Step 2: Create Task 1 (Explorer) ──────────────
    explore_task = create_explore_task(explorer_agent, repo_url)

    # ── Step 3: Run Phase 1 to get the RepoMap ────────
    phase1_crew = Crew(
        agents=[explorer_agent],
        tasks=[explore_task],
        process=Process.sequential,
        verbose=True,
    )
    phase1_result = phase1_crew.kickoff()
    repo_map: RepoMap = phase1_result.pydantic

    if not repo_map:
        raise ValueError("Explorer failed to produce a RepoMap. Check verbose output above.")

    # ── Step 4: Create Task 2 (Analyst) with RepoMap ──
    analyse_task = create_analyse_task(analyst_agent, repo_map)

    phase2_crew = Crew(
        agents=[analyst_agent],
        tasks=[analyse_task],
        process=Process.sequential,
        verbose=True,
    )
    phase2_result = phase2_crew.kickoff()
    arch_report: ArchitectureReport = phase2_result.pydantic

    if not arch_report:
        raise ValueError("Analyst failed to produce an ArchitectureReport. Check verbose output.")

    # ── Step 5: Create Task 3 (Writer) with both outputs
    write_task = create_write_task(writer_agent, repo_map, arch_report, output_path)

    phase3_crew = Crew(
        agents=[writer_agent],
        tasks=[write_task],
        process=Process.sequential,
        verbose=True,
    )
    phase3_crew.kickoff()

    return output_path


if __name__ == "__main__":
    # Quick test: run directly with python crew.py
    result = run_documenter(
        repo_url="https://github.com/ditikrushna/End-to-End-Diabetes-Prediction-Application-Using-Machine-Learning",
        output_path="./output/fastapi_README.md"
    )
    print(f"\n✅ Done! README saved to: {result}")