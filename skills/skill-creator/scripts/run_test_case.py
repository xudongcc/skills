#!/usr/bin/env python3
"""Run one full skill test case through an isolated medium-reasoning Codex."""

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from scripts.codex_exec import (
    build_codex_exec_command,
    reasoning_config,
    require_codex_cli,
)
from scripts.collect_codex_metrics import write_run_metrics
from scripts.create_eval_workspace import validate_run_directory
from scripts.utils import parse_skill_md, validate_skill_name


TEST_REASONING_CONFIG = reasoning_config("medium")
DELIVERABLE_INSTRUCTION = "Save requested deliverables under outputs/."


def build_test_command(
    run_dir: Path,
    output_path: Path,
    model: str | None = None,
) -> list[str]:
    """Build the Codex command for one full skill test run."""
    run_dir = run_dir.resolve()
    output_path = output_path.resolve()
    command = build_codex_exec_command(
        reasoning_effort="medium",
        sandbox="workspace-write",
        model=model,
    )
    command.extend([
        "--json",
        "-C",
        str(run_dir),
        "-o",
        str(output_path),
        "-",
    ])
    return command


def build_test_prompt(prompt: str) -> str:
    """Add the stable output-location instruction to a test prompt."""
    prompt = prompt.strip()
    if not prompt:
        raise ValueError("Test prompt must not be empty")
    return f"{prompt}\n\n{DELIVERABLE_INSTRUCTION}"


def prepare_run_directory(
    run_dir: Path,
    skill_path: Path | None = None,
) -> tuple[Path, Path]:
    """Prepare an empty result layout and optionally install one skill copy."""
    run_dir = run_dir.resolve()
    trace_path = run_dir / "trace.jsonl"
    output_path = run_dir / "outputs" / "final.md"
    reserved_paths = [
        trace_path,
        output_path,
        run_dir / "outputs" / "metrics.json",
        run_dir / "timing.json",
    ]
    conflicts = [str(path) for path in reserved_paths if path.exists()]
    if conflicts:
        raise ValueError(
            "Run directory already contains result artifacts: "
            + ", ".join(conflicts)
        )

    skill_name = None
    if skill_path is not None:
        skill_path = skill_path.resolve()
        skill_file = skill_path / "SKILL.md"
        if not skill_file.is_file():
            raise ValueError(f"No SKILL.md found at {skill_path}")
        if skill_path == run_dir or skill_path in run_dir.parents:
            raise ValueError("Run directory must not be inside the source skill")

        skill_name, _, _ = parse_skill_md(skill_path)
        skill_name = validate_skill_name(skill_name)

    skills_dir = run_dir / ".agents" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if skill_path is not None:
        assert skill_name is not None
        target_path = skills_dir / skill_name
        if target_path.resolve().parent != skills_dir.resolve():
            raise ValueError(f"Skill fixture path escapes its root: {target_path}")
        if target_path.exists() or target_path.is_symlink():
            raise ValueError(f"Skill fixture already exists: {target_path}")
        shutil.copytree(skill_path, target_path)

    return trace_path, output_path


def run_test_case(
    run_dir: Path,
    prompt: str,
    skill_path: Path | None = None,
    model: str | None = None,
) -> int:
    """Run one test case, then write its trace, metrics, and timing artifacts."""
    run_dir = run_dir.resolve()
    validate_run_directory(run_dir)
    require_codex_cli()
    trace_path, output_path = prepare_run_directory(run_dir, skill_path)
    command = build_test_command(run_dir, output_path, model)
    test_prompt = build_test_prompt(prompt)

    started_at = time.monotonic()
    with trace_path.open("x", encoding="utf-8") as trace_file:
        result = subprocess.run(
            command,
            input=test_prompt,
            stdout=trace_file,
            text=True,
        )
    duration_seconds = time.monotonic() - started_at

    exit_code = result.returncode
    missing_final = exit_code == 0 and not output_path.is_file()
    if missing_final:
        exit_code = 1
    write_run_metrics(
        trace_path,
        run_dir,
        duration_seconds=duration_seconds,
        exit_code=exit_code,
    )
    if missing_final:
        raise RuntimeError(
            "codex exec exited successfully but did not write "
            f"{output_path}"
        )
    return exit_code


def load_prompt(prompt: str | None, prompt_file: str | None) -> str:
    """Load a prompt from exactly one supported CLI source."""
    if prompt is not None:
        return prompt
    assert prompt_file is not None
    return Path(prompt_file).read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run one isolated full skill test case",
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        help="Fresh run directory for trace, outputs, metrics, and timing",
    )
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="Test prompt text")
    prompt_group.add_argument(
        "--prompt-file",
        help="UTF-8 file containing the prompt",
    )
    parser.add_argument(
        "--skill-path",
        default=None,
        help="Skill version to install; omit for a no-skill baseline",
    )
    parser.add_argument("--model", default=None, help="Optional Codex model")
    args = parser.parse_args()

    try:
        return run_test_case(
            Path(args.run_dir),
            load_prompt(args.prompt, args.prompt_file),
            Path(args.skill_path) if args.skill_path else None,
            args.model,
        )
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
