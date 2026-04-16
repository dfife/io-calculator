"""Checks for the exact closed-`S^3` shell-power definitions."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator.closed_shell_power import (  # noqa: E402
    closed_shell_power_support,
    covariance_from_delta_ms,
    covariance_from_delta_q,
    covariance_from_delta_scalar,
    delta_ms_prefactor,
    delta_q_prefactor,
    delta_scalar_prefactor,
    ms_shell_wavenumber,
    q_shell_wavenumber,
    s3_shell_degeneracy,
    s3_volume,
    scalar_shell_wavenumber,
    shell_variance_prefactor,
)


def test_closed_shell_support_exposes_exact_prefactors() -> None:
    """The shell package should match the exact Paper 28 closed-geometry formulas."""

    support = closed_shell_power_support(5, radius=1.0)
    volume = 2.0 * math.pi * math.pi
    assert support.shell_degeneracy == 36
    assert math.isclose(support.shell_variance_prefactor, 36.0 / volume, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(support.q_shell, 6.0, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(support.scalar_shell, math.sqrt(35.0), rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(support.ms_shell or 0.0, math.sqrt(32.0), rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(support.delta_q_prefactor, 216.0 / volume, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(support.delta_scalar_prefactor, 210.0 / volume, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(support.delta_ms_prefactor or 0.0, 192.0 / volume, rel_tol=0.0, abs_tol=1.0e-15)
    assert support.provenance_node_ids == ("paper28.closed_s3_shell_power",)


def test_closed_shell_helper_functions_match_support_object() -> None:
    """The helper functions should agree with the packaged shell support."""

    radius = 2.5
    n = 10
    support = closed_shell_power_support(n, radius=radius)
    assert s3_shell_degeneracy(n) == support.shell_degeneracy
    assert math.isclose(s3_volume(radius), 2.0 * math.pi * math.pi * radius**3, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(q_shell_wavenumber(n, radius=radius), support.q_shell, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(
        scalar_shell_wavenumber(n, radius=radius),
        support.scalar_shell,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )
    assert math.isclose(
        ms_shell_wavenumber(n, radius=radius),
        support.ms_shell or 0.0,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )
    assert math.isclose(
        shell_variance_prefactor(n, radius=radius),
        support.shell_variance_prefactor,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )
    assert math.isclose(delta_q_prefactor(n, radius=radius), support.delta_q_prefactor, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(
        delta_scalar_prefactor(n, radius=radius),
        support.delta_scalar_prefactor,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )
    assert math.isclose(
        delta_ms_prefactor(n, radius=radius),
        support.delta_ms_prefactor or 0.0,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )


def test_covariance_round_trips_through_all_three_conventions() -> None:
    """All exact shell conventions should invert back to the same covariance."""

    covariance = 1.2345e-6
    n = 7
    radius = 3.0
    assert math.isclose(
        covariance_from_delta_q(delta_q_prefactor(n, radius=radius) * covariance, n, radius=radius),
        covariance,
        rel_tol=0.0,
        abs_tol=1.0e-18,
    )
    assert math.isclose(
        covariance_from_delta_scalar(
            delta_scalar_prefactor(n, radius=radius) * covariance,
            n,
            radius=radius,
        ),
        covariance,
        rel_tol=0.0,
        abs_tol=1.0e-18,
    )
    assert math.isclose(
        covariance_from_delta_ms(delta_ms_prefactor(n, radius=radius) * covariance, n, radius=radius),
        covariance,
        rel_tol=0.0,
        abs_tol=1.0e-18,
    )


def test_ms_shell_formulas_refuse_nonphysical_scalar_shells() -> None:
    """The Mukhanov-Sasaki shell variable should stay on the physical branch only."""

    with pytest.raises(ValueError):
        ms_shell_wavenumber(1, radius=1.0)
    with pytest.raises(ValueError):
        delta_ms_prefactor(1, radius=1.0)
