"""Theorem-grade redshift selector on the strict-bare acoustic backbone.

This module does not invent a visibility threshold. It exposes the narrower
object that now survives review:

- `derived / scoped`:
  on the strict-bare homogeneous scalar/longitudinal phase sector, the exact
  selector-bearing representative of the primitive bare acoustic scalar is

      theta_bare^prim(z) = r_s^bulk(z) / D_M^bare(z)

  because Papers 20-21 force the primitive correction into the phase lattice,
  the bare numerator is the gauge-neutral 1D history ruler, and the bare
  denominator is the gauge-neutral transverse distance
- `derived / scoped`:
  on the strict bare OS branch, the bulk acoustic-angle backbone

      theta_bare^bulk(z) = r_s^bulk(z) / D_M^bare(z)

  is a continuous scalar map built entirely from theorem-grade IO inputs
- `derived / scoped`:
  on any interval where that backbone is strictly monotone, a scalar bare-angle
  readout determines a unique inverse-image redshift selector
- `derived / scoped`:
  strict monotonicity on the carried interval follows from an analytic endpoint
  bound on the exact derivative, not from a scan

What this module does not do:

- identify the exact primitive packet scalar `theta_bare^prim` on its own
- promote a raw visibility, `tau = 1`, or onset threshold to the selector
- claim theorem-grade numeric `z_*` without a theorem-grade scalar angle input
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .constants import (
    C_KM_S,
    C_SI,
    MPC_M,
    STRICT_BARE_OMEGA_B_GEOM_H2,
    STRICT_BARE_OS_BRANCH,
    BranchParameters,
    HYDROGEN_ATOM_MASS_KG,
    OMEGA_GAMMA_H2_REF,
    T_CMB_REF_K,
)
from .model import rho_crit_h2_si


STRICT_BARE_SELECTOR_Z_MIN = 900.0
STRICT_BARE_SELECTOR_Z_MAX = 1300.0
STRICT_BARE_J_THETA = 1.51899 ** (-0.5) * math.sqrt(1.0 + 0.2375**2)


@dataclass(frozen=True)
class SelectorDomainCertificate:
    """Numerical certificate that a strict-bare selector interval is invertible."""

    z_min: float
    z_max: float
    theta_min_deg: float
    theta_max_deg: float
    dm_over_rs_lower_bound: float
    cs_over_c_lower_bound: float
    cos_psi_lower_bound: float
    monotonicity_margin_lower_bound: float


def _simpson(fn, a: float, b: float, n: int) -> float:
    """Integrate a scalar function on `[a, b]` with Simpson's rule."""

    if n % 2:
        n += 1
    h = (b - a) / n
    total = fn(a) + fn(b)
    for i in range(1, n):
        total += (4.0 if i % 2 else 2.0) * fn(a + i * h)
    return total * h / 3.0


def _strict_bare_e2(z: float, branch: BranchParameters = STRICT_BARE_OS_BRANCH) -> float:
    """Return the strict-bare Friedmann factor `E(z)^2`."""

    zp1 = 1.0 + z
    return (
        branch.Omega_r * zp1**4
        + branch.Omega_m * zp1**3
        + branch.Omega_k * zp1**2
        + branch.Omega_lambda
    )


def strict_bare_hubble_si(
    z: float,
    branch: BranchParameters = STRICT_BARE_OS_BRANCH,
) -> float:
    """Return `H_bare(z)` on the strict bare OS branch in `s^-1`.

    Status: `derived / scoped`
    Authority: Paper 20 strict bare cycloid package.
    """

    return branch.H0 * 1000.0 / MPC_M * math.sqrt(_strict_bare_e2(z, branch))


def strict_bare_hydrogen_number_density_m3(
    z: float,
    *,
    omega_b_geom_h2: float = STRICT_BARE_OMEGA_B_GEOM_H2,
    branch: BranchParameters = STRICT_BARE_OS_BRANCH,
) -> float:
    """Return the strict-bare hydrogen inventory `n_H(z)` in `m^-3`.

    Status: `derived / scoped`
    """

    rho_b0 = omega_b_geom_h2 * rho_crit_h2_si()
    rho_b = rho_b0 * (1.0 + z) ** 3
    return (1.0 - branch.YHe) * rho_b / HYDROGEN_ATOM_MASS_KG


