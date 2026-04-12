"""
SQL Developer Agent.
Generates SQLite DDL from structured JSON entities, and applies fixes
based on DBA feedback during the reflection loop.
"""

from tools.llm import call_llm, strip_fences

GENERATE_PROMPT = (
    "You are a SQL Developer. Convert the following JSON database entities "
    "into strict, production-ready SQLite DDL code.\n\n"
    "Rules:\n"
    "- Use CREATE TABLE statements with appropriate data types.\n"
    "- Include PRIMARY KEY, FOREIGN KEY, NOT NULL, and UNIQUE constraints.\n"
    "- Enable foreign key relationships correctly.\n"
    "- Output ONLY the raw SQL code. No explanations, no markdown fences.\n\n"
    "JSON Entities:\n"
)

FIX_PROMPT = (
    "You are a SQL Developer. Your previous SQL code failed SQLite validation. "
    "Apply the Senior DBA's feedback to fix it.\n\n"
    "Rules:\n"
    "- Output ONLY the complete, corrected raw SQLite DDL code.\n"
    "- Do NOT omit any tables from the original — return the full schema.\n"
    "- No explanations, no markdown fences.\n\n"
)


def generate(json_entities: str, *, callback=None) -> str:
    """Generate initial SQLite DDL from JSON entities."""
    prompt = f"{GENERATE_PROMPT}{json_entities}"
    raw = call_llm("SQL Developer", prompt, callback=callback)
    return strip_fences(raw)


def fix(error_msg: str, dba_feedback: str, *, callback=None) -> str:
    """Re-generate corrected DDL based on DBA feedback."""
    prompt = (
        f"{FIX_PROMPT}"
        f"SQLite Error:\n{error_msg}\n\n"
        f"DBA Feedback:\n{dba_feedback}\n"
    )
    raw = call_llm("SQL Developer (Fix)", prompt, callback=callback)
    return strip_fences(raw)
