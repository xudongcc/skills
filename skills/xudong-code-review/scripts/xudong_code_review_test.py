#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import copy
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).with_name("xudong-code-review")
LOADER = SourceFileLoader("xudong_code_review_module", str(SCRIPT_PATH))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC is not None
XUDONG_CODE_REVIEW = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(XUDONG_CODE_REVIEW)


FINAL_REPORT = {
    "findings": [],
    "overall_correctness": "patch is correct",
    "overall_explanation": "clean",
    "overall_confidence": 0.9,
}

DRAFT_REPORT = {
    "findings": [
        {
            "title": "Draft finding",
            "body": "draft",
            "priority": "P3",
            "confidence": 0.2,
            "category": "maintainability",
            "code_location": {"file_path": "draft.js", "line": 1},
        }
    ],
    "overall_correctness": "patch is incorrect",
    "overall_explanation": "draft",
    "overall_confidence": 0.2,
}


class XudongCodeReviewInterfaceTests(unittest.TestCase):
    def test_removed_engine_and_fallback_options_are_rejected(self) -> None:
        options = [
            ["--engine", "codex"],
            ["--engine", "10"],
            ["--fallback-model", "another-model"],
        ]
        for option in options:
            with self.subTest(option=option), mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
                sys, "argv", ["xudong-code-review", *option],
            ), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    XUDONG_CODE_REVIEW.parse_args()
                self.assertEqual(error.exception.code, 2)

    def test_removed_configuration_environment_is_ignored(self) -> None:
        environment = {
            "XUDONG_CODE_REVIEW_ENGINE": "claude",
            "XUDONG_CODE_REVIEW_MODEL": "unexpected-model",
            "XUDONG_CODE_REVIEW_THINKING": "invalid",
            "XUDONG_CODE_REVIEW_ENGINE_TIMEOUT_SECONDS": "invalid",
            "XUDONG_CODE_REVIEW_CODEX_CONFIG": "unsafe_key=true",
            "XUDONG_CODE_REVIEW_CODEX_SPEED": "invalid",
            "XUDONG_CODE_REVIEW_MAX_PRIORITY": "P0",
            "XUDONG_CODE_REVIEW_STREAM_ENGINE_OUTPUT": "1",
            "CODEX_BIN": "/unexpected/codex",
        }
        for flags, expected in (
            ([], ("gpt-6.1-sol", "high", "P2", None, False, "codex", [], None)),
            (["--model", "custom-model", "--thinking", "low", "--max-priority", "P1",
              "--engine-timeout-seconds", "30", "--stream-engine-output",
              "--codex-bin", "/explicit/codex", "--codex-config", 'model_verbosity="low"',
              "--codex-speed", "fast"],
             ("custom-model", "low", "P1", 30.0, True, "/explicit/codex",
              ['model_verbosity="low"'], 'service_tier="fast"')),
        ):
            with self.subTest(flags=flags), mock.patch.dict(os.environ, environment, clear=True), mock.patch.object(
                sys, "argv", ["xudong-code-review", *flags],
            ):
                reviewer = XUDONG_CODE_REVIEW.reviewer_args(XUDONG_CODE_REVIEW.parse_args())[0]
                self.assertEqual(reviewer.engine, "codex")
                self.assertEqual((
                    reviewer.model, reviewer.thinking, reviewer.max_priority,
                    reviewer.engine_timeout_seconds, reviewer.stream_engine_output,
                    reviewer.codex_bin, XUDONG_CODE_REVIEW.codex_config_overrides(reviewer),
                    XUDONG_CODE_REVIEW.codex_speed_override(reviewer),
                ), expected)

    def test_extract_json_accepts_codex_final_report(self) -> None:
        self.assertEqual(XUDONG_CODE_REVIEW.extract_json(json.dumps(FINAL_REPORT)), FINAL_REPORT)

    def test_extract_json_rejects_wrapped_or_malformed_reports(self) -> None:
        for output in ("", "not JSON", "```json\n{}\n```", "[]", "{}", json.dumps({"result": FINAL_REPORT})):
            with self.subTest(output=output), self.assertRaises(SystemExit):
                XUDONG_CODE_REVIEW.extract_json(output)


class XudongCodeReviewPriorityTests(unittest.TestCase):
    def test_priority_filter_omits_lower_findings_and_cleans_verdict(self) -> None:
        report = copy.deepcopy(DRAFT_REPORT)
        XUDONG_CODE_REVIEW.filter_findings_by_priority(report, "P0")
        self.assertEqual(report["findings"], [])
        self.assertEqual(report["overall_correctness"], "patch is correct")
        self.assertIn("below the requested P0", report["overall_explanation"])


