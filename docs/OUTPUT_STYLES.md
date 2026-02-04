# Nexus MoA Output Style Options

This document presents 5 different ASCII/text-based output style options for the Nexus MoA pipeline. Each style offers a unique aesthetic while maintaining readability and the SRE monitoring feel.

---

## Style 1: Minimal Terminal

**Complexity:** Simple  
**Aesthetic:** Clean, minimal ASCII with focus on readability

### Characteristics
- Simple progress bars using `=` and `-`
- Basic status indicators (`✓`, `✗`, `⚠`)
- Minimal borders and separators
- Focus on content over visual elements

### Example Output

```
CONFIDENCE SCORE: 85%
[========================================] 85%

Council Status: ✓ LOGIC | ✓ CREATIVE | ✓ SPEED
STATUS: ✓ CONSENSUS ACHIEVED

─────────────────────────────────────────────
JUDGE SYNTHESIS                    14:23:45
─────────────────────────────────────────────

[Main response content here...]

─────────────────────────────────────────────
SRE TERMINAL
─────────────────────────────────────────────
[NEXUS_CORE] Route -> Ollama::Phi3 (234ms) | Token_Speed: 45 t/s | Circuit_Breaker: STABLE ✓
[NEXUS_CORE] Route -> Ollama::Gemma2 (189ms) | Token_Speed: 52 t/s | Circuit_Breaker: STABLE ✓
[NEXUS_CORE] Route -> Ollama::Qwen2 (156ms) | Token_Speed: 67 t/s | Circuit_Breaker: STABLE ✓
[NEXUS_CORE] Consensus Check: Phi3 + Gemma2 + Qwen2 -> JUDGE SYNTHESIS (1234ms)
```

### Use Case
- Quick diagnostics
- When you need fast, scannable information
- Terminal/CLI environments

### Implementation Notes
- Use `=` for filled progress bars, `-` for empty
- Single-line separators with `-`
- Minimal spacing

---

## Style 2: Box Art Terminal

**Complexity:** Medium  
**Aesthetic:** Structured with box-drawing characters

### Characteristics
- Box-drawing characters (┌─┐│└┘) for frames
- Framed sections with clear boundaries
- ASCII progress bars with borders
- Structured, organized layout

### Example Output

```
┌─────────────────────────────────────────────────────────────┐
│ NEXUS COUNCIL CONFIDENCE METER                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Confidence Score: 85%                                       │
│ ┌─────────────────────────────────────────────────────┐   │
│ │████████████████████████████████████░░░░░░░░░░░░░░░░│ 85%│
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
│ Council Status: ✓ LOGIC | ✓ CREATIVE | ✓ SPEED            │
│                                                             │
│ STATUS: ✓ CONSENSUS ACHIEVED                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘

╔═════════════════════════════════════════════════════════════╗
║ JUDGE SYNTHESIS                                   14:23:45 ║
╚═════════════════════════════════════════════════════════════╝

[Main response content here...]

┌─────────────────────────────────────────────────────────────┐
│ SRE OBSERVABILITY TERMINAL                                   │
├─────────────────────────────────────────────────────────────┤
│ [NEXUS_CORE] Route -> Ollama::Phi3 (234ms) | Token_Speed: 45 t/s │
│ [NEXUS_CORE] Route -> Ollama::Gemma2 (189ms) | Token_Speed: 52 t/s │
│ [NEXUS_CORE] Route -> Ollama::Qwen2 (156ms) | Token_Speed: 67 t/s │
│ [NEXUS_CORE] Consensus Check: Phi3 + Gemma2 + Qwen2 -> JUDGE (1234ms) │
└─────────────────────────────────────────────────────────────┘
```

### Use Case
- Professional reports
- When structure and organization are important
- Documentation-style outputs

### Implementation Notes
- Use `┌─┐│└┘` for single-line boxes
- Use `╔═╗║╚╝` for double-line headers
- Consistent padding inside boxes

---

## Style 3: Rich ASCII Dashboard

**Complexity:** Detailed  
**Aesthetic:** Complex ASCII art with visual elements

### Characteristics
- Complex ASCII art elements
- Multiple box-drawing frames
- Visual progress meters with multiple characters
- Detailed status displays
- High information density

### Example Output

