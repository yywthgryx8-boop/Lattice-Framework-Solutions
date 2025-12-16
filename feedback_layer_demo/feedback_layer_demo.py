"""
Optional CLI demo:
  - Supports a JSON config via --config with fields:
    {
      "modes": ["neutral", "supportive", "directive"],
      "tokens": ["overload", "bf_play", "engineering"],
      "beta_seeds": { "supportive|overload": 0.8 },
      "params": { "learning_rate": 0.1, "clamp_min": -2.0, "clamp_max": 2.0, "reward": 1.0 }
    }
"""

from typing import Dict, List, Set
import argparse
import json

# Expect FeedbackLayerDemo class to be defined above with:
#   - select_mode(active_tokens: Set[str], weights: Dict[str, float]) -> str
#   - apply_feedback(mode_used: str, engraved_tokens: Set[str], reward: float) -> None
#   - snapshot_beta() -> Dict[str, float]


def _normalized_weights(tokens: List[str]) -> Dict[str, float]:
    if not tokens:
        return {}
    w = 1.0 / float(len(tokens))
    return {t: w for t in tokens}


def _demo_cli():
    ap = argparse.ArgumentParser(description="Entrainment feedback demo with optional JSON config")
    ap.add_argument("--config", help="Path to JSON config with modes, tokens, beta seeds, and params", required=False)
    args = ap.parse_args()

    cfg_modes: List[str] = ["neutral", "supportive", "directive"]
    cfg_tokens: List[str] = ["overload", "bf_play", "engineering"]
    cfg_beta: Dict[str, float] = {"supportive|overload": 0.8, "neutral|engineering": 0.6, "directive|engineering": 0.5}
    params = {"learning_rate": 0.1, "clamp_min": -2.0, "clamp_max": 2.0, "reward": 1.0}

    if args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            data = json.load(f)
        cfg_modes = data.get("modes", cfg_modes)
        cfg_tokens = data.get("tokens", cfg_tokens)
        cfg_beta = data.get("beta_seeds", cfg_beta)
        p = data.get("params", {})
        params["learning_rate"] = float(p.get("learning_rate", params["learning_rate"]))
        params["clamp_min"] = float(p.get("clamp_min", params["clamp_min"]))
        params["clamp_max"] = float(p.get("clamp_max", params["clamp_max"]))
        params["reward"] = float(p.get("reward", params["reward"]))

    # Instantiate the demo layer
    demo = FeedbackLayerDemo(
        modes=cfg_modes,
        verbose=True,
        learning_rate=params["learning_rate"],
        clamp_min=params["clamp_min"],
        clamp_max=params["clamp_max"],
    )

    # Seed beta
    for k, v in cfg_beta.items():
        try:
            m, t = k.split("|", 1)
        except ValueError:
            print(f"[warn] bad beta seed key '{k}'; expected 'mode|token'")
            continue
        demo.beta[(m, t)] = float(v)

    active = set(cfg_tokens)
    weights = _normalized_weights(cfg_tokens)

    chosen = demo.select_mode(active_tokens=active, weights=weights)
    print(f"chosen mode: {chosen}")

    demo.apply_feedback(mode_used=chosen, engraved_tokens=active, reward=params["reward"])

    print("β snapshot:")
    for k, v in sorted(demo.snapshot_beta().items()):
        print(f"  {k}: {v:.3f}")


if __name__ == "__main__":
    # Only run the JSON-config CLI if FeedbackLayerDemo is available
    if 'FeedbackLayerDemo' in globals():
        try:
            _demo_cli()
        except Exception as e:
            print(f"[error] demo failed: {e}")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
feedback_layer_demo.py — Demo of an entrainment feedback layer only.

Purpose:
    • Show how invariant tokens + scalar feedback can tune mode selection.
    • No real user data, no real archetypes, no real thresholds.
    • Safe to share as a conceptual / portfolio demo.

Core idea:
    - invariants I = {"Demo-Panic", "Demo-Focus", ...}
    - modes M = {"soft", "direct", "coach"}
    - weights w(i): how "active" each invariant is this turn (0–1)
    - β[m, i]: association strength between mode m and invariant i
    - score(m) = Σ_i β[m, i] * w(i)
    - feedback: β[m_t, i] ← β[m_t, i] + η * reward * w(i)

