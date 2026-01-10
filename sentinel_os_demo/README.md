# SentinelOS Demo — Guard & Archetype Tuner

Two pieces: a content guard detector and a feedback layer for tuning guard modes per archetype.


## Why This Matters
Shows how you can bias AI behavior without retraining models — similar to how adaptive systems work in practice. 
## Features

### Part 1: Guard Detector
Detects common AI drift patterns:
- **"Therapy script"** — overly gentle/validating tone when the context doesn't call for it
- **"Assistant takeover"** — AI defaults to bullet points and brief explanations instead of full prose. Makes output look like a PowerPoint presentation. Loses nuance, feels low-effort, and frankly most users don't want to communicate with an AI like they're reading slides.
- **"Ignored user wants"** — AI sticks with its default style despite explicit user direction

Uses demo thresholds and scoring — not production-ready. Returns ALLOW, SCRUB_AND_WARN, or BLOCK_AND_RETRY with explanations.

### Part 2: Archetype Guard Mode Tuner (Feedback Layer)
- Picks guard strictness mode (STRICT, LENIENT, BALANCED) based on active drift tokens
- Updates learned associations (β) using reward signals
- Clamps β to prevent runaway weights
- Warns about misconfigured tokens
- "Archetype" here means a named interaction role or policy profile — not a personality model

## Run

Basic demo (guard detector only):
```bash
python3 "./SentinelOSdemo.py"
```

Shows the guard decision and demo scores.

With config-driven tuner:
```bash
python3 "./SentinelOSdemo.py" --config "./sentinel_config.json"
```

Shows:
- Which guard mode was chosen for active drift tokens
- Updated β snapshot (guard mode ← drift token associations)

## Sample Config

```json
{
  "modes": ["STRICT", "LENIENT", "BALANCED"],
  "tokens": ["therapy-drift", "assistant-takeover", "ignored-wants"],
  "beta_seeds": {
    "STRICT|therapy-drift": 0.9,
    "STRICT|assistant-takeover": 0.9,
    "LENIENT|ignored-wants": -0.5,
    "BALANCED|ignored-wants": 0.3
  },
  "params": {
    "learning_rate": 0.1,
    "clamp_min": -2.0,
    "clamp_max": 2.0,
    "reward": 1.0
  }
}
```

## Customize

Edit `SentinelOSdemo.py`:
- Adjust detector thresholds (HARD_BLOCK, SOFT_WARN) in guard logic
- Change guard modes and drift tokens in tuner defaults
- Update β seeds for different archetype→mode associations
- Tune `learning_rate`, `clamp_min`, `clamp_max` for stability

## Design Notes

- Guard detector always runs — it's the first checkpoint
- Tuner is opt-in (only runs with `--config` or when you explicitly enable it)
- Clamping prevents extreme updates that'd destabilize mode selection
- Verbose mode warns about missing token associations

## No Dependencies

This script uses only Python stdlib (dataclasses, enum, json, argparse).

## What's Intentionally Missing
Production-grade thresholds, real invariant vocabularies, persistence layers.

## Who This Is For

Relevant for:
- Engineers designing safety/governance layers for LLM systems
- Teams controlling AI behavior without model retraining
- Researchers studying adaptive guardrails and policy enforcement
- Product designers building controllable AI assistants

## Example Flow (Conceptual)

1. Candidate output is generated
2. Guard detector scores output for known drift patterns
3. SentinelOS returns decision: ALLOW / SCRUB_AND_WARN / BLOCK_AND_RETRY
4. (Optional) Feedback layer updates guard mode bias for future runs
