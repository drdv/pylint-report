#!/usr/bin/env python3
"""Custom json reporter for pylint and json to html export utility."""
import os
import sys
import json
import html
import argparse
import logging
from datetime import datetime
from glob import glob
from collections import OrderedDict
from pylint.reporters.base_reporter import BaseReporter
import pandas as pd

# pylint: disable=invalid-name

log = logging.getLogger()

HTML_HEAD = """<!DOCTYPE HTML>
<html>
<head>
<title>Pylint report</title>
<meta charset="utf-8">
<style type="text/css">
body {
    font-family: sans-serif;
}

table {
    border-collapse: collapse;
}

th, td {
    padding: 0.5em;
}

th {
    background-color: #8d9db6;
}

tr {
    background-color:white;
}

.score {
    color: red;
}

code {
  font-family: Consolas,"courier new";
  color: blue;
  background-color: #f1f1f1;
  padding: 2px;
  font-size: 105%;
}
</style>
</head>
"""

def get_score(stats):
    """Compute score."""
    if 'statement' not in stats or stats['statement'] == 0:
        return None

    s = stats.get('statement')
    e = stats.get('error', 0)
    w = stats.get('warning', 0)
    r = stats.get('refactor', 0)
    c = stats.get('convention', 0)

    # https://docs.pylint.org/en/1.6.0/faq.html
    return 10 - 10*(5 * e + w + r + c) / s

def get_score_history(score_dir):
    """Return a ordered dict of score history as sha:score pairs.

    Note
    -----
    The following assumptions regarding the score files in score_dir are made:

      - the filenames are ``pylint_NUMBER.SHORT_SHA.log``
      - each file contains only one number (the score)

    Returns
    --------
    :obj:`collections.OrderedDict`
        Sha:score pairs.

    """
    # pylint: disable=redefined-outer-name
    out = OrderedDict()
    for f in sorted(glob(os.path.join(score_dir, 'pylint_*.log'))):
        with open(f) as h:
            s = h.readline(1)
            out[f.split('.')[-2]] = float(s)
    return out

def plot_score_history(scores, fig_name):
    """Plot score history.

    Parameters
    ----------
    scores : :obj:`collections.OrderedDict`
        Scores generated using :func:`get_score_history`.
    fig_name : :obj:`str`
        Name of file where to save the figure.

    """
    try:
        import matplotlib.pyplot as plt
        plt.rcParams.update({'font.size': 18,
                             'axes.titlesize': 18,
                             'axes.labelsize': 18,
                             'xtick.labelsize': 18,
                             'ytick.labelsize': 18,
                             'legend.fontsize': 18,
                             'figure.titlesize': 18})
    except ModuleNotFoundError:
        log.warning('matplotlib not found, plot_score_history cannot be used.')

    plt.figure(figsize=(15, 5))
    plt.plot(list(scores.values()), 'bo--')
    plt.xticks(range(len(scores)), list(scores.keys()), rotation='vertical')
    plt.yticks([2, 4, 6, 8, 10])
    plt.grid(True)
    plt.xlabel('commits')
    plt.ylabel('score')
    plt.autoscale(enable=True, axis='x', tight=True)
    plt.subplots_adjust(bottom=0.35)
    plt.title('Score history')
    plt.savefig(fig_name, dpi=200)

