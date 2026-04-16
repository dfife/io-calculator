"""Numerical model layer for the active-branch AIO calculator.

This module currently implements only the late-time/background surface that is
already closed enough to publish on the active branch:

- curved closed-FRW distances and ages
- BAO ratios built from the carried `r_d`
- late-time `eta_IO`

It deliberately does not pretend to be the future recombination or full CMB
solver. Those Phase 2+ objects need their own typed interfaces and claim
boundaries.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .constants import (
    ACTIVE_BARYON_SLOTS,
    ACTIVE_BRANCH,
    ACTIVE_IO_CONSTANTS,
    C_KM_S,
    C_SI,
    G_SI,
    GYR_S,
    HBAR_SI,
    K_B_SI,
    MEAN_BARYON_MASS_YP_KG,
    MPC_M,
    NEUTRINO_RELATIVISTIC_FACTOR,
    OMEGA_GAMMA_H2_REF,
    T_CMB_REF_K,
    T_OBS_ETA_K,
    ZETA3,
    BranchParameters,
)


def _simpson(fn, a: float, b: float, n: int) -> float:
    """Numerically integrate `fn` with Simpson's rule.

    The calculator uses one explicit integrator everywhere so the Python engine,
    browser mirror, and tests stay easy to compare line by line.
    """

    if n <= 0:
        raise ValueError("n must be positive")
    if a == b:
        return 0.0
    if n % 2 == 1:
        n += 1
    h = (b - a) / n
    total = fn(a) + fn(b)
    for i in range(1, n):
        total += (4.0 if i % 2 else 2.0) * fn(a + i * h)
    return total * h / 3.0


def omega_gamma_h2(T_cmb: float) -> float:
    """Photon density in standard Boltzmann-code normalization."""

    return OMEGA_GAMMA_H2_REF * (T_cmb / T_CMB_REF_K) ** 4


def photon_number_density_m3(T_cmb: float) -> float:
    """Blackbody photon number density."""

    prefactor = 2.0 * ZETA3 / (math.pi**2)
    scale = K_B_SI * T_cmb / (HBAR_SI * C_SI)
    return prefactor * scale**3


def rho_crit_h2_si() -> float:
    """Critical density corresponding to h=1 in kg / m^3."""

    h100_si = 100000.0 / MPC_M
    return 3.0 * h100_si * h100_si / (8.0 * math.pi * G_SI)


def late_eta_io(
    omega_b_h2: float = ACTIVE_BARYON_SLOTS.omega_b_geom_h2,
    *,
    T_obs: float = T_OBS_ETA_K,
    mean_baryon_mass_kg: float = MEAN_BARYON_MASS_YP_KG,
) -> float:
    """Late-time baryon-to-photon ratio on the preferred Paper 35 convention."""

    rho_b = omega_b_h2 * rho_crit_h2_si()
    n_b = rho_b / mean_baryon_mass_kg
    return n_b / photon_number_density_m3(T_obs)


@dataclass(frozen=True)
class CurvedBackgroundModel:
    """Closed-FRW active-branch background calculator.

    This class is the source of truth for the math used by:

    - the CLI
    - the static bundle builder
    - the browser-side mirror in `assets/calculator.js`

    The active branch is closed (`Omega_k < 0`), but the implementation keeps
    the full `S_k` branching explicit so the geometric convention is easy to
    audit.
    """

    branch: BranchParameters = ACTIVE_BRANCH

    @property
    def omega_gamma_h2(self) -> float:
        """Photon density in `omega h^2` units for the branch temperature."""

        return omega_gamma_h2(self.branch.T_cmb)

    @property
    def omega_r_h2(self) -> float:
        """Total relativistic density using the carried standard-neutrino slot."""

        return self.omega_gamma_h2 * (
            1.0 + NEUTRINO_RELATIVISTIC_FACTOR * self.branch.N_eff
        )

    @property
    def hubble_si(self) -> float:
        """Present-day Hubble constant in inverse seconds."""

        return self.branch.H0 * 1000.0 / MPC_M

    @property
    def hubble_gyr_inv(self) -> float:
        """Present-day Hubble constant in inverse gigayears."""

        return self.hubble_si * GYR_S

    @property
    def curvature_radius_mpc(self) -> float:
        """Curvature radius corresponding to the branch `Omega_k`."""

        return (C_KM_S / self.branch.H0) / math.sqrt(abs(self.branch.Omega_k))

    def e2(self, z: float) -> float:
        """Return `E(z)^2 = H(z)^2 / H0^2` for the carried branch."""

        zp1 = 1.0 + z
        return (
            self.branch.Omega_r * zp1**4
            + self.branch.Omega_m * zp1**3
            + self.branch.Omega_k * zp1**2
            + self.branch.Omega_lambda
        )

    def e(self, z: float) -> float:
        """Return the dimensionless expansion rate `E(z)`."""

        return math.sqrt(self.e2(z))

    def hubble_km_s_mpc(self, z: float) -> float:
        """Observer-side Hubble rate in km/s/Mpc."""

        return self.branch.H0 * self.e(z)

    def hubble_distance_mpc(self, z: float) -> float:
        """Instantaneous Hubble distance `c / H(z)` in Mpc."""

        return C_KM_S / self.hubble_km_s_mpc(z)

    def chi_dimless(self, z: float, *, n: int = 4096) -> float:
        """Dimensionless line-of-sight comoving coordinate.

        The integral is performed in `u = ln(1+z)` rather than directly in `z`
        because that keeps the numerical behavior smooth from `z = 0` to the
        higher-redshift BAO rows used by the calculator.
        """

        if z < 0.0:
            raise ValueError("z must be non-negative")
        upper = math.log1p(z)
        return _simpson(
            lambda u: math.exp(u) / self.e(math.expm1(u)),
            0.0,
            upper,
            n,
        )

    def s_k(self, chi: float) -> float:
        """Curvature response function `S_k(chi)` for FRW distances."""

        if abs(self.branch.Omega_k) < 1.0e-15:
            return chi
        if self.branch.Omega_k > 0.0:
            root = math.sqrt(self.branch.Omega_k)
            return math.sinh(root * chi) / root
        root = math.sqrt(-self.branch.Omega_k)
        return math.sin(root * chi) / root

    def comoving_transverse_distance_mpc(self, z: float, *, n: int = 4096) -> float:
        """Return `D_M(z)` in Mpc."""

        return (C_KM_S / self.branch.H0) * self.s_k(self.chi_dimless(z, n=n))

    def angular_diameter_distance_mpc(self, z: float, *, n: int = 4096) -> float:
        """Return `D_A(z)` in Mpc."""

        return self.comoving_transverse_distance_mpc(z, n=n) / (1.0 + z)

    def luminosity_distance_mpc(self, z: float, *, n: int = 4096) -> float:
        """Return `D_L(z)` in Mpc."""

        return self.comoving_transverse_distance_mpc(z, n=n) * (1.0 + z)

    def volume_distance_mpc(self, z: float, *, n: int = 4096) -> float:
        """Return the isotropic BAO distance `D_V(z)` in Mpc."""

        d_m = self.comoving_transverse_distance_mpc(z, n=n)
        return (d_m * d_m * self.hubble_distance_mpc(z) * z) ** (1.0 / 3.0)

    def lookback_time_gyr(self, z: float, *, n: int = 4096) -> float:
        """Projected observer-side lookback time in gigayears."""

        if z < 0.0:
            raise ValueError("z must be non-negative")
        upper = math.log1p(z)
        integral = _simpson(
            lambda u: 1.0 / self.e(math.expm1(u)),
            0.0,
            upper,
            n,
        )
        return integral / self.hubble_gyr_inv

    def age_at_redshift_gyr(self, z: float, *, n: int = 4096) -> float:
        """Projected observer-side cosmic age at redshift `z`.

        The integral starts from a tiny nonzero scale factor rather than the
        exact `a = 0` endpoint. That keeps the numerical integrand finite while
        remaining far below any redshift used by the current calculator.
        """

        if z < 0.0:
            raise ValueError("z must be non-negative")
        a_max = 1.0 / (1.0 + z)
        a_min = 1.0e-10
        u_min = math.log(a_min)
        u_max = math.log(a_max)
        integral = _simpson(
            lambda u: 1.0 / self.e(math.exp(-u) - 1.0),
            u_min,
            u_max,
            n,
        )
        return integral / self.hubble_gyr_inv

    def age_today_gyr(self, *, n: int = 4096) -> float:
        """Convenience wrapper for the present-day observer-side age."""

        return self.age_at_redshift_gyr(0.0, n=n)

    def bao_ratios(self, z: float, *, n: int = 4096) -> dict[str, float]:
        """Return the standard BAO ratios against the carried `r_d`."""

        return {
            "DM_over_rd": self.comoving_transverse_distance_mpc(z, n=n)
            / self.branch.rd_mpc,
            "DH_over_rd": self.hubble_distance_mpc(z) / self.branch.rd_mpc,
            "DV_over_rd": self.volume_distance_mpc(z, n=n) / self.branch.rd_mpc,
        }

    def snapshot(self, z: float, *, n: int = 4096) -> dict[str, float]:
        """Collect the calculator outputs for one redshift into one payload."""

        bao = self.bao_ratios(z, n=n)
        return {
            "z": z,
            "H_km_s_mpc": self.hubble_km_s_mpc(z),
            "DM_mpc": self.comoving_transverse_distance_mpc(z, n=n),
            "DA_mpc": self.angular_diameter_distance_mpc(z, n=n),
            "DL_mpc": self.luminosity_distance_mpc(z, n=n),
            "DH_mpc": self.hubble_distance_mpc(z),
            "DV_mpc": self.volume_distance_mpc(z, n=n),
            "lookback_gyr": self.lookback_time_gyr(z, n=n),
            "age_gyr": self.age_at_redshift_gyr(z, n=n),
            **bao,
        }