def _strict_bare_omega_gamma_h2(branch: BranchParameters = STRICT_BARE_OS_BRANCH) -> float:
    """Return the strict-bare photon density in `omega h^2` units."""

    return OMEGA_GAMMA_H2_REF * (branch.T_cmb / T_CMB_REF_K) ** 4


def strict_bare_local_baryon_loading_R(
    z: float,
    *,
    omega_b_geom_h2: float = STRICT_BARE_OMEGA_B_GEOM_H2,
    branch: BranchParameters = STRICT_BARE_OS_BRANCH,
) -> float:
    """Return the isolated local loading coefficient on the strict-bare branch.

    Status: `derived / scoped`
    """

    rho_b = omega_b_geom_h2 * rho_crit_h2_si() * (1.0 + z) ** 3
    rho_gamma = _strict_bare_omega_gamma_h2(branch) * rho_crit_h2_si() * (1.0 + z) ** 4
    return 3.0 * rho_b / (4.0 * rho_gamma)


def strict_bare_local_sound_speed_m_s(z: float) -> float:
    """Return the strict-bare local photon-baryon sound speed in `m/s`.

    Status: `derived / scoped`
    """

    return C_SI / math.sqrt(3.0 * (1.0 + strict_bare_local_baryon_loading_R(z)))


def strict_bare_comoving_chi(
    z: float,
    *,
    branch: BranchParameters = STRICT_BARE_OS_BRANCH,
    n: int = 2000,
) -> float:
    """Return the dimensionless closed-FRW radial integral `chi(z)`.

    Status: `derived / scoped`
    """

    upper = math.log1p(z)

    def integrand(u: float) -> float:
        z_val = math.expm1(u)
        return math.exp(u) / math.sqrt(_strict_bare_e2(z_val, branch))

    return _simpson(integrand, 0.0, upper, n)


def strict_bare_phase_angle_psi(
    z: float,
    *,
    branch: BranchParameters = STRICT_BARE_OS_BRANCH,
    n: int = 2000,
) -> float:
    """Return the closed-space sine argument `psi(z) = sqrt(-Omega_k) chi(z)`.

    Status: `derived / scoped`
    """

    return math.sqrt(-branch.Omega_k) * strict_bare_comoving_chi(z, branch=branch, n=n)


def strict_bare_dm_mpc(
    z: float,
    *,
    branch: BranchParameters = STRICT_BARE_OS_BRANCH,
    n: int = 2000,
) -> float:
    """Return the strict-bare transverse comoving distance `D_M^bare(z)` in Mpc.

    Status: `derived / scoped`
    """

    psi = strict_bare_phase_angle_psi(z, branch=branch, n=n)
    root = math.sqrt(-branch.Omega_k)
    return (C_KM_S / branch.H0) * math.sin(psi) / root


def strict_bare_bulk_sound_horizon_mpc(
    z: float,
    *,
    branch: BranchParameters = STRICT_BARE_OS_BRANCH,
    z_max: float = 1.0e6,
    n: int = 3000,
) -> float:
    """Return the strict-bare raw bulk sound horizon `r_s^bulk(z)` in Mpc.

    Status: `derived / scoped`
    """

    u_lo = math.log1p(z)
    u_hi = math.log1p(z_max)

    def integrand(u: float) -> float:
        z_val = math.expm1(u)
        return strict_bare_local_sound_speed_m_s(z_val) / strict_bare_hubble_si(
            z_val, branch
        ) * math.exp(u)

    return _simpson(integrand, u_lo, u_hi, n) / MPC_M


def strict_bare_bulk_theta_deg(
    z: float,
    *,
    branch: BranchParameters = STRICT_BARE_OS_BRANCH,
    distance_n: int = 2000,
    sound_n: int = 3000,
) -> float:
    """Return the strict-bare bulk acoustic angle in degrees.

    Status: `derived / scoped`
    """

    rs_bulk = strict_bare_bulk_sound_horizon_mpc(z, branch=branch, n=sound_n)
    dm = strict_bare_dm_mpc(z, branch=branch, n=distance_n)
    return rs_bulk / dm * 180.0 / math.pi