```
╔═══════════════════════════════════════════════════════════════╗
║  ████  ████  ████  ████  ████  NEXUS COUNCIL METRICS  ████  ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  CONFIDENCE SCORE: 85%                                        ║
║  ┌───────────────────────────────────────────────────────┐   ║
║  │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░│   ║
║  └───────────────────────────────────────────────────────┘   ║
║                                                               ║
║  COUNCIL STATUS:                                              ║
║  ┌──────────┐  ┌──────────┐  ┌──────────┐                   ║
║  │ ✓ LOGIC  │  │ ✓ CREAT  │  │ ✓ SPEED  │                   ║
║  │   PHI-3  │  │  GEMMA-2 │  │  QWEN-2  │                   ║
║  │  234ms   │  │  189ms   │  │  156ms   │                   ║
║  └──────────┘  └──────────┘  └──────────┘                   ║
║                                                               ║
║  ═══════════════════════════════════════════════════════════  ║
║  STATUS: ✓ CONSENSUS ACHIEVED                                ║
║  ═══════════════════════════════════════════════════════════  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════╗
║  ╦╔╗╦ ╔╗╔ ╦╔╦╗ ╔═╗ ╦═╗ ╔╦╗ ╦ ╔═╗ ╔╦╗ ╦ ╔═╗ ╦═╗              ║
║  ╠╩╗║ ║║║ ║ ║  ╠═╣ ╠╦╝  ║  ║ ╚═╗  ║  ║ ║ ╦ ╠╦╝              ║
║  ╩ ╩╩ ╝╚╝ ╩ ╩  ╩ ╩ ╩╚═  ╩  ╩ ╚═╝  ╩  ╩ ╚═╝ ╩╚═              ║
║                                                               ║
║  Timestamp: 14:23:45                                          ║
╚═══════════════════════════════════════════════════════════════╝

[Main response content here...]

╔═══════════════════════════════════════════════════════════════╗
║  SRE OBSERVABILITY TERMINAL                                    ║
╠═══════════════════════════════════════════════════════════════╣
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │ [NEXUS_CORE] Route -> Ollama::Phi3                      │ ║
║  │   Latency: 234ms | Speed: 45 t/s | Circuit: STABLE ✓   │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │ [NEXUS_CORE] Route -> Ollama::Gemma2                     │ ║
║  │   Latency: 189ms | Speed: 52 t/s | Circuit: STABLE ✓   │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │ [NEXUS_CORE] Consensus -> JUDGE SYNTHESIS (1234ms)     │ ║
║  └─────────────────────────────────────────────────────────┘ ║
╚═══════════════════════════════════════════════════════════════╝
```

### Use Case
- Detailed analysis reports
- When visual impact is important
- Dashboard-style monitoring displays

### Implementation Notes
- Use `▓` and `░` for progress bars
- Multiple nested boxes for hierarchy
- ASCII art headers for sections
- Detailed metrics in sub-boxes

---

## Style 4: SRE Monitoring Style

**Complexity:** Medium-Detailed  
**Aesthetic:** Terminal log aesthetic with structured data

### Characteristics
- Terminal log aesthetic
- Timestamp formatting
- Structured data display
- Metrics tables
- Color-coded text (using markdown or ANSI codes)

### Example Output

```
═══════════════════════════════════════════════════════════════
 NEXUS COUNCIL CONFIDENCE METER
═══════════════════════════════════════════════════════════════
[2026-01-26 14:23:45] Confidence Score: 85%
[2026-01-26 14:23:45] Progress: [████████████████████████████████████░░░░░░░░░░░░░░░░] 85%

[2026-01-26 14:23:45] Council Status:
  LOGIC   : ✓ PHI-3    (234ms, 45 t/s, STABLE)
  CREATIVE: ✓ GEMMA-2  (189ms, 52 t/s, STABLE)
  SPEED   : ✓ QWEN-2   (156ms, 67 t/s, STABLE)

[2026-01-26 14:23:45] STATUS: ✓ CONSENSUS ACHIEVED
═══════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════
 JUDGE SYNTHESIS                                   14:23:45
═══════════════════════════════════════════════════════════════

[Main response content here...]

═══════════════════════════════════════════════════════════════
 SRE OBSERVABILITY TERMINAL
═══════════════════════════════════════════════════════════════
[2026-01-26 14:23:42.123] [NEXUS_CORE] Route -> Ollama::Phi3
[2026-01-26 14:23:42.123]   ├─ Latency: 234ms
[2026-01-26 14:23:42.123]   ├─ Token Speed: 45 t/s
[2026-01-26 14:23:42.123]   └─ Circuit Breaker: STABLE ✓

[2026-01-26 14:23:42.312] [NEXUS_CORE] Route -> Ollama::Gemma2
[2026-01-26 14:23:42.312]   ├─ Latency: 189ms
[2026-01-26 14:23:42.312]   ├─ Token Speed: 52 t/s
[2026-01-26 14:23:42.312]   └─ Circuit Breaker: STABLE ✓

[2026-01-26 14:23:42.468] [NEXUS_CORE] Route -> Ollama::Qwen2
[2026-01-26 14:23:42.468]   ├─ Latency: 156ms
[2026-01-26 14:23:42.468]   ├─ Token Speed: 67 t/s
[2026-01-26 14:23:42.468]   └─ Circuit Breaker: STABLE ✓

[2026-01-26 14:23:43.702] [NEXUS_CORE] Consensus Check
[2026-01-26 14:23:43.702]   ├─ Models: Phi3 + Gemma2 + Qwen2
[2026-01-26 14:23:43.702]   └─ Judge Synthesis: 1234ms
═══════════════════════════════════════════════════════════════
```

