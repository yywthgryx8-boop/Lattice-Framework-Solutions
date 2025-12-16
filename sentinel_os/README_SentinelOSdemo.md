# SentinelOS Demo — Guard & Archetype Tuner

This demo shows two key pieces: a simple content guard detector and a robust feedback layer for tuning guard modes per archetype.


## Why This Matters
- This pattern mirrors how adaptive systems bias behavior without retraining models.
- 
## Features

### Part 1: Guard Detector
- Toy heuristics for "therapy script" tone, "assistant takeover" patterns, and "ignored user wants."
- Demo thresholds and scoring (not production).
- Returns: ALLOW / SCRUB_AND_WARN / BLOCK_AND_RETRY with explanations.

### Part 2: Archetype Guard Mode Tuner (Feedback Layer)
- Selects a guard strictness mode (e.g., STRICT, LENIENT, BALANCED) based on active drift tokens.
- Updates learned associations (β) via reward signals.
- Clamps β to prevent runaway weights.
- Provides verbose warnings for misconfigured tokens.
- “Archetype” here refers to a named interaction role or policy profile
(e.g., STRICT vs. LENIENT), not a personality model.

## Run

Basic demo (guard detector only):
```bash
python3 "./SentinelOSdemo.py"
```

Output shows the guard decision and demo scores.

With config-driven tuner:
```bash
python3 "./SentinelOSdemo.py" --config "./sentinel_config.json"
```

Tuner output shows:
- Chosen guard mode for the active drift tokens.
- Updated β snapshot (guard mode ← drift token associations).

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
- Adjust detector thresholds (HARD_BLOCK, SOFT_WARN) in the guard logic.
- Change guard modes and drift tokens in the tuner defaults.
- Update β seeds for different archetype→mode associations.
- Tune `learning_rate`, `clamp_min`, `clamp_max` for stability.

## Design Notes

- The guard detector runs always; it's the first checkpoint.
- The tuner is opt-in (only runs with `--config` or explicit mode).
- Clamping prevents extreme updates that destabilize mode selection.
- Verbose mode warns about missing token associations.

## No Dependencies

This script uses only Python stdlib (dataclasses, enum, json, argparse).

## What's Intentionally Missing
- Production thresholds, real invariant vocabularies, and persistence layers are intentionally omitted.”

## Who This Is For

This demo is relevant to:
- Engineers designing safety or governance layers for LLM-based systems
- Teams exploring inference-time control without model retraining
- Researchers studying adaptive guardrails and policy enforcement
- Product designers building controllable AI assistants or copilots

## Example Flow (Conceptual)

1. Candidate output is generated.
2. Guard detector scores the output for known drift patterns.
3. SentinelOS returns a decision:
   - ALLOW
   - SCRUB_AND_WARN
   - BLOCK_AND_RETRY
4. (Optional) Feedback layer updates guard mode bias for future runs.
