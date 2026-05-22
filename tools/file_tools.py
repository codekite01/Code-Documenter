import os
from pathlib import Path
from crewai.tools import tool
import tiktoken
from dotenv import load_dotenv

load_dotenv()

# Use cl100k tokenizer (works for claude and gpt-4)
_enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """Count tokens in a string."""
    return len(_enc.encode(text))


@tool("Read File Safely")
def read_file_safe(file_path: str) -> str:
    """
    Read a file's contents. Automatically truncates if the file is too large.
    Input: absolute or relative path to the file.
    Returns: file contents as a string, with a truncation note if cut.
    """
    max_tokens = int(os.getenv("MAX_TOKENS_PER_FILE", 3000))
    try:
        path = Path(file_path)
        if not path.exists():
            return f"ERROR: File not found: {file_path}"
        if path.stat().st_size > 500_000:  # skip files over 500KB
            return f"SKIPPED: File too large ({path.stat().st_size // 1024}KB): {file_path}"

        content = path.read_text(encoding="utf-8", errors="replace")
        tokens = count_tokens(content)

        if tokens <= max_tokens:
            return f"=== {file_path} ({tokens} tokens) ===\n{content}"

        # Smart truncation: keep first 80% + last 20%
        lines = content.split("\n")
        keep_head = int(len(lines) * 0.75)
        keep_tail = int(len(lines) * 0.1)
        truncated = (
            "\n".join(lines[:keep_head])
            + f"\n\n... [TRUNCATED: {tokens} total tokens, showing partial] ...\n\n"
            + "\n".join(lines[-keep_tail:])
        )
        return f"=== {file_path} (TRUNCATED from {tokens} tokens) ===\n{truncated}"

    except UnicodeDecodeError:
        return f"SKIPPED: Binary file (cannot read as text): {file_path}"
    except Exception as e:
        return f"ERROR reading {file_path}: {str(e)}"


@tool("Write File to Disk")
def write_file(content: str, output_path: str) -> str:
    """
    Write text content to a file on disk.
    Input: content (string to write), output_path (where to save).
    Returns: confirmation message with the saved path.
    """
    try:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"SUCCESS: README written to {output_path} ({len(content)} chars)"
    except Exception as e:
        return f"ERROR writing file: {str(e)}"