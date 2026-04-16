"""Numerical checks for the publishable late-time/background calculator.

These tests are intentionally direct. Each assertion locks one carried value
that the public calculator is expected to reproduce from the active branch.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator import CurvedBackgroundModel, late_eta_io
from aio_calculator.constants import ACTIVE_BRANCH


def test_active_branch_constants() -> None:
    """The calculator should expose the exact carried active-branch package."""

    assert math.isclose(ACTIVE_BRANCH.H0, 67.57585653582628, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(
        ACTIVE_BRANCH.Omega_m, 0.34868395067621694, rel_tol=0.0, abs_tol=1.0e-15
    )
    assert math.isclose(
        ACTIVE_BRANCH.Omega_k, -0.04579112576013168, rel_tol=0.0, abs_tol=1.0e-15
    )


def test_age_today_matches_carried_value() -> None:
    """Present-day age must reproduce the carried Paper 30 late-time value."""

    model = CurvedBackgroundModel()
    assert math.isclose(
        model.age_today_gyr(),
        13.543919214135,
        rel_tol=0.0,
        abs_tol=5.0e-5,
    )


def test_bao_ratios_match_active_branch_rows() -> None:
    """BAO ratios should match the carried active-branch reference rows."""

    model = CurvedBackgroundModel()
    ratios = model.bao_ratios(0.51)
    assert math.isclose(
        ratios["DM_over_rd"],
        13.689801909487425,
        rel_tol=0.0,
        abs_tol=2.0e-5,
    )
    assert math.isclose(
        ratios["DH_over_rd"],
        23.0019673324271,
        rel_tol=0.0,
        abs_tol=2.0e-5,
    )


def test_dv_ratio_matches_active_branch_rows() -> None:
    """The isotropic BAO ratio keeps a second independent row locked down."""

    model = CurvedBackgroundModel()
    ratios = model.bao_ratios(0.295)
    assert math.isclose(
        ratios["DV_over_rd"],
        8.185296666112983,
        rel_tol=0.0,
        abs_tol=2.0e-5,
    )


def test_late_eta_matches_paper35_preferred_value() -> None:
    """Late eta_IO should stay on the preferred Paper 35 convention."""

    assert math.isclose(
        late_eta_io(),
        5.748778515173695e-10,
        rel_tol=0.0,
        abs_tol=5.0e-16,
    )
