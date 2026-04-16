"""Exact Einstein-side scalar metric-state builders on closed `S^3`.

This module closes the metric-state part of the scalar perturbation center at
the scope that is genuinely fixed once the total scalar stress-energy summary is
supplied explicitly.

Closed here:

- `derived / scoped`: the Newtonian-gauge scalar metric state from
  `(phi, delta_rho, rho_plus_p_theta, rho_plus_p_shear)`
- `derived / scoped as map`: the Newtonian-gauge energy-constraint map
  `phi = -1.5 a^2 [k_n^2 delta_rho + 3 (a'/a) rho_plus_p_theta] / [k_n^2 (k_n^2-3K)]`
- `derived / scoped`: the synchronous-gauge scalar metric state from
  `(eta, delta_rho, delta_p, rho_plus_p_theta, rho_plus_p_shear)`
- `derived / scoped`: the acoustic-drive quartet consumed by the local
  closed-`S^3` scalar generator

Not closed here:

- aggregation of the total scalar stress-energy summary from a full multi-species
  perturbation hierarchy
- automatic enforcement of the Newtonian energy constraint during evolution
- selection of a physical matter content outside the supplied typed state
- any post-Einstein readout or source dressing
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .scalar_acoustic_operator import (
    ScalarMetricDrive,
    build_newtonian_metric_drive,
    build_synchronous_metric_drive,
)
from .scalar_hierarchy import ScalarHierarchyCarrier


def _finite(value: float, *, name: str) -> float:
    """Require one finite real scalar."""

    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _positive(value: float, *, name: str) -> float:
    """Require one strictly positive finite real scalar."""

    value = _finite(value, name=name)
    if value <= 0.0:
        raise ValueError(f"{name} must be strictly positive")
    return value


@dataclass(frozen=True)
class ScalarStressEnergySummary:
    """Einstein-side scalar stress-energy summary for one shell sample.

    The normalization is the standard perturbation-engine normalization in which
    the closed scalar Einstein equations read

    - `psi = phi - 4.5 (a^2 / k_n^2) rho_plus_p_shear`
    - `phi' = -(a'/a) psi + 1.5 (a^2 / k_n^2) rho_plus_p_theta`
    - `h' = [k_n^2 s_2^2 eta + 1.5 a^2 delta_rho] / (0.5 a'/a)`
    - `eta' = [1.5 a^2 rho_plus_p_theta + 0.5 K h'] / (k_n^2 s_2^2)`
    """

    delta_rho: float
    delta_p: float
    rho_plus_p_theta: float
    rho_plus_p_shear: float
    normalization: str
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("delta_rho", "delta_p", "rho_plus_p_theta", "rho_plus_p_shear"):
            _finite(getattr(self, name), name=name)


@dataclass(frozen=True)
class NewtonianScalarMetricState:
    """Closed-`S^3` scalar metric state in Newtonian gauge."""

    carrier: ScalarHierarchyCarrier
    scale_factor: float
    a_prime_over_a_mpc_inv: float
    stress: ScalarStressEnergySummary
    phi: float
    psi: float
    phi_prime: float
    acoustic_drive: ScalarMetricDrive
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


@dataclass(frozen=True)
class SynchronousScalarMetricState:
    """Closed-`S^3` scalar metric state in synchronous gauge."""

    carrier: ScalarHierarchyCarrier
    scale_factor: float
    a_prime_over_a_mpc_inv: float
    stress: ScalarStressEnergySummary
    eta: float
    h_prime: float
    eta_prime: float
    h_prime_prime: float
    alpha: float
    alpha_prime: float
    acoustic_drive: ScalarMetricDrive
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


def build_scalar_stress_energy_summary(
    *,
    delta_rho: float,
    delta_p: float,
    rho_plus_p_theta: float,
    rho_plus_p_shear: float,
) -> ScalarStressEnergySummary:
    """Package one explicit Einstein-side scalar stress-energy summary."""

    return ScalarStressEnergySummary(
        delta_rho=_finite(delta_rho, name="delta_rho"),
        delta_p=_finite(delta_p, name="delta_p"),
        rho_plus_p_theta=_finite(rho_plus_p_theta, name="rho_plus_p_theta"),
        rho_plus_p_shear=_finite(rho_plus_p_shear, name="rho_plus_p_shear"),
        normalization=(
            "Einstein-normalized scalar totals satisfying the closed-geometry "
            "conformal Einstein equations."
        ),
        claim_status="derived / scoped explicit Einstein-side source carrier",
        provenance_node_ids=("paper23.closed_scalar_operator", "local.closed_scalar_metric_state_builder"),
        scope_boundary=(
            "Explicit total scalar stress-energy carrier only.",
            "Does not derive the total sources from a full multi-species hierarchy by itself.",
        ),
    )


def newtonian_constraint_phi(
    carrier: ScalarHierarchyCarrier,
    stress: ScalarStressEnergySummary,
    *,
    scale_factor: float,
    a_prime_over_a_mpc_inv: float,
) -> float:
    """Return the closed-`S^3` Newtonian energy-constraint potential.

    On the physical scalar shell, the closed-space constraint is

    `phi = -1.5 a^2 [k_n^2 delta_rho + 3 (a'/a) rho_plus_p_theta] / [k_n^2 (k_n^2-3K)]`

    with

    - `k_n^2 = n(n+2) / R_curv^2`
    - `k_n^2 - 3K = (n-1)(n+3) / R_curv^2`

    In the calculator notation the scalar shell label is `n`, while some
    literature uses `nu = n+1`, so `nu^2-1 = n(n+2)`.
    """

    scale_factor = _positive(scale_factor, name="scale_factor")
    a_prime_over_a = _finite(a_prime_over_a_mpc_inv, name="a_prime_over_a_mpc_inv")
    k_sq = _positive(
        carrier.mode.primary_spatial_eigenvalue * (carrier.mode.radius**2 / carrier.curvature_radius_mpc**2),
        name="laplacian_k_sq_mpc_inv2",
    )
    shifted_sq = _positive(
        (carrier.mode.shifted_scalar_operator or 0.0) * (carrier.mode.radius**2 / carrier.curvature_radius_mpc**2),
        name="shifted_scalar_sq_mpc_inv2",
    )
    a_sq = scale_factor * scale_factor
    return -1.5 * a_sq * (
        k_sq * stress.delta_rho + 3.0 * a_prime_over_a * stress.rho_plus_p_theta
    ) / (k_sq * shifted_sq)


def build_newtonian_scalar_metric_state(
    carrier: ScalarHierarchyCarrier,
    stress: ScalarStressEnergySummary,
    *,
    scale_factor: float,
    a_prime_over_a_mpc_inv: float,
    phi: float,
) -> NewtonianScalarMetricState:
    """Build the Newtonian-gauge scalar metric state from Einstein equations.

    This builder consumes a supplied `phi` and closes the remaining local map
    to `(psi, phi')`. It does not automatically replace the supplied `phi` by
    the Newtonian energy-constraint value.
    """

    scale_factor = _positive(scale_factor, name="scale_factor")
    a_prime_over_a = _finite(a_prime_over_a_mpc_inv, name="a_prime_over_a_mpc_inv")
    phi = _finite(phi, name="phi")
    k_sq = _positive(carrier.mode.primary_spatial_eigenvalue * (carrier.mode.radius**2 / carrier.curvature_radius_mpc**2), name="laplacian_k_sq_mpc_inv2")
    a_sq_over_k_sq = scale_factor * scale_factor / k_sq
    psi = phi - 4.5 * a_sq_over_k_sq * stress.rho_plus_p_shear
    phi_prime = -a_prime_over_a * psi + 1.5 * a_sq_over_k_sq * stress.rho_plus_p_theta
    return NewtonianScalarMetricState(
        carrier=carrier,
        scale_factor=scale_factor,
        a_prime_over_a_mpc_inv=a_prime_over_a,
        stress=stress,
        phi=phi,
        psi=psi,
        phi_prime=phi_prime,
        acoustic_drive=build_newtonian_metric_drive(
            phi_prime=phi_prime,
            psi=psi,
            laplacian_k_sq_mpc_inv2=k_sq,
        ),
        claim_status="derived / scoped",
        provenance_node_ids=("paper23.closed_scalar_operator", "local.closed_scalar_metric_state_builder"),
        scope_boundary=(
            "Newtonian-gauge Einstein-side metric state on an explicit closed-`S^3` scalar shell.",
            "Requires the total scalar stress-energy summary to be supplied explicitly.",
        ),
    )


def build_synchronous_scalar_metric_state(
    carrier: ScalarHierarchyCarrier,
    stress: ScalarStressEnergySummary,
    *,
    scale_factor: float,
    a_prime_over_a_mpc_inv: float,
    eta: float,
) -> SynchronousScalarMetricState:
    """Build the synchronous-gauge scalar metric state from Einstein equations."""

    scale_factor = _positive(scale_factor, name="scale_factor")
    a_prime_over_a = _finite(a_prime_over_a_mpc_inv, name="a_prime_over_a_mpc_inv")
    if a_prime_over_a == 0.0:
        raise ValueError("a_prime_over_a_mpc_inv must be non-zero")
    eta = _finite(eta, name="eta")
    k_sq = _positive(
        carrier.mode.primary_spatial_eigenvalue * (carrier.mode.radius**2 / carrier.curvature_radius_mpc**2),
        name="laplacian_k_sq_mpc_inv2",
    )
    curvature_k = 1.0 / (carrier.curvature_radius_mpc * carrier.curvature_radius_mpc)
    s2_squared = 1.0 - 3.0 * curvature_k / k_sq
    if s2_squared <= 0.0:
        raise ValueError("closed scalar shell requires positive s2_squared")
    a_sq = scale_factor * scale_factor
    h_prime = (k_sq * s2_squared * eta + 1.5 * a_sq * stress.delta_rho) / (0.5 * a_prime_over_a)
    eta_prime = (1.5 * a_sq * stress.rho_plus_p_theta + 0.5 * curvature_k * h_prime) / (k_sq * s2_squared)
    h_prime_prime = -2.0 * a_prime_over_a * h_prime + 2.0 * k_sq * s2_squared * eta - 9.0 * a_sq * stress.delta_p
    alpha = (h_prime + 6.0 * eta_prime) / (2.0 * k_sq)
    alpha_prime = -2.0 * a_prime_over_a * alpha + eta - 4.5 * (a_sq / k_sq) * stress.rho_plus_p_shear
    return SynchronousScalarMetricState(
        carrier=carrier,
        scale_factor=scale_factor,
        a_prime_over_a_mpc_inv=a_prime_over_a,
        stress=stress,
        eta=eta,
        h_prime=h_prime,
        eta_prime=eta_prime,
        h_prime_prime=h_prime_prime,
        alpha=alpha,
        alpha_prime=alpha_prime,
        acoustic_drive=build_synchronous_metric_drive(
            h_prime=h_prime,
            alpha=alpha,
            alpha_prime=alpha_prime,
            laplacian_k_sq_mpc_inv2=k_sq,
        ),
        claim_status="derived / scoped",
        provenance_node_ids=("paper23.closed_scalar_operator", "local.closed_scalar_metric_state_builder"),
        scope_boundary=(
            "Synchronous-gauge Einstein-side metric state on an explicit closed-`S^3` scalar shell.",
            "Requires the total scalar stress-energy summary to be supplied explicitly.",
        ),
    )


__all__ = [
    "NewtonianScalarMetricState",
    "ScalarStressEnergySummary",
    "SynchronousScalarMetricState",
    "build_newtonian_scalar_metric_state",
    "build_scalar_stress_energy_summary",
    "build_synchronous_scalar_metric_state",
    "newtonian_constraint_phi",
]
