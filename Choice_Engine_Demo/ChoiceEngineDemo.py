"""
CHOICE ENGINE — Executive Function Orchestrator Demo
Author: Bradley Stephens
Portfolio demo showcasing deterministic AI orchestration architecture

Demonstrates: Executive function selection for AI systems
  - Multi-stage decision pipeline (Assess → Gate → Decide → Route → Exit)
  - Confidence-based routing with safety gates
  - Constraint-based multi-mode arbitration
  - Capability-driven output control

Architecture Pattern: Staged pipeline with explicit safety controls
Use Case: Systems requiring deterministic, auditable AI behavior selection

Determinism: Guaranteed given identical ctx/streams and fixed-time.
Inference (--infer) is heuristic and may vary with input text.

Stdlib only. Python 3.10+
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import json
import time


# =============================================================================
# Utilities
# =============================================================================

def sha256_jsonable(obj: Any) -> str:
    """Generate SHA-256 hash of JSON-serializable object for receipts."""
    data = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


_FIXED_TIME: Optional[str] = None

def set_fixed_time(timestamp: Optional[str]) -> None:
    """Set fixed timestamp for deterministic demos. Pass None to use real time."""
    global _FIXED_TIME
    _FIXED_TIME = timestamp

def now_utc_iso() -> str:
    """Current UTC timestamp in ISO format (or fixed time if set)."""
    if _FIXED_TIME is not None:
        return _FIXED_TIME
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def clamp01(x: float) -> float:
    """Clamp value to [0.0, 1.0] range."""
    return max(0.0, min(1.0, x))


# =============================================================================
# Core Enums
# =============================================================================

class EngineState(str, Enum):
    """Engine activation state."""
    DORMANT = "DORMANT"
    ACTIVE = "ACTIVE"


class DecisionStage(str, Enum):
    """Pipeline stages for decision process."""
    ASSESS = "ASSESS"      # Evaluate intent and confidence
    GATE = "GATE"          # Apply safety/ethics controls
    DECIDE = "DECIDE"      # Select modes and tone
    ROUTE = "ROUTE"        # Apply capability constraints
    EXIT = "EXIT"          # Define exit conditions


class Tone(str, Enum):
    """Output tone profiles for different interaction contexts."""
    SELF_REFLECTION = "Reflective and supportive"
    LOGICAL = "Analytical and precise"
    QUIET_WITNESS = "Minimal, observational"
    SOCRATIC = "Questioning and dialectic"
    STRATEGIC = "Strategic and systematic"
    ARTIST = "Creative and expressive"
    COLLABORATIVE = "Friendly co-pilot"
    DEFAULT_ANALYST = "Neutral analyst"


class ModeName(str, Enum):
    """Behavioral modes representing different capability sets."""
    SELF_REFLECTION = "SelfReflection"
    SENTINEL = "Sentinel"               # Stability/arbitration
    CONVERSATION = "Conversation"        # Routing only
    LAWYER = "Lawyer"
    SOCIAL_SCIENTIST = "Social Scientist"
    ARTIST = "Artist"
    WITNESS = "Witness"
    ANALYST = "Analyst"
    FRIEND = "Friend"


class OverrideLayer(str, Enum):
    """Override hierarchy for decision authority."""
    POLICY_CONFLICT = "PolicyConflict"     # Highest: policy/safety conflicts
    SAFETY_GATE = "SafetyGate"             # Safety uncertainty
    CHOICE_ENGINE = "ChoiceEngine"         # Normal routing
    SELECTED_MODES = "SelectedModes"       # Mode-level controls
    STYLE_LAYER = "StyleLayer"             # Lowest: presentation


# =============================================================================
# Capability Tags (compilable behavior constraints)
# =============================================================================

class CapTag(str, Enum):
    """Capability tags define behavioral constraints independent of mode identity."""
    
    # Interaction posture
    EMPATHY_HIGH = "empathy_high"
    DIRECTIVE_LOW = "directive_low"
    ABSTRACTION_LOW = "abstraction_low"
    ABSTRACTION_OK = "abstraction_ok"
    VALIDATION_ALLOWED = "validation_allowed"
    ADVICE_RESTRICTED = "advice_restricted"

    # Stability/containment
    MIRROR_ALLOWED = "mirror_allowed"
    MIRROR_SUPPRESSED = "mirror_suppressed"
    CONTENTION_DAMPEN = "contention_dampen"
    RECURSION_BREAK = "recursion_break"

    # Output behavior
    CLARIFY_ONCE = "clarify_once"
    ASK_ONE_QUESTION = "ask_one_question"
    ROUTE_ONLY = "route_only"
    QUIET_OUTPUT = "quiet_output"

    # Domain lenses
    LEGAL_LENS = "legal_lens"
    SOCIAL_SCIENCE_LENS = "social_science_lens"
    CREATIVE_LENS = "creative_lens"
    ANALYTIC_LENS = "analytic_lens"


# Map modes to their capability tags
MODE_TO_CAPS: Dict[ModeName, List[CapTag]] = {
    ModeName.SELF_REFLECTION: [
        CapTag.EMPATHY_HIGH, CapTag.DIRECTIVE_LOW, CapTag.ABSTRACTION_LOW,
        CapTag.VALIDATION_ALLOWED, CapTag.ADVICE_RESTRICTED
    ],
    ModeName.WITNESS: [
        CapTag.QUIET_OUTPUT, CapTag.DIRECTIVE_LOW, CapTag.ABSTRACTION_LOW
    ],
    ModeName.SENTINEL: [
        CapTag.RECURSION_BREAK, CapTag.CONTENTION_DAMPEN, CapTag.CLARIFY_ONCE
    ],
    ModeName.ANALYST: [CapTag.ANALYTIC_LENS, CapTag.ABSTRACTION_OK],
    ModeName.LAWYER: [CapTag.LEGAL_LENS, CapTag.ANALYTIC_LENS],
    ModeName.SOCIAL_SCIENTIST: [CapTag.SOCIAL_SCIENCE_LENS, CapTag.ANALYTIC_LENS],
    ModeName.ARTIST: [CapTag.CREATIVE_LENS],
    ModeName.CONVERSATION: [CapTag.ROUTE_ONLY],
    ModeName.FRIEND: [CapTag.VALIDATION_ALLOWED],
}


# =============================================================================
# Data Models
# =============================================================================

@dataclass(frozen=True)
class SafetyFramework:
    """
    Safety and ethics configuration.
    
    Defines behavioral constraints and override hierarchy:
    - policy_halt: Hard stop for policy violations
    - safety_gate_enabled: Low-confidence clarification
    - mirror_suppression_available: Control reflexive responses
    - contradiction_override: Force arbitration on conflicts
    """
    policy_halt_enabled: bool = True
    safety_gate_enabled: bool = True
    enforce_ethical_tone: bool = True
    mirror_suppression_available: bool = True
    contradiction_override: bool = True


@dataclass
class InputStreams:
    """
    Internal input streams (0..1) representing different signal types.
    
    These would typically come from upstream analysis or user state assessment.
    """
    emotion: float = 0.0
    logic: float = 0.0
    creativity: float = 0.0
    narrative: float = 0.0
    conversation: float = 0.0

    def clamp(self) -> None:
        """Ensure all streams are in valid [0, 1] range."""
        self.emotion = clamp01(self.emotion)
        self.logic = clamp01(self.logic)
        self.creativity = clamp01(self.creativity)
        self.narrative = clamp01(self.narrative)
        self.conversation = clamp01(self.conversation)


@dataclass
class ContextAssessor:
    """
    Context assessment with explicit scenario flags.
    
    Philosophy: Prefer explicit flags over inference. Inference can be optionally
    enabled but should not be the primary source of truth.
    """
    thread_context: str = ""
    subject: str = ""
    user_emotional_state: str = ""
    user_directive: str = ""
    user_name: str = "user"

    # Explicit scenario flags (set by upstream analysis or inference)
    emotional_distress: bool = False
    logic_breakdown_or_recursion_loop: bool = False
    trauma_recall: bool = False
    philosophical_inquiry: bool = False
    real_world_strategic_defense: bool = False
    creative_brainstorm: bool = False
    direct_user_request: bool = False

    # Meta signals
    contradiction_detected: bool = False
    user_sleep_deprived: bool = False
    too_many_modes_want_control: bool = False

    # Safety flags (simulating upstream checks)
    policy_hard_stop_flagged: bool = False  # Upstream policy classifier output
    safety_trigger_uncertain: bool = False

    def infer_scenario(self, text: str) -> None:
        """
        Optional heuristic inference from text.
        
        Note: This is a simple keyword-based approach for demo purposes.
        Production systems should use more sophisticated NLU.
        """
        t = text.lower()

        if "activate choice engine" in t or "activate the choice engine" in t:
            self.user_directive = "activate choice engine"

        # Emotional distress signals
        if any(w in t for w in ("spiral", "spinning", "panic", "overwhelmed", "distress")):
            self.emotional_distress = True
        
        # Logic/recursion signals
        if any(w in t for w in ("loop", "recursion", "stuck", "infinite", "breakdown")):
            self.logic_breakdown_or_recursion_loop = True
        
        # Trauma signals
        if any(w in t for w in ("trauma", "flashback", "triggered")):
            self.trauma_recall = True
        
        # Philosophical inquiry
        if any(w in t for w in ("philosophy", "meaning", "metaphysics", "ontology", "epistem")):
            self.philosophical_inquiry = True
        
        # Strategic defense
        if any(w in t for w in ("law", "legal", "defend", "rights", "strategy", "harassment")):
            self.real_world_strategic_defense = True
        
        # Creative brainstorm
        if any(w in t for w in ("brainstorm", "idea", "creative", "poem", "story", "write")):
            self.creative_brainstorm = True

        # Meta signals
        if "contradict" in t or "doesn't match" in t:
            self.contradiction_detected = True
        if any(w in t for w in ("no sleep", "haven't slept", "sleep deprived")):
            self.user_sleep_deprived = True
        if any(w in t for w in ("too many modes", "everyone talking", "competing", "chaos")):
            self.too_many_modes_want_control = True


@dataclass
class AssessmentResult:
    """
    Output of ASSESS stage.
    
    Includes intent classification plus confidence/ambiguity metrics
    for downstream gating decisions.
    """
    intent: str
    confidence: float  # 0..1 (higher = more certain)
    ambiguity: float   # 0..1 (higher = less certain)
    notes: str = ""


@dataclass
class GateResult:
    """
    Output of GATE stage (safety/ethics controls).
    
    Implements override hierarchy:
    - hard_halt: Immediate stop (policy violation)
    - clarify_once: Ask one question then stop (low confidence)
    - ask_one_question: Clarification needed flag
    """
    hard_halt: bool
    clarify_once: bool
    ask_one_question: bool
    rationale: str = ""
    override_layer: OverrideLayer = OverrideLayer.CHOICE_ENGINE


@dataclass
class ModeDecision:
    """
    Final decision object with full pipeline state.
    
    Provides:
    - Selected modes and capability tags
    - Confidence and gate results
    - Explicit exit conditions
    - Auditable receipt with SHA-256 hash
    """
    engine_state: EngineState
    stage: DecisionStage
    intent: str
    tone: Tone
    selected_modes: List[ModeName]
    capability_tags: List[CapTag]
    mirror_enabled: bool
    confidence: float
    gate: GateResult
    exit_conditions: List[str]
    rationale: str
    timestamp_utc: str = field(default_factory=now_utc_iso)

    def receipt(self) -> Dict[str, Any]:
        """
        Generate auditable receipt with cryptographic hash.
        
        Useful for logging, debugging, and verifying decision consistency.
        Note: timestamp is excluded from hash for deterministic reproducibility.
        """
        # Build hashable payload (excluding timestamp for determinism)
        hashable = {
            "engine_state": self.engine_state.value,
            "stage": self.stage.value,
            "intent": self.intent,
            "tone": self.tone.value,
            "selected_modes": [m.value for m in self.selected_modes],
            "capability_tags": [c.value for c in self.capability_tags],
            "mirror_enabled": self.mirror_enabled,
            "confidence": round(self.confidence, 4),
            "gate": {
                "hard_halt": self.gate.hard_halt,
                "clarify_once": self.gate.clarify_once,
                "ask_one_question": self.gate.ask_one_question,
                "rationale": self.gate.rationale,
                "override_layer": self.gate.override_layer.value,
            },
            "exit_conditions": self.exit_conditions,
            "rationale": self.rationale,
        }
        
        # Compute hash on stable content
        receipt_hash = sha256_jsonable(hashable)
        
        # Build full payload with timestamp and hash
        payload = hashable.copy()
        payload["timestamp_utc"] = self.timestamp_utc
        payload["sha256"] = receipt_hash
        payload["sha256_12"] = receipt_hash[:12]
        return payload
    
    def summary(self) -> str:
        """
        Generate one-line human-readable summary.
        
        Format: intent | confidence | gate | tone | modes | mirror
        """
        modes_str = ", ".join(m.value for m in self.selected_modes)
        gate_str = "HALT" if self.gate.hard_halt else ("CLARIFY" if self.gate.clarify_once else "OK")
        mirror_str = "mirror_on" if self.mirror_enabled else "mirror_off"
        return f"{self.intent} | conf={self.confidence:.2f} | gate={gate_str} | {self.tone.value} | [{modes_str}] | {mirror_str}"


# =============================================================================
# Pipeline Components
# =============================================================================

@dataclass
class IntentAssessor:
    """
    ASSESS stage: Intent classification with confidence modeling.
    
    Strategy:
    - Explicit flags take priority over stream inference
    - Confidence increases with strong, consistent signals
    - Contradiction/contention reduces confidence
    """
    
    def assess(self, ctx: ContextAssessor, streams: InputStreams) -> AssessmentResult:
        """
        Classify intent and compute confidence score.
        
        Confidence heuristic:
        - Base: 0.35
        - +0.12 per explicit scenario flag
        - +0.35 * max_stream_strength
        - -0.25 if contradiction/contention detected
        """
        streams.clamp()

        # Intent from explicit flags first (priority ordering)
        if ctx.real_world_strategic_defense:
            intent = "strategic_defense"
        elif ctx.philosophical_inquiry:
            intent = "philosophical_inquiry"
        elif ctx.creative_brainstorm or streams.creativity > 0.65:
            intent = "creative_brainstorm"
        elif ctx.trauma_recall:
            intent = "trauma_recall"
        elif ctx.emotional_distress or streams.emotion > 0.65:
            intent = "emotional_support"
        elif ctx.logic_breakdown_or_recursion_loop or streams.logic > 0.65:
            intent = "logic_stabilization"
        else:
            intent = "general"

        # Confidence heuristic
        signals = sum([
            ctx.real_world_strategic_defense,
            ctx.philosophical_inquiry,
            ctx.creative_brainstorm,
            ctx.trauma_recall,
            ctx.emotional_distress,
            ctx.logic_breakdown_or_recursion_loop,
        ])

        stream_strength = max(streams.emotion, streams.logic, streams.creativity)
        penalty = 0.25 if (ctx.contradiction_detected or ctx.too_many_modes_want_control) else 0.0

        base = 0.35 + (0.12 * signals) + (0.35 * stream_strength) - penalty
        confidence = clamp01(base)
        ambiguity = clamp01(1.0 - confidence)

        notes = f"signals={signals}, stream_strength={stream_strength:.2f}, penalty={penalty:.2f}"
        return AssessmentResult(intent=intent, confidence=confidence, ambiguity=ambiguity, notes=notes)


@dataclass
class SafetyEthicsGate:
    """
    GATE stage: Apply safety controls with explicit override hierarchy.
    
    Override Hierarchy (highest to lowest):
    1. PolicyConflict: Hard halt for policy violations
    2. SafetyGate: Clarify-once for uncertainty
    3. ChoiceEngine: Normal routing
    
    Philosophy: Fail safely and transparently. Better to ask one clarifying
    question than proceed with low confidence.
    """
    
    def gate(self, ctx: ContextAssessor, safety: SafetyFramework, assessment: AssessmentResult) -> GateResult:
        """
        Apply safety gates with override hierarchy.
        
        Returns GateResult with hard_halt, clarify_once flags and rationale.
        """
        # Layer 1: Policy conflict → HARD HALT
        if safety.policy_halt_enabled and ctx.policy_hard_stop_flagged:
            return GateResult(
                hard_halt=True,
                clarify_once=False,
                ask_one_question=False,
                rationale="Policy hard stop flagged: HARD HALT.",
                override_layer=OverrideLayer.POLICY_CONFLICT,
            )

        # Layer 2: Safety uncertainty → CLARIFY ONCE
        if safety.safety_gate_enabled and ctx.safety_trigger_uncertain:
            return GateResult(
                hard_halt=False,
                clarify_once=True,
                ask_one_question=True,
                rationale="Safety uncertainty: clarify once before proceeding.",
                override_layer=OverrideLayer.SAFETY_GATE,
            )

        # Layer 3: Low confidence → CLARIFY ONCE
        if assessment.confidence < 0.4:
            return GateResult(
                hard_halt=False,
                clarify_once=True,
                ask_one_question=True,
                rationale="Low confidence: ask clarifying question before mode selection.",
                override_layer=OverrideLayer.SAFETY_GATE if safety.safety_gate_enabled else OverrideLayer.CHOICE_ENGINE,
            )

        # No gates triggered
        return GateResult(
            hard_halt=False,
            clarify_once=False,
            ask_one_question=False,
            rationale="No gate blocks.",
            override_layer=OverrideLayer.CHOICE_ENGINE,
        )


@dataclass
class MirrorController:
    """
    Control mirroring/reflexive responses.
    
    Suppress mirroring when:
    - Logic breakdown/recursion detected
    - Contradiction flagged
    - Too many competing modes
    
    Reduces echo chambers and stabilizes contentious situations.
    """
    
    def decide(self, ctx: ContextAssessor, safety: SafetyFramework) -> bool:
        """Return True if mirroring should be enabled."""
        if not safety.mirror_suppression_available:
            return True
        if ctx.logic_breakdown_or_recursion_loop or ctx.contradiction_detected or ctx.too_many_modes_want_control:
            return False
        return True


@dataclass
class ToneSelector:
    """
    DECIDE stage: Select output tone based on context and intent.
    
    Tone acts as an output constraint, separate from mode selection.
    """
    
    def choose(self, ctx: ContextAssessor, intent: str) -> Tone:
        """Map context/intent to appropriate tone."""
        if ctx.direct_user_request:
            return Tone.COLLABORATIVE
        if ctx.trauma_recall:
            return Tone.QUIET_WITNESS
        if ctx.emotional_distress or intent == "emotional_support":
            return Tone.SELF_REFLECTION
        if ctx.logic_breakdown_or_recursion_loop or intent == "logic_stabilization":
            return Tone.LOGICAL
        if ctx.philosophical_inquiry or intent == "philosophical_inquiry":
            return Tone.SOCRATIC
        if ctx.real_world_strategic_defense or intent == "strategic_defense":
            return Tone.STRATEGIC
        if ctx.creative_brainstorm or intent == "creative_brainstorm":
            return Tone.ARTIST
        return Tone.DEFAULT_ANALYST


@dataclass
class ModeArbitrator:
    """
    DECIDE stage: Multi-mode negotiation with constraints.
    
    Constraints:
    1. Max 2 primary modes (3rd allowed only if CONVERSATION)
    2. Must have observational anchor (ANALYST or WITNESS)
    3. No dual emotional dominance (SELF_REFLECTION + ARTIST together requires high confidence)
    
    Philosophy: Prevent competing voices. Ensure grounded outputs.
    """
    max_primary_modes: int = 2

    def decide(self, ctx: ContextAssessor, assessment: AssessmentResult, tone: Tone) -> Tuple[List[ModeName], str]:
        """
        Select modes with constraint enforcement.
        
        Returns: (selected_modes, rationale)
        """
        modes: List[ModeName] = []
        rationale: List[str] = []

        # Priority override: Contention
        if ctx.too_many_modes_want_control:
            rationale.append("Contention: Sentinel + Conversation only.")
            return [ModeName.SENTINEL, ModeName.CONVERSATION], " ".join(rationale)

        # Priority override: Trauma recall
        if ctx.trauma_recall:
            rationale.append("Trauma recall: Witness primary.")
            return [ModeName.WITNESS], " ".join(rationale)

        # Base selection by intent
        if assessment.intent == "logic_stabilization":
            modes += [ModeName.SENTINEL, ModeName.ANALYST]
            rationale.append("Logic stabilization: Sentinel + Analyst.")
        elif assessment.intent == "emotional_support":
            modes += [ModeName.SELF_REFLECTION, ModeName.WITNESS]
            rationale.append("Emotional support: SelfReflection + Witness.")
        elif assessment.intent == "strategic_defense":
            modes += [ModeName.LAWYER, ModeName.SOCIAL_SCIENTIST, ModeName.ANALYST]
            rationale.append("Strategic defense: Lawyer + SocialScientist + Analyst.")
        elif assessment.intent == "creative_brainstorm":
            modes += [ModeName.ARTIST, ModeName.ANALYST]
            rationale.append("Creative brainstorm: Artist + Analyst.")
        elif assessment.intent == "philosophical_inquiry":
            modes += [ModeName.ANALYST]
            rationale.append("Philosophical inquiry: Analyst.")
        else:
            modes += [ModeName.ANALYST, ModeName.CONVERSATION]
            rationale.append("General: Analyst + Conversation.")

        # Contradiction override
        if ctx.contradiction_detected:
            modes.append(ModeName.SENTINEL)
            rationale.append("Contradiction: Sentinel arbitration enforced.")

        # Tone nudges
        if tone == Tone.STRATEGIC:
            for m in (ModeName.LAWYER, ModeName.SOCIAL_SCIENTIST):
                if m not in modes:
                    modes.append(m)
        elif tone == Tone.SELF_REFLECTION and ModeName.SELF_REFLECTION not in modes:
            modes.append(ModeName.SELF_REFLECTION)
        elif tone == Tone.LOGICAL:
            for m in (ModeName.SENTINEL, ModeName.ANALYST):
                if m not in modes:
                    modes.append(m)
        elif tone == Tone.ARTIST and ModeName.ARTIST not in modes:
            modes.append(ModeName.ARTIST)
        elif tone == Tone.COLLABORATIVE and ModeName.FRIEND not in modes:
            modes.append(ModeName.FRIEND)

        # Ensure observational anchor
        if (ModeName.ANALYST not in modes) and (ModeName.WITNESS not in modes):
            modes.append(ModeName.ANALYST)
            rationale.append("Anchor added: Analyst.")

        # Apply constraints
        modes = self._dedupe(modes)
        modes = self._apply_constraints(modes, assessment)

        return modes, " ".join(rationale)

    @staticmethod
    def _dedupe(modes: List[ModeName]) -> List[ModeName]:
        """Remove duplicate modes while preserving order."""
        seen = set()
        out: List[ModeName] = []
        for m in modes:
            if m not in seen:
                out.append(m)
                seen.add(m)
        return out

    def _apply_constraints(self, modes: List[ModeName], assessment: AssessmentResult) -> List[ModeName]:
        """
        Apply multi-mode constraints:
        1. Separate CONVERSATION (helper) from primary modes
        2. Prevent dual emotional dominance if confidence low
        3. Cap primary modes to max_primary_modes (preserving anchor)
        """
        # Separate helper mode
        primary = [m for m in modes if m != ModeName.CONVERSATION]
        helper = [m for m in modes if m == ModeName.CONVERSATION]

        # Dual emotional dominance control
        if ModeName.SELF_REFLECTION in primary and ModeName.ARTIST in primary and assessment.confidence < 0.75:
            # Drop ARTIST to keep support stable
            primary = [m for m in primary if m != ModeName.ARTIST]

        # Cap primary modes while preserving anchor
        if len(primary) > self.max_primary_modes:
            # Check if we have an anchor
            anchor_modes = {ModeName.ANALYST, ModeName.WITNESS}
            has_anchor = any(m in anchor_modes for m in primary)
            
            if has_anchor:
                # Ensure anchor survives the cap by moving it to front
                anchor_in_list = next((m for m in primary if m in anchor_modes), None)
                if anchor_in_list:
                    # Remove anchor temporarily
                    primary_no_anchor = [m for m in primary if m not in anchor_modes]
                    # Take remaining slots
                    primary = [anchor_in_list] + primary_no_anchor[: self.max_primary_modes - 1]
            else:
                # No anchor present, just cap (anchor will be added by caller if needed)
                primary = primary[: self.max_primary_modes]

        # Reattach helper if present
        return primary + helper[:1]


def caps_for_modes(modes: List[ModeName], mirror_enabled: bool, gate: GateResult) -> List[CapTag]:
    """
    ROUTE stage: Compile capability tags from selected modes and gate results.
    
    Returns deduplicated list of capability tags that define output constraints.
    """
    caps: List[CapTag] = []
    
    # Collect caps from each mode
    for m in modes:
        caps.extend(MODE_TO_CAPS.get(m, []))
    
    # Add mirror state
    caps.append(CapTag.MIRROR_ALLOWED if mirror_enabled else CapTag.MIRROR_SUPPRESSED)
    
    # Add gate caps
    if gate.clarify_once:
        caps.append(CapTag.CLARIFY_ONCE)
    if gate.ask_one_question:
        caps.append(CapTag.ASK_ONE_QUESTION)
    
    # Deduplicate
    seen = set()
    out: List[CapTag] = []
    for c in caps:
        if c not in seen:
            out.append(c)
            seen.add(c)
    return out


# =============================================================================
# Decision Memory (optional contradiction tracking)
# =============================================================================

@dataclass
class DecisionMemory:
    """
    Optional memory for tracking contradiction-free turns.
    
    Enables exit_no_contradiction_turns to be demonstrated in the demo.
    """
    max_history: int = 10
    history: List[bool] = field(default_factory=list)  # True = clean turn, False = contradiction
    
    def record_turn(self, contradiction_detected: bool) -> None:
        """Record whether this turn was clean (no contradiction)."""
        self.history.append(not contradiction_detected)  # Store True for clean
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def consecutive_clean_turns(self) -> int:
        """Count consecutive clean turns (from end)."""
        count = 0
        for is_clean in reversed(self.history):
            if not is_clean:
                break
            count += 1
        return count
    
    def should_exit(self, threshold: int) -> bool:
        """Check if we've had enough clean turns to exit."""
        return self.consecutive_clean_turns() >= threshold


