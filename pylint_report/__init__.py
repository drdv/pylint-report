"""Module interface."""
try:
    from ._version import __version__
except ModuleNotFoundError:  # pragma: no cover
    __version__ = "unknown (package not installed)"

from pylint_report.pylint_report import CustomJsonReporter, register
