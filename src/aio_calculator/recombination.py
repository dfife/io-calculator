"""Theorem-grade Phase 2 recombination surface for the AIO calculator.

This module only implements objects that are currently admitted by the
calculator rules:

- `derived / scoped`: the Paper 31 local background-state map
- `derived / scoped`: local chemistry and primitive local opacity on
  `omega_b,geom`
- `derived / scoped`: reduced visibility/readout as an operator acting on a
  supplied exact Stage-2 history
- `derived / scoped`: isolated local `R` and `c_s` on the inventory branch

What this module deliberately does not do:

- fake the exact Stage-2 dynamic-network completion with a live Peebles or
  RECFAST/HyRec approximation
- compress the visibility packet to a unique `z_*`
- claim theorem-grade `r_s(z_*)` or `theta_s`
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from .constants import (
    ACTIVE_BARYON_SLOTS,
    ACTIVE_BRANCH,
    ACTIVE_IO_CONSTANTS,
    C_SI,
    HBAR_SI,
    HYDROGEN_ATOM_MASS_KG,
    HYDROGEN_IONIZATION_ENERGY_J,
    IO_SCHWARZSCHILD_RADIUS_M,
    K_B_SI,
    M_ELECTRON_KG,
    SIGMA_T_SI,
    T_IO_REF_K,
)
from .model import omega_gamma_h2, rho_crit_h2_si


def _float_tuple(values: Sequence[float], *, name: str) -> tuple[float, ...]:
    """Convert a finite sequence to a validated tuple of floats."""

    if not values:
        raise ValueError(f"{name} must not be empty")
    coerced = tuple(float(value) for value in values)
    if any(not math.isfinite(value) for value in coerced):
        raise ValueError(f"{name} must contain only finite values")
    return coerced


def _validate_redshift(z: float) -> None:
    """Reject negative observer-side redshifts."""

    if z < 0.0:
        raise ValueError("z must be non-negative")


def local_u(z: float) -> float:
    """Return the exact Paper 31 local scale-factor ratio `u(z)`.

    Status: `derived / scoped`
    Authority: Paper 31 local background-state map theorem.
    """

    _validate_redshift(z)
    return 1.0 / (ACTIVE_IO_CONSTANTS.x * (1.0 + z))


def local_scale_factor_m(z: float) -> float:
    """Return the dimensionful local scale factor `a_loc(z) = r_s * u(z)`.

    Status: `derived / scoped`
    """

    return IO_SCHWARZSCHILD_RADIUS_M * local_u(z)


def local_hubble_si(z: float) -> float:
    """Return the exact local expansion rate `H_loc(z)` in inverse seconds.

    Status: `derived / scoped`
    Authority: Paper 31 local background-state map theorem.
    """

    u = local_u(z)
    return (C_SI / IO_SCHWARZSCHILD_RADIUS_M) * math.sqrt((1.0 - u) / (u**3))


def local_radiation_temperature_K(
    z: float,
    *,
    t_io_ref_k: float = T_IO_REF_K,
) -> float:
    """Return the local bulk radiation temperature `T_R,loc(z)` in kelvin.

    Status: `derived / conditional`
    Remaining condition: Premise 2 plus the carried Paper 31 classification of
    the inherited `TR` variable as local bulk radiation, not observer readout.
    """

    _validate_redshift(z)
    return float(t_io_ref_k) * (1.0 + z)


def local_os_proper_time_dz(z: float) -> float:
    """Return `d tau_OS / dz` on the homogeneous IO background.

    Status: `derived / scoped`
    Authority: Paper 31 recombination clock transport theorem.
    """

    _validate_redshift(z)
    x = ACTIVE_IO_CONSTANTS.x
    return -IO_SCHWARZSCHILD_RADIUS_M / (
        C_SI * x * (1.0 + z) ** 2 * math.sqrt(x * (1.0 + z) - 1.0)
    )


def hydrogen_number_density_m3(
    z: float,
    *,
    omega_b_h2: float = ACTIVE_BARYON_SLOTS.omega_b_geom_h2,
    helium_mass_fraction: float = ACTIVE_BRANCH.YHe,
) -> float:
    """Return `n_H(z)` on the local inventory branch in `m^-3`.

    Status: `derived / scoped`
    """

    _validate_redshift(z)
    rho_b0 = omega_b_h2 * rho_crit_h2_si()
    rho_b = rho_b0 * (1.0 + z) ** 3
    return (1.0 - helium_mass_fraction) * rho_b / HYDROGEN_ATOM_MASS_KG


def saha_equilibrium_xe(
    z: float,
    *,
    hydrogen_density_m3: float | None = None,
    radiation_temperature_K: float | None = None,
    omega_b_h2: float = ACTIVE_BARYON_SLOTS.omega_b_geom_h2,
    helium_mass_fraction: float = ACTIVE_BRANCH.YHe,
    t_io_ref_k: float = T_IO_REF_K,
) -> float:
    """Return the hydrogen-only Saha equilibrium ionization fraction.

    Status: `derived / conditional`
    Remaining condition: Premise 2, which imports standard atomic equilibrium
    physics for the local bulk recombination chemistry sector.
    """

    n_h = (
        hydrogen_density_m3
        if hydrogen_density_m3 is not None
        else hydrogen_number_density_m3(
            z,
            omega_b_h2=omega_b_h2,
            helium_mass_fraction=helium_mass_fraction,
        )
    )
    temperature = (
        radiation_temperature_K
        if radiation_temperature_K is not None
        else local_radiation_temperature_K(z, t_io_ref_k=t_io_ref_k)
    )
    if n_h <= 0.0:
        raise ValueError("hydrogen_density_m3 must be positive")
    if temperature <= 0.0:
        raise ValueError("radiation_temperature_K must be positive")

    saha_ratio = ((M_ELECTRON_KG * K_B_SI * temperature) / (2.0 * math.pi * HBAR_SI**2)) ** 1.5
    saha_ratio *= math.exp(-HYDROGEN_IONIZATION_ENERGY_J / (K_B_SI * temperature))
    saha_ratio /= n_h

    x_e = 0.5 * (math.sqrt(saha_ratio * (saha_ratio + 4.0)) - saha_ratio)
    return max(0.0, min(1.0, x_e))


def free_electron_density_m3(
    z: float,
    x_e: float,
    *,
    omega_b_h2: float = ACTIVE_BARYON_SLOTS.omega_b_geom_h2,
    helium_mass_fraction: float = ACTIVE_BRANCH.YHe,
) -> float:
    """Return `n_e(z) = x_e n_H(z)` on the local inventory branch.

    Status: `derived / scoped`
    """

    if x_e < 0.0:
        raise ValueError("x_e must be non-negative")
    return x_e * hydrogen_number_density_m3(
        z,
        omega_b_h2=omega_b_h2,
        helium_mass_fraction=helium_mass_fraction,
    )


def local_thomson_scattering_rate_si(
    z: float,
    x_e: float,
    *,
    omega_b_h2: float = ACTIVE_BARYON_SLOTS.omega_b_geom_h2,
    helium_mass_fraction: float = ACTIVE_BRANCH.YHe,
) -> float:
    """Return the local Thomson scattering rate `c sigma_T n_e` in `s^-1`.

    Status: `derived / scoped`
    """

    return C_SI * SIGMA_T_SI * free_electron_density_m3(
        z,
        x_e,
        omega_b_h2=omega_b_h2,
        helium_mass_fraction=helium_mass_fraction,
    )


def primitive_local_kappa_prime(
    z: float,
    x_e: float,
    *,
    omega_b_h2: float = ACTIVE_BARYON_SLOTS.omega_b_geom_h2,
    helium_mass_fraction: float = ACTIVE_BRANCH.YHe,
) -> float:
    """Return the primitive local Thomson opacity kernel `kappa'_loc = a n_e sigma_T`.

    Status: `derived / scoped`
    This is the local microphysical contact operator, not the reduced
    observer-side optical depth.
    """

    return local_scale_factor_m(z) * free_electron_density_m3(
        z,
        x_e,
        omega_b_h2=omega_b_h2,
        helium_mass_fraction=helium_mass_fraction,
    ) * SIGMA_T_SI


def optical_depth_gradient_per_redshift(
    z: float,
    x_e: float,
    *,
    omega_b_h2: float = ACTIVE_BARYON_SLOTS.omega_b_geom_h2,
    helium_mass_fraction: float = ACTIVE_BRANCH.YHe,
) -> float:
    """Return `d tau_obs / dz` from the exact local Thomson history.

    Status: `derived / scoped`
    This is the operator-level bridge component `I_LOS o T_clock`; it is not a
    separate fitted visibility projector.
    """

    return local_thomson_scattering_rate_si(
        z,
        x_e,
        omega_b_h2=omega_b_h2,
        helium_mass_fraction=helium_mass_fraction,
    ) * abs(local_os_proper_time_dz(z))


def local_scattering_to_expansion_ratio(
    z: float,
    x_e: float,
    *,
    omega_b_h2: float = ACTIVE_BARYON_SLOTS.omega_b_geom_h2,
    helium_mass_fraction: float = ACTIVE_BRANCH.YHe,
) -> float:
    """Return the theorem-grade onset ratio `Gamma_T / H_loc`.

    Status: `derived / scoped`
    This is a physical decoupling-onset observable. It is not promoted here to
    the last-scattering selector `z_*`.
    """

    return local_thomson_scattering_rate_si(
        z,
        x_e,
        omega_b_h2=omega_b_h2,
        helium_mass_fraction=helium_mass_fraction,
    ) / local_hubble_si(z)


def local_baryon_loading_R(
    z: float,
    *,
    omega_b_geom_h2: float = ACTIVE_BARYON_SLOTS.omega_b_geom_h2,
    t_io_ref_k: float = T_IO_REF_K,
) -> float:
    """Return the isolated local momentum-loading ratio `R(z)` on `omega_b,geom`.

    Status: `derived / scoped`
    Scope boundary: this closes the primitive local momentum-loading object
    used by the theorem-grade drag/sound-speed leg. It does not by itself solve
    the full observed CMB acoustic/readout hierarchy.
    """

    _validate_redshift(z)
    rho_b = float(omega_b_geom_h2) * rho_crit_h2_si() * (1.0 + z) ** 3
    rho_gamma = omega_gamma_h2(float(t_io_ref_k)) * rho_crit_h2_si() * (1.0 + z) ** 4
    return 3.0 * rho_b / (4.0 * rho_gamma)


def local_sound_speed_m_s(
    z: float,
    *,
    omega_b_geom_h2: float = ACTIVE_BARYON_SLOTS.omega_b_geom_h2,
    t_io_ref_k: float = T_IO_REF_K,
) -> float:
    """Return the isolated local photon-baryon sound speed in `m/s`.

    Status: `derived / scoped`
    Scope boundary: this is the local sound-speed leg built from the primitive
    local loading ratio on `omega_b,geom`, not a full perturbation/readout
    closure.
    """

    return C_SI / math.sqrt(
        3.0
        * (
            1.0
            + local_baryon_loading_R(
                z,
                omega_b_geom_h2=omega_b_geom_h2,
                t_io_ref_k=t_io_ref_k,
            )
        )
    )


@dataclass(frozen=True)
class LocalBackgroundState:
    """Exact local background state sampled at one observed redshift."""

    z_obs: float
    u: float
    a_loc_m: float
    H_loc_s_inv: float
    T_r_loc_K: float
    n_H_geom_m3: float


def local_background_state(
    z: float,
    *,
    omega_b_h2: float = ACTIVE_BARYON_SLOTS.omega_b_geom_h2,
    helium_mass_fraction: float = ACTIVE_BRANCH.YHe,
    t_io_ref_k: float = T_IO_REF_K,
) -> LocalBackgroundState:
    """Package the theorem-grade local background map at one redshift."""

    return LocalBackgroundState(
        z_obs=z,
        u=local_u(z),
        a_loc_m=local_scale_factor_m(z),
        H_loc_s_inv=local_hubble_si(z),
        T_r_loc_K=local_radiation_temperature_K(z, t_io_ref_k=t_io_ref_k),
        n_H_geom_m3=hydrogen_number_density_m3(
            z,
            omega_b_h2=omega_b_h2,
            helium_mass_fraction=helium_mass_fraction,
        ),
    )


@dataclass(frozen=True)
class Stage2History:
    """Typed Stage-2 history state sampled on an observer-redshift grid.

    The exact Stage-2 solver state is the extended object
    `(x_e, T_m, D_-(q;z), L_-(z))`. This container keeps that typing visible
    even though the live calculator only consumes `x_e` directly today.
    """

    z_obs: tuple[float, ...]
    x_e: tuple[float, ...]
    T_m_loc_K: tuple[float, ...]
    D_minus_norm: tuple[float, ...] | None = None
    L_minus: tuple[float, ...] | None = None

    def __post_init__(self) -> None:
        if len(self.z_obs) != len(self.x_e) or len(self.z_obs) != len(self.T_m_loc_K):
            raise ValueError("z_obs, x_e, and T_m_loc_K must have the same length")
        if len(self.z_obs) < 2:
            raise ValueError("Stage2History requires at least two samples")
        if any(z < 0.0 for z in self.z_obs):
            raise ValueError("z_obs values must be non-negative")
        if any(b <= a for a, b in zip(self.z_obs, self.z_obs[1:])):
            raise ValueError("z_obs must be strictly increasing")
        if any(x < 0.0 for x in self.x_e):
            raise ValueError("x_e values must be non-negative")
        if self.D_minus_norm is not None and len(self.D_minus_norm) != len(self.z_obs):
            raise ValueError("D_minus_norm must match z_obs length when provided")
        if self.L_minus is not None and len(self.L_minus) != len(self.z_obs):
            raise ValueError("L_minus must match z_obs length when provided")

    @classmethod
    def from_sequences(
        cls,
        z_obs: Sequence[float],
        x_e: Sequence[float],
        T_m_loc_K: Sequence[float],
        *,
        D_minus_norm: Sequence[float] | None = None,
        L_minus: Sequence[float] | None = None,
    ) -> Stage2History:
        """Build a validated Stage-2 history from generic sequences."""

        return cls(
            z_obs=_float_tuple(z_obs, name="z_obs"),
            x_e=_float_tuple(x_e, name="x_e"),
            T_m_loc_K=_float_tuple(T_m_loc_K, name="T_m_loc_K"),
            D_minus_norm=(
                None
                if D_minus_norm is None
                else _float_tuple(D_minus_norm, name="D_minus_norm")
            ),
            L_minus=None if L_minus is None else _float_tuple(L_minus, name="L_minus"),
        )


@dataclass(frozen=True)
class VisibilityPacket:
    """Reduced observer-side visibility packet built from an exact local history.

    `tau_obs` is always measured relative to the supplied lower redshift
    boundary. It becomes the full observer-to-source optical depth only when
    the history starts at `z = 0`.
    """

    z_obs: tuple[float, ...]
    d_tau_obs_dz: tuple[float, ...]
    tau_obs: tuple[float, ...]
    g_obs: tuple[float, ...]
    lower_boundary_z: float
    absolute_to_observer: bool


class ExactStage2Solver(Protocol):
    """Protocol for theorem-grade exact Stage-2 history solvers.

    The live calculator does not implement this operator yet. Any future solver
    admitted here must respect the Paper 31/32 extended-state grammar rather
    than collapsing to a one-field Peebles shortcut.
    """

    def solve_history(self, z_obs: Sequence[float]) -> Stage2History:
        """Return the exact IO Stage-2 history on the requested redshift grid."""


class OpenTheoremBoundaryError(RuntimeError):
    """Raised when code reaches an intentionally open theorem boundary."""


def solve_exact_stage2_history(
    z_obs: Sequence[float],
    *,
    solver: ExactStage2Solver | None = None,
) -> Stage2History:
    """Request the exact Stage-2 history or fail honestly if none exists.

    Status: `open`
    The exact dynamic-network completion inside `U_rec^hist` remains the active
    Paper 31/32 frontier. The live calculator therefore refuses to invent one.
    """

    if solver is None:
        raise OpenTheoremBoundaryError(
            "Exact Stage-2 recombination history remains open. "
            "Pass an explicit solver that implements the Paper 31/32 extended-state grammar."
        )
    return solver.solve_history(z_obs)


def _cumulative_trapezoid(x: Sequence[float], y: Sequence[float]) -> tuple[float, ...]:
    """Return the cumulative trapezoid integral with a zero lower boundary."""

    cumulative = [0.0]
    total = 0.0
    for x0, x1, y0, y1 in zip(x, x[1:], y, y[1:]):
        total += 0.5 * (y0 + y1) * (x1 - x0)
        cumulative.append(total)
    return tuple(cumulative)


def build_visibility_packet(
    history: Stage2History,
    *,
    omega_b_h2: float = ACTIVE_BARYON_SLOTS.omega_b_geom_h2,
    helium_mass_fraction: float = ACTIVE_BRANCH.YHe,
) -> VisibilityPacket:
    """Build the reduced visibility packet from an exact local Stage-2 history.

    Status: `derived / scoped`
    The visibility operator is closed at the typed level as
    `F_red o I_LOS o T_clock o U_rec^hist`. This helper implements the last
    three steps on a supplied exact history grid without inventing a packet
    compression theorem.
    """

    d_tau_obs_dz = tuple(
        optical_depth_gradient_per_redshift(
            z,
            x_e,
            omega_b_h2=omega_b_h2,
            helium_mass_fraction=helium_mass_fraction,
        )
        for z, x_e in zip(history.z_obs, history.x_e)
    )
    tau_obs = _cumulative_trapezoid(history.z_obs, d_tau_obs_dz)
    g_obs = tuple(
        math.exp(-tau_value) * gradient
        for tau_value, gradient in zip(tau_obs, d_tau_obs_dz)
    )
    lower_boundary_z = history.z_obs[0]
    return VisibilityPacket(
        z_obs=history.z_obs,
        d_tau_obs_dz=d_tau_obs_dz,
        tau_obs=tau_obs,
        g_obs=g_obs,
        lower_boundary_z=lower_boundary_z,
        absolute_to_observer=math.isclose(lower_boundary_z, 0.0, abs_tol=1.0e-12),
    )


__all__ = [
    "ExactStage2Solver",
    "LocalBackgroundState",
    "OpenTheoremBoundaryError",
    "Stage2History",
    "VisibilityPacket",
    "build_visibility_packet",
    "free_electron_density_m3",
    "hydrogen_number_density_m3",
    "local_background_state",
    "local_baryon_loading_R",
    "local_hubble_si",
    "local_os_proper_time_dz",
    "local_radiation_temperature_K",
    "local_scale_factor_m",
    "local_scattering_to_expansion_ratio",
    "local_sound_speed_m_s",
    "local_thomson_scattering_rate_si",
    "local_u",
    "optical_depth_gradient_per_redshift",
    "primitive_local_kappa_prime",
    "saha_equilibrium_xe",
    "solve_exact_stage2_history",
]
