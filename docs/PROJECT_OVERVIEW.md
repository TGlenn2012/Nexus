# Nexus: The Resilient AI Consensus Engine — Project Overview

This document explains the Nexus project in plain language: what it is, how it works, how Open WebUI fits in, and how you might use and improve it in the future. It is based on the **Product Requirements Document (PRD)** in `Nexus PRD.rtf` (version 1.0).

---

## 0. At a glance (from the PRD)

- **Role:** SRE portfolio piece (observability, reliability, traffic management).
- **Platform:** Open WebUI (Docker), Ollama (local inference), Pipelines (Python logic).
- **Hardware (reference):** Designed to run on modest GPUs (e.g. 8GB VRAM; PRD mentions RTX 2080 Max-Q).
- **Council models:** Phi-3 (Logic), Gemma 2 (Creative), Qwen 2 (Speed). **Judge:** Llama 3 (Synthesizer).

---

## 1. What Is Nexus?

**Nexus** is a self-hosted AI application that gives you **more reliable answers** by not relying on a single AI model. Instead of asking one “brain,” your question goes to a **small council of different AI models** that each answer in parallel. A separate **judge** model then reads all their answers and produces one clear, synthesized response. Think of it as getting a second (and third, and fourth) opinion before you see the final answer.

- **Self-hosted** means you run it on your own machine or server; your data does not have to leave your environment.
- **Air-gapped** means it can run without internet access once everything is set up, which is important for secure or isolated networks.
- The project is built as an **SRE (Site Reliability Engineering) portfolio piece**, showcasing reliability, observability, and traffic-style routing for AI.

---

## 2. The Big Idea: Mixture of Agents (MoA)

Usually, when you chat with an AI, one model handles your question. If that model is wrong, slow, or down, you get a bad or missing answer.

Nexus uses a **Mixture of Agents (MoA)** design:

1. **Council** — Several smaller, specialized models (the “council”) each get your question and answer at the same time.
2. **Judge** — One larger model (the “judge”) reads all council answers and writes a single, coherent response.
3. **Resilience** — If one council member is slow or fails, the system can still continue with the others (graceful degradation).

So you get:
- **Diversity** — Different “personalities” (logical, creative, fast) in the council.
- **Consensus** — The judge combines the best of each perspective.
- **Reliability** — Less dependence on any single model.

---

## 3. Who Is It For?

- **Primary users:** Site Reliability Engineers and DevOps professionals who want strong, consistent AI help without depending on a single vendor or model.
- **Interview / portfolio:** The project demonstrates skills in system resilience, latency trade-offs, and integrating open-source AI tooling.

---

## 4. How It Works (Simple Flow)

1. You type a message in the Nexus chat interface.
2. The message is sent to **Open WebUI**, which runs a **Nexus pipeline** (a custom processing step).
3. The pipeline sends your message to **three council models** at once (via **Ollama**, running locally):
   - **Phi-3 (Logic)** — Focused on clear, analytical reasoning.
   - **Gemma 2 (Creative)** — More creative and varied angles.
   - **Qwen 2 (Speed)** — Fast, practical answers.
4. Each model answers within a time limit. If one times out, it’s skipped; the rest continue (circuit breaker behavior).
5. All council answers are sent to the **Judge** (Llama 3), which:
   - Synthesizes one answer.
   - Can output a **confidence score** (0–100) based on how much the council agreed.
6. The pipeline returns this structured result (answer + confidence + council details + metrics) to the UI.
7. The **Nexus app** (React front end) shows:
   - The judge’s final answer.
   - A **confidence meter**.
   - **Council deliberation** (each council member’s response, if you want to dig in).
   - An **SRE-style terminal** with latency and token usage.

So: **Your question → Council (parallel) → Judge (synthesis) → One answer + observability.**

---

## 5. Main Parts of the System

| Part | Role in plain language |
|------|------------------------|
| **Nexus App (React)** | The chat UI you see in the browser: sessions, messages, council status, confidence meter, deliberation, and SRE terminal. It talks to Open WebUI’s API. |
| **Open WebUI** | The “host” application. It provides the API, auth, and a way to plug in custom pipelines (like Nexus). Nexus does **not** replace Open WebUI; it extends it. |
| **Nexus Pipeline (Python)** | Custom logic that runs inside Open WebUI’s pipeline system. It receives your message, calls the council models and judge via Ollama, and returns the structured Nexus response. |
| **Ollama** | Runs the actual AI models (Phi-3, Gemma 2, Qwen 2, Llama 3) on your machine. No cloud required. |
| **Docker** | Often used to run Open WebUI and the Pipelines service in containers for easy setup and portability. |

---

## 6. Open WebUI and How Nexus Uses It

### What is Open WebUI?

**Open WebUI** is an open-source web interface for talking to AI models. It supports multiple back ends (including Ollama) and provides:

- User accounts and API keys  
- Chat and model selection  
- **Pipelines** — pluggable Python logic that can change how requests are processed before and after the model runs  

So Open WebUI is both the “front door” (API + optional built-in UI) and the place where **custom behavior** (like Nexus) is attached.

### How Nexus is integrated

- **No forking.** Nexus does not modify Open WebUI’s source code. It uses the **Pipelines** feature.
- **Nexus pipeline:** A single Python pipeline (`nexus_moa.py`) is registered in Open WebUI. When you choose the “Nexus MoA” model in the API (or in a client that uses that model name), Open WebUI runs this pipeline instead of a single direct model call.
- **Pipeline steps:**
  - **Inlet:** Adds Nexus metadata to the request.
  - **Pipe:** Receives the user message, calls the three council models in parallel (with timeouts), then calls the judge, then builds the final JSON (answer, confidence, council results, SRE logs).
