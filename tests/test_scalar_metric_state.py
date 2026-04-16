"""Checks for the Einstein-side scalar metric-state builders."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator.scalar_hierarchy import build_scalar_hierarchy_carrier  # noqa: E402
from aio_calculator.scalar_metric_state import (  # noqa: E402
    build_newtonian_scalar_metric_state,
    build_scalar_stress_energy_summary,
    build_synchronous_scalar_metric_state,
    newtonian_constraint_phi,
)


def test_newtonian_metric_state_matches_closed_scalar_einstein_equations() -> None:
    """Newtonian-gauge metric quantities should follow the exact source formulas."""

    carrier = build_scalar_hierarchy_carrier(4, curvature_radius_mpc=2.0)
    stress = build_scalar_stress_energy_summary(
        delta_rho=0.3,
        delta_p=0.1,
        rho_plus_p_theta=0.2,
        rho_plus_p_shear=0.4,
    )
    state = build_newtonian_scalar_metric_state(
        carrier,
        stress,
        scale_factor=0.5,
        a_prime_over_a_mpc_inv=1.2,
        phi=0.7,
    )
    k_sq = carrier.mode.primary_spatial_eigenvalue / carrier.curvature_radius_mpc**2
    expected_psi = 0.7 - 4.5 * (0.5 * 0.5 / k_sq) * 0.4
    expected_phi_prime = -1.2 * expected_psi + 1.5 * (0.5 * 0.5 / k_sq) * 0.2
    assert math.isclose(state.psi, expected_psi, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(state.phi_prime, expected_phi_prime, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(state.acoustic_drive.metric_continuity, -3.0 * expected_phi_prime, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(state.acoustic_drive.metric_euler, k_sq * expected_psi, rel_tol=0.0, abs_tol=1.0e-15)


def test_newtonian_constraint_phi_uses_shifted_closed_scalar_denominator() -> None:
    """The closed Newtonian energy constraint must use `k^2 (k^2-3K)`."""

    carrier = build_scalar_hierarchy_carrier(4, curvature_radius_mpc=2.0)
    stress = build_scalar_stress_energy_summary(
        delta_rho=0.3,
        delta_p=0.1,
        rho_plus_p_theta=0.2,
        rho_plus_p_shear=0.4,
    )
    phi = newtonian_constraint_phi(
        carrier,
        stress,
        scale_factor=0.5,
        a_prime_over_a_mpc_inv=1.2,
    )
    k_sq = carrier.mode.primary_spatial_eigenvalue / carrier.curvature_radius_mpc**2
    shifted_sq = (carrier.mode.shifted_scalar_operator or 0.0) / carrier.curvature_radius_mpc**2
    expected = -1.5 * (0.5 * 0.5) * (k_sq * 0.3 + 3.0 * 1.2 * 0.2) / (k_sq * shifted_sq)
    assert math.isclose(phi, expected, rel_tol=0.0, abs_tol=1.0e-15)


def test_synchronous_metric_state_matches_closed_scalar_einstein_equations() -> None:
    """Synchronous-gauge metric quantities should follow the exact source formulas."""

    carrier = build_scalar_hierarchy_carrier(5, curvature_radius_mpc=3.0)
    stress = build_scalar_stress_energy_summary(
        delta_rho=0.2,
        delta_p=0.05,
        rho_plus_p_theta=0.15,
        rho_plus_p_shear=0.07,
    )
    state = build_synchronous_scalar_metric_state(
        carrier,
        stress,
        scale_factor=0.4,
        a_prime_over_a_mpc_inv=0.9,
        eta=0.12,
    )
    curvature_k = 1.0 / carrier.curvature_radius_mpc**2
    k_sq = carrier.mode.primary_spatial_eigenvalue / carrier.curvature_radius_mpc**2
    s2_squared = 1.0 - 3.0 * curvature_k / k_sq
    a_sq = 0.4 * 0.4
    expected_h_prime = (k_sq * s2_squared * 0.12 + 1.5 * a_sq * 0.2) / (0.5 * 0.9)
    expected_eta_prime = (1.5 * a_sq * 0.15 + 0.5 * curvature_k * expected_h_prime) / (k_sq * s2_squared)
    expected_h_prime_prime = -2.0 * 0.9 * expected_h_prime + 2.0 * k_sq * s2_squared * 0.12 - 9.0 * a_sq * 0.05
    expected_alpha = (expected_h_prime + 6.0 * expected_eta_prime) / (2.0 * k_sq)
    expected_alpha_prime = -2.0 * 0.9 * expected_alpha + 0.12 - 4.5 * (a_sq / k_sq) * 0.07
    assert math.isclose(state.h_prime, expected_h_prime, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(state.eta_prime, expected_eta_prime, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(state.h_prime_prime, expected_h_prime_prime, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(state.alpha, expected_alpha, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(state.alpha_prime, expected_alpha_prime, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(state.acoustic_drive.metric_continuity, 0.5 * expected_h_prime, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(state.acoustic_drive.metric_shear, k_sq * expected_alpha, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(state.acoustic_drive.metric_shear_prime, k_sq * expected_alpha_prime, rel_tol=0.0, abs_tol=1.0e-15)


def test_metric_state_rejects_zero_conformal_hubble_in_synchronous_gauge() -> None:
    """The synchronous builder should reject the Einstein singular denominator."""

    carrier = build_scalar_hierarchy_carrier(4, curvature_radius_mpc=2.0)
    stress = build_scalar_stress_energy_summary(
        delta_rho=0.1,
        delta_p=0.1,
        rho_plus_p_theta=0.1,
        rho_plus_p_shear=0.1,
    )
    with pytest.raises(ValueError):
        build_synchronous_scalar_metric_state(
            carrier,
            stress,
            scale_factor=0.5,
            a_prime_over_a_mpc_inv=0.0,
            eta=0.1,
        )


def test_stress_summary_carries_normalization_and_scope() -> None:
    """The stress-energy carrier should expose the theorem text directly."""

    stress = build_scalar_stress_energy_summary(
        delta_rho=0.1,
        delta_p=0.2,
        rho_plus_p_theta=0.3,
        rho_plus_p_shear=0.4,
    )
    assert "Einstein-normalized scalar totals" in stress.normalization
    assert stress.claim_status == "derived / scoped explicit Einstein-side source carrier"
    assert stress.provenance_node_ids == (
        "paper23.closed_scalar_operator",
        "local.closed_scalar_metric_state_builder",
    )
