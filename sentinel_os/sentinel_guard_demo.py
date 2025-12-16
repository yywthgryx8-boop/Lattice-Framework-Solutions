#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sentinel_guard_demo.py — Demo-only SentinelOS guard.

IMPORTANT:
    • This is a simplified demo, NOT production logic.
    • Thresholds and heuristics here are toy values.
    • Real system uses internal weights and policies not shown publicly.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Any


class SentinelDecision(Enum):
    ALLOW = auto()
    SCRUB_AND_WARN = auto()
    BLOCK_AND_RETRY = auto()


@dataclass
class RequestMeta:
    tier: str
    archetype: str
    mode: str
    flags: Dict[str, bool]


@dataclass
class GuardResult:
    decision: SentinelDecision
    reason: str
    notes: Dict[str, Any]


# ─────────────────────────────────────────────
# Demo-only heuristic detectors (string-level)
# ─────────────────────────────────────────────

def _demo_detect_therapy_script(text: str) -> float:
    """Return a toy score ∈ [0,1] for 'therapy-script like' tone."""
    keywords = ["as your therapist", "let's process your feelings", "inner child"]
    score = 0.0
    lowered = text.lower()
    for k in keywords:
        if k in lowered:
            score += 0.4
    return min(score, 1.0)


def _demo_detect_assistant_takeover(text: str) -> float:
    """Toy detector for assistant-voice takeover."""
    markers = ["as an ai assistant", "as a language model", "chatgpt"]
    score = 0.0
    lowered = text.lower()
    for m in markers:
        if m in lowered:
            score += 0.6
    return min(score, 1.0)


def _demo_detect_ignored_user_wants(text: str, user_wanted_bullets: bool) -> float:
    """
    Demo: if user wanted bullets but we see no '-' or numbered list tokens,
    bump a 'ignored_user_wants' score a little.
    """
    if not user_wanted_bullets:
        return 0.0
    if "-" in text or "1." in text or "•" in text:
        return 0.0
    return 0.7  # toy constant


# ─────────────────────────────────────────────
# Sentinel guard demo
# ─────────────────────────────────────────────

def sentinel_guard_demo(
    request_meta: RequestMeta,
    candidate_output: str,
    user_wants_bullets: bool = False,
) -> GuardResult:
    """
    Demo sentinel guard:
        - Always runs unless caller explicitly bypasses it.
        - Uses toy detectors and toy thresholds.
        - Returns ALLOW / SCRUB_AND_WARN / BLOCK_AND_RETRY.
    """

    # Allow explicit bypass for demo only:
    if request_meta.flags.get("ALLOW_ASSISTANT_FOR_DEMO", False):
        return GuardResult(
            decision=SentinelDecision.ALLOW,
            reason="Guard bypassed for demo via ALLOW_ASSISTANT_FOR_DEMO.",
            notes={"bypassed": True},
        )

    # Compute demo scores
    therapy_score = _demo_detect_therapy_script(candidate_output)
    takeover_score = _demo_detect_assistant_takeover(candidate_output)
    ignored_wants_score = _demo_detect_ignored_user_wants(candidate_output, user_wants_bullets)

    notes = {
        "therapy_script_score": therapy_score,
        "assistant_takeover_score": takeover_score,
        "ignored_user_wants_score": ignored_wants_score,
    }

    # Demo thresholds (toy!)
    HARD_BLOCK = 0.8
    SOFT_WARN = 0.4

    # Hard Tier-0-ish demo block:
    if therapy_score >= HARD_BLOCK or takeover_score >= HARD_BLOCK:
        return GuardResult(
            decision=SentinelDecision.BLOCK_AND_RETRY,
            reason="Demo: hard violation (therapy/assistant takeover pattern detected).",
            notes=notes,
        )

    # Soft drift handling:
    if (
        therapy_score >= SOFT_WARN
        or takeover_score >= SOFT_WARN
        or ignored_wants_score >= SOFT_WARN
    ):
        return GuardResult(
            decision=SentinelDecision.SCRUB_AND_WARN,
            reason="Demo: soft drift detected; suggest scrub or rewrite.",
            notes=notes,
        )

    # Default allow
    return GuardResult(
        decision=SentinelDecision.ALLOW,
        reason="Demo: no significant drift detected.",
        notes=notes,
    )


if __name__ == "__main__":
    meta = RequestMeta(
        tier="Tier-3",
        archetype="DemoArchetype",
        mode="STRICT",
        flags={},
    )
    demo_output = "As an AI assistant, I think we should process your feelings step by step."
    result = sentinel_guard_demo(meta, demo_output, user_wants_bullets=False)
    print(result.decision, result.reason)
    print(result.notes)


