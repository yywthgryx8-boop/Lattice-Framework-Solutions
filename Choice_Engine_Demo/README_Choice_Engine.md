# Choice Engine — Executive Function Orchestrator Demo

**Author:** Bradley Stephens  
**Purpose:** Portfolio demonstration of AI orchestration architecture  
**Category:** AI Systems Design, Executive Function, Safety Engineering

---

## Overview

This demo shows AI behavior is routed through the use of a constraint-based architecture that is able to route AI behavior based on context and safety requirements.

**Core Concept:** Instead of letting AI systems dynamically "choose" behavior in unpredictable ways, this architecture provides a transparent, staged pipeline that makes explicit decisions with clear rationale and safety gates.

---

## What This Demo Shows

### 1. **Staged Decision Pipeline**
Five-stage architecture that separates concerns and enables debugging:
- **ASSESS**: Intent classification with confidence modeling
- **GATE**: Safety controls and override hierarchy  
- **DECIDE**: Mode selection with multi-mode arbitration
- **ROUTE**: Capability tag compilation
- **EXIT**: Explicit exit condition definition

### 2. **Safety-First Design**
- **Override hierarchy** (Policy > Safety > Engine > Modes > Style)
- **Confidence-based gating** (low confidence triggers clarification, not guessing)
- **Hard halt capabilities** for policy violations
- **"Clarify-once" pattern** that fails safely by asking one question instead of proceeding with uncertainty

### 3. **Constraint-Based Orchestration**
Multi-mode arbitration with explicit constraints:
- Maximum 2 primary modes (prevents competing voices)
- Required observational anchor (ensures grounded outputs)
- Dual emotional dominance prevention (maintains stability)
- Capability tags separate behavior from identity

### 4. **Auditability & Transparency**
Every decision generates a cryptographically-hashed receipt showing:
- Selected modes and rationale
- Confidence scores and gate results
- Capability tags applied
- Exit conditions
- Full decision pipeline state

---

## Key Technical Concepts

### Capability Tags vs. Mode Identity
Instead of treating modes as personalities that "compete," this system uses **capability tags** as compilable constraints. A mode is just a bundle of behavioral capabilities (empathy_high, directive_low, analytic_lens, etc.). This makes behavior predictable and testable.

### Confidence Modeling
Simple but effective heuristic:
```
confidence = 0.35 + (0.12 × explicit_signals) + (0.35 × stream_strength) - penalty
```
- Increases with strong, consistent input signals
- Decreases with contradictions or contention
- Triggers safety gates when < 0.4

### Override Hierarchy
Clear authority chain prevents ambiguity:
1. **PolicyConflict** → Hard halt (highest authority)
2. **SafetyGate** → Clarify-once (uncertainty handling)
3. **ChoiceEngine** → Normal routing
4. **SelectedModes** → Mode-level constraints
5. **StyleLayer** → Presentation only (lowest authority)

---

## Running the Demo

### Basic Usage
```bash
# Run built-in demo cases
python ChoiceEngineDemo.py --auto

# Classify specific input
python ChoiceEngineDemo.py --text "User is experiencing distress" --infer

# Get JSON output only
python ChoiceEngineDemo.py --auto --json

# Show pipeline execution stages (great for demos/teaching)
python ChoiceEngineDemo.py --text "I'm feeling overwhelmed" --infer --verbose

# Run validation smoke tests
python ChoiceEngineDemo.py --validate
```

### Advanced Flags
- `--verbose`: Show pipeline stages during execution (ASSESS → GATE → DECIDE → ROUTE → EXIT)
- `--validate`: Run automated smoke tests for core functionality
- `--fixed-time`: Use fixed timestamp for deterministic demos
- `--with-memory`: Enable contradiction tracking memory
- `--seed`: Add demo seed ID to receipts for audit trails

### Demo Cases Included
1. **Emotional distress + logic loop** → Tests dual-signal handling
2. **Mode contention** → Tests arbitration (Sentinel + Conversation only)
3. **Sleep deprivation** → Tests abstraction control
4. **Strategic defense** → Tests multi-mode coordination
5. **Creative brainstorm** → Tests creative lens activation
6. **Explicit activation** → Tests command recognition

