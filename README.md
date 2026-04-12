# 🏛️ Autonomous DB-Architect

> **Academic Note:** *Developed as the first project for **YZV 445E — Artificial Intelligence Project** at **Istanbul Technical University (ITU)**, 2026.*

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![LiteLLM](https://img.shields.io/badge/LLM-LiteLLM-orange)](https://github.com/BerriAI/litellm)

An **autonomous multi-agent AI pipeline** that translates natural-language database requirements into **production-ready SQLite schemas** and **ER diagram visualizations** — with a built-in self-correction loop.

![Workflow Architecture](assets/workflow-graph.svg)

---

## 🚀 How It Works

Instead of relying on a single monolithic prompt, DB-Architect chains four specialized AI agents:

| # | Agent | Role |
|---|-------|------|
| 1 | **Requirements Analyst** | Parses human language into structured JSON entities |
| 2 | **SQL Developer** | Converts JSON into strict SQLite DDL |
| 3 | **DBA Critic** *(Reflection Loop)* | Validates SQL in an in-memory SQLite runtime; if it fails, the Critic agent diagnoses the error and the Developer re-generates — looping until 100% valid |
| 4 | **D2 Designer** | Transforms validated SQL into a d2lang ER diagram |

### The Reflection Pattern

The core innovation is the **Producer-Critic loop**: generated SQL is executed inside an actual SQLite engine. If runtime crashes, a secondary DBA agent reads the raw error, analyzes the root cause, and forces the Developer to fix it — iterating autonomously until fully valid SQL is verified.

---

## 💡 Example Prompts

Check out **[example_prompts.md](example_prompts.md)** for ready-to-use prompts covering e-commerce, hospital, social media, university, HR, hotel, library, and SaaS architectures.

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| LLM Router | [LiteLLM](https://github.com/BerriAI/litellm) — supports OpenAI, Gemini, Anthropic, and 100+ providers |
| Validation | SQLite3 (in-memory runtime) |
| Diagrams | [d2lang](https://d2lang.com) |
| Web UI | FastAPI + Vanilla JS |
| CLI Output | [Rich](https://github.com/Textualize/rich) |

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.10+**
- **d2** — the diagram compiler ([install guide](https://d2lang.com/tour/install))
- An **API key** from OpenAI, Google Gemini, or any LiteLLM-supported provider

### Installation

```bash
# Clone the repository
git clone https://github.com/semihcellk/autonomous-db-architect.git
cd autonomous-db-architect

# Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and insert your API key
OPENAI_API_KEY=sk-your-key-here
MODEL=gpt-4o-mini              # or gemini/gemini-2.0-flash, etc.
```

### Run — CLI Mode

```bash
python main.py
```

You'll get a rich, color-coded terminal interface showing each agent's progress.

### Run — Web UI Mode

```bash
python server.py
```

Opens a browser-based interface at `http://localhost:8000` with:
- Real-time agent pipeline visualization
- Live reflection loop progress
- SQL schema output with copy button
- ER diagram preview (SVG)

---

## 📁 Project Structure

```
autonomous-db-architect/
├── agents/                   # AI agent modules
│   ├── analyst.py            # Requirements Analyst
│   ├── sql_developer.py      # SQL Developer (generate + fix)
│   ├── dba_critic.py         # DBA Critic (reflection feedback)
│   └── d2_designer.py        # D2 Diagram Designer
├── tools/                    # Utility modules
│   ├── llm.py                # LLM calling + fence stripping
│   ├── sqlite_validator.py   # In-memory SQLite DDL validation
│   └── d2_compiler.py        # D2 CLI compilation wrapper
├── static/                   # Web UI frontend
│   ├── index.html
│   ├── style.css
│   └── app.js
├── assets/                   # Documentation assets
│   └── workflow-graph.svg
├── output/                   # Generated schemas & diagrams
├── config.py                 # Centralized configuration
├── pipeline.py               # Main orchestration pipeline
├── main.py                   # CLI entry point
├── server.py                 # Web UI server (FastAPI)
├── example_prompts.md        # Ready-to-use example prompts
├── requirements.txt
├── .env.example
└── LICENSE
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
