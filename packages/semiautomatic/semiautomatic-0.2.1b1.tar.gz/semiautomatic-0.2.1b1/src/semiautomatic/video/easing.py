"""
Easing curve functions for speed ramping effects.

Library usage:
    from semiautomatic.video.easing import apply_easing_curve
    t_remapped = apply_easing_curve(0.5, "ease-in-out")
"""

from __future__ import annotations

from typing import Literal

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EasingCurve = Literal[
    "linear",
    "ease-in",
    "ease-in-cubic",
    "ease-in-quartic",
    "ease-in-quintic",
    "ease-out",
    "ease-in-out",
    "ease-out-in",
]

EASING_CURVES: list[str] = [
    "ease-in",
    "ease-in-cubic",
    "ease-in-quartic",
    "ease-in-quintic",
    "ease-out",
    "ease-in-out",
    "ease-out-in",
]

# ---------------------------------------------------------------------------
# Easing Functions
# ---------------------------------------------------------------------------


def ease_in(t: float) -> float:
    """Ease-in curve: accelerates (quadratic)."""
    return t * t


def ease_in_cubic(t: float) -> float:
    """Ease-in cubic: more aggressive acceleration."""
    return t * t * t


def ease_in_quartic(t: float) -> float:
    """Ease-in quartic: very aggressive acceleration."""
    return t * t * t * t


def ease_in_quintic(t: float) -> float:
    """Ease-in quintic: extremely aggressive acceleration."""
    return t * t * t * t * t


def ease_out(t: float) -> float:
    """Ease-out curve: decelerates."""
    return 1 - (1 - t) * (1 - t)


def ease_in_out(t: float) -> float:
    """Ease-in-out curve: slow at start/end, fast in middle."""
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - 2 * (1 - t) * (1 - t)


def ease_out_in(t: float) -> float:
    """Ease-out-in curve: fast-slow-fast (whip effect)."""
    if t < 0.5:
        return 0.5 - 0.5 * (1 - 2 * t) * (1 - 2 * t)
    else:
        return 0.5 + 0.5 * (2 * t - 1) * (2 * t - 1)


def apply_easing_curve(t: float, curve_type: str) -> float:
    """
    Apply easing curve to normalized time value (0-1).

    Args:
        t: Normalized time value between 0 and 1
        curve_type: Name of the easing curve to apply

    Returns:
        Remapped time value with easing applied
    """
    if curve_type == "ease-in-out":
        return ease_in_out(t)
    elif curve_type == "ease-out-in":
        return ease_out_in(t)
    elif curve_type == "ease-in":
        return ease_in(t)
    elif curve_type == "ease-in-cubic":
        return ease_in_cubic(t)
    elif curve_type == "ease-in-quartic":
        return ease_in_quartic(t)
    elif curve_type == "ease-in-quintic":
        return ease_in_quintic(t)
    elif curve_type == "ease-out":
        return ease_out(t)
    else:  # linear
        return t