- **Nexus React app** calls Open WebUI’s **Chat Completions** API with the Nexus MoA model and optional settings (e.g. which agents are enabled, max tokens). The response is the pipeline’s JSON, which the app parses and displays (confidence, deliberation, terminal).

So: **Open WebUI** = host + API + pipeline runner. **Nexus** = one pipeline + one front end that consumes that API.

---

## 7. Visual Design (Minimalist Neo-Future)

The UI is designed to feel like a **command center** while staying readable:

- **Colors:** Dark slate/charcoal backgrounds; cyan for info, green for healthy/consensus, amber for warnings.
- **Typography:** Sans-serif for chat; monospace for metrics and logs.
- **Elements:** Council header (Phi-3, Gemma-2, Qwen-2 status), confidence meter, expandable council deliberation, and SRE terminal with latency and token stats.

Customization is done via Open WebUI’s admin (e.g. custom CSS) and the Nexus app’s own styles, without forking Open WebUI.

---

## 8. Screenshots and Examples

### Dashboard (Chat) view

The main screen shows the NEXUS branding, system status (e.g. SYSTEM ONLINE), and the Council header (LOGIC / Phi-3, CREATIVE / Gemma-2, SPEED / Qwen-2). Below are session tabs, the message list, and the input box. After a response, the UI shows the judge’s answer plus the confidence meter, council deliberation, and SRE terminal.

![Dashboard – main chat and council status](screenshots/01-dashboard.png)

**Adding screenshots:** Run the app (`cd nexus-app && npm run dev`), open `http://localhost:5173`, then capture the dashboard, Alerts, Agents, and Settings views. Save them as `01-dashboard.png`, `02-alerts.png`, `03-agents.png`, `04-settings.png` in the `docs/screenshots/` folder so they appear above.

### Other views

- **Alerts** — System alerts (e.g. “System initialized successfully”).

![Alerts view](screenshots/02-alerts.png)

- **Agents** — Information about the council agents (Phi-3, Gemma-2, Qwen-2).

![Agents view](screenshots/03-agents.png)

- **Settings** — Toggle which agents are enabled (Phi-3, Gemma-2, Qwen-2) and set max tokens; values are stored in the browser and sent with each request.

![Settings view](screenshots/04-settings.png)

Place the corresponding PNG files in `docs/screenshots/` for the images to display. The project also includes example visuals in the `UI Screens/` folder (e.g. Gemini-generated mockups) for design reference.

---

## 9. Example Use Cases

- **SRE diagnostics:** “We see high CPU and packet loss on node X; what’s the most likely cause and what should we check?”
- **Runbook drafting:** “Turn this incident summary into a short runbook.”
- **Decision support:** “Here are three options for scaling the cache; compare trade-offs.”
- **Learning:** “Explain circuit breakers and how they’re used in this pipeline.”

The council’s mix of logic, creativity, and speed, plus the judge’s synthesis, makes answers more balanced and easier to trust for operational use.

---

## 10. Forward-Thinking and Creative Uses

- **Internal “AI war room”:** Run Nexus on-prem for incidents; multiple perspectives and a confidence score help avoid single-model blind spots.
- **Compliance and air-gapped environments:** Keep all models and data on your side; no data sent to external APIs.
- **Cost and latency experiments:** Swap in different council models or judge, or change timeouts, and compare quality vs. speed and resource use.
- **Teaching and demos:** Show how MoA, circuit breakers, and observability (latency, tokens) work in one place.
- **Multi-region or hybrid:** Run Ollama in different regions or data centers and route council members to different back ends for redundancy or locality.
- **Domain-specific councils:** Add or swap models fine-tuned for security, networking, or your own runbooks, and keep the same judge-and-observe pattern.

---

## 11. Suggested Future Improvements

- **Semantic confidence:** Today, confidence is largely based on “how many council members answered successfully.” Later, add similarity or agreement metrics between council answers to drive a more meaningful confidence score.
- **Streaming:** Stream the judge’s reply (and optionally council replies) so the user sees output as it’s generated.
- **Persistent observability:** Store latency, token usage, and errors in a small database or log sink and add a simple dashboard or export for trend analysis.
- **Configurable council:** Let admins add/remove or replace council models and the judge via the pipeline valves or a small config file without editing pipeline code.
- **Caching:** Cache judge (or full pipeline) responses for repeated or near-identical prompts to reduce load and latency.
- **Stronger error handling:** Clearer user-facing messages when Ollama is down, a model is missing, or the judge returns invalid JSON; optional retries or fallback to a single model.
- **Auth and multi-tenancy:** If Nexus is used by multiple teams, consider per-user or per-team API keys and optional usage or rate limits.
- **Alerts view:** Connect the Alerts view to real pipeline or system events (e.g. circuit breaker trips, timeouts) instead of mock data.
- **Export and audit:** Export chat history and pipeline metrics (tokens, latency, model used) for audit or cost tracking.

---

## 12. Summary

- **Nexus** = multi-model “council + judge” AI that runs on your own infrastructure.
- **Open WebUI** hosts the API and runs the **Nexus pipeline**; the **Nexus React app** is the chat client that displays the judge’s answer, confidence, council details, and SRE-style metrics.
- **Ollama** runs the models locally; **Docker** is commonly used for Open WebUI and Pipelines.
- The design emphasizes **reliability** (circuit breaker, parallel council), **observability** (latency, tokens, confidence), and **extensibility** (pipelines, valves, no forking).

By combining several small models with a judge and clear observability, Nexus is a practical example of resilient, explainable AI for SRE and DevOps workflows, with room to grow in confidence logic, streaming, and operations tooling.