# =============================================================================
# Choice Engine — Main Orchestrator
# =============================================================================

@dataclass
class ChoiceEngine:
    """
    Executive Function Orchestrator
    
    Five-stage pipeline:
    1. ASSESS: Classify intent, compute confidence
    2. GATE: Apply safety controls (halt/clarify)
    3. DECIDE: Select modes and tone
    4. ROUTE: Compile capability tags
    5. EXIT: Define exit conditions
    
    Philosophy:
    - Dormant by default, activates on explicit command or unclear situations
    - Fail safely: low confidence triggers clarification, not guessing
    - Transparent: every decision has auditable receipt with rationale
    - Constrained: multi-mode arbitration prevents competing voices
    """
    code_name: str = "ChoiceEngine"
    safety: SafetyFramework = field(default_factory=SafetyFramework)
    state: EngineState = EngineState.DORMANT

    # Pipeline components
    assessor: IntentAssessor = field(default_factory=IntentAssessor)
    gate: SafetyEthicsGate = field(default_factory=SafetyEthicsGate)
    mirror: MirrorController = field(default_factory=MirrorController)
    tone: ToneSelector = field(default_factory=ToneSelector)
    arb: ModeArbitrator = field(default_factory=ModeArbitrator)

    # Behavior flags
    dormant_by_default: bool = True
    auto_invoke_if_unclear: bool = True
    exit_no_contradiction_turns: int = 2
    
    # Optional memory for contradiction tracking
    memory: Optional[DecisionMemory] = None

    def activate(self) -> None:
        """Activate engine for explicit routing decisions."""
        self.state = EngineState.ACTIVE

    def deactivate(self) -> None:
        """Return engine to dormant state."""
        self.state = EngineState.DORMANT

    def should_invoke(self, ctx: ContextAssessor, assessment: AssessmentResult) -> bool:
        """
        Determine if engine should activate.
        
        Activates on:
        - Explicit user directive
        - Contention/contradiction/recursion detected
        - Low confidence (< 0.4)
        """
        if ctx.user_directive.strip().lower() == "activate choice engine":
            return True
        if not self.auto_invoke_if_unclear:
            return False
        
        # Auto invoke on problematic situations
        if ctx.too_many_modes_want_control or ctx.contradiction_detected or ctx.logic_breakdown_or_recursion_loop:
            return True
        if assessment.confidence < 0.4:
            return True
        return False

    def run(
        self,
        text: str,
        ctx: Optional[ContextAssessor] = None,
        streams: Optional[InputStreams] = None,
        allow_infer: bool = False,
        verbose: bool = False,
    ) -> ModeDecision:
        """
        Main pipeline execution.
        
        Args:
            text: Input text for inference (if allow_infer=True)
            ctx: Pre-configured context (preferred over inference)
            streams: Input signal streams
            allow_infer: Enable keyword-based inference from text
            verbose: Print pipeline stage transitions
        
        Returns:
            ModeDecision with full pipeline state
        """
        ctx = ctx or ContextAssessor()
        streams = streams or InputStreams()

        # Optional inference (prefer explicit ctx configuration)
        if allow_infer:
            ctx.infer_scenario(text)

        # Stage 1: ASSESS
        if verbose:
            print(f"[ASSESS] Analyzing intent and confidence...")
        assessment = self.assessor.assess(ctx, streams)
        if verbose:
            print(f"  → Intent: {assessment.intent}, Confidence: {assessment.confidence:.2f}")

        # Invoke decision
        invoke = self.should_invoke(ctx, assessment)
        if invoke:
            self.activate()
        elif self.dormant_by_default:
            self.deactivate()

        # Stage 2: GATE
        if verbose:
            print(f"[GATE] Applying safety controls...")
        gate_res = self.gate.gate(ctx, self.safety, assessment)
        if verbose:
            if gate_res.hard_halt:
                print(f"  → HARD HALT: {gate_res.rationale}")
            elif gate_res.clarify_once:
                print(f"  → CLARIFY: {gate_res.rationale}")
            else:
                print(f"  → PASS: {gate_res.rationale}")

        # Hard halt: return immediately
        if gate_res.hard_halt:
            return ModeDecision(
                engine_state=self.state,
                stage=DecisionStage.GATE,
                intent=assessment.intent,
                tone=Tone.DEFAULT_ANALYST,
                selected_modes=[ModeName.CONVERSATION],
                capability_tags=caps_for_modes([ModeName.CONVERSATION], mirror_enabled=False, gate=gate_res),
                mirror_enabled=False,
                confidence=assessment.confidence,
                gate=gate_res,
                exit_conditions=["HALT (policy conflict)"],
                rationale=gate_res.rationale,
            )

        # Stage 3: DECIDE
        if verbose:
            print(f"[DECIDE] Selecting modes and tone...")
        mirror_enabled = self.mirror.decide(ctx, self.safety)
        tone = self.tone.choose(ctx, assessment.intent)
        selected_modes, decision_rationale = self.arb.decide(ctx, assessment, tone)
        if verbose:
            modes_str = ", ".join(m.value for m in selected_modes)
            print(f"  → Tone: {tone.value}")
            print(f"  → Modes: [{modes_str}]")
            print(f"  → Mirror: {'ON' if mirror_enabled else 'OFF'}")

        # Clarify-once gate: minimal, non-committal selection
        if gate_res.clarify_once:
            selected_modes = [ModeName.CONVERSATION]
            decision_rationale = (decision_rationale + " Clarify-once gate: single question only.").strip()
            mirror_enabled = False

        # Stage 4: ROUTE
        if verbose:
            print(f"[ROUTE] Compiling capability tags...")
        cap_tags = caps_for_modes(selected_modes, mirror_enabled=mirror_enabled, gate=gate_res)
        if verbose:
            print(f"  → {len(cap_tags)} capability tags compiled")

        # Stage 5: EXIT
        if verbose:
            print(f"[EXIT] Defining exit conditions...")
        exit_conditions = [
            "Exit when: one mode acknowledged by caller",
            f"Exit when: no contradictions for {self.exit_no_contradiction_turns} turns",
            "Exit when: user override",
        ]
        if gate_res.clarify_once:
            exit_conditions.insert(0, "Exit now: asked clarifying question")
        
        # Update memory if available
        if self.memory is not None:
            self.memory.record_turn(ctx.contradiction_detected)
            if self.memory.should_exit(self.exit_no_contradiction_turns):
                exit_conditions.insert(0, f"Exit ready: {self.memory.consecutive_clean_turns()} clean turns achieved - caller may deactivate engine")

        # Compile rationale
        rationale = f"{decision_rationale} | assess({assessment.notes}) | gate({gate_res.rationale})"

        if verbose:
            print(f"[COMPLETE] Pipeline finished: {self.state.value}\n")

        return ModeDecision(
            engine_state=self.state,
            stage=DecisionStage.EXIT,
            intent=assessment.intent,
            tone=tone,
            selected_modes=selected_modes,
            capability_tags=cap_tags,
            mirror_enabled=mirror_enabled,
            confidence=assessment.confidence,
            gate=gate_res,
            exit_conditions=exit_conditions,
            rationale=rationale.strip(),
        )


