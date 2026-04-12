"""
D2 Designer Agent.
Converts validated SQLite DDL into a d2lang diagram specification.
"""

from tools.llm import call_llm, strip_fences

SYSTEM_PROMPT = (
    "You are an expert Diagram Designer using 'd2lang' (https://d2lang.com). "
    "Given verified SQLite DDL, generate a complete D2 diagram.\n\n"
    "Rules:\n"
    "- Use `direction: right`.\n"
    "- Each table must use `shape: sql_table`.\n"
    "- Mark primary keys with `{constraint: primary_key}` and "
    "foreign keys with `{constraint: foreign_key}`.\n"
    "- Draw relationship arrows between tables using the foreign key fields.\n"
    "- Use crow's foot notation: `source-arrowhead: {shape: cf-one}` / "
    "`target-arrowhead: {shape: cf-many}`.\n"
    "- Output ONLY the raw D2 code. No explanations, no markdown fences.\n\n"
)


def design(sql_ddl: str, *, callback=None) -> str:
    """Generate d2lang diagram code from validated SQL DDL."""
    prompt = f"{SYSTEM_PROMPT}SQL DDL:\n{sql_ddl}"
    raw = call_llm("D2 Designer", prompt, callback=callback)
    return strip_fences(raw)
