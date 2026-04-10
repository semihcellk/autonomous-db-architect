"""
Autonomous DB-Architect
Implements: Requirements Analyst -> SQL Developer <-> DBA Critic (Reflection with SQLite) -> D2 Designer
"""
import os
import subprocess
import sqlite3
import uuid
from pathlib import Path
import litellm

# === API Configuration ===
# Insert your OpenAI or Gemini API keys here before running securely
os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY_HERE"
MODEL = os.environ.get("MODEL", "gpt-4o-mini")

MAX_REFLECTION_RETRIES = 5

def call_llm(agent_name: str, prompt: str) -> str:
    print(f"[{agent_name}] Generating response...")
    response = litellm.completion(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def strip_fences(code: str) -> str:
    lines = code.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()

def test_sqlite_ddl(ddl_code: str) -> tuple[bool, str]:
    try:
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        cursor.executescript(ddl_code)
        conn.commit()
        conn.close()
        return True, "SUCCESS"
    except Exception as e:
        return False, str(e)

def compile_d2(code: str, file_name: str) -> Path:
    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    src = out_dir / f"{file_name}.d2"
    svg = out_dir / f"{file_name}.svg"
    src.write_text(code, encoding="utf-8")
    subprocess.run(["d2", str(src), str(svg)], check=True, capture_output=True)
    return svg

def run(user_request: str) -> str:
    run_id = uuid.uuid4().hex[:8]
    print(f"\n[INFO] Starting DB-Architect Run: {run_id}")
    
    # 1. Requirements Analyst
    analyst_prompt = (
        "You are a Requirements Analyst for databases. Read the user request and extract the entities (tables) "
        "and their fields. Return ONLY a clean JSON object containing the entities, their fields and relationships. "
        "No markdown fences.\n\n"
        f"User Request: {user_request}"
    )
    json_entities = strip_fences(call_llm("Requirements Analyst", analyst_prompt))
    
    # 2. SQL Developer
    sql_dev_prompt = (
        "You are a SQL Developer. Convert the following JSON database entities into strict SQLite DDL code "
        "Output ONLY the raw SQL code. No markdown fences.\n"
        "INSTRUCTION: Introduce one syntax error to trigger the Reflection Loop dynamically.\n\n"
        f"JSON Entities: {json_entities}"
    )
    current_sql = strip_fences(call_llm("SQL Developer", sql_dev_prompt))
    
    # 3. Reflection Loop (DBA Critic + SQLite Tool)
    print("\n[INFO] Starting Producer-Critic Reflection Loop...")
    for iter_count in range(1, MAX_REFLECTION_RETRIES + 1):
        is_valid, error_msg = test_sqlite_ddl(current_sql)
        if is_valid:
            print(f"  -> SQLite Runtime Test PASSED at iteration {iter_count}.")
            break
            
        print(f"  -> SQLite Runtime Test FAILED at iter {iter_count}. Error: '{error_msg}'")
        
        if iter_count == MAX_REFLECTION_RETRIES:
            break
            
        dba_prompt = (
            "You are a Senior DBA. Analyze the error and provide clear feedback to the SQL Developer "
            "on how to fix it. Do NOT write the corrected SQL yourself.\n\n"
            f"Error Message: {error_msg}\nCode:\n{current_sql}\n"
        )
        dba_feedback = call_llm("DBA Critic", dba_prompt)
        
        sql_fix_prompt = (
            "You are a SQL Developer. Your previous code failed with an error. Apply the Senior DBA's feedback "
            "to fix it. Output ONLY the complete, corrected raw SQLite DDL code.\n\n"
            f"SQLite Error: {error_msg}\nDBA Feedback:\n{dba_feedback}\n"
        )
        current_sql = strip_fences(call_llm("SQL Developer (Fix)", sql_fix_prompt))
    
    # 4. D2 Designer
    print("\n[INFO] Compiling D2 Architecture Visualization...")
    designer_prompt = (
        "You are an expert Diagram Designer using 'd2lang' (d2lang.com). "
        "Given the following SQLite DDL, generate a complete D2 diagram code with 'direction: right'. "
        "Return ONLY the D2 code.\n\n"
        f"SQL DDL:\n{current_sql}"
    )
    d2_code = strip_fences(call_llm("D2 Designer", designer_prompt))
    
    svg_path = compile_d2(d2_code, f"db_diagram_{run_id}")
    print(f"\n[OK] Run {run_id} is complete! Diagram saved locally.")
    return d2_code

if __name__ == "__main__":
    request = input("Define the target database system:\n> ")
    run(request)