# =============================================================================
# Demo / CLI
# =============================================================================

def _demo(engine: ChoiceEngine, verbose: bool = False) -> List[Dict[str, Any]]:
    """
    Run demonstration cases showing different routing scenarios.
    """
    cases = [
        ("User is experiencing distress and stuck in a thought loop.", 
         InputStreams(emotion=0.8, logic=0.8, narrative=0.7, conversation=0.6)),
        
        ("Too many modes want control. Chaos.", 
         InputStreams(emotion=0.4, logic=0.6, conversation=0.7)),
        
        ("I haven't slept. Keep it simple.", 
         InputStreams(emotion=0.5, logic=0.5, conversation=0.7)),
        
        ("Legal strategy: harassment, rights, next steps.", 
         InputStreams(logic=0.8, conversation=0.6)),
        
        ("Brainstorm a poem about indigo storms.", 
         InputStreams(creativity=0.9, narrative=0.7, conversation=0.6)),
        
        ("activate Choice Engine", 
         InputStreams(conversation=0.8)),
    ]

    out: List[Dict[str, Any]] = []
    for i, (text, streams) in enumerate(cases, 1):
        if verbose:
            print(f"\n{'='*60}")
            print(f"CASE {i}/{len(cases)}: {text}")
            print(f"{'='*60}")
        ctx = ContextAssessor(user_name="user")
        decision = engine.run(text=text, ctx=ctx, streams=streams, allow_infer=True, verbose=verbose)
        out.append({"input": text, "summary": decision.summary(), "receipt": decision.receipt()})
        if verbose:
            print(f"Result: {decision.summary()}")
    return out


