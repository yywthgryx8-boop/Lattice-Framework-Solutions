# Choice Engine — Executive Function Orchestrator Demo

**Author:** Bradley Stephens  
**Purpose:** Portfolio demonstration of AI orchestration architecture  
**Category:** AI Systems Design, Executive Function, Deterministic Routing

---

## Overview

This is a deterministic executive function selector for AI systems, an auditable orchestration that routes behavior based on context, confidence (systems' certainty about user intent classification), and safety rules.

**Core idea:** AI systems without explicit behavior orchestration are hard to debug because of the systems' unpredictable behavior. This architecture uses a transparent, staged pipeline that makes explicit decisions with clear rationale and safety gates.

---

## What This Demo Shows

### 1. **Staged Decision Pipeline**
Five-stage architecture that separates concerns:
- **ASSESS**: Intent classification with confidence modeling
- **GATE**: Safety controls and override hierarchy  
- **DECIDE**: Mode selection with multi-mode arbitration
- **ROUTE**: Capability tag compilation
- **EXIT**: Explicit exit condition definition

### 2. **Safety-First Design**
- **Override hierarchy** (Policy > Safety > Engine > Modes > Style)
- **Confidence-based gating** — low confidence triggers clarification, not guessing
- **Hard halt** for policy violations
- **"Clarify-once" pattern** — fails safely by asking one question instead of proceeding with low confidence

### 3. **Constraint-Based Orchestration**
Multi-mode arbitration with explicit constraints:
- Max 2 primary modes (prevents competing voices)
- Required observational anchor (Analyst or Witness — keeps outputs grounded)
- Prevents conflicting emotional modes at low confidence
- Capability tags separate behavior from identity

### 4. **Auditability & Transparency**
Every decision generates a cryptographically-hashed receipt with:
- Selected modes + rationale
- Confidence scores + gate results
- Capability tags
- Exit conditions
- Full pipeline state

---

## Key Technical Concepts

### Capability Tags vs. Mode Identity
Modes aren't personalities that compete for control — they're just bundles of capability tags. Tags like `empathy_high`, `directive_low`, `analytic_lens` are compilable constraints. The mode label (SelfReflection, Analyst, etc.) is just shorthand for which tags get loaded. Makes behavior way more predictable and testable.

### Confidence Modeling
Simple heuristic:
```
confidence = 0.35 + (0.12 × explicit_signals) + (0.35 × stream_strength) - penalty
```
Increases with strong signals, decreases with contradictions/contention. Triggers safety gates when < 0.4.

### Override Hierarchy
Clear authority chain:
1. **PolicyConflict** → Hard halt (highest)
2. **SafetyGate** → Clarify-once
3. **ChoiceEngine** → Normal routing
4. **SelectedModes** → Mode-level constraints
5. **StyleLayer** → Presentation only (lowest)

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
1. **Emotional distress + logic loop** → dual-signal handling
2. **Mode contention** → arbitration (Sentinel + Conversation only)
3. **Sleep deprivation** → abstraction control
4. **Strategic defense** → multi-mode coordination
5. **Creative brainstorm** → creative lens
6. **Explicit activation** → command recognition

### Example Output
```json
{
  "engine_state": "ACTIVE",
  "stage": "EXIT",
  "intent": "emotional_support",
  "tone": "Reflective and supportive",
  "selected_modes": ["SelfReflection", "Witness"],
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
  "rationale": "Emotional support: SelfReflection + Witness. | assess(signals=2, stream_strength=0.80) | gate(No gate blocks.)",
  "sha256_12": "a3f7d9e8c2b1"
}
```

---

## Architecture Highlights

### Why This Matters for AI Ed Tech

1. **Teachability** — clear pipeline stages make decisions transparent
2. **Safety** — explicit gates prevent systems from winging it with low confidence
3. **Debuggability** — auditable receipts for post-hoc analysis
4. **Scalability** — capability tags separate behavior from implementation

### Design Philosophy

- **Fail safely, not smoothly** — low confidence → clarify, don't guess
- **Explicit over implicit** — all constraints/overrides are named and ordered
- **Conservative routing** — prefer minimal mode sets
- **Auditable by design** — every decision has a hash-verifiable receipt

---

## Educational Context

Designed to demonstrate:

### For AI/ML Roles
- System architecture (staged pipelines)
- Safety engineering (gates, confidence modeling)
- Deterministic orchestration
- Test-driven validation

### For Tech Ed Roles
- Clear conceptual separation (assess vs. gate vs. decide)
- Teachable abstractions (capability tags, override hierarchy)
- Debugging-friendly (receipts, rationale tracking)
- Live demo support (--verbose)

### For Product Roles
- User safety prioritization (clarify-once)
- Transparent decisions
- Constraint-based predictability

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

To keep the demo focused:
- Multi-turn state tracking (external session manager handles this)
- Stream computation (assumes upstream analysis provides InputStreams)
- Mode implementation (focuses on selection, not execution)
- Real policy/safety checks (uses boolean flags for simulation)

---

## Questions This Demo Answers

**Q: How do you prevent AI systems from being unpredictable?**  
Explicit constraints, staged pipelines, confidence-based gating.

**Q: How do you make AI decisions auditable?**  
Every decision generates a cryptographically-hashed receipt with full rationale.

**Q: How do you handle low-confidence situations safely?**  
"Clarify-once" pattern — ask one question and stop instead of guessing.

**Q: How do you prevent competing AI voices?**  
Multi-mode arbitration with explicit constraints (max modes, required anchors, dual dominance prevention).

---

## Contact

**Bradley Stephens**  
Targeting roles in: AI Tech Ed, AI/ML Systems, Learning Experience Design

*This demo represents one component of a larger portfolio showcasing different AI capability dimensions. See also: SentinelDemo (guardrail systems), SocialScientistDemo (analytical frameworks).*

---

## License Note

This is a portfolio demonstration. The architecture concepts are educational and freely adaptable. If you'd like to discuss implementation details or extensions, please contact me.
