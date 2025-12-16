"""
social_scientist_demo.py — runnable demo for Social Scientist Mode

What it does:
- Loads SocialScientistMode from social_scientist_mode.py
- Runs:
  1) quick_triage
  2) analyze (auto-focus)
  3) analyze with explicit focuses
  4) design_study (MMR scaffold)

Run:
  python social_scientist_demo.py
  python social_scientist_demo.py --text "Your question here"
  python social_scientist_demo.py --focus discourse --text "Your question here"
  python social_scientist_demo.py --mmr explanatory_sequential --text "Your question here"
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

# expects this file sits next to social_scientist_mode.py in the same folder
try:
    from social_scientist_mode import SocialScientistMode
except Exception as e:
    print("ERROR: Could not import SocialScientistMode.")
    print("Make sure social_scientist_demo.py and social_scientist_mode.py are in the same folder.")
    print(f"Details: {e}")
    sys.exit(2)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="social_scientist_demo",
        description="Demo runner for Social Scientist Mode (qualitative + mixed-methods scaffolding).",
    )
    p.add_argument(
        "--text",
        type=str,
        default="Why do workplace cultures reward overwork even when it causes burnout?",
        help="Phenomenon/question to analyze.",
    )
    p.add_argument(
        "--focus",
        type=str,
        default="",
        choices=["", "structure", "culture", "power", "discourse", "methods", "reflexive"],
        help="Force a specific analysis lens (default: auto).",
    )
    p.add_argument(
        "--mmr",
        type=str,
        default="",
        choices=[
            "",
            "convergent",
            "explanatory_sequential",
            "exploratory_sequential",
            "embedded",
            "multiphase",
            "transformative",
            "case_study_mmr",
        ],
        help="Force a specific mixed-methods design (default: auto).",
    )
    p.add_argument(
        "--show-mode",
        action="store_true",
        help="Print the full mode specification before running the demo.",
    )
    return p


def _header(title: str) -> str:
    return f"\n{'=' * 80}\n{title}\n{'=' * 80}\n"


def run_demo(text: str, focus: Optional[str], mmr: Optional[str], show_mode: bool) -> int:
    engine = SocialScientistMode()

    if show_mode:
        print(_header("MODE SPEC"))
        print(engine.describe_mode())

    print(_header("INPUT"))
    print(text)

    print(_header("TRIAGE (fast focus suggestion + clarifiers)"))
    print(engine.quick_triage(text))

    if focus:
        print(_header(f"ANALYSIS (forced focus: {focus})"))
        print(engine.analyze(text, focus=focus))
    else:
        print(_header("ANALYSIS (auto focus)"))
        print(engine.analyze(text))

        # Optional: show how the same prompt looks under multiple lenses (quick comparison)
        print(_header("ANALYSIS SNAPSHOT (structure vs power vs discourse)"))
        print("— STRUCTURE —\n")
        print(engine.analyze(text, focus="structure"))
        print("\n— POWER —\n")
        print(engine.analyze(text, focus="power"))
        print("\n— DISCOURSE —\n")
        print(engine.analyze(text, focus="discourse"))

    print(_header("METHOD SUGGESTIONS"))
    print(engine.suggest_methods(text))

    if mmr:
        print(_header(f"MMR STUDY DESIGN (forced: {mmr})"))
        print(engine.design_study(text, design=mmr))
    else:
        print(_header("MMR STUDY DESIGN (auto design pick)"))
        print(engine.design_study(text))

    return 0


def main() -> int:
    args = _build_parser().parse_args()
    focus = args.focus.strip() or None
    mmr = args.mmr.strip() or None
    return run_demo(args.text, focus, mmr, args.show_mode)


if __name__ == "__main__":
    raise SystemExit(main())

