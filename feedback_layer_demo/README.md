# Entrainment Feedback Loop Demo

This demo illustrates a simple and stable feedback layer for mode selection based on qualitative invariants. It is specifically built to be recruiter- and manager-readable.

Purpose

Show how an invariant→mode scoring layer can use reward/punishment to elicit a response style.
Update learned associations (β) from qualitative reward.
Clamp β within bounds to prevent runaway weights. β (association weight) is the learned strength between an invariant (token) and a mode.
Provide optional, detailed warnings for misconfigured or unknown invariants.
This pattern generalizes to systems that need predictable response styles, safety-aware routing, or human–AI collaboration workflows.

## Key Features
- Mode scoring: `score_modes(active_tokens, weights)` computes per-mode scores.
- Deterministic selection: `select_mode(...)` picks the best mode with stable tie-breaking.
- Feedback update: `apply_feedback(mode_used, engraved_tokens, reward)` updates β.
- Clamping: β entries are bounded by `clamp_min`/`clamp_max` after each update.
- Visibility: `snapshot_beta()` returns a compact view of learned β.

## Run
This script is self-contained (no external deps). From the Demos folder:

```bash
python3 "./EntrainmentFeedbackLoop.py"
```

Or run with a JSON config:

```bash
python3 "./EntrainmentFeedbackLoop.py" --config "./demo_config.json"
```

You should see output similar to:
- The chosen mode.
- A β snapshot showing clamped updates.
- Any warnings for unknown tokens if `verbose=True`.

## Customize
Open `EntrainmentFeedbackLoop.py` and adjust:
- `modes`: the response styles to consider.
- Initial `beta` seeds: e.g., `beta[("supportive", "overload")] = 0.8`.
- Token set and weights: pass your active invariants and a weight map.
- `learning_rate`, `clamp_min`, `clamp_max`: tune stability vs responsiveness.
- `verbose=True`: prints helpful warnings when tokens lack associations or weights.

### Minimal usage snippet
If you prefer using it programmatically, this pattern matches the demo inside the file:

```python
from EntrainmentFeedbackLoop import FeedbackLayerDemo

modes = ["neutral", "supportive", "directive"]
demo = FeedbackLayerDemo(modes=modes, verbose=True, learning_rate=0.1, clamp_min=-2.0, clamp_max=2.0)

active_tokens = {"overload", "bf_play", "engineering"}
weights = {t: 1.0/len(active_tokens) for t in active_tokens}

# seed associations
demo.beta[("supportive", "overload")] = 0.8
demo.beta[("neutral", "engineering")] = 0.6
demo.beta[("directive", "engineering")] = 0.5

chosen = demo.select_mode(active_tokens=active_tokens, weights=weights)
demo.apply_feedback(mode_used=chosen, engraved_tokens=active_tokens, reward=+1.0)
print(demo.snapshot_beta())
```

### JSON config schema (optional)
The script supports a simple JSON config:

```json
{
	"modes": ["neutral", "supportive", "directive"],
	"tokens": ["overload", "bf_play", "engineering"],
	"beta_seeds": {
		"supportive|overload": 0.8,
		"neutral|engineering": 0.6,
		"directive|engineering": 0.5
	},
	"params": {
		"learning_rate": 0.1,
		"clamp_min": -2.0,
		"clamp_max": 2.0,
		"reward": 1.0
	}
}
```

## Design Notes
- The demo uses a minimal structure to keep the focus on the feedback mechanism.
- Clamping guards against extreme updates that can destabilize selection.
- Deterministic tie-breaking makes results repeatable across runs.

## Related
- See `SocialScientistFeedback.py` for a config-driven variant (`--config` JSON) and a matching `README.md`.

## Why This Matters
- Shows how qualitative signals can be stabilized into deterministic behavior.
- Demonstrates learning without training, memory, or model modification.
- Useful for safety layers, copilots, and adaptive UX systems.
