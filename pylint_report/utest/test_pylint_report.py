"""Utests for :mod:`project_factory`."""
import filecmp
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

import pytest

# pylint: disable=wrong-import-position
UTEST_DIR = Path(__file__).resolve().parent
sys.path.append(str(UTEST_DIR / "../.."))
from pylint_report.pylint_report import main

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

    def test_json(self):
        """Test creating json file."""
        tmp_dest = Path(tempfile.mkdtemp(prefix="pylint_report_test_"))
        cmd = [
            "pylint",
            "--load-plugins",
            "pylint_report",
            "--output-format",
            "pylint_report.CustomJsonReporter",
            *[str(p) for p in sorted(RESOURCES_DIR.glob("*.py"))],
        ]
        # pylint: disable=subprocess-run-check
        with open(tmp_dest / ".pylint_report_utest.json", "w", encoding="utf-8") as h:
            subprocess.run(cmd, stdout=h)

        with open(tmp_dest / ".pylint_report_utest.json", "r", encoding="utf-8") as h:
            data = json.load(h)

        self.assertTrue("messages" in data)
        self.assertTrue("stats" in data)
        self.assertTrue("statement" in data["stats"])
        self.assertTrue("error" in data["stats"])
        self.assertTrue("warning" in data["stats"])
        self.assertTrue("refactor" in data["stats"])
        self.assertTrue("convention" in data["stats"])
        self.assertTrue("by_module" in data["stats"])
        self.assertTrue("resources.__init__" in data["stats"]["by_module"])
        self.assertTrue("resources.linting_problems" in data["stats"]["by_module"])
        self.assertTrue("resources.more_problems" in data["stats"]["by_module"])
        self.assertTrue("resources.no_problems" in data["stats"]["by_module"])

        # probably this will fail with future versions of pylint
        # self.assertTrue(
        #     filecmp.cmp(
        #         RESOURCES_DIR / ".pylint_report_utest.json",
        #         tmp_dest / ".pylint_report_utest.json",
        #         shallow=False,
        #     )
        # )

        shutil.rmtree(tmp_dest)
