"""
social_scientist_demo.py — runnable demo for Social Scientist Mode

What it does:
- Loads SocialScientistMode from a module you specify or from defaults.
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

When module is in a different folder (e.g., in a GitHub repo):
    python social_scientist_demo.py --module-name yourpackage.social_scientist_mode
    python social_scientist_demo.py --module-path "/path/to/folder"  # containing social_scientist_mode.py
Or use env var:
    SOCIAL_SCIENTIST_MODE_PATH="/path/to/folder" python social_scientist_demo.py
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional
import os
import importlib
import importlib.util


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
    p.add_argument(
        "--module-path",
        type=str,
        default="",
        help="Optional: path to folder containing social_scientist_mode.py if not colocated.",
    )
    p.add_argument(
        "--module-name",
        type=str,
        default="social_scientist_mode",
        help="Optional: module import path for SocialScientistMode (e.g., 'yourpkg.social_scientist_mode').",
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
    global SocialScientistMode  # type: ignore
    # Import SocialScientistMode after parsing to allow flexible locations
    # 1) Try explicit --module-name
    # 2) Try default 'social_scientist_mode' (same dir or PYTHONPATH)
    # 3) Try package-relative 'social_scientist_demo.social_scientist_mode'
    # 4) Try --module-path or env var SOCIAL_SCIENTIST_MODE_PATH to load file directly
    module_loaded = False
    err: Exception | None = None

    # Step 1/2/3: import by name
    for name in (args.module_name, "social_scientist_mode", "social_scientist_demo.social_scientist_mode"):
        try:
            mod = importlib.import_module(name)
            cls = getattr(mod, "SocialScientistMode", None)
            if cls is not None:
                SocialScientistMode = cls  # type: ignore
                module_loaded = True
                break
        except Exception as e:
            err = e

    # Step 4: file-path load if not imported by name
    if not module_loaded:
        candidate_dir = args.module_path or os.environ.get("SOCIAL_SCIENTIST_MODE_PATH", "")
        if candidate_dir:
            sys.path.insert(0, candidate_dir)
            candidate_file = os.path.join(candidate_dir, "social_scientist_mode.py")
            if os.path.isfile(candidate_file):
                try:
                    spec = importlib.util.spec_from_file_location("social_scientist_mode", candidate_file)
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        cls = getattr(mod, "SocialScientistMode", None)
                        if cls is not None:
                            SocialScientistMode = cls  # type: ignore
                            module_loaded = True
                except Exception as e:
                    err = e

    if not module_loaded:
        print("ERROR: Could not import SocialScientistMode.")
        print("Tried module names:")
        print("  -", args.module_name)
        print("  - social_scientist_mode")
        print("  - social_scientist_demo.social_scientist_mode")
        print("Also attempted file path from --module-path or SOCIAL_SCIENTIST_MODE_PATH.")
        if args.module_path or os.environ.get("SOCIAL_SCIENTIST_MODE_PATH"):
            print("Checked folder:")
            print("  -", args.module_path or os.environ.get("SOCIAL_SCIENTIST_MODE_PATH"))
        if err:
            print(f"Details: {err}")
        print("Tip: For GitHub repos, set --module-name to your package path, e.g., 'yourpkg.social_scientist_mode'.")
        return 2
    focus = args.focus.strip() or None
    mmr = args.mmr.strip() or None
    return run_demo(args.text, focus, mmr, args.show_mode)


if __name__ == "__main__":
    raise SystemExit(main())

