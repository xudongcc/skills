from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from test_code_review import CODE_REVIEW as helper, FINAL_REPORT


def parse(*flags: str) -> argparse.Namespace:
    with mock.patch.object(sys, "argv", ["code-review", *flags]):
        return helper.reviewer_args(helper.parse_args())[0]


def result_stream(report: object = FINAL_REPORT, status: str = "SUCCESS") -> str:
    return "\n".join([
        json.dumps({"event": "init", "conversation_id": "test"}),
        json.dumps({"event": "text", "text": "an intermediate draft"}),
        json.dumps({"event": "result", "result": {
            "status": status, "structured_output": report, "response": "ignore free text",
        }}),
    ]) + "\n"


class AntigravityTests(unittest.TestCase):
    def test_engine_defaults_and_explicit_overrides(self) -> None:
        codex = parse()
        self.assertEqual((codex.engine, codex.model, codex.thinking), ("codex", "gpt-6.1-sol", "high"))
        agy = parse("--engine", "antigravity")
        self.assertEqual((agy.engine, agy.model, agy.thinking, agy.antigravity_bin), ("antigravity", "gemini-4-carbon", "high", "agy"))
        agy = parse("--engine", "antigravity", "--thinking", "low")
        self.assertEqual((agy.model, agy.thinking), ("gemini-4-carbon", "low"))
        agy = parse("--engine", "antigravity", "--model", "custom-model", "--thinking", "max", "--antigravity-bin", "/trusted/agy")
        self.assertEqual((agy.model, agy.thinking, agy.antigravity_bin), ("custom-model", "max", "/trusted/agy"))

    def test_rejects_incompatible_effort_and_codex_tuning(self) -> None:
        for engine in ("antigravity", "agy"):
            for flags in (("--thinking", "none"), ("--thinking", "minimal"), ("--codex-speed", "fast"), ("--codex-config", 'model_verbosity="low"')):
                with self.subTest(engine=engine, flags=flags), self.assertRaises(SystemExit):
                    parse("--engine", engine, *flags)

    def test_agy_alias_normalizes_before_reviewer_selection(self) -> None:
        for flags in ((), ("--model", "custom-model", "--thinking", "low")):
            with self.subTest(flags=flags):
                self.assertEqual(vars(parse("--engine", "agy", *flags)), vars(parse("--engine", "antigravity", *flags)))
        with mock.patch.object(sys, "argv", ["code-review", "--engine", "agy"]):
            self.assertEqual(helper.parse_args().engine, "antigravity")

    def test_requires_success_and_exactly_one_structured_terminal_result(self) -> None:
        self.assertEqual(json.loads(helper.extract_antigravity_report(result_stream())), FINAL_REPORT)
        for text in ("", "not json", "[]", result_stream(None), result_stream("{}"), result_stream(status="ERROR"), result_stream() + result_stream()):
            with self.subTest(text=text), self.assertRaises(SystemExit):
                helper.extract_antigravity_report(text)
        # A valid-looking free-text response must never substitute for schema output.
        text = json.dumps({"event": "result", "result": {"status": "SUCCESS", "response": json.dumps(FINAL_REPORT)}})
        with self.assertRaisesRegex(SystemExit, "structured_output"):
            helper.extract_antigravity_report(text)

    def test_runs_with_isolated_home_empty_workspace_and_stdin_bundle(self) -> None:
        args = parse("--engine", "antigravity", "--model", "pinned-model", "--thinking", "xhigh", "--engine-timeout-seconds", "17", "--stream-engine-output")
        observed = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            repo.mkdir()
            (repo / ".env").write_text("must stay outside reviewer inputs")
            source_home = root / "source-home"
            source_home.mkdir()
            (source_home / ".gemini").mkdir()
            (source_home / ".gemini" / "hooks.json").write_text("must not load")

            def fake_run(command: list[str], cwd: Path, **kwargs: object) -> subprocess.CompletedProcess[str]:
                observed.append(command)
                self.assertEqual(list(cwd.iterdir()), [])
                self.assertFalse(helper.is_within(cwd.resolve(), repo.resolve()))
                self.assertNotIn("bundle content", command)
                self.assertEqual(json.loads(kwargs["input_text"]), {"event": "user", "message": {"content": "bundle content"}})
                self.assertEqual(kwargs["max_runtime_seconds"], 17)
                self.assertIsInstance(kwargs["stream_display"], helper.AntigravityStreamDisplay)
                self.assertEqual(command[command.index("--model") + 1], "pinned-model")
                self.assertEqual(command[command.index("--effort") + 1], "xhigh")
                self.assertNotIn("--dangerously-skip-permissions", command)
                schema = Path(command[command.index("--json-schema") + 1])
                self.assertEqual(json.loads(schema.read_text()), helper.SCHEMA)
                settings = json.loads(command[command.index("--settings") + 1])
                self.assertIn("read_file(*)", settings["permissions"]["deny"])
                self.assertIn("command(*)", settings["permissions"]["deny"])
                self.assertFalse(settings["allowNonWorkspaceAccess"])
                env = kwargs["env"]
                self.assertNotEqual(env["HOME"], str(source_home))
                self.assertNotIn("OPENAI_API_KEY", env)
                self.assertNotIn("GEMINI_CONFIG_DIR", env)
                self.assertNotIn("NODE_OPTIONS", env)
                self.assertEqual(env["HOME"], env["USERPROFILE"])
                agent = Path(env["HOME"]) / ".gemini/config/agents/code-review.md"
                self.assertIn('["finish", "search_web", "read_url_content"]', agent.read_text())
                self.assertIn("excludeDefaultComponents: true", agent.read_text())
                self.assertFalse((Path(env["HOME"]) / ".gemini/hooks.json").exists())
                return subprocess.CompletedProcess(command, 0, result_stream(), "")

            with mock.patch.dict(os.environ, {"HOME": str(source_home), "GEMINI_CONFIG_DIR": str(source_home), "OPENAI_API_KEY": "unrelated", "NODE_OPTIONS": "untrusted"}), mock.patch.object(
                helper, "ensure_antigravity_isolation_supported", return_value="/trusted/agy",
            ), mock.patch.object(helper, "run_with_heartbeat", side_effect=fake_run):
                self.assertEqual(json.loads(helper.run_engine(args, repo, "bundle content")), FINAL_REPORT)
        self.assertEqual(len(observed), 1)

    def test_provider_failure_is_returned_without_fallback(self) -> None:
        args = parse("--engine", "antigravity", "--model", "pinned-model")
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            helper, "ensure_antigravity_isolation_supported", return_value="/trusted/agy",
        ), mock.patch.object(helper, "run_with_heartbeat", return_value=subprocess.CompletedProcess([], 3, "", "capacity failure")) as provider:
            with self.assertRaisesRegex(SystemExit, "capacity failure"):
                helper.run_antigravity(args, Path(directory), "bundle")
            self.assertEqual(provider.call_count, 1)

    def test_bundle_only_disables_web_and_local_access(self) -> None:
        args = parse("--engine", "antigravity", "--no-web-search")
        settings = helper.antigravity_settings(args)
        self.assertEqual(settings["permissions"]["allow"], [])
        self.assertIn("read_url(*)", settings["permissions"]["deny"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            helper.prepare_antigravity_agent(root, web_search=False)
            agent = (root / "home/.gemini/config/agents/code-review.md").read_text()
            self.assertNotIn("search_web", agent)
            self.assertNotIn("read_url_content", agent)
            self.assertIn('["finish"]', agent)

    def test_preflight_requires_isolated_startup_and_required_flags(self) -> None:
        args = parse("--engine", "antigravity")
        for returncode, help_text, expected in (
            (0, "--settings --json-schema --input-format --output-format --agent --effort --disable-slash-commands", True),
            (0, "--json-schema", False),
            (1, "", False),
        ):
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as directory, mock.patch.object(
                helper, "resolve_command", return_value="/trusted/agy",
            ), mock.patch.object(helper, "run", return_value=subprocess.CompletedProcess([], returncode, help_text, "")):
                available, _ = helper.resolve_engine_binary(args, Path(directory))
                self.assertEqual(available, expected)

    def test_only_auth_sources_are_linked_and_repo_sources_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            repo.mkdir()
            source = root / "source"
            auth = source / ".gemini/antigravity-cli/antigravity-oauth-token"
            auth.parent.mkdir(parents=True)
            auth.write_text("auth fixture")
            (source / ".gemini/config").mkdir()
            (source / "Library/Keychains").mkdir(parents=True)
            runtime = root / "runtime"
            with mock.patch.object(Path, "home", return_value=source), mock.patch.object(sys, "platform", "darwin"):
                helper.prepare_antigravity_auth(repo, runtime)
            isolated = runtime / "home"
            self.assertEqual((isolated / ".gemini/antigravity-cli/antigravity-oauth-token").resolve(), auth.resolve())
            self.assertEqual((isolated / "Library/Keychains").resolve(), (source / "Library/Keychains").resolve())
            self.assertFalse((isolated / ".gemini/config").exists())
            auth.unlink()
            (repo / "unreviewed-auth").write_text("must not load")
            auth.symlink_to(repo / "unreviewed-auth")
            with mock.patch.object(Path, "home", return_value=source), self.assertRaisesRegex(SystemExit, "outside the reviewed repository"):
                helper.prepare_antigravity_auth(repo, root / "other-runtime")

    def test_file_auth_can_use_hardlink_when_symlinks_are_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            auth = source / ".gemini/antigravity-cli/antigravity-oauth-token"
            auth.parent.mkdir(parents=True)
            auth.write_text("auth fixture")
            runtime = root / "runtime"
            with mock.patch.object(Path, "home", return_value=source), mock.patch.object(sys, "platform", "win32"), mock.patch.object(Path, "symlink_to", side_effect=OSError("not permitted")):
                helper.prepare_antigravity_auth(root / "repo", runtime)
            self.assertTrue(auth.samefile(runtime / "home/.gemini/antigravity-cli/antigravity-oauth-token"))

    def test_stream_display_does_not_print_intermediate_text_or_tool_payloads(self) -> None:
        display = helper.AntigravityStreamDisplay()
        for event in ({"event": "text", "text": "draft"}, {"event": "tool", "arguments": "file contents"}):
            self.assertIsNone(display("stdout", json.dumps(event)))
        self.assertIn("SUCCESS", display("stdout", json.dumps({"event": "result", "result": {"status": "SUCCESS"}})))


if __name__ == "__main__":
    unittest.main()
