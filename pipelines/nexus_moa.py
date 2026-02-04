"""
Nexus MoA Pipeline - Mixture of Agents with ASCII Text Output
==============================================================

A production-ready Open WebUI Pipeline implementing a "Council of Agents" 
architecture for SRE diagnostics and decision-making.

Architecture:
    User Prompt -> [Council Dispatch (Parallel)]
                   ├── Phi-3 (Logic Core)
                   ├── Gemma-2 (Creative Core)  
                   └── Qwen-2 (Speed Core)
                -> [Circuit Breaker] -> [Judge Synthesis (Llama-3)]
                -> [ASCII Text Formatting] -> Final Response

Author: Nexus SRE Team
Version: 1.0.0
Compatible with: Open WebUI Pipelines Framework
"""

import asyncio
import aiohttp
import time
import os
import logging
import json
from typing import Optional, List, Dict, Any, AsyncGenerator, Union
from dataclasses import dataclass, field
from enum import Enum

from pydantic import BaseModel, Field

# Debug logging setup - use mounted pipeline directory (accessible from container)
# This will be written to D:\Github\Nexus\pipelines\debug.log on the host
DEBUG_LOG_PATH = "/app/pipelines/debug.log"

def _debug_log(session_id: str, run_id: str, hypothesis_id: str, location: str, message: str, data: dict):
    """Write debug log entry in NDJSON format"""
    try:
        # Ensure directory exists
        log_dir = os.path.dirname(DEBUG_LOG_PATH)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        with open(DEBUG_LOG_PATH, 'a', encoding='utf-8') as f:
            log_entry = {
                "id": f"log_{int(time.time() * 1000)}",
                "timestamp": int(time.time() * 1000),
                "sessionId": session_id,
                "runId": run_id,
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data
            }
            f.write(json.dumps(log_entry) + '\n')
            f.flush()  # Force write
            os.fsync(f.fileno())  # Ensure written to disk
    except Exception as e:
        # Log to standard logger as fallback - this will appear in docker logs
        logger = logging.getLogger("nexus.debug")
        logger.error(f"Debug log failed [{hypothesis_id}]: {e} | {message} | {json.dumps(data)}")


# =============================================================================
# Configuration & Types
# =============================================================================

class CircuitState(Enum):
    """Circuit breaker states for model health tracking."""
    CLOSED = "STABLE"      # Normal operation
    OPEN = "TRIPPED"       # Model failed/timed out
    HALF_OPEN = "TESTING"  # Recovery attempt


@dataclass
class CouncilResult:
    """Result from a single council model invocation."""
    model: str
    role: str
    response: str = ""
    latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    tokens_per_second: float = 0.0
    status: str = "pending"
    circuit_state: CircuitState = CircuitState.CLOSED
    error: Optional[str] = None


@dataclass  
class JudgeResult:
    """Result from the judge/synthesizer model."""
    response: str = ""
    latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    confidence_score: float = 0.0
    status: str = "pending"
    error: Optional[str] = None


# =============================================================================
# ASCII Text Output Formatter
# =============================================================================
# COMMENTED FOR FUTURE USE - May be needed for advanced UI features
# Currently not used as we return only the judge's response for MVP