def json2html(data, score_figure=None):
    """Generate an html file (based on :obj:`data`)."""
    out = HTML_HEAD
    out += '<body>\n<h1><u>Pylint report</u></h1>\n'

    now = datetime.now()
    out += ('<small>Report generated on {} at {} by '
            '<a href="https://github.com/drdv/pylint-report">pytest-report</a>'
            '</small>\n'). format(now.strftime('%Y-%d-%m'),
                                  now.strftime('%H:%M:%S'))

    s = get_score(data['stats'])

    score = ('<h2>'
             '<span>Score:</span>'
             '<span class="score"> {:.2f} </span>'
             '<span> / 10 </span>'
             '</h2>')
    out += score.format(s if s is not None else -1)

    if score_figure is not None:
        out += '<img src="{}" alt="Score history" width="70%">\n'.format(score_figure)

    msg = dict()
    if data['messages']:
        msg = {name: df_.sort_values(['line', 'column']).reset_index(drop=True) for
               name, df_ in pd.DataFrame(data['messages']).groupby('module')}

    # modules summary
    out += '<ul>'
    for module in data['stats']['by_module'].keys():
        if module in msg:
            out += '<li><a href="#{0}">{0}</a> ({1})</li>\n'.format(module,
                                                                    len(msg[module]))
        else:
            out += '<li>{} ({})</li>\n'.format(module, 0)
    out += '</ul>'

    # modules
    section = ('<h2>'
               '<span>Module:</span>'
               '<span id="{module}"> <code>{module} ({count})</code> </span>'
               '</h2>')
    cols2keep = ['line', 'column', 'symbol', 'type', 'obj', 'message']
    for module, value in msg.items():
        out += '<br>\n<hr>'
        out += section.format(module=module, count=len(value))
        out += '<hr><table><tr>'

        s1 = value.groupby('symbol')['module'].count().to_frame().reset_index().\
            rename(columns={'module': '# msg'}).to_html(index=False, justify='center')

        s2 = value.groupby('type')['module'].count().to_frame().reset_index().\
            rename(columns={'module': '# msg'}).to_html(index=False, justify='center')

        out += ''.join(['\n<td valign="top">\n' + s1 + '\n</td>\n',
                        '\n<td valign="top">\n' + s2 + '\n</td>\n'])
        out += '</tr></table>'

        out += value[cols2keep].to_html(justify='center').replace('\\n', '<br>')
        out += '\n</section>\n'

    # end of document
    out += '</body>\n</html>'
    return out

class _SetEncoder(json.JSONEncoder):
    """Handle sets when dumping to json.

    Note
    -----
    See https://stackoverflow.com/a/8230505
    """
    # pylint: disable=method-hidden
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

    def __init__(self, output=sys.stdout):
        """Construct object."""
        super().__init__(output)
        self.messages = []

    def handle_message(self, msg):
        """Manage message of different type and in the context of path."""
        self.messages.append({"type": msg.category,
                              "module": msg.module,
                              "obj": msg.obj,
                              "line": msg.line,
                              "column": msg.column,
                              "path": msg.path,
                              "symbol": msg.symbol,
                              "message": html.escape(msg.msg or "", quote=False),
                              "message-id": msg.msg_id})

    def display_messages(self, layout):
        """See ``pylint/reporters/base_reporter.py``."""

    def display_reports(self, layout):
        """See ``pylint/reporters/base_reporter.py``."""

    def _display(self, layout):
        """See ``pylint/reporters/base_reporter.py``."""

    def on_close(self, stats, previous_stats):
        """See ``pylint/reporters/base_reporter.py``."""
        print(json.dumps({'messages': self.messages,
                          'stats': stats,
                          'previous_stats': previous_stats},
                         cls=_SetEncoder, indent=2),
              file=self.out)

def register(linter):
    """Register a reporter (required by :mod:`pylint`)."""
    linter.register_reporter(CustomJsonReporter)

def get_parser():
    """Define command-line argument parser."""
    parser = argparse.ArgumentParser()
    # see https://stackoverflow.com/a/11038508
    parser.add_argument(
        'json_file',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help='Json file/stdin generated by pylint.')
    parser.add_argument(
        '-o', '--html-file',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help='Name of html file to generate.')
    parser.add_argument(
        '-s', '--score',
        action='store_true',
        help='Output only the score.')
    parser.add_argument(
        '--score-history-dir',
        default=None,
        help='Directory with score history.')
    parser.add_argument(
        '--score-history-fig',
        default=None,
        help='Filename where to store the score history figure.')

    return parser

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    args = get_parser().parse_args()

    if args.score_history_dir is not None:
        if args.score_history_fig is not None:
            plot_score_history(get_score_history(args.score_history_dir),
                               args.score_history_fig)
        else:
            log.warning(('Score history figure not generated '
                         '(--score_history-fig flag not provided).'))
    else:
        with args.json_file as h:
            json_data = json.load(h)

        if args.score:
            print('pylint score: {:.2f}'.format(get_score(json_data['stats'])),
                  file=sys.stdout)
        else:
            print(json2html(json_data, args.score_history_fig), file=args.html_file)
