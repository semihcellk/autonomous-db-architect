"""
LLM helper utilities shared across all agents.
"""

import litellm
from core.config import MODEL


def call_llm(agent_name: str, prompt: str, *, callback=None) -> str:
    """
    Send a prompt to the configured LLM and return the text response.

    Parameters
    ----------
    agent_name : str
        Human-readable label for logging (e.g. "Requirements Analyst").
    prompt : str
        The full prompt to send.
    callback : callable, optional
        If provided, called with (agent_name, "generating") at start and
        (agent_name, "done") when the response is received. Used by the
        web UI to push real-time status updates.
    """
    if callback:
        callback(agent_name, "generating")

    response = litellm.completion(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.choices[0].message.content

    if callback:
        callback(agent_name, "done")

    return text


def strip_fences(code: str) -> str:
    """Remove markdown code fences (```...```) that LLMs commonly wrap output in."""
    lines = code.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()
