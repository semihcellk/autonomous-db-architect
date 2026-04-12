"""
D2 diagram compilation tool.
Writes .d2 source and invokes the `d2` CLI to produce SVG output.
"""

import shutil
import subprocess
from pathlib import Path
from config import OUTPUT_DIR


class D2NotInstalledError(Exception):
    """Raised when the `d2` CLI binary is not found on the system PATH."""


class D2CompilationError(Exception):
    """Raised when the `d2` CLI fails to compile the diagram source."""


def compile_d2(code: str, file_name: str) -> Path:
    """
    Write *code* to ``output/<file_name>.d2`` and compile it to SVG.

    Returns the path to the generated SVG file.

    Raises
    ------
    D2NotInstalledError
        If the ``d2`` binary cannot be found.
    D2CompilationError
        If the ``d2`` compiler rejects the source code.
    """
    if shutil.which("d2") is None:
        raise D2NotInstalledError(
            "The 'd2' CLI is not installed or not on your PATH.\n"
            "Install it from https://d2lang.com/tour/install and try again."
        )

    src = OUTPUT_DIR / f"{file_name}.d2"
    svg = OUTPUT_DIR / f"{file_name}.svg"

    src.write_text(code, encoding="utf-8")

    result = subprocess.run(
        ["d2", str(src), str(svg)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise D2CompilationError(
            f"D2 compilation failed:\n{result.stderr.strip()}"
        )

    return svg
