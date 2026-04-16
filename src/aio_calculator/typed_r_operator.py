"""Typed photon-baryon loading operator on the closed IO perturbation stack.

This module closes the surviving `R` debt at the honest scope supported by the
current archive plus Premise 2 standard microphysics.

What is closed here:

- `derived / scoped`: the primitive local loading ratio
  `R_geom(z) = 3 rho_b,geom(z) / [4 rho_gamma(z)]`
- `derived / scoped`: the hierarchy-convention loading
  `R_hier(z) = 1 / R_geom(z) = 4 rho_gamma(z) / [3 rho_b,geom(z)]`
- `derived / scoped`: the momentum-exchange site maps
  `Gamma_gammab = thomson_drag_rate`
  and
  `Gamma_bgamma = R_hier * thomson_drag_rate = 1 / [R_geom tau_c]`
- `derived / scoped`: the pressure/inertia site maps
  `c_bgamma^2 = 1 / [3 (1 + R_geom)]`,
  `M_bgamma^TCA = 1 + R_hier`,
  and
  `L_odd/even^TCA = R_hier / (1 + R_hier)`
- `derived / scoped`: the tight-coupling slip factor
  `F_tca = tau_c / (1 + R_hier)` with `tau_c = 1 / thomson_drag_rate`
- `derived / scoped`: the split Silk-damping operator
  `D_heat = R_geom^2 / [6 (1+R_geom)^2 thomson_drag_rate]`
  and
  `D_visc = 16 / [90 (1+R_geom) thomson_hierarchy_rate]`
- `derived / scoped`: the dynamic odd/even loading is generated inside the
  oscillator by `c_bgamma^2` and `L_odd/even`, while the observed peak-height
  ratio is still a downstream transfer/readout functional, not a new primitive
  baryon-slot reassignment

What is *not* claimed here:

- no theorem-grade back-propagation of observer-side `omega_b,eff` into the
  primitive local `R` leg
- no theorem-grade one-slot closure of the full observed peak/readout hierarchy
- no claim that the exploratory TT driver already implements every one of these
  composites on its current low-redshift handoff branch
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .constants import ACTIVE_BARYON_SLOTS, T_IO_REF_K
from .recombination import local_baryon_loading_R
from .thomson_history_contract import ThomsonHistorySample


def _finite(value: float, *, name: str) -> float:
    """Require one finite scalar."""

    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _positive(value: float, *, name: str) -> float:
    """Require one strictly positive finite scalar."""

    value = _finite(value, name=name)
    if value <= 0.0:
        raise ValueError(f"{name} must be strictly positive")
    return value


def single_rate_silk_diffusion_integrand(R_loading: float, scattering_rate: float) -> float:
    """Return the standard single-rate Silk diffusion integrand.

    This is the unsplit exterior/local formula

    `D_silk = [1 / (6 scattering_rate)] * [R^2 / (1+R) + 16/15] / (1+R)`

    used as the reduction target for the typed split when
    `thomson_drag_rate = thomson_hierarchy_rate = scattering_rate`.
    """

    R_loading = _positive(R_loading, name="R_loading")
    scattering_rate = _positive(scattering_rate, name="scattering_rate")
    return (1.0 / (6.0 * scattering_rate)) * (
        (R_loading * R_loading) / (1.0 + R_loading) + 16.0 / 15.0
    ) / (1.0 + R_loading)


@dataclass(frozen=True)
class TypedROperatorSample:
    """Role-by-role typed `R` composites on one explicit history sample."""

    z_obs: float
    R_local_geom: float
    R_hierarchy: float
    thomson_drag_rate: float
    thomson_hierarchy_rate: float
    tau_c_drag: float
    photon_momentum_exchange_rate: float
    baryon_momentum_exchange_rate: float
    photon_baryon_sound_speed_sq: float
    baryon_inertia_factor: float
    odd_even_dynamic_loading_factor: float
    inverse_baryon_loading_factor: float
    tight_coupling_slip_factor: float
    diffusion_heat_conduction_integrand: float
    diffusion_viscosity_integrand: float
    diffusion_total_integrand: float
    odd_even_loading_driver: float
    observer_readout_slot: str
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]

    def __post_init__(self) -> None:
        _finite(self.z_obs, name="z_obs")
        for name in (
            "R_local_geom",
            "R_hierarchy",
            "thomson_drag_rate",
            "thomson_hierarchy_rate",
            "tau_c_drag",
            "photon_momentum_exchange_rate",
            "baryon_momentum_exchange_rate",
            "photon_baryon_sound_speed_sq",
            "baryon_inertia_factor",
            "odd_even_dynamic_loading_factor",
            "inverse_baryon_loading_factor",
            "tight_coupling_slip_factor",
            "diffusion_heat_conduction_integrand",
            "diffusion_viscosity_integrand",
            "diffusion_total_integrand",
            "odd_even_loading_driver",
        ):
            _positive(getattr(self, name), name=name)


def build_typed_r_operator_sample(
    z_obs: float,
    thomson: ThomsonHistorySample,
    *,
    omega_b_geom_h2: float = ACTIVE_BARYON_SLOTS.omega_b_geom_h2,
    t_io_ref_k: float = T_IO_REF_K,
) -> TypedROperatorSample:
    """Return the theorem-grade typed `R` map on one explicit sample.

    The closure is:

    - primitive local acoustic loading:
      `R_geom = 3 rho_b,geom / (4 rho_gamma)`
    - executable hierarchy loading convention:
      `R_hier = 1 / R_geom`
    - photon-side momentum exchange:
      `Gamma_gammab = thomson_drag_rate`
    - baryon-side momentum exchange:
      `Gamma_bgamma = R_hier * thomson_drag_rate = thomson_drag_rate / R_geom`
    - pressure/inertia maps:
      `c_bgamma^2 = 1 / [3 (1 + R_geom)]`
      `M_bgamma^TCA = 1 + R_hier`
      `L_odd/even^TCA = R_hier / (1 + R_hier)`
    - TCA slip factor:
      `F_tca = tau_c / (1 + R_hier)`
    - split Silk diffusion:
      `D_heat = R_geom^2 / [6 (1+R_geom)^2 thomson_drag_rate]`
      `D_visc = 16 / [90 (1+R_geom) thomson_hierarchy_rate]`

    The observed odd/even peak-height ratio is *not* itself a primitive `R`
    assignment. The oscillator is dynamically loaded by the local enthalpy
    maps above; the final peak-height readout is downstream and remains
    observer-side.
    """

    z_obs = _finite(z_obs, name="z_obs")
    R_loading = _positive(
        local_baryon_loading_R(
            z_obs,
            omega_b_geom_h2=omega_b_geom_h2,
            t_io_ref_k=t_io_ref_k,
        ),
        name="R_local_geom",
    )
    drag_rate = _positive(thomson.thomson_drag_rate, name="thomson_drag_rate")
    hierarchy_rate = _positive(thomson.thomson_hierarchy_rate, name="thomson_hierarchy_rate")
    _positive(thomson.tau_c, name="tau_c")
    tau_c = 1.0 / drag_rate
    hierarchy_loading = 1.0 / R_loading
    inertia_factor = 1.0 + hierarchy_loading
    odd_even_factor = hierarchy_loading / inertia_factor
    D_heat = (R_loading * R_loading) / (6.0 * (1.0 + R_loading) * (1.0 + R_loading) * drag_rate)
    D_visc = 16.0 / (90.0 * (1.0 + R_loading) * hierarchy_rate)
    return TypedROperatorSample(
        z_obs=z_obs,
        R_local_geom=R_loading,
        R_hierarchy=hierarchy_loading,
        thomson_drag_rate=drag_rate,
        thomson_hierarchy_rate=hierarchy_rate,
        tau_c_drag=tau_c,
        photon_momentum_exchange_rate=drag_rate,
        baryon_momentum_exchange_rate=hierarchy_loading * drag_rate,
        photon_baryon_sound_speed_sq=1.0 / (3.0 * (1.0 + R_loading)),
        baryon_inertia_factor=inertia_factor,
        odd_even_dynamic_loading_factor=odd_even_factor,
        inverse_baryon_loading_factor=1.0 / hierarchy_loading,
        tight_coupling_slip_factor=tau_c / inertia_factor,
        diffusion_heat_conduction_integrand=D_heat,
        diffusion_viscosity_integrand=D_visc,
        diffusion_total_integrand=D_heat + D_visc,
        odd_even_loading_driver=R_loading,
        observer_readout_slot="omega_b,eff",
        claim_status="derived / scoped as maps",
        provenance_node_ids=(
            "paper29.sound_speed_selector",
            "paper32.typed_baryon_slot_spec",
            "calculator.thomson_history_realization",
            "local.typed_r_operator",
            "local.typed_r_site_uniqueness",
        ),
        scope_boundary=(
            "Closes the full oscillator-site `R` maps and their Thomson-tuple composites on one explicit sample.",
            "Does not back-propagate observer-side `omega_b,eff` into the primitive local enthalpy ratio.",
            "Does not claim that the full observed odd/even peak ratio is itself a one-slot `R` assignment.",
        ),
    )


__all__ = [
    "TypedROperatorSample",
    "build_typed_r_operator_sample",
    "single_rate_silk_diffusion_integrand",
]
