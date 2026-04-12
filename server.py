"""
Autonomous DB-Architect — Web Server
Run: python server.py
Opens a browser-based UI with real-time agent progress via Server-Sent Events.
"""

import json
import asyncio
import queue
import threading
import webbrowser
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="DB-Architect")

STATIC_DIR = Path(__file__).parent / "static"
OUTPUT_DIR = Path(__file__).parent / "output"


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main UI page."""
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/api/run")
async def run_pipeline(request: Request, prompt: str = ""):
    """
    Execute the pipeline and stream events via SSE.
    Query param: ?prompt=<user database description>
    """
    if not prompt.strip():
        return JSONResponse({"error": "No prompt provided."}, status_code=400)

    event_queue: queue.Queue = queue.Queue()

    def callback(event: str, data: dict):
        """Thread-safe callback: pipeline runs in a thread, pushes events."""
        # Convert Path objects to strings for JSON serialization
        safe = {}
        for k, v in data.items():
            safe[k] = str(v) if isinstance(v, Path) else v
        event_queue.put({"event": event, "data": safe})

    def run_in_thread():
        try:
            from core.pipeline import run
            run(prompt, callback=callback)
        except Exception as e:
            event_queue.put({"event": "error", "data": {"message": str(e)}})
        finally:
            event_queue.put(None)  # sentinel

    thread = threading.Thread(target=run_in_thread, daemon=True)
    thread.start()

    async def event_stream():
        while True:
            if await request.is_disconnected():
                break
            try:
                item = event_queue.get(timeout=0.1)
            except queue.Empty:
                await asyncio.sleep(0.05)
                continue

            if item is None:
                yield "data: [DONE]\n\n"
                break

            yield f"data: {json.dumps(item)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/api/output/{filename}")
async def get_output_file(filename: str):
    """Serve files from the output directory (SQL, D2, SVG)."""
    # Security: prevent directory traversal
    safe_name = Path(filename).name
    file_path = OUTPUT_DIR / safe_name

    if not file_path.exists():
        return JSONResponse({"error": "File not found."}, status_code=404)

    suffix = file_path.suffix.lower()
    media_types = {
        ".sql": "text/plain",
        ".d2": "text/plain",
        ".svg": "image/svg+xml",
    }
    media_type = media_types.get(suffix, "application/octet-stream")
    content = file_path.read_text(encoding="utf-8")
    return HTMLResponse(content=content, media_type=media_type)


# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


if __name__ == "__main__":
    print("\n[DB-Architect] Web UI -> http://localhost:8000\n")
    webbrowser.open("http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