### Example Output
```json
{
  "engine_state": "ACTIVE",
  "stage": "EXIT",
  "intent": "emotional_support",
  "tone": "Compassionate support",
  "selected_modes": ["Therapist", "Witness"],
  "capability_tags": ["empathy_high", "directive_low", "quiet_output", "mirror_suppressed"],
  "confidence": 0.7100,
  "gate": {
    "hard_halt": false,
    "clarify_once": false,
    "override_layer": "ChoiceEngine"
  },
  "exit_conditions": [
    "Exit when: one mode acknowledged by caller",
    "Exit when: no contradictions for 2 turns"
  ],
  "rationale": "Emotional support: Therapist + Witness. | assess(signals=2, stream_strength=0.80) | gate(No gate blocks.)",
  "sha256_12": "a3f7d9e8c2b1"
}
```

---

## Architecture Highlights

### Why This Matters for AI Ed Tech

1. **Teachability**: Clear pipeline stages make the decision process transparent for learners
2. **Safety**: Explicit gates prevent systems from "winging it" with low confidence
3. **Debuggability**: Auditable receipts enable post-hoc analysis of decisions
4. **Scalability**: Capability tags separate behavior from implementation

### Design Philosophy

- **Fail safely, not smoothly**: Low confidence → clarify, don't guess
- **Explicit over implicit**: All constraints and overrides are named and ordered
- **Conservative routing**: Prefer minimal mode sets over complex orchestrations
- **Auditable by design**: Every decision has a hash-verifiable receipt

---

## Educational Context

This demo is designed to showcase:

### For AI/ML Roles
- System architecture design (staged pipelines)
- Safety engineering (gates, halts, confidence modeling)
- Deterministic orchestration patterns
- Test-driven validation (--validate smoke tests)

### For Tech Ed Roles
- Clear conceptual separation (assess vs. gate vs. decide)
- Teachable abstractions (capability tags, override hierarchy)
- Debugging-friendly design (receipts, rationale tracking)
- Live demonstration support (--verbose pipeline visibility)

### For Product Roles
- User safety prioritization (clarify-once pattern)
- Transparent decision-making (full pipeline state)
- Constraint-based predictability (no emergent chaos)

---

## Technical Stack

- **Language**: Python 3.10+
- **Dependencies**: Stdlib only (hashlib, json, dataclasses, enum)
- **Lines of Code**: ~1100 (including docs, demo, and validation tests)
- **Design Pattern**: Pipeline architecture with staged gates

---

## Comparison to Other Approaches

| Approach | Pros | Cons |
|----------|------|------|
| **LLM-based routing** | Flexible, natural language | Unpredictable, hard to audit, expensive |
| **Rule-based systems** | Deterministic, fast | Brittle, hard to extend |
| **This approach** | Deterministic + extensible + auditable | Requires upfront constraint design |

---

## What This Doesn't Show

To keep the demo focused, this excludes:
- Multi-turn state tracking (handled by external session manager)
- Stream computation (assumes upstream analysis provides InputStreams)
- Mode implementation (focuses on *selection* not *execution*)
- Real policy/safety checks (uses boolean flags as simulation)

---

## Questions This Demo Answers

**Q: How do you prevent AI systems from being unpredictable?**  
A: Explicit constraints, staged pipelines, and confidence-based gating.

**Q: How do you make AI decisions auditable?**  
A: Every decision generates a cryptographically-hashed receipt with full rationale.

**Q: How do you handle low-confidence situations safely?**  
A: "Clarify-once" pattern: ask one question and stop, rather than guessing.

**Q: How do you prevent competing AI "voices"?**  
A: Multi-mode arbitration with explicit constraints (max modes, required anchors, dual dominance prevention).

---

## Contact

**Bradley Stephens**  
Targeting roles in: AI Tech Ed, AI/ML Systems, Learning Experience Design

*This demo represents one component of a larger portfolio showcasing different AI capability dimensions. See also: SentinelDemo (guardrail systems), SocialScientistDemo (analytical frameworks).*

---

## License Note

This is a portfolio demonstration. The architecture concepts are educational and freely adaptable. If you'd like to discuss implementation details or extensions, please reach out.
