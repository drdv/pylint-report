#!/usr/bin/env python3
"""Custom JSON reporter for pylint, and JSON to HTML export utility."""
import argparse
import html
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from pylint.reporters.base_reporter import BaseReporter

CURRENT_DIR = Path(__file__).resolve().parent

COLS2KEEP = ["line", "column", "symbol", "type", "obj", "message"]

HTML_HEAD = """<!DOCTYPE HTML>
<html lang="en">
<head>
  <title>Pylint report</title>
  <meta charset="utf-8">
  <style>
  {style}
  </style>
</head>
"""

SECTION = """
<br>\n<hr>
<section>
<h2>
  <span>Module:</span>
  <span id="{module}"> <code>{module} ({count})</code> </span>
</h2>
<hr><table><tr>
\n<td>\n
  {by_symbol}
\n</td>\n
\n<td>\n
  {by_type}
\n</td>\n
</tr></table>
  {msg}
\n</section>\n
"""

SCORE = """
<h2>
  <span>Score:</span>
  <span class="score"> {score:.2f} </span>
  <span> / 10 </span>
</h2>
"""

REPORT_HEADER = """
<small>
  Report generated on {date} at {time} using <a href="https://github.com/drdv/pylint-report">pylint-report</a>
</small>
"""


def get_score(stats):
    """Compute score.

    Note
    -----
    https://pylint.pycqa.org/en/latest/user_guide/configuration/all-options.html#evaluation

    """
    f = stats.get("fatal", False)
    e = stats.get("error", 0)
    w = stats.get("warning", 0)
    r = stats.get("refactor", 0)
    c = stats.get("convention", 0)
    s = stats.get("statement", 0)

    if s == 0:
        return None
    return max(0, 0 if f else 10 * (1 - ((5 * e + w + r + c) / s)))


def json2html(data, css_file=None):
    """Generate an html file (based on :obj:`data`)."""

    if css_file is None:
        css_file = CURRENT_DIR / "style/default.css"

    with open(css_file, "r") as h:
        out = HTML_HEAD.format(style=h.read())

    out += "<body>\n<h1><u>Pylint report</u></h1>\n"

    now = datetime.now()
    out += REPORT_HEADER.format(
        date=now.strftime("%Y-%d-%m"), time=now.strftime("%H:%M:%S")
    )

    s = get_score(data["stats"])
    out += SCORE.format(score=s if s is not None else -1)

    msg = {}
    if data["messages"]:
        msg = {
            name: df.sort_values(["line", "column"]).reset_index(drop=True)
            for name, df in pd.DataFrame(data["messages"]).groupby("module")
        }

    # modules summary
    out += "<ul>"
    for module in data["stats"]["by_module"].keys():
        if module in msg:
            out += '<li><a href="#{module}">{module}</a> ({numb})</li>\n'.format(
                module=module, numb=len(msg[module])
            )
        else:
            out += f"<li>{module} (0)</li>\n"
    out += "</ul>"

    # modules
    for module, value in msg.items():
        by_symbol = (
            value.groupby("symbol")["module"]
            .count()
            .to_frame()
            .reset_index()
            .rename(columns={"module": "# msg"})
            .to_html(index=False, justify="center")
        )

        by_type = (
            value.groupby("type")["module"]
            .count()
            .to_frame()
            .reset_index()
            .rename(columns={"module": "# msg"})
            .to_html(index=False, justify="center")
        )

        msg_html = value[COLS2KEEP].to_html(justify="center").replace("\\n", "<br>")
        out += SECTION.format(
            module=module,
            count=len(value),
            msg=msg_html,
            by_symbol=by_symbol,
            by_type=by_type,
        )

    # end of document
    out += "</body>\n</html>"
    return out


class _SetEncoder(json.JSONEncoder):
    """Handle sets when dumping to json.

    Note
    -----
    See https://stackoverflow.com/a/8230505

    """

    def default(self, o):
        if isinstance(o, set):
            return list(o)
        return json.JSONEncoder.default(self, o)


class CustomJsonReporter(BaseReporter):
    """Customize the default json reporter.

    Note
    -----
    See ``pylint/reporters/json_reporter.py``

    """

    name = "custom json"

    def __init__(self, output=None):
        """Construct object."""
        super().__init__(sys.stdout if output is None else output)
        self.messages = []

    def handle_message(self, msg):
        """Manage message of different type and in the context of path."""
        self.messages.append(
            {
                "type": msg.category,
                "module": msg.module,
                "obj": msg.obj,
                "line": msg.line,
                "column": msg.column,
                "path": msg.path,
                "symbol": msg.symbol,
                "message": html.escape(msg.msg or "", quote=False),
                "message-id": msg.msg_id,
            }
        )

    def display_messages(self, layout):
        """See ``pylint/reporters/base_reporter.py``."""

    def display_reports(self, layout):
        """See ``pylint/reporters/base_reporter.py``."""

    def _display(self, layout):
        """See ``pylint/reporters/base_reporter.py``."""

    def on_close(self, stats, previous_stats):
        """See ``pylint/reporters/base_reporter.py``."""
        if not isinstance(stats, dict):  # behavior from version 2.12.0
            stats = {
                key: getattr(stats, key)
                for key in [
                    "by_module",
                    "statement",
                    "error",
                    "warning",
                    "refactor",
                    "convention",
                ]
            }

        print(
            json.dumps(
                {"messages": self.messages, "stats": stats}, cls=_SetEncoder, indent=2
            ),
            file=self.out,
        )


def register(linter):
    """Register a reporter (required by :mod:`pylint`)."""
    linter.register_reporter(CustomJsonReporter)


def get_parser():
    """Define cli parser."""
    parser = argparse.ArgumentParser()

    # see https://stackoverflow.com/a/11038508
    parser.add_argument(
        "json_file",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Json file/stdin generated by pylint.",
    )
    parser.add_argument(
        "-o",
        "--html-file",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Name of html file to generate.",
    )
    parser.add_argument(
        "-s",
        "--score",
        action="store_true",
        help="Output only the score.",
    )

    return parser


def main():
    """Main."""
    args = get_parser().parse_args()

    with args.json_file as h:
        json_data = json.load(h)

    if args.score:
        score = get_score(json_data["stats"])
        print(f"pylint score: {score:.2f}", file=sys.stdout)
    else:
        print(json2html(json_data), file=args.html_file)


if __name__ == "__main__":
    main()
