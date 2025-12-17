"""
Signal plugins for GADE difficulty measurement.

Each signal is normalized to [0, 1] range.
"""

from gade.signals.base import SignalPlugin
from gade.signals.edit_churn import EditChurnSignal
from gade.signals.error_density import ErrorDensitySignal
from gade.signals.gradient import GradientProxySignal
from gade.signals.semantic_complexity import SemanticComplexitySignal
from gade.signals.uncertainty import UncertaintyProxySignal

__all__ = [
    "SignalPlugin",
    "EditChurnSignal",
    "ErrorDensitySignal",
    "GradientProxySignal",
    "SemanticComplexitySignal",
    "UncertaintyProxySignal",
]


def get_all_signals() -> list[SignalPlugin]:
    """Return instances of all available signal plugins."""
    return [
        EditChurnSignal(),
        ErrorDensitySignal(),
        SemanticComplexitySignal(),
        UncertaintyProxySignal(),
        GradientProxySignal(),
    ]