### Use Case
- SRE monitoring and diagnostics
- When detailed logging is needed
- Troubleshooting scenarios

### Implementation Notes
- Timestamp every log entry
- Tree structure with `├─` and `└─`
- Structured key-value pairs
- Double-line separators with `═`

---

## Style 5: Hybrid Visual

**Complexity:** Variable  
**Aesthetic:** Combination of ASCII art and structured text

### Characteristics
- Visual elements where appropriate
- Clean text where needed
- Balanced approach
- Mix of simple and detailed sections

### Example Output

```
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║     ████  NEXUS COUNCIL CONFIDENCE  ████            ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝

Confidence Score: 85%
Progress: [████████████████████████████████████░░░░░░░░░░░░░░░░] 85%

Council Status:
  ✓ LOGIC (Phi-3)    - 234ms, 45 t/s, STABLE
  ✓ CREATIVE (Gemma-2) - 189ms, 52 t/s, STABLE
  ✓ SPEED (Qwen-2)   - 156ms, 67 t/s, STABLE

Status: ✓ CONSENSUS ACHIEVED

───────────────────────────────────────────────────────────────
JUDGE SYNTHESIS                                   14:23:45
───────────────────────────────────────────────────────────────

[Main response content here...]

───────────────────────────────────────────────────────────────
SRE TERMINAL
───────────────────────────────────────────────────────────────

┌─ Council Dispatch ─────────────────────────────────────────┐
│ [NEXUS_CORE] Route -> Ollama::Phi3 (234ms) | 45 t/s | ✓   │
│ [NEXUS_CORE] Route -> Ollama::Gemma2 (189ms) | 52 t/s | ✓ │
│ [NEXUS_CORE] Route -> Ollama::Qwen2 (156ms) | 67 t/s | ✓   │
└────────────────────────────────────────────────────────────┘

┌─ Judge Synthesis ──────────────────────────────────────────┐
│ [NEXUS_CORE] Consensus: Phi3 + Gemma2 + Qwen2              │
│ [NEXUS_CORE] Judge Synthesis: 1234ms                        │
└────────────────────────────────────────────────────────────┘
```

### Use Case
- General purpose use
- When you want visual appeal without overwhelming detail
- Balanced readability and aesthetics

### Implementation Notes
- Use visual elements for headers and important sections
- Keep data sections clean and readable
- Mix of box-drawing and simple separators
- Progress bars with `█` and `░`

---

## Comparison Table

| Style | Complexity | Visual Density | Readability | Best For |
|-------|-----------|----------------|-------------|----------|
| Minimal Terminal | Low | Low | High | Quick scans, CLI |
| Box Art Terminal | Medium | Medium | High | Reports, documentation |
| Rich ASCII Dashboard | High | High | Medium | Dashboards, detailed analysis |
| SRE Monitoring Style | Medium | Medium | High | Logs, diagnostics |
| Hybrid Visual | Variable | Variable | High | General purpose |

---

## Implementation Notes

### Current Implementation
The current pipeline uses **Style 2: Box Art Terminal** as the default. This provides a good balance of structure and readability.

### Switching Styles
To switch styles, modify the `ASCIIOutputFormatter` class methods in `pipelines/nexus_moa.py`:
- `confidence_meter()` - Update progress bar and layout
- `sre_terminal()` - Update terminal log format
- `council_deliberation()` - Update deliberation display
- `judge_response_header()` - Update header style

### Unicode Support
All styles use Unicode box-drawing characters. Ensure your terminal/font supports:
- Basic: `─│┌┐└┘├┤┬┴┼`
- Double: `═║╔╗╚╝╠╣╦╩╬`
- Blocks: `█▓▒░`

### Markdown Compatibility
All styles are designed to render correctly in Open WebUI's markdown renderer. Use code blocks (triple backticks) if needed for monospace formatting.

---

## Recommendations

1. **For Development/Debugging:** Use Style 1 (Minimal Terminal) or Style 4 (SRE Monitoring)
2. **For Production/Reports:** Use Style 2 (Box Art Terminal) or Style 5 (Hybrid Visual)
3. **For Dashboards/Displays:** Use Style 3 (Rich ASCII Dashboard)
4. **For General Use:** Use Style 5 (Hybrid Visual) - current default

---

## Customization

You can mix and match elements from different styles:
- Use Style 1's simple progress bars with Style 2's box frames
- Combine Style 4's timestamps with Style 3's visual elements
- Create your own hybrid based on your needs

The key is maintaining consistency within each output section while ensuring overall readability.