def strict_bare_monotonicity_margin(
    z: float,
    *,
    branch: BranchParameters = STRICT_BARE_OS_BRANCH,
    distance_n: int = 2000,
    sound_n: int = 3000,
) -> float:
    """Return the exact derivative-sign margin on the strict-bare backbone.

    Define

        M(z) := (c_s/c) (D_M/r_s) + cos(psi).

    Then

        d theta_bare^bulk / dz
          = -(180/pi) * c * r_s * M(z) / (H D_M^2).

    Status: `derived / scoped`
    """

    rs_bulk = strict_bare_bulk_sound_horizon_mpc(z, branch=branch, n=sound_n)
    dm = strict_bare_dm_mpc(z, branch=branch, n=distance_n)
    cs_over_c = strict_bare_local_sound_speed_m_s(z) / C_SI
    cos_psi = math.cos(strict_bare_phase_angle_psi(z, branch=branch, n=distance_n))
    return cs_over_c * (dm / rs_bulk) + cos_psi


def strict_bare_bulk_theta_derivative_deg_per_redshift(
    z: float,
    *,
    branch: BranchParameters = STRICT_BARE_OS_BRANCH,
    distance_n: int = 2000,
    sound_n: int = 3000,
) -> float:
    """Return the exact strict-bare bulk derivative `d theta / dz` in degrees.

    Status: `derived / scoped`
    """

    rs_bulk = strict_bare_bulk_sound_horizon_mpc(z, branch=branch, n=sound_n)
    dm = strict_bare_dm_mpc(z, branch=branch, n=distance_n)
    margin = strict_bare_monotonicity_margin(
        z,
        branch=branch,
        distance_n=distance_n,
        sound_n=sound_n,
    )
    prefactor = -(180.0 / math.pi) * C_SI * rs_bulk * MPC_M
    prefactor /= strict_bare_hubble_si(z, branch) * (dm * MPC_M) ** 2
    return prefactor * margin


def certify_strict_bare_selector_domain(
    *,
    z_min: float = STRICT_BARE_SELECTOR_Z_MIN,
    z_max: float = STRICT_BARE_SELECTOR_Z_MAX,
) -> SelectorDomainCertificate:
    """Certify a monotone strict-bare selector interval analytically.

    The derivative identity

        d theta_bare^bulk / dz
          = -[c_s D_M + c r_s cos(psi)] / [H D_M^2]

    shows strict monotonic decrease whenever

        (c_s / c) (D_M / r_s) + cos(psi) > 0.

    Status:
    - derivative formula: `derived / scoped`
    - interval certificate on a fixed branch: `derived / scoped`
    """

    if z_min <= 0.0 or z_max <= z_min:
        raise ValueError("selector domain requires 0 < z_min < z_max")

    theta_at_min = strict_bare_bulk_theta_deg(z_min)
    theta_at_max = strict_bare_bulk_theta_deg(z_max)

    psi_min = strict_bare_phase_angle_psi(z_min, n=3000)
    psi_max = strict_bare_phase_angle_psi(z_max, n=3000)
    if not (math.pi / 2.0 < psi_min < psi_max < math.pi):
        raise RuntimeError("selector interval does not stay inside the monotone closed-space sector")

    # On `(pi/2, pi)`, `sin(psi)` decreases and `cos(psi)` decreases as `psi`
    # increases. Since `psi(z)` increases with `z`, the strict-bare distance
    # decreases and `cos(psi)` reaches its minimum at `z_max`.
    dm_lower = strict_bare_dm_mpc(z_max, n=3000)
    cos_lower = math.cos(psi_max)

    # The local loading `R(z) = const / (1+z)` decreases with redshift on the
    # strict-bare branch, so `c_s(z)` increases and its minimum sits at `z_min`.
    cs_over_c_lower = strict_bare_local_sound_speed_m_s(z_min) / C_SI

    # The sound horizon decreases because `d r_s / dz = -c_s / H < 0`, so its
    # maximum sits at `z_min`. Therefore `D_M / r_s` is bounded below by the
    # endpoint quotient `D_M(z_max) / r_s(z_min)` without any scan.
    rs_upper = strict_bare_bulk_sound_horizon_mpc(z_min, n=4000)
    ratio_lower = dm_lower / rs_upper
    min_margin = cs_over_c_lower * ratio_lower + cos_lower

    if not theta_at_min > theta_at_max or min_margin <= 0.0:
        raise RuntimeError("supplied interval is not a certified monotone selector domain")

    return SelectorDomainCertificate(
        z_min=z_min,
        z_max=z_max,
        theta_min_deg=theta_at_max,
        theta_max_deg=theta_at_min,
        dm_over_rs_lower_bound=ratio_lower,
        cs_over_c_lower_bound=cs_over_c_lower,
        cos_psi_lower_bound=cos_lower,
        monotonicity_margin_lower_bound=min_margin,
    )


