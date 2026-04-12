"""
Requirements Analyst Agent.
Parses natural language database descriptions into structured JSON entities.
"""

from tools.llm import call_llm, strip_fences

SYSTEM_PROMPT = (
    "You are a Requirements Analyst specializing in database design. "
    "Read the user's description carefully and extract every entity (table), "
    "its fields (with appropriate data types), and the relationships between entities.\n\n"
    "Return ONLY a clean JSON object. Do NOT wrap it in markdown fences.\n"
    "The JSON must follow this structure:\n"
    "{\n"
    '  "entities": [\n'
    '    {\n'
    '      "name": "TableName",\n'
    '      "fields": [\n'
    '        {"name": "id", "type": "INTEGER", "constraints": ["PRIMARY KEY"]},\n'
    '        {"name": "other_field", "type": "TEXT", "constraints": ["NOT NULL"]}\n'
    '      ],\n'
    '      "relationships": [\n'
    '        {"target": "OtherTable", "type": "one-to-many", "foreign_key": "other_table_id"}\n'
    '      ]\n'
    '    }\n'
    "  ]\n"
    "}\n"
)


def analyze(user_request: str, *, callback=None) -> str:
    """
    Convert a natural-language database description into structured JSON.

    Returns the raw JSON string.
    """
    prompt = f"{SYSTEM_PROMPT}\nUser Request:\n{user_request}"
    raw = call_llm("Requirements Analyst", prompt, callback=callback)
    return strip_fences(raw)
