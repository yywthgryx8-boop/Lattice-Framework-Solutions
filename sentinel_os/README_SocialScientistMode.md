# Social Scientist Demo — Robust Feedback Layer

- This repository contains a self-contained demonstration of a qualitative feedback mechanism used to stabilize response-mode selection in AI systems.
- This folder includes a minimal, runnable demo of a qualitative feedback layer for mode selection. It’s designed to be recruiter-friendly: simple to run, with clear output.

## Files
- `SocialScientistFeedback.py`: Standalone demo of the feedback layer.
- `SocialScientistdemo.py`: Long-form narrative file; a compact demo block is appended at the end but the file contains non-code text at the top, so use the standalone demo for running.

## What It Does
- Maintains an association matrix β between invariants (tokens) and response modes.
- Scores modes based on active invariants and normalized weights.
- Selects a mode deterministically (stable tie-break).
- Updates β via a reward signal and clamps within bounds to prevent runaway growth.
- Warns when unknown invariants are present (helps debugging configs).
- This demo does not modify or train any language model.

## Quick Start
Run the standalone demo:

```bash
python3 "./SocialScientistFeedback.py"
```

You should see:
- One chosen mode (e.g., `supportive`).
- A β snapshot showing updated associations, clamped in-range.

## Customize
Edit `SocialScientistFeedback.py` to change:
- `modes = ["neutral", "supportive", "directive"]`
- `session_tokens = ["overload", "bf_play", "engineering"]`
- Seed β values (search for `demo.beta[...]`).

To add stronger defaults, set more initial β entries or adjust `learning_rate`, `clamp_min`, `clamp_max`.

## Notes
- `SocialScientistdemo.py` contains a large narrative transcript. Its appended demo block can be invoked with `--demo` once the top content is wrapped or relocated; for now, prefer the standalone file.
- No external dependencies; runs on Python 3.x.
