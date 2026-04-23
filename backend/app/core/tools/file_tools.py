import os
import json
import csv
import io
import logging
from langchain_core.tools import tool
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _safe_path(filename: str) -> str:
    """Restrict file access to the upload/output directory to prevent path traversal."""
    safe = os.path.realpath(os.path.join(settings.UPLOAD_DIR, os.path.basename(filename)))
    if not safe.startswith(os.path.realpath(settings.UPLOAD_DIR)):
        raise ValueError("Path traversal attempt detected.")
    return safe


@tool
def read_json_file(filename: str) -> str:
    """
    Read and return the contents of a JSON file from the data vault.
    Input: filename (basename only, e.g. 'data.json').
    Returns the JSON as a formatted string.
    """
    try:
        path = _safe_path(filename)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2)
    except FileNotFoundError:
        return f"File not found: {filename}"
    except Exception as e:
        logger.error("read_json_file error: %s", e)
        return f"Error reading file: {e}"


@tool
def write_json_file(filename: str, content: str) -> str:
    """
    Write JSON content to a file in the data vault.
    Input: filename (basename), content (valid JSON string).
    Returns a confirmation message.
    """
    try:
        path = _safe_path(filename)
        data = json.loads(content)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return f"Successfully wrote {filename} ({os.path.getsize(path)} bytes)."
    except Exception as e:
        logger.error("write_json_file error: %s", e)
        return f"Error writing file: {e}"


@tool
def read_csv_file(filename: str) -> str:
    """
    Read and return a CSV file from the data vault as a structured text table.
    Input: filename (basename only, e.g. 'report.csv').
    Returns the first 100 rows as plain text.
    """
    try:
        path = _safe_path(filename)
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if not rows:
            return "CSV is empty."
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows[:100])
        return output.getvalue()
    except FileNotFoundError:
        return f"File not found: {filename}"
    except Exception as e:
        logger.error("read_csv_file error: %s", e)
        return f"Error reading CSV: {e}"


@tool
def write_text_file(filename: str, content: str) -> str:
    """
    Write plain text content to a file in the data vault.
    Useful for saving agent-generated reports or summaries.
    Input: filename (basename), content (plain text string).
    """
    try:
        path = _safe_path(filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {filename} ({len(content)} chars)."
    except Exception as e:
        logger.error("write_text_file error: %s", e)
        return f"Error writing file: {e}"


FILE_TOOLS = [read_json_file, write_json_file, read_csv_file, write_text_file]
TOOL_IDS = ["read_json_file", "write_json_file", "read_csv_file", "write_text_file"]