def select_phase_equivalent_redshift(
    theta_bare_deg: float,
    *,
    z_min: float = STRICT_BARE_SELECTOR_Z_MIN,
    z_max: float = STRICT_BARE_SELECTOR_Z_MAX,
    tol: float = 1.0e-10,
    max_iter: int = 80,
) -> float:
    """Invert the strict-bare bulk acoustic angle to a unique redshift.

    Status: `derived / scoped`
    This is the theorem-grade selector map once the primitive bare acoustic
    angle has been supplied by a theorem-grade readout chain.
    """

    if theta_bare_deg <= 0.0:
        raise ValueError("theta_bare_deg must be positive")

    cert = certify_strict_bare_selector_domain(z_min=z_min, z_max=z_max)
    if not cert.theta_min_deg <= theta_bare_deg <= cert.theta_max_deg:
        raise ValueError("theta_bare_deg lies outside the certified selector range")

    lo = z_min
    hi = z_max
    theta_lo = strict_bare_bulk_theta_deg(lo)
    theta_hi = strict_bare_bulk_theta_deg(hi)
    if math.isclose(theta_lo, theta_bare_deg, rel_tol=0.0, abs_tol=tol):
        return lo
    if math.isclose(theta_hi, theta_bare_deg, rel_tol=0.0, abs_tol=tol):
        return hi

    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        theta_mid = strict_bare_bulk_theta_deg(mid)
        if math.isclose(theta_mid, theta_bare_deg, rel_tol=0.0, abs_tol=tol):
            return mid
        if theta_mid > theta_bare_deg:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            return 0.5 * (lo + hi)

    return 0.5 * (lo + hi)


def observer_theta_to_phase_equivalent_redshift(
    theta_obs_deg: float,
    *,
    j_theta: float = STRICT_BARE_J_THETA,
    z_min: float = STRICT_BARE_SELECTOR_Z_MIN,
    z_max: float = STRICT_BARE_SELECTOR_Z_MAX,
) -> float:
    """Convert an observer-side acoustic angle to the strict-bare selector leaf.

    Status: `derived / scoped`
    Uses the exact Paper 20 / 21 observer law `theta_obs = J_theta theta_bare`.
    """

    if j_theta <= 0.0:
        raise ValueError("j_theta must be positive")
    return select_phase_equivalent_redshift(
        theta_obs_deg / j_theta,
        z_min=z_min,
        z_max=z_max,
    )


def observer_theta100_to_phase_equivalent_redshift(theta_obs_100: float) -> float:
    """Convert `100 theta_obs` to the strict-bare selector leaf.

    Status: `derived / scoped`
    """

    theta_obs_deg = theta_obs_100 * 180.0 / (100.0 * math.pi)
    return observer_theta_to_phase_equivalent_redshift(theta_obs_deg)


__all__ = [
    "STRICT_BARE_J_THETA",
    "STRICT_BARE_SELECTOR_Z_MAX",
    "STRICT_BARE_SELECTOR_Z_MIN",
    "SelectorDomainCertificate",
    "certify_strict_bare_selector_domain",
    "observer_theta100_to_phase_equivalent_redshift",
    "observer_theta_to_phase_equivalent_redshift",
    "select_phase_equivalent_redshift",
    "strict_bare_bulk_sound_horizon_mpc",
    "strict_bare_bulk_theta_derivative_deg_per_redshift",
    "strict_bare_bulk_theta_deg",
    "strict_bare_comoving_chi",
    "strict_bare_dm_mpc",
    "strict_bare_hubble_si",
    "strict_bare_local_baryon_loading_R",
    "strict_bare_local_sound_speed_m_s",
    "strict_bare_monotonicity_margin",
    "strict_bare_phase_angle_psi",
]
