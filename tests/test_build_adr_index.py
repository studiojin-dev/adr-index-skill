import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "adr-index" / "scripts" / "build_adr_index.py"


class BuildAdrIndexTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name) / "repo"
        self.script_path = self.repo / ".codex" / "skills" / "adr-index" / "scripts" / "build_adr_index.py"
        self.adr_dir = self.repo / "docs" / "adr"
        self.index_path = self.adr_dir / "index.json"

        self.script_path.parent.mkdir(parents=True, exist_ok=True)
        self.adr_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SCRIPT, self.script_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_adr(self, name: str, content: str) -> None:
        (self.adr_dir / name).write_text(content, encoding="utf-8")

    def _run_script(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(self.script_path)],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

    def _suggested_ids_from_error(self, stderr: str) -> list[list[str]]:
        groups: list[list[str]] = []
        prefix = "  suggested IDs: "

        for line in stderr.splitlines():
            if line.startswith(prefix):
                groups.append(line[len(prefix) :].split(", "))

        return groups

    def test_generates_index_for_unique_ids_and_optional_date(self) -> None:
        self._write_adr(
            "alpha.md",
            "\n".join(
                [
                    "# ADR-20260306-0001-ABC: First decision",
                    "",
                    "Tags: api, adr",
                    "Status: Accepted",
                    "Date: 2026-03-06",
                    "TL;DR: First decision summary.",
                    "",
                    "## Context",
                    "Alpha.",
                ]
            )
            + "\n",
        )
        self._write_adr(
            "beta.md",
            "\n".join(
                [
                    "# ADR-20260305-0001-DEF: Second decision",
                    "",
                    "Tags: docs",
                    "Status: Proposed",
                    "TL;DR: Second decision summary.",
                    "",
                    "## Context",
                    "Beta.",
                ]
            )
            + "\n",
        )

        result = self._run_script()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "ADRs: 2; index.json changed: yes")
        self.assertEqual(result.stderr, "")
        self.assertEqual(
            json.loads(self.index_path.read_text(encoding="utf-8")),
            [
                {
                    "id": "ADR-20260306-0001-ABC",
                    "title": "First decision",
                    "tags": ["api", "adr"],
                    "status": "Accepted",
                    "date": "2026-03-06",
                    "tldr": "First decision summary.",
                    "path": "docs/adr/alpha.md",
                },
                {
                    "id": "ADR-20260305-0001-DEF",
                    "title": "Second decision",
                    "tags": ["docs"],
                    "status": "Proposed",
                    "date": None,
                    "tldr": "Second decision summary.",
                    "path": "docs/adr/beta.md",
                },
            ],
        )

    def test_allows_missing_date_metadata(self) -> None:
        self._write_adr(
            "alpha.md",
            "\n".join(
                [
                    "# ADR-20260306-0001-ABC: First decision",
                    "",
                    "Status: Accepted",
                    "TL;DR: Missing Date is still valid.",
                ]
            )
            + "\n",
        )

        result = self._run_script()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "ADRs: 1; index.json changed: yes")
        payload = json.loads(self.index_path.read_text(encoding="utf-8"))
        self.assertEqual(payload[0]["id"], "ADR-20260306-0001-ABC")
        self.assertIsNone(payload[0]["date"])

    def test_rejects_duplicate_ids_without_writing_index(self) -> None:
        sentinel = "unchanged\n"
        self.index_path.write_text(sentinel, encoding="utf-8")
        self._write_adr(
            "alpha.md",
            "\n".join(
                [
                    "# ADR-20260306-0001-ABC: First decision",
                    "Date: 2026-03-06",
                ]
            )
            + "\n",
        )
        self._write_adr(
            "beta.md",
            "\n".join(
                [
                    "# ADR-20260306-0001-ABC: Second decision",
                    "Date: 2026-03-06",
                ]
            )
            + "\n",
        )

        result = self._run_script()

        self.assertEqual(result.returncode, 1)
        self.assertIn("Duplicate ADR IDs found:", result.stderr)
        self.assertIn("- ADR-20260306-0001-ABC", result.stderr)
        self.assertIn("  keep: docs/adr/alpha.md", result.stderr)
        self.assertIn("  change: docs/adr/beta.md", result.stderr)
        self.assertIn("AI next step:", result.stderr)
        self.assertIn("Default choice: use the first suggested ID", result.stderr)
        suggestion_groups = self._suggested_ids_from_error(result.stderr)
        self.assertEqual(len(suggestion_groups), 1)
        self.assertEqual(len(suggestion_groups[0]), 3)
        self.assertEqual(len(set(suggestion_groups[0])), 3)
        for suggestion in suggestion_groups[0]:
            self.assertRegex(suggestion, r"^ADR-20260306-\d{4}-[0-9A-Z]{3}$")
            self.assertNotEqual(suggestion, "ADR-20260306-0001-ABC")
        self.assertEqual(self.index_path.read_text(encoding="utf-8"), sentinel)

    def test_suggests_non_overlapping_ids_for_multiple_duplicate_files(self) -> None:
        sentinel = "unchanged\n"
        self.index_path.write_text(sentinel, encoding="utf-8")
        duplicate_body = "\n".join(
            [
                "# ADR-20260306-0001-ABC: Duplicate decision",
                "Date: 2026-03-06",
            ]
        )
        self._write_adr("alpha.md", duplicate_body + "\n")
        self._write_adr("beta.md", duplicate_body + "\n")
        self._write_adr("gamma.md", duplicate_body + "\n")

        result = self._run_script()

        self.assertEqual(result.returncode, 1)
        self.assertIn("  change: docs/adr/beta.md", result.stderr)
        self.assertIn("  change: docs/adr/gamma.md", result.stderr)
        suggestion_groups = self._suggested_ids_from_error(result.stderr)
        self.assertEqual(len(suggestion_groups), 2)
        flattened = [item for group in suggestion_groups for item in group]
        self.assertEqual(len(flattened), 6)
        self.assertEqual(len(set(flattened)), 6)
        for suggestion in flattened:
            self.assertRegex(suggestion, r"^ADR-20260306-\d{4}-[0-9A-Z]{3}$")
            self.assertNotEqual(suggestion, "ADR-20260306-0001-ABC")
        self.assertEqual(self.index_path.read_text(encoding="utf-8"), sentinel)

    def test_reports_when_no_replacement_ids_are_available(self) -> None:
        sentinel = "unchanged\n"
        self.index_path.write_text(sentinel, encoding="utf-8")
        duplicate_body = "\n".join(
            [
                "# ADR-20260306-9999-ABC: Exhausted decision",
                "Date: 2026-03-06",
            ]
        )
        self._write_adr("alpha.md", duplicate_body + "\n")
        self._write_adr("beta.md", duplicate_body + "\n")

        result = self._run_script()

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr.strip(),
            "No replacement ADR IDs available for docs/adr/beta.md: "
            "sequence space exhausted for date 20260306",
        )
        self.assertEqual(self.index_path.read_text(encoding="utf-8"), sentinel)

    def test_rejects_date_mismatch_without_writing_index(self) -> None:
        sentinel = "unchanged\n"
        self.index_path.write_text(sentinel, encoding="utf-8")
        self._write_adr(
            "alpha.md",
            "\n".join(
                [
                    "# ADR-20260306-0001-ABC: First decision",
                    "Date: 2026-03-05",
                ]
            )
            + "\n",
        )

        result = self._run_script()

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr.strip(),
            "Header date does not match Date in docs/adr/alpha.md: "
            "header=2026-03-06, Date=2026-03-05",
        )
        self.assertEqual(self.index_path.read_text(encoding="utf-8"), sentinel)


if __name__ == "__main__":
    unittest.main()
