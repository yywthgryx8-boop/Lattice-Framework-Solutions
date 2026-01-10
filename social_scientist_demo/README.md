# Social Scientist Demo — Robust Feedback Layer

Self-contained demo of a qualitative feedback mechanism for stabilizing response-mode selection in AI systems.

## Files
- `SocialScientistFeedback.py`: Standalone demo
- `SocialScientistdemo.py`: Long-form narrative file with demo block appended (use standalone for running)

## What It Does
- Maintains association matrix β between invariants (tokens) and response modes
- Scores each response mode by summing weights for active tokens, then normalizes the results
- Picks the highest-scoring mode — ties broken consistently, not randomly
- Updates β via reward signal, clamped to prevent runaway growth
- Logs a warning when it sees tokens that aren't in the β matrix — helps catch config errors
- Does not modify or train any language model

## Quick Start
Run the standalone demo:

```bash
python3 "./SocialScientistFeedback.py"
```

You should see:
- One chosen mode (e.g., `supportive`)
- β snapshot showing updated associations (clamped in-range)

## Customize
Edit `SocialScientistFeedback.py` to change:
- `modes = ["neutral", "supportive", "directive"]`
- `session_tokens = ["overload", "bf_play", "engineering"]`
- Seed β values (search for `demo.beta[...]`)

For stronger defaults, set more initial β entries or adjust `learning_rate`, `clamp_min`, `clamp_max`.

## Notes
- `SocialScientistdemo.py` contains a large narrative transcript with demo block appended (prefer standalone file for now)
- No external dependencies — Python 3.x stdlib only