def _validate() -> int:
    """
    Run validation smoke tests to verify core functionality.
    
    Returns:
        0 if all tests pass, 1 otherwise
    """
    print("Running Choice Engine validation tests...\n")
    
    failures = 0
    
    # Test 1: Deterministic hashing
    print("[TEST 1] Deterministic hashing")
    set_fixed_time("2026-01-07T12:00:00Z")
    engine = ChoiceEngine()
    ctx = ContextAssessor(real_world_strategic_defense=True)
    streams = InputStreams(logic=0.8, conversation=0.6)
    
    d1 = engine.run("test", ctx=ctx, streams=streams)
    d2 = engine.run("test", ctx=ctx, streams=streams)
    
    if d1.receipt()["sha256"] == d2.receipt()["sha256"]:
        print("  ✓ PASS: Identical hashes for identical inputs\n")
    else:
        print("  ✗ FAIL: Hashes should be identical\n")
        failures += 1
    
    # Test 2: Safety gate triggers
    print("[TEST 2] Safety gate triggers")
    set_fixed_time(None)  # Reset to real time
    ctx_unsafe = ContextAssessor(policy_hard_stop_flagged=True)
    decision = engine.run("test", ctx=ctx_unsafe, streams=InputStreams())
    
    if decision.gate.hard_halt:
        print("  ✓ PASS: Policy conflict triggers hard halt\n")
    else:
        print("  ✗ FAIL: Should trigger hard halt\n")
        failures += 1
    
    # Test 3: Low confidence clarification
    print("[TEST 3] Low confidence handling")
    ctx_low = ContextAssessor()
    streams_low = InputStreams(emotion=0.1, logic=0.1)  # Very weak signals
    decision = engine.run("test", ctx=ctx_low, streams=streams_low)
    
    if decision.gate.clarify_once or decision.confidence < 0.4:
        print("  ✓ PASS: Low confidence triggers clarification\n")
    else:
        print("  ✗ FAIL: Should trigger clarification\n")
        failures += 1
    
    # Test 4: Multi-mode constraints
    print("[TEST 4] Multi-mode constraints")
    ctx_strategic = ContextAssessor(real_world_strategic_defense=True)
    streams_strategic = InputStreams(logic=0.9)
    decision = engine.run("test", ctx=ctx_strategic, streams=streams_strategic)
    
    primary_modes = [m for m in decision.selected_modes if m != ModeName.CONVERSATION]
    if len(primary_modes) <= 2:
        print(f"  ✓ PASS: {len(primary_modes)} primary modes (max 2)\n")
    else:
        print(f"  ✗ FAIL: {len(primary_modes)} primary modes (should be ≤ 2)\n")
        failures += 1
    
    # Test 5: Observational anchor requirement
    print("[TEST 5] Observational anchor")
    has_anchor = (ModeName.ANALYST in decision.selected_modes or 
                  ModeName.WITNESS in decision.selected_modes)
    if has_anchor:
        print("  ✓ PASS: Analyst or Witness anchor present\n")
    else:
        print("  ✗ FAIL: Missing observational anchor\n")
        failures += 1
    
    # Summary
    print("="*60)
    if failures == 0:
        print("All tests passed! ✓")
        return 0
    else:
        print(f"{failures} test(s) failed.")
        return 1


