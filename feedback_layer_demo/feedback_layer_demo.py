"""
feedback_layer_demo.py — Minimal entrainment feedback layer demo (stdlib-only).

Features
- Feedback layer with invariants, modes, β weights, online update, clamping.
- Two runnable demos:
  1) JSON-config CLI (`--config path.json`) for custom modes/tokens/β seeds.
  2) Simple scripted demo (`--simple-demo`) that shows learning over 3 rounds.

This is portfolio-safe: toy invariants/modes; no external deps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List
import argparse
import json
import sys

Invariant = str
Mode = str


# ---------------------------------------------------------------------------
# Feedback Layer
# ---------------------------------------------------------------------------
@dataclass
class FeedbackLayerDemo:
    """Minimal feedback layer demo.

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
        """Compute score_t(m) = Σ_i β[m, i] * w(i) for each mode m."""
        if self.verbose:
            unknown = [inv for inv in active_weights if inv not in self.invariants]
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
        """Pick the mode with maximum score (ties broken by list order)."""
        scores = self.score_modes(active_weights)
        return max(scores, key=scores.get)

    # ---- feedback -------------------------------------------------------

    def apply_feedback(
        self,
        chosen_mode: Mode,
        engraved_invariants: Dict[Invariant, float],
        reward: float,
    ) -> None:
        """Update β[chosen_mode, i] for engraved invariants, then clamp."""
        if reward == 0.0:
            return
        row = self.beta[chosen_mode]
        for inv, w in engraved_invariants.items():
            delta = self.learning_rate * reward * w
            row[inv] = row.get(inv, 0.0) + delta
            if row[inv] < self.clamp_min:
                row[inv] = self.clamp_min
            elif row[inv] > self.clamp_max:
                row[inv] = self.clamp_max

    # ---- inspection / printing -----------------------------------------

    def snapshot_beta(self) -> Dict[Mode, Dict[Invariant, float]]:
        """Return a shallow snapshot of β (for logging / JSON / tests)."""
        return {
            m: {inv: self.beta[m][inv] for inv in self.invariants}
            for m in self.modes
        }

    def print_beta(self) -> None:
        print("\nCurrent β (mode ↦ invariant weights):")
        header = ["mode"] + self.invariants
        print("\t".join(header))
        for m in self.modes:
            row = [m]
            for inv in self.invariants:
                row.append(f"{self.beta[m][inv]:+.2f}")
            print("\t".join(row))
        print()


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _normalized_weights(tokens: List[str]) -> Dict[str, float]:
    if not tokens:
        return {}
    w = 1.0 / float(len(tokens))
    return {t: w for t in tokens}


def _apply_beta_seeds(engine: FeedbackLayerDemo, seeds: Dict[str, float]) -> None:
    """Accept seeds as {"mode|token": value} and load into engine.beta."""
    for k, v in seeds.items():
        try:
            m, t = k.split("|", 1)
        except ValueError:
            print(f"[warn] bad beta seed key '{k}'; expected 'mode|token'")
            continue
        if m not in engine.beta:
            print(f"[warn] unknown mode '{m}' in beta seed; skipping")
            continue
        if t not in engine.invariants:
            print(f"[warn] unknown invariant '{t}' in beta seed; skipping")
            continue
        engine.beta[m][t] = float(v)


# ---------------------------------------------------------------------------
# Demo runners
# ---------------------------------------------------------------------------

def run_json_config_demo(cfg_path: str | None) -> int:
    cfg_modes: List[str] = ["neutral", "supportive", "directive"]
    cfg_tokens: List[str] = ["overload", "bf_play", "engineering"]
    cfg_beta: Dict[str, float] = {
        "supportive|overload": 0.8,
        "neutral|engineering": 0.6,
        "directive|engineering": 0.5,
    }
    params = {"learning_rate": 0.1, "clamp_min": -2.0, "clamp_max": 2.0, "reward": 1.0}

    if cfg_path:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cfg_modes = data.get("modes", cfg_modes)
        cfg_tokens = data.get("tokens", cfg_tokens)
        cfg_beta = data.get("beta_seeds", cfg_beta)
        p = data.get("params", {})
        params["learning_rate"] = float(p.get("learning_rate", params["learning_rate"]))
        params["clamp_min"] = float(p.get("clamp_min", params["clamp_min"]))
        params["clamp_max"] = float(p.get("clamp_max", params["clamp_max"]))
        params["reward"] = float(p.get("reward", params["reward"]))

    engine = FeedbackLayerDemo(
        invariants=cfg_tokens,
        modes=cfg_modes,
        learning_rate=params["learning_rate"],
        clamp_min=params["clamp_min"],
        clamp_max=params["clamp_max"],
        verbose=True,
    )
    _apply_beta_seeds(engine, cfg_beta)

    active = set(cfg_tokens)
    weights = _normalized_weights(cfg_tokens)

    chosen = engine.select_mode(active_weights=weights)
    print(f"chosen mode: {chosen}")

    engine.apply_feedback(chosen_mode=chosen, engraved_invariants=weights, reward=params["reward"])

    print("β snapshot:")
    for m, row in sorted(engine.snapshot_beta().items()):
        for inv, val in sorted(row.items()):
            print(f"  {m}|{inv}: {val:+.3f}")

    return 0


def run_scripted_demo() -> int:
    invariants = ["Demo-Panic", "Demo-Focus", "Demo-Sad", "Demo-Playful"]
    modes = ["soft", "direct", "coach"]

    engine = FeedbackLayerDemo(invariants=invariants, modes=modes)

    print("=== Entrainment Feedback Layer Demo ===")
    print("Invariants:", invariants)
    print("Modes:", modes)
    engine.print_beta()

    # Round 1
    active1 = {"Demo-Panic": 1.0}
    print("Round 1 — active invariants:", active1)
    m1 = engine.select_mode(active1)
    print("Selected mode:", m1)
    engine.apply_feedback(chosen_mode=m1, engraved_invariants=active1, reward=+1.0)
    engine.print_beta()

    # Round 2
    print("Round 2 — active invariants:", active1)
    m2 = engine.select_mode(active1)
    print("Selected mode:", m2, "(should be biased by previous reward)")
    engine.apply_feedback(chosen_mode=m2, engraved_invariants=active1, reward=+1.0)
    engine.print_beta()

    # Round 3
    active3 = {"Demo-Panic": 0.7, "Demo-Focus": 0.8}
    print("Round 3 — active invariants:", active3)
    m3 = engine.select_mode(active3)
    print("Selected mode:", m3)
    engine.apply_feedback(chosen_mode=m3, engraved_invariants=active3, reward=-0.5)
    engine.print_beta()

    print("Demo complete. (Real systems would use different invariants and β.)")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Entrainment feedback layer demo")
    p.add_argument("--config", help="Path to JSON config for modes/tokens/beta/params")
    p.add_argument("--simple-demo", action="store_true", help="Run the built-in 3-round scripted demo")
    return p


def main() -> int:
    args = _build_parser().parse_args()
    if args.simple_demo:
        return run_scripted_demo()
    return run_json_config_demo(args.config)


if __name__ == "__main__":
    sys.exit(main())