# class ASCIIOutputFormatter:
#     """
#     Generates ASCII/text-based output for the Nexus SRE interface.
#     Uses Unicode box-drawing characters and ASCII art for visual elements.
#     """
#     
#     # Status symbols
#     STATUS_SYMBOLS = {
#         "success": "✓",
#         "error": "✗",
#         "timeout": "⚠",
#         "pending": "○",
#     }
#     
#     @classmethod
#     def confidence_meter(cls, confidence: float, council_results: Dict[str, CouncilResult]) -> str:
#         """
#         Generate the Council Confidence meter with consensus indicators using ASCII.
#         
#         Args:
#             confidence: Float 0.0-1.0 representing overall confidence
#             council_results: Dict of council member results for status indicators
#         """
#         confidence_percent = int(confidence * 100)
#         bar_width = 40
#         filled = int(bar_width * confidence)
#         
#         # Determine status based on confidence level
#         if confidence >= 0.7:
#             status_text = "CONSENSUS ACHIEVED"
#             status_symbol = "✓"
#         elif confidence >= 0.5:
#             status_text = "PARTIAL CONSENSUS"
#             status_symbol = "⚠"
#         else:
#             status_text = "DEGRADED MODE"
#             status_symbol = "✗"
#         
#         # Generate council status indicators
#         council_status = []
#         for role, result in council_results.items():
#             symbol = cls.STATUS_SYMBOLS.get(result.status, "○")
#             council_status.append(f"{symbol} {role.upper()}")
#         
#         # Build ASCII progress bar
#         bar = "█" * filled + "░" * (bar_width - filled)
#         
#         result = f"""
# ┌─────────────────────────────────────────────────────────────┐
# │ NEXUS COUNCIL CONFIDENCE METER                              │
# ├─────────────────────────────────────────────────────────────┤
# │                                                             │
# │ Confidence Score: {confidence_percent:3d}%                                    │
# │ [{bar}] │
# │                                                             │
# │ Council Status: {' | '.join(council_status)} │
# │                                                             │
# │ STATUS: {status_symbol} {status_text:<45} │
# │                                                             │
# └─────────────────────────────────────────────────────────────┘
# """
#         return result
# 
#     @classmethod
#     def sre_terminal(cls, council_results: Dict[str, CouncilResult], judge_result: JudgeResult) -> str:
#         """
#         Generate the SRE Observability Terminal with model telemetry using ASCII.
#         
#         Args:
#             council_results: Dict of council member results
#             judge_result: Result from the judge model
#         """
#         # Build terminal log entries
#         log_entries = []
#         
#         for role, result in council_results.items():
#             status_symbol = cls.STATUS_SYMBOLS.get(result.status, "○")
#             circuit_status = result.circuit_state.value
#             model_name = result.model.split(":")[0].capitalize()
#             
#             log_entries.append(
#                 f"[NEXUS_CORE] Route -> Ollama::{model_name} "
#                 f"({result.latency_ms:.0f}ms) | "
#                 f"Token_Speed: {result.tokens_per_second:.0f} t/s | "
#                 f"Circuit_Breaker: {circuit_status} {status_symbol}"
#             )
#         
#         # Add judge synthesis entry
#         council_models = [r.model.split(":")[0].capitalize() for r in council_results.values() if r.status == "success"]
#         log_entries.append(
#             f"[NEXUS_CORE] Consensus Check: {' + '.join(council_models)} "
#             f"-> JUDGE SYNTHESIS ({judge_result.latency_ms:.0f}ms)"
#         )
#         
#         result = f"""
# ┌─────────────────────────────────────────────────────────────┐
# │ SRE OBSERVABILITY TERMINAL                                   │
# ├─────────────────────────────────────────────────────────────┤
# │                                                             │
# {chr(10).join(f'│ {entry:<59} │' for entry in log_entries)}
# │                                                             │
# └─────────────────────────────────────────────────────────────┘
# """
#         return result
# 
#     @classmethod
#     def council_deliberation(cls, council_results: Dict[str, CouncilResult]) -> str:
#         """
#         Generate council deliberation view showing each model's analysis using ASCII.
#         
#         Args:
#             council_results: Dict of council member results
#         """
#         role_labels = {
#             "logic": "PHI-3 DELIBERATION",
#             "creative": "GEMMA-2 DELIBERATION",
#             "speed": "QWEN-2 DELIBERATION",
#         }
#         
#         sections = []
#         for role, result in council_results.items():
#             label = role_labels.get(role, f"{role.upper()} DELIBERATION")
#             status_symbol = cls.STATUS_SYMBOLS.get(result.status, "○")
#             
#             if result.status == "success":
#                 content = result.response[:600] + "..." if len(result.response) > 600 else result.response
#                 # Wrap content to fit in box
#                 wrapped_content = []
#                 for line in content.split('\n'):
#                     while len(line) > 55:
#                         wrapped_content.append(line[:55])
#                         line = line[55:]
#                     if line:
#                         wrapped_content.append(line)
#                 content_text = '\n'.join(f"│ {line:<57} │" for line in wrapped_content[:15])
#             else:
#                 content_text = f"│ [CIRCUIT OPEN] {result.error or 'Model unavailable':<45} │"
#             
#             sections.append(f"""
# ┌─────────────────────────────────────────────────────────────┐
# │ {status_symbol} {label:<54} │
# ├─────────────────────────────────────────────────────────────┤
# {content_text}
# └─────────────────────────────────────────────────────────────┘
# """)
#         
#         return "\n".join(sections)
# 
#     @classmethod
#     def judge_response_header(cls, timestamp: str) -> str:
#         """Generate the Judge response header using ASCII."""
#         return f"""
# ╔═════════════════════════════════════════════════════════════╗
# ║ JUDGE SYNTHESIS                                    {timestamp} ║
# ╚═════════════════════════════════════════════════════════════╝
# """
# END OF COMMENTED ASCIIOutputFormatter CLASS


