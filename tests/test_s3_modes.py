"""Checks for the theorem-grade closed-`S^3` mode registry."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator.s3_modes import (  # noqa: E402
    S3Channel,
    closed_k_squared_from_q,
    closed_q_squared,
    closed_supports_ell,
    hyperspherical_nu,
    scalar_mode,
    tensor_mode,
    vector_mode,
)


def test_scalar_mode_carries_closed_shift_and_role_boundaries() -> None:
    """Scalar shells should expose both the Paper 22 and Paper 23 data."""

    mode = scalar_mode(2)
    assert mode.channel is S3Channel.SCALAR
    assert mode.primary_spatial_operator == "scalar_hodge_laplacian"
    assert math.isclose(mode.primary_spatial_eigenvalue, 8.0, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(mode.shifted_scalar_operator or 0.0, 5.0, rel_tol=0.0, abs_tol=1.0e-15)
    assert mode.multiplicity == 9
    assert mode.diagonal_spin_range == (0, 2)
    assert mode.physical_role == "physical"
    assert mode.provenance_node_ids == (
        "paper22.spatial_mode_ladder",
        "paper23.closed_scalar_operator",
    )


def test_scalar_mode_marks_background_and_gauge_shells_explicitly() -> None:
    """The non-physical scalar shells should stay visible instead of being hidden."""

    assert scalar_mode(0).physical_role == "background"
    assert scalar_mode(1).physical_role == "gauge"


def test_vector_and_tensor_modes_match_paper22_s3_branch_formulas() -> None:
    """Vector and tensor ladders should preserve the Paper 22 multiplicities."""

    vector = vector_mode(3)
    assert vector.channel is S3Channel.VECTOR
    assert math.isclose(vector.primary_spatial_eigenvalue, 16.0, rel_tol=0.0, abs_tol=1.0e-15)
    assert vector.multiplicity == 30
    assert vector.diagonal_spin_range == (1, 3)

    tensor = tensor_mode(4)
    assert tensor.channel is S3Channel.TENSOR
    assert tensor.primary_spatial_operator == "tt_rough_laplacian"
    assert math.isclose(tensor.primary_spatial_eigenvalue, 22.0, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(
        tensor.lichnerowicz_eigenvalue or 0.0,
        28.0,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )
    assert tensor.multiplicity == 42
    assert tensor.diagonal_spin_range == (2, 4)


def test_closed_q_ladder_round_trips_by_channel() -> None:
    """The Paper 32 closed `q` ladder should invert channel by channel."""

    for channel, expected_floor in (
        (S3Channel.SCALAR, 1.0),
        (S3Channel.VECTOR, 2.0),
        (S3Channel.TENSOR, 3.0),
    ):
        q_sq = closed_q_squared(5.0, 1.0, channel)
        assert math.isclose(q_sq, 25.0 + expected_floor, rel_tol=0.0, abs_tol=1.0e-15)
        assert math.isclose(
            closed_k_squared_from_q(math.sqrt(q_sq), 1.0, channel),
            25.0,
            rel_tol=0.0,
            abs_tol=1.0e-12,
        )


def test_closed_support_rule_uses_ell_strictly_below_nu() -> None:
    """The closed transfer support should remain the audited `ell < nu` rule."""

    nu = hyperspherical_nu(4.0, 1.0)
    assert math.isclose(nu, 4.0, rel_tol=0.0, abs_tol=1.0e-15)
    assert closed_supports_ell(3, 4.0, 1.0) is True
    assert closed_supports_ell(4, 4.0, 1.0) is False


def test_closed_q_ladder_rejects_subfloor_shells() -> None:
    """The inverse map should refuse `q` below the geometric curvature floor."""

    with pytest.raises(ValueError):
        closed_k_squared_from_q(0.5, 1.0, S3Channel.TENSOR)
