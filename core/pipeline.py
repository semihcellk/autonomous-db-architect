"""
Autonomous DB-Architect Pipeline
Orchestrates: Requirements Analyst → SQL Developer ↔ DBA Critic (Reflection) → D2 Designer

All critical bugs have been fixed:
- SQL output is now saved to disk
- Reflection loop failure raises an error instead of silently continuing
- No deliberate error injection in prompts
"""

import uuid
from pathlib import Path

from core.config import MAX_REFLECTION_RETRIES, OUTPUT_DIR
from agents import analyst, sql_developer, dba_critic, d2_designer
from tools.sqlite_validator import validate_ddl
from tools.d2_compiler import compile_d2, D2NotInstalledError, D2CompilationError


class PipelineError(Exception):
    """Raised when the pipeline cannot produce valid output."""


def run(user_request: str, *, callback=None) -> dict:
    """
    Execute the full DB-Architect pipeline.

    Parameters
    ----------
    user_request : str
        Natural-language description of the desired database.
    callback : callable, optional
        Called with (event: str, data: dict) to report progress.
        Events: "stage", "log", "reflection", "result", "error"

    Returns
    -------
    dict with keys:
        run_id, json_entities, sql_ddl, d2_code,
        sql_path, d2_path, svg_path, reflection_iterations
    """
    run_id = uuid.uuid4().hex[:8]
    _emit(callback, "stage", {"stage": "init", "run_id": run_id})

    # ── 1. Requirements Analyst ──────────────────────────────────────
    _emit(callback, "stage", {"stage": "analyst", "status": "running"})
    json_entities = analyst.analyze(user_request, callback=_agent_cb(callback))
    _emit(callback, "log", {"agent": "Requirements Analyst", "output": json_entities})
    _emit(callback, "stage", {"stage": "analyst", "status": "done"})

    # ── 2. SQL Developer ─────────────────────────────────────────────
    _emit(callback, "stage", {"stage": "sql_developer", "status": "running"})
    current_sql = sql_developer.generate(json_entities, callback=_agent_cb(callback))
    _emit(callback, "log", {"agent": "SQL Developer", "output": current_sql})
    _emit(callback, "stage", {"stage": "sql_developer", "status": "done"})

    # ── 3. Reflection Loop (DBA Critic + SQLite Tool) ────────────────
    _emit(callback, "stage", {"stage": "reflection", "status": "running"})
    reflection_count = 0

    for iteration in range(1, MAX_REFLECTION_RETRIES + 1):
        is_valid, error_msg = validate_ddl(current_sql)

        if is_valid:
            _emit(callback, "reflection", {
                "iteration": iteration,
                "passed": True,
                "message": f"SQLite validation PASSED at iteration {iteration}.",
            })
            reflection_count = iteration
            break

        _emit(callback, "reflection", {
            "iteration": iteration,
            "passed": False,
            "message": f"SQLite validation FAILED: {error_msg}",
        })

        if iteration == MAX_REFLECTION_RETRIES:
            err = (
                f"Pipeline aborted: SQL could not be fixed after "
                f"{MAX_REFLECTION_RETRIES} reflection iterations.\n"
                f"Last error: {error_msg}"
            )
            _emit(callback, "error", {"message": err})
            raise PipelineError(err)

        # DBA Critic reviews the error
        feedback = dba_critic.critique(error_msg, current_sql, callback=_agent_cb(callback))
        _emit(callback, "log", {"agent": "DBA Critic", "output": feedback})

        # SQL Developer applies the fix
        current_sql = sql_developer.fix(error_msg, feedback, callback=_agent_cb(callback))
        _emit(callback, "log", {"agent": "SQL Developer (Fix)", "output": current_sql})

    _emit(callback, "stage", {"stage": "reflection", "status": "done"})

    # ── 4. Save validated SQL ────────────────────────────────────────
    sql_path = OUTPUT_DIR / f"schema_{run_id}.sql"
    sql_path.write_text(current_sql, encoding="utf-8")

    # ── 5. D2 Designer ───────────────────────────────────────────────
    _emit(callback, "stage", {"stage": "d2_designer", "status": "running"})
    d2_code = d2_designer.design(current_sql, callback=_agent_cb(callback))
    _emit(callback, "log", {"agent": "D2 Designer", "output": d2_code})

    svg_path = None
    d2_path = None
    d2_error = None
    try:
        svg_path = compile_d2(d2_code, f"db_diagram_{run_id}")
        d2_path = OUTPUT_DIR / f"db_diagram_{run_id}.d2"
    except D2NotInstalledError as e:
        d2_error = str(e)
        _emit(callback, "log", {
            "agent": "D2 Compiler",
            "output": f"⚠ {e}\nSQL schema was saved successfully. Diagram skipped.",
        })
    except D2CompilationError as e:
        d2_error = str(e)
        _emit(callback, "log", {
            "agent": "D2 Compiler",
            "output": f"⚠ {e}\nSQL schema was saved successfully. Diagram may need manual review.",
        })

    _emit(callback, "stage", {"stage": "d2_designer", "status": "done"})

    # ── Build result ─────────────────────────────────────────────────
    result = {
        "run_id": run_id,
        "json_entities": json_entities,
        "sql_ddl": current_sql,
        "d2_code": d2_code,
        "sql_path": str(sql_path),
        "d2_path": str(d2_path) if d2_path else None,
        "svg_path": str(svg_path) if svg_path else None,
        "d2_error": d2_error,
        "reflection_iterations": reflection_count,
    }

    _emit(callback, "result", result)
    return result


# ── Internal helpers ─────────────────────────────────────────────────

def _emit(callback, event: str, data: dict):
    """Safely invoke the callback if provided."""
    if callback:
        callback(event, data)


def _agent_cb(callback):
    """Create a lightweight agent-level callback from the pipeline callback."""
    if not callback:
        return None

    def _inner(agent_name, status):
        _emit(callback, "log", {"agent": agent_name, "status": status})

    return _inner