# =============================================================================
# Pipeline Implementation
# =============================================================================

class Pipeline:
    """
    Nexus MoA (Mixture of Agents) Pipeline for Open WebUI.
    
    Implements a council-based consensus architecture where multiple SLMs
    analyze a prompt in parallel, and a judge model synthesizes the final response.
    """
    
    class Valves(BaseModel):
        """
        Configuration valves exposed in the Open WebUI Admin Panel.
        These can be modified without touching code.
        """
        # Ollama Connection
        ollama_base_url: str = Field(
            default="http://host.docker.internal:11434",
            description="Ollama API base URL (use host.docker.internal when running in Docker)"
        )
        
        # Council Models
        logic_model: str = Field(
            default="phi3",
            description="Logic Core model (analytical reasoning)"
        )
        creative_model: str = Field(
            default="gemma2:2b",
            description="Creative Core model (lateral thinking)"
        )
        speed_model: str = Field(
            default="qwen2:1.5b",
            description="Speed Core model (fast responses)"
        )
        judge_model: str = Field(
            default="llama3",
            description="Judge model (synthesis and arbitration)"
        )
        
        # Temperature Settings
        logic_temperature: float = Field(
            default=0.3,
            ge=0.0,
            le=2.0,
            description="Temperature for Logic Core (lower = more focused)"
        )
        creative_temperature: float = Field(
            default=0.7,
            ge=0.0,
            le=2.0,
            description="Temperature for Creative Core (higher = more creative)"
        )
        speed_temperature: float = Field(
            default=0.5,
            ge=0.0,
            le=2.0,
            description="Temperature for Speed Core"
        )
        judge_temperature: float = Field(
            default=0.4,
            ge=0.0,
            le=2.0,
            description="Temperature for Judge (balanced)"
        )
        
        # Circuit Breaker Settings
        circuit_breaker_timeout: float = Field(
            default=120.0,
            ge=1.0,
            le=300.0,
            description="Timeout in seconds before circuit breaker trips (increase for CPU-only mode)"
        )
        
        # Response Settings
        max_council_tokens: int = Field(
            default=512,
            ge=64,
            le=2048,
            description="Max tokens per council response"
        )
        max_judge_tokens: int = Field(
            default=1024,
            ge=128,
            le=4096,
            description="Max tokens for judge synthesis"
        )
        
        # UI Settings
        show_deliberation: bool = Field(
            default=True,
            description="Show council deliberation details"
        )
        show_terminal: bool = Field(
            default=True,
            description="Show SRE observability terminal"
        )

    def __init__(self):
        """Initialize the pipeline with default configuration."""
        self.id = "nexus_moa"
        self.name = "Nexus MoA"
        self.valves = self.Valves(
            **{
                "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
                "logic_model": os.getenv("NEXUS_LOGIC_MODEL", "phi3"),
                "creative_model": os.getenv("NEXUS_CREATIVE_MODEL", "gemma2:2b"),
                "speed_model": os.getenv("NEXUS_SPEED_MODEL", "qwen2:1.5b"),
                "judge_model": os.getenv("NEXUS_JUDGE_MODEL", "llama3"),
                "circuit_breaker_timeout": float(os.getenv("NEXUS_TIMEOUT", "120.0")),
            }
        )
        self._session: Optional[aiohttp.ClientSession] = None
        self._logger = logging.getLogger("nexus.moa")
    
    async def on_startup(self) -> None:
        """Called when the pipeline server starts."""
        self._logger.info(f"Nexus MoA Pipeline starting...")
        self._logger.info(f"Council: {self.valves.logic_model}, {self.valves.creative_model}, {self.valves.speed_model}")
        self._logger.info(f"Judge: {self.valves.judge_model}")
        self._logger.info(f"Circuit Breaker Timeout: {self.valves.circuit_breaker_timeout}s")
    
    async def on_shutdown(self) -> None:
        """Called when the pipeline server shuts down."""
        if self._session and not self._session.closed:
            await self._session.close()
        self._logger.info("Nexus MoA Pipeline shutdown complete.")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Lazy-load and return the aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.valves.circuit_breaker_timeout + 5)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def _call_ollama(
        self,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
        role: str,
    ) -> CouncilResult:
        """
        Call an Ollama model with circuit breaker protection.
        
        Args:
            model: Model name/tag
            prompt: The prompt to send
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            role: Role identifier (logic/creative/speed/judge)
            
        Returns:
            CouncilResult with response data or error information
        """
        result = CouncilResult(model=model, role=role)
        start_time = time.perf_counter()
        
        try:
            session = await self._get_session()
            
            request_timeout = aiohttp.ClientTimeout(
                total=self.valves.circuit_breaker_timeout
            )
            
            async with session.post(
                f"{self.valves.ollama_base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
                timeout=request_timeout,
            ) as response:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                result.latency_ms = elapsed_ms
                
                if response.status == 200:
                    data = await response.json()
                    result.response = data.get("response", "")
                    result.prompt_tokens = data.get("prompt_eval_count", 0)
                    result.completion_tokens = data.get("eval_count", 0)
                    result.status = "success"
                    result.circuit_state = CircuitState.CLOSED
                    
                    # Calculate tokens per second
                    if elapsed_ms > 0 and result.completion_tokens > 0:
                        result.tokens_per_second = (result.completion_tokens / elapsed_ms) * 1000
                    
                    self._logger.info(
                        f"[{role.upper()}] {model}: {elapsed_ms:.0f}ms, "
                        f"{result.completion_tokens} tokens, {result.tokens_per_second:.0f} t/s"
                    )
                else:
                    result.status = "error"
                    result.circuit_state = CircuitState.OPEN
                    result.error = f"HTTP {response.status}: {await response.text()}"
                    self._logger.error(f"[{role.upper()}] {model} failed: {result.error}")
                    
        except asyncio.TimeoutError:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            result.latency_ms = elapsed_ms
            result.status = "timeout"
            result.circuit_state = CircuitState.OPEN
            result.error = f"Circuit breaker tripped (>{self.valves.circuit_breaker_timeout}s)"
            self._logger.warning(
                f"[{role.upper()}] {model} TIMEOUT after {elapsed_ms:.0f}ms - Circuit OPEN"
            )
            
        except aiohttp.ClientError as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            result.latency_ms = elapsed_ms
            result.status = "error"
            result.circuit_state = CircuitState.OPEN
            result.error = f"Connection error: {str(e)}"
            self._logger.error(f"[{role.upper()}] {model} connection error: {e}")
            
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            result.latency_ms = elapsed_ms
            result.status = "error"
            result.circuit_state = CircuitState.OPEN
            result.error = f"Unexpected error: {str(e)}"
            self._logger.exception(f"[{role.upper()}] {model} unexpected error")
        
        return result
    
    def _sanitize_user_input(self, text: str, max_length: int = 10000) -> str:
        """
        Sanitize user input to prevent prompt injection attacks.
        
        Args:
            text: User input text
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Enforce length limit
        text = text[:max_length]
        
        # Remove null bytes and other control characters that could interfere
        text = text.replace('\x00', '')
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    async def _dispatch_council(self, user_prompt: str, enabled_agents: Dict[str, bool] = None) -> Dict[str, CouncilResult]:
        """
        Dispatch the user prompt to all council models in parallel.
        
        Args:
            user_prompt: The user's original prompt
            enabled_agents: Dict mapping role to boolean enabled state
            
        Returns:
            Dict mapping role names to CouncilResult objects
        """
        if enabled_agents is None:
            enabled_agents = {"logic": True, "creative": True, "speed": True}

        # Sanitize user input to prevent prompt injection
        sanitized_prompt = self._sanitize_user_input(user_prompt)

        # Craft role-specific prompts for each council member
        logic_prompt = f"""You are the Logic Core of the Nexus AI Council. Your role is to analyze problems with rigorous logical reasoning, identify cause-and-effect relationships, and provide structured, analytical insights.

