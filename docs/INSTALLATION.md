# Nexus MoA Pipeline - Installation Guide

> **The Resilient AI Consensus Engine**  
> A Mixture of Agents (MoA) architecture for Site Reliability Engineering diagnostics

---

## Prerequisites

Before installing the Nexus pipeline, ensure you have:

### 1. Ollama Running Locally

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not installed, get it from https://ollama.ai
```

### 2. Required Models Pulled

Pull the four models used by the Nexus Council:

```bash
# Council Members (SLMs - Small Language Models)
ollama pull phi3           # Logic Core - 3.8B params
ollama pull gemma2:2b      # Creative Core - 2B params  
ollama pull qwen2:1.5b     # Speed Core - 1.5B params

# Judge (Synthesizer)
ollama pull llama3         # Judge - 8B params
```

**Note:** These models are optimized for 8GB VRAM (RTX 2080 Max-Q compatible).

### 3. Open WebUI with Pipelines Support

Ensure you have Open WebUI installed with Pipelines enabled:

```bash
# Docker installation (recommended)
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

---

## Installation Methods

### Method A: Direct Pipeline Installation (Recommended)

1. **Locate your Open WebUI pipelines directory:**

   ```bash
   # Linux/macOS
   ~/.local/share/open-webui/pipelines/
   
   # Or if using Docker, the mounted volume location
   # Check your docker-compose.yml or docker run command
   ```

2. **Copy the pipeline file:**

   ```bash
   # Copy nexus_moa.py to the pipelines directory
   cp pipelines/nexus_moa.py ~/.local/share/open-webui/pipelines/
   ```

3. **Install dependencies:**

   ```bash
   # If running Open WebUI locally (not Docker)
   pip install -r requirements.txt
   
   # For Docker, dependencies should be installed in the container
   # or add them to your custom Dockerfile
   ```

4. **Restart Open WebUI to load the pipeline:**

   ```bash
   # Docker
   docker restart open-webui
   
   # Or systemd service
   sudo systemctl restart open-webui
   ```

### Method B: Using Pipelines Container (Isolated)

For production deployments, run pipelines in a separate container:

```bash
# 1. Start the Pipelines container
docker run -d -p 9099:9099 \
  --add-host=host.docker.internal:host-gateway \
  -v ./pipelines:/app/pipelines \
  --name pipelines \
  --restart always \
  ghcr.io/open-webui/pipelines:main

# 2. Copy the pipeline
cp pipelines/nexus_moa.py ./pipelines/

# 3. Connect in Open WebUI Admin Panel:
#    Admin > Settings > Connections
#    Add: http://localhost:9099
```

---

## Configuration

### Admin Panel Configuration

Once the pipeline is loaded, configure it in Open WebUI:

1. Navigate to **Admin Panel** → **Settings** → **Pipelines**
2. Select **"Nexus MoA"** from the pipeline list
3. Configure the Valves:

| Valve | Default | Description |
|-------|---------|-------------|
| `ollama_base_url` | `http://localhost:11434` | Ollama API endpoint |
| `logic_model` | `phi3` | Logic Core model |
| `creative_model` | `gemma2:2b` | Creative Core model |
| `speed_model` | `qwen2:1.5b` | Speed Core model |
| `judge_model` | `llama3` | Judge/Synthesizer model |
| `logic_temperature` | `0.3` | Lower = more focused |
| `creative_temperature` | `0.7` | Higher = more creative |
| `speed_temperature` | `0.5` | Balanced |
| `judge_temperature` | `0.4` | Balanced synthesis |
| `circuit_breaker_timeout` | `10.0` | Seconds before dropping a model |
| `max_council_tokens` | `512` | Max tokens per council response |
| `max_judge_tokens` | `1024` | Max tokens for judge |
| `show_deliberation` | `true` | Show council deliberation panel |
| `show_terminal` | `true` | Show SRE observability terminal |

### Environment Variables (Alternative)

You can also configure via environment variables:

```bash
export OLLAMA_BASE_URL="http://localhost:11434"
export NEXUS_LOGIC_MODEL="phi3"
export NEXUS_CREATIVE_MODEL="gemma2:2b"
export NEXUS_SPEED_MODEL="qwen2:1.5b"
export NEXUS_JUDGE_MODEL="llama3"
export NEXUS_TIMEOUT="10.0"
```