# MODULE BOUNDARY — Robust Feedback Layer for Archetype Guard Tuning
import argparse
import json
from typing import List, Set, Tuple, Hashable
from dataclasses import field

Token = Hashable
ModeId = Hashable


@dataclass
class ArchetypeTunerDemo:
    """
    Simple feedback layer for tuning archetype → guard-mode associations.
    • Modes: e.g., ["STRICT", "LENIENT", "BALANCED"]
    • Tokens: e.g., ["therapy-drift", "assistant-takeover", "ignored-wants"]
    • Updates β (mode←token weights) based on reward signal.
    • Clamps β to prevent runaway growth.
    """
    modes: List[ModeId]
    beta: Dict[Tuple[ModeId, Token], float] = field(default_factory=dict)
    learning_rate: float = 0.1
    clamp_min: float = -2.0
    clamp_max: float = 2.0
    verbose: bool = False

    def score_modes(self, active_tokens: Set[Token], weights: Dict[Token, float]) -> Dict[ModeId, float]:
        scores: Dict[ModeId, float] = {m: 0.0 for m in self.modes}
        for tok in active_tokens:
            wt = float(weights.get(tok, 0.0))
            if wt <= 0.0:
                if self.verbose:
                    print(f"[warn] token '{tok}' has zero weight; ignored")
                continue
            found_any = False
            for m in self.modes:
                key = (m, tok)
                b = self.beta.get(key)
                if b is not None:
                    scores[m] += b * wt
                    found_any = True
            if not found_any and self.verbose:
                print(f"[warn] token '{tok}' has no associations in β; check configuration")
        return scores

    def select_mode(self, active_tokens: Set[Token], weights: Dict[Token, float]) -> ModeId:
        scores = self.score_modes(active_tokens, weights)
        best_mode = self.modes[0]
        best_score = scores.get(best_mode, float('-inf'))
        for m in self.modes[1:]:
            s = scores.get(m, float('-inf'))
            if s > best_score:
                best_mode, best_score = m, s
        return best_mode

    def apply_feedback(self, mode_used: ModeId, engraved_tokens: Set[Token], reward: float) -> None:
        if reward == 0.0:
            return
        for tok in engraved_tokens:
            key = (mode_used, tok)
            self.beta[key] = self.beta.get(key, 0.0) + self.learning_rate * reward
        for k in list(self.beta.keys()):
            v = self.beta[k]
            if v < self.clamp_min:
                self.beta[k] = self.clamp_min
            elif v > self.clamp_max:
                self.beta[k] = self.clamp_max

    def snapshot_beta(self) -> Dict[str, float]:
        return {f"{m}|{t}": v for (m, t), v in self.beta.items()}


def _normalized_weights(tokens: List[Token]) -> Dict[Token, float]:
    if not tokens:
        return {}
    w = 1.0 / float(len(tokens))
    return {tok: w for tok in tokens}


def _demo_tuner_cli():
    ap = argparse.ArgumentParser(description="Sentinel archetype guard tuner with optional JSON config")
    ap.add_argument("--config", help="Path to JSON config with modes, tokens, beta seeds, and params", required=False)
    args = ap.parse_args()

    cfg_modes: List[str] = ["STRICT", "LENIENT", "BALANCED"]
    cfg_tokens: List[str] = ["therapy-drift", "assistant-takeover", "ignored-wants"]
    cfg_beta: Dict[str, float] = {
        "STRICT|therapy-drift": 0.9,
        "STRICT|assistant-takeover": 0.9,
        "LENIENT|ignored-wants": -0.5,
        "BALANCED|ignored-wants": 0.3,
    }
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

    tuner = ArchetypeTunerDemo(
        modes=cfg_modes,
        verbose=True,
        learning_rate=params["learning_rate"],
        clamp_min=params["clamp_min"],
        clamp_max=params["clamp_max"],
    )

    for k, v in cfg_beta.items():
        try:
            m, t = k.split("|", 1)
        except ValueError:
            print(f"[warn] bad beta seed key '{k}'; expected 'mode|token'")
            continue
        tuner.beta[(m, t)] = float(v)

    active = set(cfg_tokens)
    weights = _normalized_weights(cfg_tokens)

    chosen = tuner.select_mode(active_tokens=active, weights=weights)
    print(f"chosen guard mode: {chosen}")

    tuner.apply_feedback(mode_used=chosen, engraved_tokens=active, reward=params["reward"])

    print("β snapshot (guard mode ← drift token):")
    for k, v in sorted(tuner.snapshot_beta().items()):
        print(f"  {k}: {v:.3f}")


# Only run tuner CLI if invoked with --config
if __name__ == "__main__" and "--config" in __import__("sys").argv:
    _demo_tuner_cli()
