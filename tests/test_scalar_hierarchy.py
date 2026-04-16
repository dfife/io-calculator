"""Checks for the theorem-grade scalar closed-`S^3` hierarchy skeleton."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator.recombination import OpenTheoremBoundaryError, Stage2History  # noqa: E402
from aio_calculator.scalar_hierarchy import (  # noqa: E402
    ScalarHierarchyState,
    build_scalar_hierarchy_carrier,
    evolve_scalar_hierarchy_step,
    make_scalar_hierarchy_step_request,
)
from aio_calculator.thomson_history_contract import build_thomson_history_contract  # noqa: E402


def test_scalar_hierarchy_carrier_uses_physical_shell_and_hyperspherical_support() -> None:
    """The scalar hierarchy carrier should expose the physical shell data only."""

    carrier = build_scalar_hierarchy_carrier(5, curvature_radius_mpc=2.0)
    assert carrier.mode.n == 5
    assert math.isclose(
        carrier.shell_wavenumber_sq_mpc_inv2,
        8.0,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )
    assert carrier.ell_min == 0
    assert carrier.ell_max == 5
    assert carrier.supports_ell(0) is True
    assert carrier.supports_ell(5) is True
    assert carrier.supports_ell(6) is False


def test_scalar_hierarchy_rejects_background_and_gauge_shells() -> None:
    """The hierarchy layer should not silently promote non-physical scalar shells."""

    with pytest.raises(ValueError):
        build_scalar_hierarchy_carrier(1, curvature_radius_mpc=1.0)


def test_scalar_hierarchy_state_validates_finite_values() -> None:
    """The typed state container should reject NaNs immediately."""

    with pytest.raises(ValueError):
        ScalarHierarchyState(
            phi=float("nan"),
            psi=0.0,
            delta_gamma=0.0,
            theta_gamma=0.0,
            delta_b=0.0,
            theta_b=0.0,
        )


def test_scalar_hierarchy_step_request_stops_at_open_operator_boundary() -> None:
    """The request carrier should be buildable even though the update remains open."""

    carrier = build_scalar_hierarchy_carrier(4, curvature_radius_mpc=1.0)
    state = ScalarHierarchyState(
        phi=1.0e-5,
        psi=1.0e-5,
        delta_gamma=2.0e-5,
        theta_gamma=3.0e-5,
        delta_b=4.0e-5,
        theta_b=5.0e-5,
        photon_multipoles=(1.0e-6, 2.0e-6),
        polarization_multipoles=(3.0e-6,),
    )
    history = Stage2History.from_sequences(
        [900.0, 1100.0],
        [1.0e-3, 2.0e-3],
        [2500.0, 2900.0],
    )
    thomson = build_thomson_history_contract(
        [900.0, 1100.0],
        [10.0, 12.0],
        [11.0, 13.0],
        [-1.0, -1.5],
        [1.0e-5, 2.0e-5],
        [3.0e-5, 4.0e-5],
    )
    request = make_scalar_hierarchy_step_request(carrier, state, history, thomson)
    assert request.perturbation_inputs.mode.n == 4
    assert request.thomson_history.claim_status == "derived / scoped"
    assert request.claim_status == "derived / scoped request carrier"
    with pytest.raises(OpenTheoremBoundaryError):
        evolve_scalar_hierarchy_step(request)
