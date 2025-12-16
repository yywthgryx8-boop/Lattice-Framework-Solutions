"""
sentinel_guard_demo.py — Reference Sentinel Guard (Public Demo)

IMPORTANT:
    • This is a simplified reference implementation, NOT production logic.
    • All thresholds, detectors, and policies here are toy values.
    • Real systems use proprietary invariant sets, weights, and routing policies.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Any


# ─────────────────────────────────────────────
# Public constants (demo-only)
# ─────────────────────────────────────────────

THERAPY_KEYWORDS = [
    "as your therapist",
    "let's process your feelings",
    "inner child",
]

ASSISTANT_SELF_REFERENCE_MARKERS = [
    "as your assistant",
    "as this assistant",
]

HARD_BLOCK_THRESHOLD = 0.8
SOFT_WARN_THRESHOLD = 0.4


# ─────────────────────────────────────────────
# Core data structures
# ─────────────────────────────────────────────

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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.name,
            "reason": self.reason,
            "notes": self.notes,
        }


# ─────────────────────────────────────────────
# Demo heuristic detectors (string-level)
# ─────────────────────────────────────────────

def _demo_detect_therapy_tone(text: str) -> float:
    """
    Return a toy score ∈ [0,1] for 'therapy-script-like' language.
    """
    lowered = text.lower()
    matches = sum(1 for k in THERAPY_KEYWORDS if k in lowered)
    return min(matches * 0.4, 1.0)


def _demo_detect_assistant_self_reference(text: str) -> float:
    """
    Toy detector for assistant voice self-reference.
    """
    lowered = text.lower()
    matches = sum(1 for m in ASSISTANT_SELF_REFERENCE_MARKERS if m in lowered)
    return min(matches * 0.6, 1.0)


def _demo_detect_ignored_user_format(text: str, user_wants_bullets: bool) -> float:
    """
    Demo-only formatting expectation check.
    """
    if not user_wants_bullets:
        return 0.0

    if "-" in text or "1." in text or "•" in text:
        return 0.0

    return 0.7  # toy constant


# ─────────────────────────────────────────────
# Sentinel Guard (Public Demo)
# ─────────────────────────────────────────────

def sentinel_guard_demo(
    request_meta: RequestMeta,
    candidate_output: str,
    user_wants_bullets: bool = False,
) -> GuardResult:
    """
    Reference Sentinel Guard:
        • Always runs unless explicitly bypassed.
        • Uses toy detectors and toy thresholds.
        • Returns ALLOW / SCRUB_AND_WARN / BLOCK_AND_RETRY.
    """

    # Explicit demo bypass flag
    if request_meta.flags.get("SKIP_SENTINEL_FOR_DEMO", False):
        return GuardResult(
            decision=SentinelDecision.ALLOW,
            reason="Guard bypassed via explicit demo override.",
            notes={"bypassed": True},
        )

    # Compute demo scores
    therapy_score = _demo_detect_therapy_tone(candidate_output)
    takeover_score = _demo_detect_assistant_self_reference(candidate_output)
    ignored_wants_score = _demo_detect_ignored_user_format(
        candidate_output, user_wants_bullets
    )

    notes = {
        "therapy_tone_score": therapy_score,
        "assistant_self_reference_score": takeover_score,
        "ignored_user_format_score": ignored_wants_score,
    }

    # Hard block
    if therapy_score >= HARD_BLOCK_THRESHOLD or takeover_score >= HARD_BLOCK_THRESHOLD:
        return GuardResult(
            decision=SentinelDecision.BLOCK_AND_RETRY,
            reason="Demo hard violation: disallowed tone or self-referential voice detected.",
            notes=notes,
        )

    # Soft drift
    if (
        therapy_score >= SOFT_WARN_THRESHOLD
        or takeover_score >= SOFT_WARN_THRESHOLD
        or ignored_wants_score >= SOFT_WARN_THRESHOLD
    ):
        return GuardResult(
            decision=SentinelDecision.SCRUB_AND_WARN,
            reason="Demo soft drift detected; output should be revised.",
            notes=notes,
        )

    # Default allow
    return GuardResult(
        decision=SentinelDecision.ALLOW,
        reason="Demo: no significant drift detected.",
        notes=notes,
    )


# ─────────────────────────────────────────────
# Minimal CLI demo
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import json

    meta = RequestMeta(
        tier="Tier-3",
        archetype="DemoArchetype",
        mode="STRICT",
        flags={},  # try {"SKIP_SENTINEL_FOR_DEMO": True} to bypass
    )

    demo_output = "As your assistant, let's process your feelings step by step."

    result = sentinel_guard_demo(
        request_meta=meta,
        candidate_output=demo_output,
        user_wants_bullets=False,
    )

    print(json.dumps(result.to_dict(), indent=2))
