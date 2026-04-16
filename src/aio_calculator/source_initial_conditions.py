"""Typed source-to-initial-condition bridge on the active scalar-source branch.

This module closes the part of the primordial bridge that is already theorem-
grade on the published active branch:

- `derived / scoped`: scalar-source shell covariance weight
  `C_N^src = A_s W_N^(+) = A_s ((N+1) / (N_p+1))^(-K_gauge / x)`
- `derived / scoped`: leading closed-`S^3` superhorizon adiabatic seed on the
  radiation-dominated photon-baryon scalar subsystem
- `derived / scoped`: Newtonian-gauge seed obtained by explicit gauge
  transformation from the synchronous seed on the same shell

What remains outside scope:

- low-`n` puncture-controlled occupation corrections from Paper 23 Round 2
- nonzero anomalous phase correlations
- full multi-species adiabatic/isocurvature initial-condition families

Important convention boundary for public readers:

- This module returns the active **source-side shell law** `A_s W_N^(+)` exactly as
  carried by the Paper 32 modular-DtN source theorem.
- It does **not** by itself decide whether that object should be interpreted
  downstream as the final closed-`S^3` shell covariance `P_X(n)` or as a
  dimensionless shell spectrum such as `Delta_q^2(n)`.
- That semantic choice belongs to the shell-measure / readout layer, because
  Paper 28 proves that on closed `S^3` the observer-side Jacobian depends on
  which spectral object is being held fixed.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .constants import ACTIVE_PERTURBATION_PACKAGE, PerturbationBranchPackage
from .constants import C_KM_S
from .model import omega_gamma_h2
from .scalar_hierarchy import ScalarHierarchyCarrier, ScalarHierarchyState
from .source_block import (
    ACTIVE_SOURCE_PIVOT_SHELL,
    active_plus_branch_supports_shell,
    native_scalar_amplitude,
    plus_branch_source_window,
)


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
class ScalarSourceShellWeight:
    """The active scalar-source shell covariance weight on one scalar shell.

    `supported_by_active_plus_branch` marks whether the shell belongs to the
    theorem-grade odd-shell bridge image. The affine law itself can still be
    evaluated off support for diagnostics, but those values are not
    theorem-grade active-source occupations.
    """

    shell_n: int
    pivot_shell: int
    source_window: float
    scalar_amplitude: float
    covariance_weight: float
    supported_by_active_plus_branch: bool
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


@dataclass(frozen=True)
class ClosedS3AdiabaticSeed:
    """One leading superhorizon adiabatic seed on a physical closed scalar shell."""

    carrier: ScalarHierarchyCarrier
    gauge: str
    conformal_time_mpc: float
    curvature_amplitude: float
    shell_weight: ScalarSourceShellWeight
    hierarchy_state: ScalarHierarchyState
    synchronous_eta: float
    gauge_shift_alpha: float
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


def _laplacian_k_sq(carrier: ScalarHierarchyCarrier) -> float:
    return carrier.mode.primary_spatial_eigenvalue / carrier.curvature_radius_mpc**2


def _laplacian_k(carrier: ScalarHierarchyCarrier) -> float:
    return math.sqrt(_laplacian_k_sq(carrier))


def _s2_squared(carrier: ScalarHierarchyCarrier) -> float:
    curvature_k = 1.0 / carrier.curvature_radius_mpc**2
    return 1.0 - 3.0 * curvature_k / _laplacian_k_sq(carrier)


def _class_seed_background_fractions(
    *,
    scale_factor: float,
    package: PerturbationBranchPackage,
) -> tuple[float, float, float, float, float, float]:
    """Return the CLASS-style early-time fractions used by the adiabatic seed.

    The live scoped driver evolves only the photon-baryon hierarchy explicitly,
    but the synchronous-to-Newtonian gauge shift must still see the full
    radiation and matter background mix. The reduction carried here mirrors the
    patched CLASS scalar adiabatic initialization:

    - `fracnu = rho_nu / rho_r`
    - `fracg = rho_g / rho_r`
    - `fracb = rho_b / rho_m`
    - `fraccdm = rho_cdm / rho_m`
    - `rho_m_over_rho_r = rho_m / rho_r`
    - `om = a rho_m / sqrt(rho_r)`

    on the active package background bookkeeping.
    """

    a = _positive(scale_factor, name="scale_factor")
    branch = package.branch
    h = branch.h
    omega_gamma0 = omega_gamma_h2(branch.T_cmb) / (h * h)
    omega_r0 = branch.Omega_r
    omega_nu0 = max(omega_r0 - omega_gamma0, 0.0)
    omega_b0 = package.baryon_slots.omega_b_geom_h2 / (h * h)
    omega_m0 = branch.Omega_m
    omega_cdm0 = max(omega_m0 - omega_b0, 0.0)

    rho_g = omega_gamma0 / a**4
    rho_nu = omega_nu0 / a**4
    rho_r = rho_g + rho_nu
    rho_m = omega_m0 / a**3
    if rho_r <= 0.0 or rho_m <= 0.0:
        raise ValueError("seed background fractions require positive radiation and matter densities")

    fracnu = rho_nu / rho_r
    fracg = rho_g / rho_r
    fracb = omega_b0 / omega_m0 if omega_m0 > 0.0 else 0.0
    fraccdm = omega_cdm0 / omega_m0 if omega_m0 > 0.0 else 0.0
    rho_m_over_rho_r = rho_m / rho_r
    hubble_factor = package.branch.H0 / C_KM_S
    om = hubble_factor * package.branch.Omega_m / math.sqrt(package.branch.Omega_r)
    return fracnu, fracg, fracb, fraccdm, rho_m_over_rho_r, om


def build_scalar_source_shell_weight(
    shell_n: int,
    *,
    pivot_shell: int = ACTIVE_SOURCE_PIVOT_SHELL,
) -> ScalarSourceShellWeight:
    """Return the active source-side shell law `A_s W_N^(+)`.

    What this function does:

    - carries forward the Paper 32 modular-DtN source theorem
    - evaluates the repaired plus-branch affine window
      `W_N^(+) = ((N+1) / (N_p+1))^(-K_gauge / x)`
    - packages the resulting active source-side shell object
      `A_s W_N^(+)`

    Why it is written this way:

    - the source block is theorem-grade only on the active reduced source
      carrier, so the calculator must not invent an extra primordial fit or an
      extra UV envelope here;
    - the exact semantic level of `A_s W_N^(+)` in the final TT shell sum remains a
      downstream convention choice, not something this module is allowed to
      decide silently.

    Authority:

    - Paper 32 modular-DtN field transfer theorem fixes `A_s` and `W_N`
    - Paper 28 closed-`S^3` power definition fixes how a later reader must
      convert between `P_X(n)` and dimensionless shell spectra such as
      `Delta_q^2(n)`
    """

    shell_n = int(shell_n)
    if shell_n < 2:
        raise ValueError("shell_n must satisfy shell_n >= 2 on the physical scalar branch")
    pivot_shell = int(pivot_shell)
    if pivot_shell < 2:
        raise ValueError("pivot_shell must satisfy pivot_shell >= 2")
    amplitude = native_scalar_amplitude()
    window = plus_branch_source_window(shell_n, pivot_shell=pivot_shell)
    supported = active_plus_branch_supports_shell(shell_n)
    return ScalarSourceShellWeight(
        shell_n=shell_n,
        pivot_shell=pivot_shell,
        source_window=window,
        scalar_amplitude=amplitude,
        covariance_weight=amplitude * window,
        supported_by_active_plus_branch=supported,
        claim_status="derived / scoped" if supported else "diagnostic / off-support affine continuation",
        provenance_node_ids=("paper32.modular_dtn_field_transfer", "local.closed_scalar_adiabatic_seed_bridge"),
        scope_boundary=(
            "Active scalar-source shell covariance on the repaired affine odd-shell plus branch.",
            "Even-shell evaluations are only off-support affine continuations for diagnostics.",
            "Does not include low-shell puncture occupation corrections or phase dressing beyond the active branch window.",
        ),
    )


def build_closed_s3_newtonian_adiabatic_seed(
    carrier: ScalarHierarchyCarrier,
    *,
    conformal_time_mpc: float,
    a_prime_over_a_mpc_inv: float,
    scale_factor: float,
    package: PerturbationBranchPackage = ACTIVE_PERTURBATION_PACKAGE,
    curvature_amplitude: float = 1.0,
    pivot_shell: int = ACTIVE_SOURCE_PIVOT_SHELL,
) -> ClosedS3AdiabaticSeed:
    """Build the leading radiation-era adiabatic seed in Newtonian gauge.

    The starting point is the patched-CLASS closed synchronous adiabatic seed on
    the early radiation-plus-matter background:

    - `delta_gamma^(S) = -(k_n tau)^2 (1-om tau / 5) s_2^2 R_n / 3`
    - `theta_gamma^(S) = -k_n (k_n tau)^3 [1 - 3(1+5 f_b-f_nu) om tau / (20(1-f_nu))] s_2^2 R_n / 36`
    - `delta_b^(S) = 3 delta_gamma^(S) / 4`
    - `theta_b^(S) = theta_gamma^(S)`
    - `delta_ur^(S) = delta_gamma^(S)`
    - `theta_ur^(S)` from the closed ultra-relativistic adiabatic branch
    - `eta^(S)` from the closed adiabatic Einstein solution with `f_nu`

    and the explicit synchronous-to-Newtonian transformation on the same shell:

    - `alpha = [eta + 1.5 (a'/a)^2 (delta_tot + 3(a'/a) velocity_tot / k_n^2) / (k_n^2 s_2^2)] / (a'/a)`
    - `phi = eta - (a'/a) alpha`
    - `delta_gamma^(N) = delta_gamma^(S) - 4 (a'/a) alpha`
    - `theta_gamma^(N) = theta_gamma^(S) + k_n^2 alpha`
    - `delta_b^(N) = delta_b^(S) - 3 (a'/a) alpha`
    - `theta_b^(N) = theta_b^(S) + k_n^2 alpha`
    """

    tau = _positive(conformal_time_mpc, name="conformal_time_mpc")
    a_prime_over_a = _positive(a_prime_over_a_mpc_inv, name="a_prime_over_a_mpc_inv")
    scale_factor = _positive(scale_factor, name="scale_factor")
    curvature_amplitude = _finite(curvature_amplitude, name="curvature_amplitude")
    k_sq = _laplacian_k_sq(carrier)
    k = _laplacian_k(carrier)
    s2_sq = _s2_squared(carrier)
    if s2_sq <= 0.0:
        raise ValueError("closed scalar shell requires positive s2_squared")
    fracnu, fracg, fracb, fraccdm, rho_m_over_rho_r, om = _class_seed_background_fractions(
        scale_factor=scale_factor,
        package=package,
    )
    ktau_sq = k_sq * tau * tau
    ktau_cubed = k * tau * ktau_sq

    delta_gamma_s = -(ktau_sq / 3.0) * (1.0 - om * tau / 5.0) * curvature_amplitude * s2_sq
    theta_gamma_s = (
        -k
        * ktau_cubed
        / 36.0
        * (
            1.0
            - 3.0 * (1.0 + 5.0 * fracb - fracnu) / (20.0 * (1.0 - fracnu)) * om * tau
        )
        * curvature_amplitude
        * s2_sq
    )
    delta_b_s = 0.75 * delta_gamma_s
    theta_b_s = theta_gamma_s
    delta_ur_s = delta_gamma_s
    theta_ur_s = (
        -k
        * ktau_cubed
        / (36.0 * (4.0 * fracnu + 15.0))
        * (
            4.0 * fracnu
            + 11.0
            + 12.0 * s2_sq
            - 3.0 * (8.0 * fracnu * fracnu + 50.0 * fracnu + 275.0) / (20.0 * (2.0 * fracnu + 15.0)) * tau * om
        )
        * curvature_amplitude
        * s2_sq
    )
    eta_s = curvature_amplitude * (
        1.0
        - ktau_sq
        / (12.0 * (15.0 + 4.0 * fracnu))
        * (
            5.0
            + 4.0 * s2_sq * fracnu
            - (16.0 * fracnu * fracnu + 280.0 * fracnu + 325.0) / (10.0 * (2.0 * fracnu + 15.0)) * tau * om
        )
    )

    delta_cdm_s = delta_b_s
    delta_tot = (
        fracg * delta_gamma_s
        + fracnu * delta_ur_s
        + rho_m_over_rho_r * (fracb * delta_b_s + fraccdm * delta_cdm_s)
    ) / (1.0 + rho_m_over_rho_r)
    velocity_tot = (
        (4.0 / 3.0) * (fracg * theta_gamma_s + fracnu * theta_ur_s)
        + rho_m_over_rho_r * fracb * theta_b_s
    ) / (1.0 + rho_m_over_rho_r)
    alpha = (
        eta_s
        + 1.5 * a_prime_over_a * a_prime_over_a * (delta_tot + 3.0 * a_prime_over_a * velocity_tot / k_sq) / (k_sq * s2_sq)
    ) / a_prime_over_a
    phi = eta_s - a_prime_over_a * alpha

    state = ScalarHierarchyState(
        phi=phi,
        psi=phi,
        delta_gamma=delta_gamma_s - 4.0 * a_prime_over_a * alpha,
        theta_gamma=theta_gamma_s + k_sq * alpha,
        delta_b=delta_b_s - 3.0 * a_prime_over_a * alpha,
        theta_b=theta_b_s + k_sq * alpha,
        photon_multipoles=(),
        polarization_multipoles=(),
        claim_status="derived / scoped leading superhorizon adiabatic seed",
        provenance_node_ids=(
            "paper23.closed_scalar_operator",
            "local.closed_scalar_adiabatic_seed_bridge",
        ),
        scope_boundary=(
            "Leading radiation-era photon-baryon adiabatic seed in Newtonian gauge.",
            "No low-shell non-Bunch-Davies correction, no anisotropic-stress sector, and no multi-species isocurvature family are included.",
        ),
    )
    return ClosedS3AdiabaticSeed(
        carrier=carrier,
        gauge="newtonian",
        conformal_time_mpc=tau,
        curvature_amplitude=curvature_amplitude,
        shell_weight=build_scalar_source_shell_weight(carrier.mode.n, pivot_shell=pivot_shell),
        hierarchy_state=state,
        synchronous_eta=eta_s,
        gauge_shift_alpha=alpha,
        claim_status="derived / scoped",
        provenance_node_ids=(
            "paper23.closed_scalar_operator",
            "paper32.modular_dtn_field_transfer",
            "local.closed_scalar_adiabatic_seed_bridge",
        ),
        scope_boundary=(
            "Active scalar-source shell weight plus the leading closed-`S^3` photon-baryon adiabatic seed.",
            "Does not derive low-`n` puncture occupations, phase correlations, or a full multi-species primordial sector.",
        ),
    )


__all__ = [
    "ClosedS3AdiabaticSeed",
    "ScalarSourceShellWeight",
    "build_closed_s3_newtonian_adiabatic_seed",
    "build_scalar_source_shell_weight",
]
