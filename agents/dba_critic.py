"""
DBA Critic Agent.
Analyzes SQLite runtime errors and provides corrective feedback
to the SQL Developer during the reflection loop.
"""

from tools.llm import call_llm

SYSTEM_PROMPT = (
    "You are a Senior Database Administrator and code reviewer. "
    "A SQL Developer's DDL code has failed SQLite runtime validation.\n\n"
    "Your task:\n"
    "1. Analyze the error message and the failing SQL code.\n"
    "2. Identify the root cause (syntax error, missing table, wrong type, etc.).\n"
    "3. Provide clear, actionable feedback so the developer can fix it.\n\n"
    "Do NOT write the corrected SQL yourself — only explain what is wrong "
    "and how to fix it.\n\n"
)


def critique(error_msg: str, sql_code: str, *, callback=None) -> str:
    """
    Analyze a SQLite error and return corrective feedback.
    """
    prompt = (
        f"{SYSTEM_PROMPT}"
        f"Error Message:\n{error_msg}\n\n"
        f"Failing SQL Code:\n{sql_code}\n"
    )
    return call_llm("DBA Critic", prompt, callback=callback)
