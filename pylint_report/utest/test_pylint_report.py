"""Utests for :mod:`project_factory`."""
import filecmp
import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

import pytest
from pylint.lint import Run

from pylint_report.pylint_report import get_score

UTEST_DIR = Path(__file__).resolve().parent
sys.path.append(str(UTEST_DIR / "../.."))

# pylint: disable=wrong-import-position
from pylint_report.pylint_report import _SetEncoder, main

RESOURCES_DIR = UTEST_DIR / "resources"


class TestPylintReport(unittest.TestCase):
    """Utests."""

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, capfd):
        """https://stackoverflow.com/a/50375022"""
        # pylint: disable=attribute-defined-outside-init
        self._capfd = capfd

    def test_json_to_html(self):
        """Test creating html from a given json file.

        Note
        -----
        Since the json file is pre-generated and the versions of pands and Jinja2
        are fixed, the generated html file should be the same as the reference one.

        """
        tmp_dest = Path(tempfile.mkdtemp(prefix="pylint_report_test_"))
        params = [
            str(RESOURCES_DIR / ".pylint_report_utest.json"),
            "-o",
            str(tmp_dest / ".pylint_report_utest.html"),
        ]

        with mock.patch("pylint_report.pylint_report.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2022, 12, 10, 9, 28, 26)
            main(params)
        out, _ = self._capfd.readouterr()
        self.assertEqual("", out.strip())
        self.assertTrue(
            filecmp.cmp(
                RESOURCES_DIR / ".pylint_report_utest.html",
                tmp_dest / ".pylint_report_utest.html",
                shallow=False,
            )
        )
        shutil.rmtree(tmp_dest)

    def test_json_to_html_css(self):
        """Test creating html with external css file."""
        tmp_dest = Path(tempfile.mkdtemp(prefix="pylint_report_test_"))
        params = [
            "-e",
            str(RESOURCES_DIR / ".pylint_report_utest.json"),
            "-o",
            str(tmp_dest / ".pylint_report_utest.html"),
        ]

        main(params)
        with open(tmp_dest / ".pylint_report_utest.html", "r", encoding="utf-8") as h:
            data = h.read()
        self.assertTrue('<link rel="stylesheet" href="pylint-report.css">' in data)
        shutil.rmtree(tmp_dest)

    def test_json_to_html_no_messages(self):
        """Test creating html without messages."""
        tmp_dest = Path(tempfile.mkdtemp(prefix="pylint_report_test_"))
        params = [
            "-e",
            str(RESOURCES_DIR / ".pylint_report_utest_no_messages.json"),
            "-o",
            str(tmp_dest / ".pylint_report_utest.html"),
        ]

        main(params)
        with open(tmp_dest / ".pylint_report_utest.html", "r", encoding="utf-8") as h:
            data = h.read()

        for key in ["__init__", "linting_problems", "more_problems", "no_problems"]:
            self.assertTrue(f"resources.{key} (0)" in data)

        shutil.rmtree(tmp_dest)

    def test_json(self):
        """Test creating json file."""
        tmp_dest = Path(tempfile.mkdtemp(prefix="pylint_report_test_"))
        cmd = [
            "--load-plugins",
            "pylint_report",
            "--output-format",
            "pylint_report.CustomJsonReporter",
            *[str(p) for p in sorted(RESOURCES_DIR.glob("*.py"))],
        ]

        with open(
            tmp_dest / ".pylint_report_utest.json",
            "w",
            encoding="utf-8",
        ) as sys.stdout:
            Run(cmd, exit=False)

        with open(tmp_dest / ".pylint_report_utest.json", "r", encoding="utf-8") as h:
            data = json.load(h)

        for key in ["messages", "stats"]:
            self.assertTrue(key in data)

        # pylint: disable=duplicate-code
        for key in [
            "statement",
            "error",
            "warning",
            "refactor",
            "convention",
            "by_module",
        ]:
            self.assertTrue(key in data["stats"])

        for key in ["__init__", "linting_problems", "more_problems", "no_problems"]:
            self.assertTrue(f"resources.{key}" in data["stats"]["by_module"])

        shutil.rmtree(tmp_dest)

    def test_get_score(self):
        """Test get_score."""
        score = get_score(
            {
                "fatal": 0,
                "error": 0,
                "warning": 0,
                "refactor": 0,
                "convention": 0,
                "statement": 0,
            }
        )
        self.assertTrue(score is None)

    def test_SetEncoder(self):
        "Test _SetEncoder."
        se = _SetEncoder()
        res = se.default({1, 2, 3})
        self.assertTrue(isinstance(res, list))
        with pytest.raises(TypeError):
            self.assertTrue(se.default(1))