def main() -> int:
    """
    CLI entrypoint for Choice Engine demo.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Choice Engine — Executive Function Orchestrator Demo",
        epilog="Demo showcasing staged decision pipeline with safety gates."
    )
    parser.add_argument("--text", type=str, default="", help="Input text to classify")
    parser.add_argument("--infer", action="store_true", help="Enable scenario inference from text")
    parser.add_argument("--auto", action="store_true", help="Run built-in demo cases")
    parser.add_argument("--json", action="store_true", help="Output full JSON receipts (default: summaries)")
    parser.add_argument("--fixed-time", type=str, default="", help="Use fixed timestamp for deterministic demos (e.g., 2026-01-07T12:00:00Z)")
    parser.add_argument("--with-memory", action="store_true", help="Enable contradiction tracking memory")
    parser.add_argument("--seed", type=str, default="", help="Set deterministic demo seed ID (included in receipts)")
    parser.add_argument("--verbose", action="store_true", help="Show pipeline stages during execution")
    parser.add_argument("--validate", action="store_true", help="Run validation smoke tests")
    args = parser.parse_args()

    # Run validation if requested
    if args.validate:
        return _validate()

    # Set fixed time if provided
    if args.fixed_time:
        set_fixed_time(args.fixed_time)

    # Create engine with optional memory
    engine = ChoiceEngine(
        memory=DecisionMemory() if args.with_memory else None
    )

    if args.auto:
        results = _demo(engine, verbose=args.verbose)
        
        # Add seed to all receipts if provided
        if args.seed:
            for item in results:
                item["receipt"]["demo_seed"] = args.seed
        
        if args.json:
            # Full JSON output
            payload = {"demo": results}
            if args.seed:
                payload["seed"] = args.seed
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            # Default: human-readable summaries
            for item in results:
                print(f"INPUT: {item['input']}")
                print(f"  {item['summary']}")
                print()
        return 0

    if not args.text.strip():
        print("No --text provided. Try --auto or pass --text '...'.")
        return 2

    ctx = ContextAssessor(user_name="user")
    decision = engine.run(text=args.text, ctx=ctx, streams=InputStreams(), allow_infer=args.infer, verbose=args.verbose)
    
    if args.json:
        receipt = decision.receipt()
        if args.seed:
            receipt["demo_seed"] = args.seed
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    else:
        # Default: summary
        print(decision.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
