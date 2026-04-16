"""Checks for the active scalar-source to adiabatic-seed bridge."""

from __future__ import annotations

import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator.constants import ACTIVE_BRANCH, ACTIVE_PERTURBATION_PACKAGE, C_KM_S  # noqa: E402
from aio_calculator.model import omega_gamma_h2  # noqa: E402
from aio_calculator.scalar_hierarchy import build_scalar_hierarchy_carrier  # noqa: E402
from aio_calculator.source_block import ACTIVE_SOURCE_PIVOT_SHELL, plus_branch_source_window  # noqa: E402
from aio_calculator.source_initial_conditions import (  # noqa: E402
    build_closed_s3_newtonian_adiabatic_seed,
    build_scalar_source_shell_weight,
)


def test_scalar_source_shell_weight_reproduces_active_source_window() -> None:
    """The source-shell weight should be exactly `A_s W_N^(+)`."""

    pivot = build_scalar_source_shell_weight(ACTIVE_SOURCE_PIVOT_SHELL)
    assert math.isclose(pivot.source_window, 1.0, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(pivot.covariance_weight, ACTIVE_BRANCH.A_s, rel_tol=0.0, abs_tol=1.0e-24)
    assert pivot.supported_by_active_plus_branch is True

    shifted = build_scalar_source_shell_weight(ACTIVE_SOURCE_PIVOT_SHELL + 3)
    assert math.isclose(
        shifted.source_window,
        plus_branch_source_window(ACTIVE_SOURCE_PIVOT_SHELL + 3),
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )
    assert math.isclose(
        shifted.covariance_weight,
        ACTIVE_BRANCH.A_s * shifted.source_window,
        rel_tol=0.0,
        abs_tol=1.0e-24,
    )
    unsupported = build_scalar_source_shell_weight(ACTIVE_SOURCE_PIVOT_SHELL + 1)
    assert unsupported.supported_by_active_plus_branch is False
    assert unsupported.claim_status == "diagnostic / off-support affine continuation"


def test_newtonian_adiabatic_seed_matches_explicit_superhorizon_formulas() -> None:
    """The bridge should expose the closed-shell superhorizon formulas directly."""

    carrier = build_scalar_hierarchy_carrier(4, curvature_radius_mpc=10.0)
    scale_factor = 1.0e-5
    seed = build_closed_s3_newtonian_adiabatic_seed(
        carrier,
        conformal_time_mpc=0.01,
        a_prime_over_a_mpc_inv=100.0,
        scale_factor=scale_factor,
        curvature_amplitude=1.3,
    )
    k_sq = carrier.mode.primary_spatial_eigenvalue / carrier.curvature_radius_mpc**2
    k = math.sqrt(k_sq)
    curvature_k = 1.0 / carrier.curvature_radius_mpc**2
    s2_sq = 1.0 - 3.0 * curvature_k / k_sq
    h = ACTIVE_PERTURBATION_PACKAGE.branch.h
    omega_gamma0 = omega_gamma_h2(ACTIVE_PERTURBATION_PACKAGE.branch.T_cmb) / (h * h)
    omega_r0 = ACTIVE_PERTURBATION_PACKAGE.branch.Omega_r
    omega_nu0 = omega_r0 - omega_gamma0
    omega_b0 = ACTIVE_PERTURBATION_PACKAGE.baryon_slots.omega_b_geom_h2 / (h * h)
    omega_m0 = ACTIVE_PERTURBATION_PACKAGE.branch.Omega_m
    omega_cdm0 = max(omega_m0 - omega_b0, 0.0)
    rho_g = omega_gamma0 / scale_factor**4
    rho_nu = omega_nu0 / scale_factor**4
    rho_r = rho_g + rho_nu
    rho_m = omega_m0 / scale_factor**3
    fracnu = rho_nu / rho_r
    fracg = rho_g / rho_r
    fracb = omega_b0 / omega_m0
    fraccdm = omega_cdm0 / omega_m0
    rho_m_over_rho_r = rho_m / rho_r
    om = (ACTIVE_PERTURBATION_PACKAGE.branch.H0 / C_KM_S) * ACTIVE_PERTURBATION_PACKAGE.branch.Omega_m / math.sqrt(
        ACTIVE_PERTURBATION_PACKAGE.branch.Omega_r
    )
    ktau_sq = k_sq * 0.01 * 0.01
    ktau_cubed = k * 0.01 * ktau_sq
    delta_gamma_s = -(ktau_sq / 3.0) * (1.0 - om * 0.01 / 5.0) * 1.3 * s2_sq
    theta_gamma_s = (
        -k
        * ktau_cubed
        / 36.0
        * (1.0 - 3.0 * (1.0 + 5.0 * fracb - fracnu) / (20.0 * (1.0 - fracnu)) * om * 0.01)
        * 1.3
        * s2_sq
    )
    delta_ur_s = delta_gamma_s
    theta_ur_s = (
        -k
        * ktau_cubed
        / (36.0 * (4.0 * fracnu + 15.0))
        * (
            4.0 * fracnu
            + 11.0
            + 12.0 * s2_sq
            - 3.0 * (8.0 * fracnu * fracnu + 50.0 * fracnu + 275.0) / (20.0 * (2.0 * fracnu + 15.0)) * 0.01 * om
        )
        * 1.3
        * s2_sq
    )
    eta_s = 1.3 * (
        1.0
        - ktau_sq
        / (12.0 * (15.0 + 4.0 * fracnu))
        * (
            5.0
            + 4.0 * s2_sq * fracnu
            - (16.0 * fracnu * fracnu + 280.0 * fracnu + 325.0) / (10.0 * (2.0 * fracnu + 15.0)) * 0.01 * om
        )
    )
    delta_tot = (
        fracg * delta_gamma_s
        + fracnu * delta_ur_s
        + rho_m_over_rho_r * (fracb * (0.75 * delta_gamma_s) + fraccdm * (0.75 * delta_gamma_s))
    ) / (1.0 + rho_m_over_rho_r)
    velocity_tot = (
        (4.0 / 3.0) * (fracg * theta_gamma_s + fracnu * theta_ur_s)
        + rho_m_over_rho_r * fracb * theta_gamma_s
    ) / (1.0 + rho_m_over_rho_r)
    alpha = (
        eta_s
        + 1.5 * 100.0 * 100.0 * (delta_tot + 3.0 * 100.0 * velocity_tot / k_sq) / (k_sq * s2_sq)
    ) / 100.0
    expected_phi = eta_s - 100.0 * alpha
    assert math.isclose(seed.synchronous_eta, eta_s, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(seed.gauge_shift_alpha, alpha, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(seed.hierarchy_state.phi, expected_phi, rel_tol=0.0, abs_tol=1.0e-12)
    assert math.isclose(seed.hierarchy_state.psi, expected_phi, rel_tol=0.0, abs_tol=1.0e-12)
    assert math.isclose(seed.hierarchy_state.delta_b, 0.75 * delta_gamma_s - 3.0 * 100.0 * alpha, rel_tol=0.0, abs_tol=1.0e-12)
    assert math.isclose(seed.hierarchy_state.theta_b, theta_gamma_s + k_sq * alpha, rel_tol=0.0, abs_tol=1.0e-12)


def test_seed_carries_scope_boundary_and_shell_weight() -> None:
    """The seed package should expose its theorem boundary and weight directly."""

    carrier = build_scalar_hierarchy_carrier(5, curvature_radius_mpc=8.0)
    seed = build_closed_s3_newtonian_adiabatic_seed(
        carrier,
        conformal_time_mpc=0.02,
        a_prime_over_a_mpc_inv=50.0,
        scale_factor=1.0e-5,
    )
    assert seed.claim_status == "derived / scoped"
    assert seed.gauge == "newtonian"
    assert seed.shell_weight.shell_n == carrier.mode.n
    assert seed.scope_boundary[1].startswith("Does not derive low-`n` puncture occupations")