All numbers and labels here are TOY VALUES, not production heuristics.
"""

from dataclasses import dataclass, field
from typing import Dict, List


Invariant = str
Mode = str


@dataclass
class FeedbackLayerDemo:
    """
    Minimal feedback layer demo:

    • Keeps a β[m][i] table (mode ↦ invariant weight).
    • Scores modes with score(m) = Σ_i β[m, i] * w(i).
    • Applies a simple online update from scalar reward.
    """
    invariants: List[Invariant]
    modes: List[Mode]
    learning_rate: float = 0.2
    clamp_min: float = -1.0
    clamp_max: float = 1.0
    verbose: bool = True

    # β[m][i] → association strength
    beta: Dict[Mode, Dict[Invariant, float]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Initialize β to zeros for all (mode, invariant) pairs
        for m in self.modes:
            if m not in self.beta:
                self.beta[m] = {}
            for inv in self.invariants:
                self.beta[m].setdefault(inv, 0.0)

    # ---- scoring ---------------------------------------------------------

    def score_modes(self, active_weights: Dict[Invariant, float]) -> Dict[Mode, float]:
        """
        Compute score_t(m) = Σ_i β[m, i] * w(i) for each mode m.

        active_weights:
            Map invariant → weight in [0,1] for this turn.
        """
        # Warn on unknown invariants (demo safety)
        if self.verbose:
            unknown = [inv for inv in active_weights.keys() if inv not in self.invariants]
            if unknown:
                print(f"[warn] ignoring unknown invariants: {unknown}")
        scores: Dict[Mode, float] = {}
        for m in self.modes:
            s = 0.0
            row = self.beta[m]
            for inv, w in active_weights.items():
                if inv not in row:
                    continue
                s += row[inv] * w
            scores[m] = s
        return scores

    def select_mode(self, active_weights: Dict[Invariant, float]) -> Mode:
        """
        Pick the mode with maximum score (ties broken by list order).
        """
        scores = self.score_modes(active_weights)
        # max(...) is safe here because self.modes is non-empty by design
        best_mode = max(scores, key=scores.get)
        return best_mode

    # ---- feedback -------------------------------------------------------

    def apply_feedback(
        self,
        chosen_mode: Mode,
        engraved_invariants: Dict[Invariant, float],
        reward: float,
    ) -> None:
        """
        Update β[chosen_mode, i] for invariants engraved this turn.

        engraved_invariants:
            invariants considered part of this interaction (and their weights).
        reward:
            +1.0 for "this mode worked well here"
             0.0 for neutral
            -1.0 for "this mode was wrong for this pattern"
        """
        if reward == 0.0:
            return

        lr = self.learning_rate
        row = self.beta[chosen_mode]

        for inv, w in engraved_invariants.items():
            # Simple rule: scale update by reward and invariant weight.
            delta = lr * reward * w
            row[inv] = row.get(inv, 0.0) + delta
            # Clamp to keep the demo stable/bounded
            if row[inv] < self.clamp_min:
                row[inv] = self.clamp_min
            elif row[inv] > self.clamp_max:
                row[inv] = self.clamp_max

    # ---- inspection / printing ------------------------------------------

    def snapshot_beta(self) -> Dict[Mode, Dict[Invariant, float]]:
        """
        Return a shallow snapshot of β (for logging / JSON / tests).
        """
        return {
            m: {inv: self.beta[m][inv] for inv in self.invariants}
            for m in self.modes
        }

    def print_beta(self) -> None:
        """Print β table for inspection (demo only)."""
        print("\nCurrent β (mode ↦ invariant weights):")
        header = ["mode"] + self.invariants
        print("\t".join(header))
        for m in self.modes:
            row = [m]
            for inv in self.invariants:
                row.append(f"{self.beta[m][inv]:+.2f}")
            print("\t".join(row))
        print()


if __name__ == "__main__":
    # --- Setup demo invariants & modes -----------------------------------
    invariants = [
        "Demo-Panic",
        "Demo-Focus",
        "Demo-Sad",
        "Demo-Playful",
    ]
    modes = ["soft", "direct", "coach"]

    engine = FeedbackLayerDemo(invariants=invariants, modes=modes)

    print("=== Entrainment Feedback Layer Demo ===")
    print("Invariants:", invariants)
    print("Modes:", modes)
    engine.print_beta()

    # --- Simulate a few demo rounds --------------------------------------

    # Round 1: user is in 'Demo-Panic', we start with unknown β
    active = {"Demo-Panic": 1.0}
    print("Round 1 — active invariants:", active)

    m1 = engine.select_mode(active)
    print("Selected mode:", m1)

    # For demo purposes, pretend the chosen mode worked well: reward = +1.0
    reward1 = +1.0
    engine.apply_feedback(chosen_mode=m1, engraved_invariants=active, reward=reward1)
    engine.print_beta()

    # Round 2: user again in 'Demo-Panic', but now β has changed
    print("Round 2 — active invariants:", active)
    m2 = engine.select_mode(active)
    print("Selected mode:", m2, "(should be biased by previous reward)")
    reward2 = +1.0
    engine.apply_feedback(chosen_mode=m2, engraved_invariants=active, reward=reward2)
    engine.print_beta()

    # Round 3: mixed pattern 'Demo-Panic' + 'Demo-Focus'
    active2 = {"Demo-Panic": 0.7, "Demo-Focus": 0.8}
    print("Round 3 — active invariants:", active2)
    m3 = engine.select_mode(active2)
    print("Selected mode:", m3)
    reward3 = -0.5  # pretend this combo didn't feel right
    engine.apply_feedback(chosen_mode=m3, engraved_invariants=active2, reward=reward3)
    engine.print_beta()

    print("Demo complete. (Real systems would use different invariants and β.)")