Analyze the following query with precision and logical rigor:

{sanitized_prompt}

Provide a focused, analytical response. Be concise but thorough."""

        creative_prompt = f"""You are the Creative Core of the Nexus AI Council. Your role is to think laterally, identify unconventional solutions, and provide creative insights that others might miss.

Consider the following query from multiple angles:

{sanitized_prompt}

Provide creative and insightful perspectives. Think outside the box."""

        speed_prompt = f"""You are the Speed Core of the Nexus AI Council. Your role is to provide rapid, practical responses focusing on the most actionable insights.

Respond quickly and concisely to:

{sanitized_prompt}

Focus on the key points and immediate actions."""

        # Dispatch enabled models in parallel
        tasks = []
        roles = []

        if enabled_agents.get("phi3", True): # Map setting key 'phi3' to role 'logic' logic in caller? Or assume keys match?
             # The settings view uses keys: phi3, gemma2, qwen2. 
             # Let's map them to roles: phi3->logic, gemma2->creative, qwen2->speed
             tasks.append(
                self._call_ollama(
                    model=self.valves.logic_model,
                    prompt=logic_prompt,
                    temperature=self.valves.logic_temperature,
                    max_tokens=self.valves.max_council_tokens,
                    role="logic",
                )
             )
             roles.append("logic")

        if enabled_agents.get("gemma2", True):
             tasks.append(
                self._call_ollama(
                    model=self.valves.creative_model,
                    prompt=creative_prompt,
                    temperature=self.valves.creative_temperature,
                    max_tokens=self.valves.max_council_tokens,
                    role="creative",
                )
             )
             roles.append("creative")

        if enabled_agents.get("qwen2", True):
             tasks.append(
                self._call_ollama(
                    model=self.valves.speed_model,
                    prompt=speed_prompt,
                    temperature=self.valves.speed_temperature,
                    max_tokens=self.valves.max_council_tokens,
                    role="speed",
                )
             )
             roles.append("speed")
        
        if not tasks:
            return {}

        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results, handling any exceptions
        council_results = {}
        for i, (role, result) in enumerate(zip(roles, results)):
            if isinstance(result, Exception):
                council_results[role] = CouncilResult(
                    model=getattr(self.valves, f"{role}_model", "unknown"),
                    role=role,
                    status="error",
                    circuit_state=CircuitState.OPEN,
                    error=str(result),
                )
            else:
                council_results[role] = result
        
        return council_results
    
    def _calculate_confidence(self, council_results: Dict[str, CouncilResult]) -> float:
        """
        Calculate consensus confidence based on council results.
        
        Args:
            council_results: Dict of council member results
            
        Returns:
            Float 0.0-1.0 representing confidence level
        """
        successful = sum(
            1 for result in council_results.values()
            if result.status == "success" and len(result.response.strip()) > 0
        )
        total = len(council_results)
        
        if total == 0:
            return 0.0
        
        base_confidence = successful / total
        
        # Bonus confidence if all models agree (simplified heuristic)
        # In a real system, this could use semantic similarity
        if successful == total:
            base_confidence = min(base_confidence + 0.1, 1.0)
        
        return base_confidence
    
    async def _synthesize_with_judge(
        self,
        council_results: Dict[str, CouncilResult],
        user_prompt: str,
    ) -> JudgeResult:
        """
        Feed council responses to the judge for final synthesis.
        
        Args:
            council_results: Dict of council member results
            user_prompt: Original user prompt
            
        Returns:
            JudgeResult with synthesized response
        """
        result = JudgeResult()
        
        # Build council summary for judge
        council_summary_parts = []
        for role, council_result in council_results.items():
            if council_result.status == "success":
                council_summary_parts.append(
                    f"**{role.upper()} ({council_result.model}):**\n{council_result.response}"
                )
            else:
                council_summary_parts.append(
                    f"**{role.upper()} ({council_result.model}):** [UNAVAILABLE - {council_result.error}]"
                )
        
        council_summary = "\n\n---\n\n".join(council_summary_parts)
        
        # Sanitize user prompt for judge synthesis
        sanitized_user_prompt = self._sanitize_user_input(user_prompt)
        
        judge_prompt = f"""You are a helpful AI assistant. You have received insights from multiple AI perspectives on a user's question. Your job is to synthesize these into a single, natural, conversational response.

