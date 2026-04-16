"""Checks for the theorem-grade active-branch theta-star closure."""

from __future__ import annotations

import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator import compute_active_branch_theta_star  # noqa: E402
from aio_calculator.constants import ACTIVE_BRANCH_THETA_STAR_SELECTOR_Z  # noqa: E402
from aio_calculator.selector import observer_theta100_to_phase_equivalent_redshift  # noqa: E402


def test_active_branch_theta_star_theorem_round_trips_selector_leaf() -> None:
    """The theorem payload should invert back to its carried selector leaf."""

    result = compute_active_branch_theta_star()
    assert result.claim_status.startswith("derived / scoped")
    assert math.isclose(
        result.selector_leaf_z,
        ACTIVE_BRANCH_THETA_STAR_SELECTOR_Z,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )
    assert math.isclose(
        observer_theta100_to_phase_equivalent_redshift(result.theta_star_100),
        result.selector_leaf_z,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )
    assert math.isclose(
        result.theta_star_100,
        1.048683904878751,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )
    assert math.isclose(
        result.selector_roundtrip_error,
        0.0,
        rel_tol=0.0,
        abs_tol=1.0e-18,
    )
