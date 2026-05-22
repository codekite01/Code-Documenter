# 🤖 Multi-Agent Codebase Documenter

An automated, AI-powered documentation generator built with [CrewAI](https://www.crewai.com/) and Google Gemini. This tool deploys a team of autonomous AI agents to clone, analyze, and map any GitHub repository, ultimately producing a comprehensive, developer-ready `README.md` in minutes.

## ✨ Key Features

- **Zero-Touch Analysis:** Just provide a GitHub URL. The agents handle cloning, file tree mapping, and dependency parsing automatically.
- **Intelligent Triage:** Ignores noise (`node_modules`, `.venv`, cache files) to focus only on critical architectural files.
- **Deep Context Extraction:** Identifies the tech stack, API endpoints, environment variables, and testing frameworks.
- **Powered by Gemini:** Optimized to use Google's highly efficient `gemini-1.5-flash` model for fast, cost-effective context processing.

## 🧠 Agent Architecture

This tool uses a sequential process with three specialized agents:

1. **🕵️ Explorer (Senior Repository Analyst):** Clones the repository, maps the directory tree, reads package files (e.g., `requirements.txt`, `package.json`), and identifies the top 10 most critical files in the project.
2. **🔬 Analyst (Software Architecture Expert):** Safely reads the contents of the critical files identified by the Explorer. It reverse-engineers the application flow, data schemas, and API endpoints.
3. **✍️ Writer (Technical Documentation Specialist):** Synthesizes the Explorer's map and the Analyst's architectural report into a beautifully formatted Markdown file.

## 🛠 Tech Stack

- **Python 3.10+**
- **CrewAI** (Agent orchestration)
- **Google GenAI / LiteLLM** (LLM integration)
- **GitPython** (Repository cloning)
- **Rich** (Terminal UI and progress tracking)

## 🚀 Getting Started

### Prerequisites

Ensure you have Python installed, then set up a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

## Installation

1. Clone this repository to your local machine.

2. Install the required dependencies:

```bash
pip install crewai GitPython python-dotenv rich google-genai
pip install -r requirements.txt
```
3. Create a .env file in the root directory and add your Google API key:

``` 
GOOGLE_API_KEY=your_google_api_key_here
MODEL_NAME=gemini-1.5-flash
TEMP_REPO_DIR=./tmp_repos
```
## 💻 Usage

Run the main script and pass the target GitHub repository URL as an argument:

```bash
python main.py https://github.com/username/repository
```
# Optional arguments
```
-o or --output: Specify a custom path and filename for the generated README (default is ./output/README.md).

-q or --quiet: Suppress the verbose output from the agents to keep the terminal clean.
```
## 🗂 Project Structure

```
├── agents/
│   ├── analyst.py       # Architecture extraction logic
│   ├── explorer.py      # Repo mapping and dependency logic
│   └── writer.py        # Markdown generation logic
├── models/
│   └── schemas.py       # Pydantic models (RepoMap, ArchitectureReport)
├── tools/
│   ├── file_tools.py    # Safe file reading/writing
│   ├── git_tools.py     # Cloning and directory tree mapping
│   └── github_tools.py  # Dependency parsing
├── main.py              # CLI entry point and Rich UI
├── crew.py              # CrewAI sequential process definition
└── .env                 # Environment variables configuration
```