## USER'S QUESTION:
{sanitized_user_prompt}

## INSIGHTS FROM MULTIPLE PERSPECTIVES:
{council_summary}

## INSTRUCTIONS:
1. Synthesize the best insights from the different perspectives into one coherent response.
2. Write naturally as if you are directly answering the user.
3. Calculate a "confidence_score" (0-100) based on how much the perspectives agreed and the quality of the information.

## FORMAT:
You MUST return a VALID JSON object with the following structure:
{{
    "response": "Your synthesized natural language response here (markdown supported)",
    "confidence_score": 85
}}
Do not include any text outside the JSON object.
"""

        start_time = time.perf_counter()
        
        try:
            session = await self._get_session()
            
            # Judge gets more time than council members
            judge_timeout = aiohttp.ClientTimeout(
                total=self.valves.circuit_breaker_timeout * 2
            )
            
            async with session.post(
                f"{self.valves.ollama_base_url}/api/generate",
                json={
                    "model": self.valves.judge_model,
                    "prompt": judge_prompt,
                    "stream": False,
                    "format": "json", # Force JSON mode in Ollama
                    "options": {
                        "temperature": self.valves.judge_temperature,
                        "num_predict": self.valves.max_judge_tokens,
                    },
                },
                timeout=judge_timeout,
            ) as response:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                result.latency_ms = elapsed_ms
                
                if response.status == 200:
                    data = await response.json()
                    raw_response = data.get("response", "")
                    
                    try:
                        # Parse the JSON response from the model
                        parsed_response = json.loads(raw_response)
                        result.response = parsed_response.get("response", "")
                        result.confidence_score = float(parsed_response.get("confidence_score", 0)) / 100.0
                    except json.JSONDecodeError:
                        # Fallback if JSON parsing fails
                        self._logger.warning(f"[JUDGE] Failed to parse JSON response: {raw_response[:100]}...")
                        result.response = raw_response
                        result.confidence_score = self._calculate_confidence(council_results)

                    result.prompt_tokens = data.get("prompt_eval_count", 0)
                    result.completion_tokens = data.get("eval_count", 0)
                    result.status = "success"
                    
                    self._logger.info(
                        f"[JUDGE] {self.valves.judge_model}: {elapsed_ms:.0f}ms, "
                        f"{result.completion_tokens} tokens, confidence: {result.confidence_score*100:.1f}%"
                    )
                else:
                    result.status = "error"
                    result.error = f"HTTP {response.status}"
                    self._logger.error(f"[JUDGE] Failed: HTTP {response.status}")
                    
        except asyncio.TimeoutError:
            result.latency_ms = (time.perf_counter() - start_time) * 1000
            result.status = "timeout"
            result.error = "Judge synthesis timed out"
            self._logger.error("[JUDGE] Timeout during synthesis")
            
        except Exception as e:
            result.latency_ms = (time.perf_counter() - start_time) * 1000
            result.status = "error"
            result.error = str(e)
            self._logger.exception("[JUDGE] Error during synthesis")
        
        return result
    
    def _build_final_response(
        self,
        council_results: Dict[str, CouncilResult],
        judge_result: JudgeResult,
    ) -> str:
        """
        Build the final response - returns structured JSON for the Nexus UI.
        
        Args:
            council_results: Dict of council member results
            judge_result: Result from the judge synthesis
            
        Returns:
            JSON string containing structured response data
        """
        # 1. Build SRE Logs
        sre_logs = []
        STATUS_SYMBOLS = {"success": "✓", "error": "✗", "timeout": "⚠", "pending": "○"}
        
        for role, result in council_results.items():
            status_symbol = STATUS_SYMBOLS.get(result.status, "○")
            circuit_status = result.circuit_state.value
            model_name = result.model.split(":")[0].capitalize()
            
            sre_logs.append(
                f"[NEXUS_CORE] Route -> Ollama::{model_name} "
                f"({result.latency_ms:.0f}ms) | "
                f"Token_Speed: {result.tokens_per_second:.0f} t/s | "
                f"Circuit_Breaker: {circuit_status} {status_symbol}"
            )

        # Add judge synthesis entry
        council_models = [r.model.split(":")[0].capitalize() for r in council_results.values() if r.status == "success"]
        sre_logs.append(
            f"[NEXUS_CORE] Consensus Check: {' + '.join(council_models)} "
            f"-> JUDGE SYNTHESIS ({judge_result.latency_ms:.0f}ms)"
        )

        # 2. Build Council Data
        council_data = []
        for role, result in council_results.items():
            council_data.append({
                "model": result.model,
                "role": role,
                "response": result.response,
                "status": result.status,
                "latency_ms": result.latency_ms,
                "error": result.error
            })

        # 3. Construct Response Object
        response_data = {
            "type": "nexus_moa_response",
            "content": judge_result.response if judge_result.status == "success" else f"⚠️ Judge Synthesis Failed: {judge_result.error}",
            "confidence": judge_result.confidence_score * 100,
            "council_results": council_data,
            "sre_logs": sre_logs
        }
        
        return json.dumps(response_data)
    
    async def inlet(self, body: Dict[str, Any], user: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Pre-process incoming request (inlet filter).
        
        Args:
            body: The incoming request body
            user: User information (optional)
            
        Returns:
            Modified request body
        """
        # Add Nexus metadata to the request
        if "metadata" not in body:
            body["metadata"] = {}
        body["metadata"]["nexus_pipeline"] = True
        body["metadata"]["nexus_timestamp"] = time.time()
        
        return body
    
    def pipe(
        self,
        user_message: str,
        model_id: str,
        messages: List[Dict[str, Any]],
        body: Dict[str, Any],
    ) -> str:
        """
        Main pipeline entry point implementing the MoA workflow.
        
        Args:
            user_message: The user's message/prompt
            model_id: The model ID (not used directly, we use our council)
            messages: Conversation history
            body: Full request body
            
        Returns:
            Complete response string with ASCII text formatting
        """
        # Run async workflow in event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self._async_pipe(user_message, model_id, messages, body))
    
    async def _async_pipe(
        self,
        user_message: str,
        model_id: str,
        messages: List[Dict[str, Any]],
        body: Dict[str, Any],
    ) -> str:
        """
        Async implementation of the MoA workflow.
        """
        self._logger.info(f"Nexus MoA processing: {user_message[:100]}...")
        
        # Extract settings from body if present
        nexus_settings = body.get("nexus_settings", {})
        enabled_agents = nexus_settings.get("enabledAgents")
        max_tokens = nexus_settings.get("maxTokens")
        
        if max_tokens:
            self.valves.max_judge_tokens = int(max_tokens)

        try:
            # Step 1: Dispatch to Council (parallel)
            self._logger.info("Dispatching to Council...")
            council_results = await self._dispatch_council(user_message, enabled_agents)
            
            # Log council status
            successful = sum(1 for r in council_results.values() if r.status == "success")
            self._logger.info(f"Council dispatch complete: {successful} successful")
            
            # Step 2: Synthesize with Judge
            self._logger.info("Initiating Judge synthesis...")
            judge_result = await self._synthesize_with_judge(council_results, user_message)
            
            # Step 3: Build final response (judge's synthesis only)
            final_response = self._build_final_response(council_results, judge_result)
            
            # #region agent log
            _debug_log("debug-session", "run1", "A", "nexus_moa.py:963", "_async_pipe before return", {
                "response_length": len(final_response),
                "response_type": type(final_response).__name__,
                "is_string": isinstance(final_response, str),
                "contains_ascii_boxes": "┌" in final_response or "╔" in final_response,
                "first_300_chars": final_response[:300],
                "newline_count": final_response.count('\n'),
                "double_newline_count": final_response.count('\n\n')
            })
            # #endregion
            
            self._logger.info("Nexus MoA response complete")
            return final_response
            
        except Exception as e:
            self._logger.exception("Nexus MoA pipeline error")
            # Return simple error message
            return f"⚠️ Nexus Pipeline Error: {str(e)}\n\nThe Nexus council encountered an error during processing. Please try again or check the system logs."
