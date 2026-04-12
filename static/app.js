/**
 * DB-Architect — Frontend Application
 * Connects to the FastAPI SSE endpoint and drives the pipeline UI.
 */

(() => {
    "use strict";

    // ── DOM References ──────────────────────────────────────
    const promptInput     = document.getElementById("prompt-input");
    const runBtn          = document.getElementById("run-btn");
    const exampleBtn      = document.getElementById("example-btn");
    const pipelineSection = document.getElementById("pipeline-section");
    const resultsSection  = document.getElementById("results-section");
    const reflectionLog   = document.getElementById("reflection-log");
    const sqlCode         = document.getElementById("sql-code");
    const d2Code          = document.getElementById("d2-code");
    const svgContainer    = document.getElementById("svg-container");

    const steps     = document.querySelectorAll(".step");
    const connectors = document.querySelectorAll(".step-connector");

    // ── Example Prompts ─────────────────────────────────────
    const EXAMPLES = [
        "I need a database for an e-commerce platform like Amazon. There should be users who can have multiple shipping addresses. Users can place orders. Each order contains multiple order items, and each item references a product. Products belong to categories. We also need to track payments linked to orders, including payment status and payment method, as well as product reviews left by users.",
        "Design a database for a hospital. We have doctors and patients. A doctor has a specialty and a room number. Patients have medical history records. Doctors can schedule appointments with patients. When an appointment occurs, a doctor might write a prescription that contains multiple medications. We also need a billing table to track invoices for each patient's visits.",
        "I want to build a social network. Users have profiles with a bio and avatar. Users can write posts with content and timestamps. Users can follow each other. Posts can have multiple likes and comments from other users. Also, include a notification system where users get notified when someone likes their post or follows them.",
        "Create a course registration system for a university. We have students, professors, and departments. A professor belongs to a department. Professors teach courses. Each course can have multiple prerequisites (other courses). Students enroll in courses and receive grades. The system should also keep track of classrooms where the courses are held, including capacity and building name.",
        "Design an HR system. The company has multiple departments and branch locations. Employees work in a department and report to a manager (who is also an employee). We need to track employee attendance, leave requests (vacation, sick days) including approval status, and monthly payroll/salary slips with deductions and bonuses.",
    ];

    let exampleIndex = 0;

    // ── Event Listeners ─────────────────────────────────────
    runBtn.addEventListener("click", startPipeline);
    exampleBtn.addEventListener("click", () => {
        promptInput.value = EXAMPLES[exampleIndex % EXAMPLES.length];
        exampleIndex++;
        promptInput.focus();
    });

    // Ctrl/Cmd + Enter to run
    promptInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            startPipeline();
        }
    });

    // Tab switching
    document.querySelectorAll(".tab").forEach((tab) => {
        tab.addEventListener("click", () => {
            const target = tab.dataset.tab;
            tab.closest(".result-card").querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
            tab.closest(".result-card").querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
            tab.classList.add("active");
            document.getElementById(target).classList.add("active");
        });
    });

    // Copy buttons
    document.querySelectorAll(".btn-copy").forEach((btn) => {
        btn.addEventListener("click", () => {
            const targetEl = document.getElementById(btn.dataset.target);
            if (!targetEl) return;
            navigator.clipboard.writeText(targetEl.textContent).then(() => {
                btn.textContent = "Copied!";
                btn.classList.add("copied");
                setTimeout(() => {
                    btn.textContent = "Copy";
                    btn.classList.remove("copied");
                }, 2000);
            });
        });
    });

    // ── Pipeline Execution ──────────────────────────────────
    function startPipeline() {
        const prompt = promptInput.value.trim();
        if (!prompt) {
            promptInput.focus();
            return;
        }

        // Reset UI
        resetPipelineUI();
        pipelineSection.classList.remove("hidden");
        resultsSection.classList.add("hidden");
        runBtn.disabled = true;
        runBtn.classList.add("loading");
        runBtn.querySelector(".btn-icon").textContent = "⟳";
        runBtn.querySelector(".btn-label").textContent = "Generating…";

        // Scroll to pipeline
        pipelineSection.scrollIntoView({ behavior: "smooth", block: "start" });

        // Connect SSE
        const url = `/api/run?prompt=${encodeURIComponent(prompt)}`;
        const evtSource = new EventSource(url);

        evtSource.onmessage = (e) => {
            if (e.data === "[DONE]") {
                evtSource.close();
                onPipelineDone();
                return;
            }

            try {
                const msg = JSON.parse(e.data);
                handleEvent(msg.event, msg.data);
            } catch (err) {
                console.warn("SSE parse error:", err, e.data);
            }
        };

        evtSource.onerror = () => {
            evtSource.close();
            onPipelineError("Connection to server lost. Make sure the server is running.");
        };
    }

    // ── Event Handler ───────────────────────────────────────
    let latestResult = null;

    function handleEvent(event, data) {
        switch (event) {
            case "stage":
                handleStage(data);
                break;

            case "reflection":
                handleReflection(data);
                break;

            case "log":
                handleLog(data);
                break;

            case "result":
                latestResult = data;
                break;

            case "error":
                onPipelineError(data.message);
                break;
        }
    }

    function handleStage(data) {
        const { stage, status } = data;
        const step = document.querySelector(`.step[data-stage="${stage}"]`);
        if (!step) return;

        if (status === "running") {
            step.classList.add("active");
            step.classList.remove("done");
        } else if (status === "done") {
            step.classList.remove("active");
            step.classList.add("done");
            // Light up the connector before this step
            lightConnectorBefore(step);
        }
    }

    function handleReflection(data) {
        const entry = document.createElement("div");
        entry.className = `reflection-entry ${data.passed ? "passed" : "failed"}`;
        entry.innerHTML = `
            <span class="icon">${data.passed ? "✅" : "❌"}</span>
            <span>${escapeHtml(data.message)}</span>
        `;
        reflectionLog.appendChild(entry);
    }

    function handleLog(data) {
        const { agent, output } = data;
        if (!output) return;

        // Map agent names to stages
        const stageMap = {
            "Requirements Analyst": "analyst",
            "SQL Developer": "sql_developer",
            "D2 Designer": "d2_designer",
        };

        const stage = stageMap[agent];
        if (!stage) return;

        const step = document.querySelector(`.step[data-stage="${stage}"]`);
        if (!step) return;

        const outputEl = step.querySelector(".step-output");
        if (outputEl) {
            outputEl.textContent = truncate(output, 600);
            outputEl.classList.remove("hidden");
        }
    }

    // ── Pipeline Complete ───────────────────────────────────
    function onPipelineDone() {
        resetButton();

        if (!latestResult) return;

        // Populate results
        sqlCode.textContent = latestResult.sql_ddl || "No SQL generated.";
        d2Code.textContent  = latestResult.d2_code || "No D2 code generated.";

        // Load SVG
        if (latestResult.svg_path) {
            const filename = latestResult.svg_path.split(/[\\/]/).pop();
            fetch(`/api/output/${filename}`)
                .then(r => r.ok ? r.text() : Promise.reject("SVG not found"))
                .then(svg => {
                    svgContainer.innerHTML = svg;
                })
                .catch(() => {
                    svgContainer.innerHTML = '<p class="svg-placeholder">Diagram not available.</p>';
                });
        } else {
            svgContainer.innerHTML = `<p class="svg-placeholder">${latestResult.d2_error || "Diagram not generated."}</p>`;
        }

        resultsSection.classList.remove("hidden");
        resultsSection.classList.add("fade-in");

        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
        }, 200);
    }

    function onPipelineError(message) {
        resetButton();

        // Show error inside pipeline section
        const errorEl = document.createElement("div");
        errorEl.className = "error-banner";
        errorEl.textContent = message;
        pipelineSection.appendChild(errorEl);
    }

    // ── Helpers ──────────────────────────────────────────────
    function resetPipelineUI() {
        steps.forEach(s => {
            s.classList.remove("active", "done");
            const out = s.querySelector(".step-output");
            if (out) { out.textContent = ""; out.classList.add("hidden"); }
        });
        connectors.forEach(c => c.classList.remove("lit"));
        reflectionLog.innerHTML = "";
        latestResult = null;

        // Remove any previous error banners
        pipelineSection.querySelectorAll(".error-banner").forEach(el => el.remove());
    }

    function resetButton() {
        runBtn.disabled = false;
        runBtn.classList.remove("loading");
        runBtn.querySelector(".btn-icon").textContent = "▶";
        runBtn.querySelector(".btn-label").textContent = "Generate Schema";
    }

    function lightConnectorBefore(stepEl) {
        const prev = stepEl.previousElementSibling;
        if (prev && prev.classList.contains("step-connector")) {
            prev.classList.add("lit");
        }
    }

    function truncate(str, max) {
        if (str.length <= max) return str;
        return str.slice(0, max) + "\n… (truncated)";
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }
})();