class XudongCodeReviewTruffleHogTests(unittest.TestCase):
    def test_findings_map_to_prompt_dataset_untracked_and_diff_paths(self) -> None:
        prompt = "\n".join(
            (
                "# Prompt file: review-notes.md",
                "prompt body",
                "# Dataset: evidence.json",
                "dataset body",
                "# Untracked File",
                'path: "new/config.ts"',
                "source-line 1: redacted example",
                "diff --git a/old.ts b/new.ts",
                "--- a/old.ts",
                "+++ b/new.ts",
                "@@ -1 +1 @@",
                "+redacted example",
            )
        )
        output = "\n".join(
            json.dumps(
                {
                    "SourceMetadata": {
                        "Data": {"Filesystem": {"line": line_number}}
                    }
                }
            )
            for line_number in (2, 4, 7, 12)
        )

        self.assertEqual(
            XUDONG_CODE_REVIEW.trufflehog_review_pack_paths(prompt, output),
            ["evidence.json", "new.ts", "new/config.ts", "review-notes.md"],
        )

    def test_deleted_diff_finding_maps_to_original_path(self) -> None:
        prompt = "\n".join(
            (
                "# Change Bundle",
                "diff --git a/config.ts b/config.ts",
                "deleted file mode 100644",
                "--- a/config.ts",
                "+++ /dev/null",
                "@@ -1 +0,0 @@",
                "-redacted example",
            )
        )
        output = json.dumps(
            {
                "SourceMetadata": {
                    "Data": {"Filesystem": {"Line": 7}}
                }
            }
        )

        self.assertEqual(
            XUDONG_CODE_REVIEW.trufflehog_review_pack_paths(prompt, output),
            ["config.ts"],
        )

    def test_unusable_scanner_output_falls_back_without_echoing_it(self) -> None:
        output = "not-json\n" + json.dumps(
            {
                "SourceMetadata": {
                    "Data": {"Filesystem": {"line": "invalid"}}
                },
                "Raw": "must-not-be-returned",
            }
        )

        self.assertEqual(
            XUDONG_CODE_REVIEW.trufflehog_review_pack_paths("prompt", output),
            ["review pack"],
        )

    def test_scanner_command_requests_verified_and_unknown_results(self) -> None:
        prompt = "review pack with redacted examples only"
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)

            def run_scanner(
                command: list[str],
                cwd: Path,
                **kwargs: object,
            ) -> subprocess.CompletedProcess[str]:
                self.assertEqual(cwd, Path(command[2]).parent)
                self.assertEqual(Path(command[2]).read_text(encoding="utf-8"), prompt)
                self.assertEqual(
                    command[3:],
                    [
                        "--json",
                        "--no-color",
                        "--results=verified,unknown",
                        "--fail",
                        "--fail-on-scan-errors",
                    ],
                )
                self.assertEqual(kwargs["check"], False)
                return subprocess.CompletedProcess(command, 0, "", "")

            with mock.patch.object(
                XUDONG_CODE_REVIEW,
                "find_command",
                return_value="/trusted/trufflehog",
            ), mock.patch.object(XUDONG_CODE_REVIEW, "run", side_effect=run_scanner):
                XUDONG_CODE_REVIEW.scan_outgoing_review_pack(repo, prompt)


class XudongCodeReviewCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.home_dir = tempfile.TemporaryDirectory(prefix="xudong-code-review-test-home.")
        cls.home_patch = mock.patch.object(Path, "home", return_value=Path(cls.home_dir.name))
        cls.home_patch.start()
        cls.home_keys = ("HOME", "USERPROFILE", "HOMEDRIVE", "HOMEPATH")
        cls.old_home_env = {key: os.environ.get(key) for key in cls.home_keys}
        os.environ["HOME"] = cls.home_dir.name
        os.environ["USERPROFILE"] = cls.home_dir.name
        os.environ.pop("HOMEDRIVE", None)
        os.environ.pop("HOMEPATH", None)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.home_patch.stop()
        for key, value in cls.old_home_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        cls.home_dir.cleanup()


    def test_codex_config_status_exposes_keys_only(self) -> None:
        args = argparse.Namespace(codex_config=['model_verbosity="low"'])
        self.assertEqual(XUDONG_CODE_REVIEW.codex_config_keys(args), ["model_verbosity"])

    def test_codex_surfaces_provider_failures_without_model_fallback(self) -> None:
        for message in (
            "The model `gpt-6.1-sol` does not exist or you do not have access to it.",
            "network timeout",
            "model_not_available: gpt-6.1-sol is temporarily unavailable due to capacity",
        ):
            with self.subTest(message=message):
                args = argparse.Namespace(
                    codex_bin="codex",
                    codex_config=None,
                    codex_speed=None,
                    model="gpt-6.1-sol",
                    stream_engine_output=False,
                    thinking="high",
                    tools=True,
                    web_search=False,
                )
                models: list[str] = []

                def fake_run(command: list[str], *_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
                    model = command[command.index("--model") + 1]
                    models.append(model)
                    return subprocess.CompletedProcess(
                        command,
                        1,
                        "",
                        message,
                    )

                with tempfile.TemporaryDirectory(prefix="xudong-code-review-codex-fallback.") as tmpdir, mock.patch.object(
                    XUDONG_CODE_REVIEW,
                    "resolve_command",
                    return_value="/usr/bin/codex",
                ), mock.patch.object(
                    XUDONG_CODE_REVIEW,
                    "ensure_codex_isolation_supported",
                    return_value="/usr/bin/codex",
                ), mock.patch.object(XUDONG_CODE_REVIEW, "codex_auth_config_flags", return_value=[]), mock.patch.object(
                    XUDONG_CODE_REVIEW,
                    "prepare_codex_runtime_auth",
                    return_value=None,
                ), mock.patch.object(
                    XUDONG_CODE_REVIEW,
                    "run_with_heartbeat",
                    side_effect=fake_run,
                ):
                    with self.assertRaises(SystemExit) as error:
                        XUDONG_CODE_REVIEW.run_codex(args, Path(tmpdir), "review")

                self.assertIn(message, str(error.exception))
                self.assertEqual(models, ["gpt-6.1-sol"])

    def test_codex_runs_outside_repo_with_bundle_only_workspace(self) -> None:
        args = argparse.Namespace(
            codex_bin="codex",
            codex_config=None,
            codex_speed=None,
            model="gpt-6.1-sol",
            stream_engine_output=False,
            thinking="high",
            tools=True,
            web_search=False,
        )
        observed: dict[str, object] = {}

        def fake_run(
            command: list[str],
            cwd: Path,
            *_args: object,
            **kwargs: object,
        ) -> subprocess.CompletedProcess[str]:
            observed["cwd"] = cwd
            observed["command"] = command
            observed["command_cwd"] = Path(command[command.index("-C") + 1])
            observed["workspace_entries"] = list(cwd.iterdir())
            observed["env"] = kwargs["env"]
            output_path = Path(command[command.index("--output-last-message") + 1])
            output_path.write_text(json.dumps(FINAL_REPORT))
            return subprocess.CompletedProcess(command, 0, "", "")

        with tempfile.TemporaryDirectory(prefix="xudong-code-review-codex-workspace-test.") as tmpdir:
            repo = Path(tmpdir)
            (repo / ".env").write_text("ignored environment fixture\n")
            with mock.patch.dict(
                os.environ,
                {"CODEX_HOME": ""},
                clear=False,
            ), mock.patch.object(
                XUDONG_CODE_REVIEW,
                "resolve_command",
                return_value="/usr/bin/codex",
            ), mock.patch.object(
                XUDONG_CODE_REVIEW,
                "ensure_codex_isolation_supported",
                return_value="/usr/bin/codex",
            ), mock.patch.object(
                XUDONG_CODE_REVIEW,
                "codex_auth_config_flags",
                return_value=[],
            ), mock.patch.object(
                XUDONG_CODE_REVIEW,
                "prepare_codex_runtime_auth",
                return_value=None,
            ), mock.patch.object(
                XUDONG_CODE_REVIEW,
                "codex_source_home",
                return_value=None,
            ), mock.patch.object(
                XUDONG_CODE_REVIEW,
                "run_with_heartbeat",
                side_effect=fake_run,
            ):
                output = XUDONG_CODE_REVIEW.run_codex(args, repo, "review")

            self.assertEqual(json.loads(output), FINAL_REPORT)
            observed_cwd = observed["cwd"]
            command_cwd = observed["command_cwd"]
            self.assertIsInstance(observed_cwd, Path)
            self.assertIsInstance(command_cwd, Path)
            assert isinstance(observed_cwd, Path)
            assert isinstance(command_cwd, Path)
            self.assertNotEqual(observed_cwd.resolve(), repo.resolve())
            self.assertEqual(observed_cwd, command_cwd)
            self.assertEqual(observed["workspace_entries"], [])
            env = observed["env"]
            self.assertIsInstance(env, dict)
            assert isinstance(env, dict)
            self.assertNotEqual(env["HOME"], os.environ.get("HOME"))
            self.assertEqual(env["USERPROFILE"], env["HOME"])
            self.assertNotEqual(env.get("CODEX_HOME"), str(repo.resolve()))
            self.assertEqual(Path(env["CODEX_HOME"]).name, "codex-home")
            self.assertNotEqual(env["CODEX_HOME"], str((Path.home() / ".codex").resolve()))
            self.assertIn("features.shell_snapshot=false", observed["command"])
            self.assertIn("features.hooks=false", observed["command"])
            self.assertIn("features.plugins=false", observed["command"])
            self.assertIn("skills.include_instructions=false", observed["command"])

if __name__ == "__main__":
    unittest.main()
