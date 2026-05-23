# Multi-Agent Codebase Documenter

Developers are getting tired of writing READMEs. So I built a tool that does it for them.

You give it a GitHub URL. Three AI agents — an Explorer, an Analyst, and a Writer — work through the repo in sequence and hand you back a complete, structured README.md. The whole thing runs in a few minutes and costs fractions of a cent per repo.

This is a portfolio project I built to learn multi-agent orchestration with CrewAI. It's not perfect, but it works on real codebases and taught me more about agentic AI than any tutorial did.

## How it works

The pipeline runs three agents back to back, each with a specific job:

**Explorer** — Clones the repo and maps the directory tree. It reads dependency files (`requirements.txt`, `package.json`, `go.mod`, etc.) and figures out which files actually matter. It skips the noise — `node_modules`, `.venv`, lock files, build artifacts — and hands the Analyst a prioritized list of the 10 most important files to read.

**Analyst** — Takes that list and reads the files. It's looking for how the application is structured, what the API looks like, what environment variables are needed, and how you'd actually run the thing. It produces a structured report that the Writer can use.

**Writer** — Takes the Explorer's repo map and the Analyst's architectural report and writes the README. It knows what sections to include, when to skip sections (no API endpoints? no API reference), and how to format code blocks properly.

The agents don't share a context window — each one gets a clean, structured handoff from the previous one. This keeps things predictable and makes it easy to debug when something goes wrong.

## Tech stack

- Python 3.10+
- CrewAI for agent orchestration
- Google Gemini (`gemini-1.5-flash`) via LiteLLM
- GitPython for cloning and tree traversal
- Pydantic v2 for structured agent outputs
- Rich for the terminal UI

## Setup

Clone the repo and create a virtual environment:

```bash
git clone https://github.com/username/codebase-documenter
cd codebase-documenter
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the root:
```
GOOGLE_API_KEY=your_google_api_key_here
MODEL_NAME=gemini-1.5-flash
TEMP_REPO_DIR=./tmp_repos
```
Get your Google API key from [aistudio.google.com](https://aistudio.google.com). The free tier is enough to run this comfortably.

## Usage

```bash
python main.py https://github.com/username/repo
```

Save the output somewhere specific:

```bash
python main.py https://github.com/username/repo --output ./docs/README.md
```

Suppress the agent chatter if you just want the result:

```bash
python main.py https://github.com/username/repo --quiet
```

The generated README lands at `./output/README.md` by default. Open it, skim it, fix anything that's wrong (there's usually something small), and you're done.

## Project structure
```

codebase-documenter/
├── agents/
│   ├── explorer.py       # repo mapping, dependency detection
│   ├── analyst.py        # file reading, architecture extraction
│   └── writer.py         # README generation
├── models/
│   └── schemas.py        # Pydantic models for agent outputs
├── tools/
│   ├── git_tools.py      # clone_repository, map_directory_tree
│   ├── file_tools.py     # read_file_safe, write_file
│   └── github_tools.py   # get_dependencies
├── crew.py               # wires agents together into a pipeline
├── main.py               # CLI entry point
└── .env                  # API keys (don't commit this)
```

## Things I learned building this

Token limits are the main engineering problem, not the agents themselves. A real codebase can be 50,000+ tokens. The Explorer has to be smart about which files it prioritizes, and the Analyst has to truncate intelligently without losing the important parts. Getting that right took more iteration than anything else.

Structured outputs matter a lot. Early versions had the agents returning plain text, which made it hard to pass information cleanly between them. Switching to Pydantic models for each agent's output made the whole pipeline more reliable and much easier to debug.

Prompt engineering is still writing. The quality of the generated README is almost entirely determined by how clearly you describe what you want in the task description. Vague instructions produce vague documentation.

## Known limitations

- Works best on repos under ~50k tokens of source code. Very large monorepos will hit token limits even with truncation.
- Private repos need a GitHub token set in `.env` as `GITHUB_TOKEN`.
- The Writer occasionally hallucinates installation steps for projects with unusual build systems. Always read the output before shipping it.
- Not tested on repos that use languages other than Python, JavaScript, TypeScript, and Go.

## License

MIT