---

## Testing the Installation

### Quick Test Prompt

In Open WebUI, select the Nexus MoA pipeline and send:

```
Diagnose latency spike on Cluster-Alpha. 
Network metrics show 40% packet loss on node-04.
CPU usage is at 92% across segment 3.
```

### Expected Response Structure

You should see:

1. **Confidence Meter** - A styled progress bar showing council consensus (e.g., "92%")
2. **Council Consensus Squares** - 3-4 colored squares indicating which models responded
3. **Judge Response** - The synthesized diagnosis with:
   - Primary Cause
   - Secondary Factors
   - Evidence
   - Recommended Actions
4. **Council Deliberation** (expandable) - Raw responses from each council member
5. **SRE Observability Terminal** (expandable) - Latency and token metrics

### Troubleshooting

**Pipeline not appearing in list:**
```bash
# Check if the file is in the correct location
ls -la ~/.local/share/open-webui/pipelines/nexus_moa.py

# Check Open WebUI logs for loading errors
docker logs open-webui 2>&1 | grep -i pipeline
```

**Ollama connection errors:**
```bash
# Verify Ollama is accessible
curl http://localhost:11434/api/tags

# If using Docker, ensure host.docker.internal is working
# Or use the host IP address directly in ollama_base_url
```

**Models timing out:**
- Increase `circuit_breaker_timeout` in Valves
- Ensure sufficient GPU memory is available
- Check `ollama ps` for running model instances

**HTML not rendering:**
- Ensure Open WebUI version supports HTML in markdown
- Try disabling any content sanitization settings

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER PROMPT                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COUNCIL DISPATCH (Parallel)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   PHI-3     │  │  GEMMA-2    │  │   QWEN-2    │             │
│  │ Logic Core  │  │Creative Core│  │ Speed Core  │             │
│  │   (0.3°)    │  │   (0.7°)    │  │   (0.5°)    │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          │                                      │
│              ┌───────────▼───────────┐                          │
│              │   CIRCUIT BREAKER     │                          │
│              │   (10s timeout)       │                          │
│              └───────────┬───────────┘                          │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    JUDGE SYNTHESIS                               │
│              ┌─────────────────────┐                            │
│              │      LLAMA-3        │                            │
│              │   Judge/Arbiter     │                            │
│              │      (0.4°)         │                            │
│              └──────────┬──────────┘                            │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    UI INJECTION                                  │
│  ┌─────────────────┐ ┌────────────────┐ ┌───────────────────┐  │
│  │Confidence Meter │ │Council Delib.  │ │ SRE Terminal      │  │
│  │(Progress Bar)   │ │(Expandable)    │ │ (Telemetry Logs)  │  │
│  └─────────────────┘ └────────────────┘ └───────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FINAL RESPONSE                                │
│           (HTML-styled markdown with cyberpunk theme)            │
└─────────────────────────────────────────────────────────────────┘
```

---

## UI Color Palette

The Nexus UI uses a cyberpunk-inspired color scheme:

| Element | Color | Hex Code |
|---------|-------|----------|
| Background (Slate) | Dark slate | `#1E293B` |
| Background (Dark) | Near black | `#0F172A` |
| Accent (Cyan) | Neon cyan | `#06B6D4` |
| Accent (Green) | Electric green | `#10B981` |
| Warning (Amber) | Amber | `#FBBF24` |
| Error (Crimson) | Crimson | `#EF4444` |
| Text (Muted) | Slate gray | `#94A3B8` |
| Text (Light) | Light gray | `#E2E8F0` |
| Border | Slate border | `#334155` |

---

## Performance Notes

- **VRAM Usage:** ~6-7GB with all models loaded
- **Typical Response Time:** 15-30 seconds (depends on prompt complexity)
- **Council Dispatch:** Parallel execution reduces total latency
- **Circuit Breaker:** Prevents single model failures from blocking response

---

## License

This pipeline is part of the Nexus SRE Portfolio Project.

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Open WebUI logs for errors
3. Verify Ollama model availability
