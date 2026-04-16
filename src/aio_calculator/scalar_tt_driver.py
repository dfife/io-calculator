"""Scoped closed-`S^3` TT driver with explicit validation diagnostics.

This module turns the current perturbation stack into a reproducible numerical
driver without overstating what it closes.

Closed here:

- `conditional / scoped`: a reproducible active-branch TT driver using
  - the inherited-FULL Stage-2 history on `z <= z_exact_max`
  - a thermal prehistory extension on `z > z_exact_max`
  - a visibility-derived conformal Thomson tuple
  - the local scalar acoustic generator
  - the transparent closed-`S^3` transfer projector
  - shell-weighted `C_l` assembly

Not closed here:

- a theorem-grade validated TT spectrum on the active branch
- the exact hierarchy-wide metric-source closure
- the exact hierarchy-wide Thomson/TCA closure
- a universal IO-native Stage-2 renormalization theorem beyond the inherited
  FULL scope

The resulting spectrum is numerically executable and reproducible, but its
validation status must be read from the returned diagnostics rather than
assumed from the existence of a `C_l` array.

Public-release convention note:

- The shell sum in this module is not just "some weight times `|Delta_l|^2`".
- It is the composition of a source-side shell law with an observer-side
  closed-`S^3` Jacobian from Paper 28.
- The crucial convention choice is whether the active source theorem
  `A_s W_N^(+)` on the repaired affine odd-shell plus branch is being inserted
  as the shell covariance `P_X(n)` or as the dimensionless shell spectrum
  `Delta_q^2(n)`.
- That choice is exposed explicitly through
  `ScopedTTDriverConfig.source_shell_weight_interpretation` and must never be
  hidden behind an undocumented default.

Public-release implementation note:

- The thermal prehistory on `z > z_exact_max` is a shell-seeding carrier built
  on one common early-time slice for the whole run.
- That common slice is intentional. A shell-local localization diagnostic was
  tested and found to move the TT peak materially, which means it changes the
  cross-shell phase carrier rather than acting as a harmless runtime cleanup.
- Therefore the live driver keeps one common seed/history carrier set by the
  configured support ceiling. Any future shell-local alternative would require
  a new theorem-grade phase-coherent replacement, not a silent refactor.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import math
from dataclasses import dataclass, replace
from itertools import repeat

from .closed_shell_power import covariance_from_delta_q, shell_variance_prefactor
from .constants import ACTIVE_PERTURBATION_PACKAGE, C_KM_S, PerturbationBranchPackage
from .los_transfer import ClosedAngularPowerSpectrum, assemble_closed_s3_angular_power_spectrum, weight_closed_s3_transfer_packet
from .model import CurvedBackgroundModel, omega_gamma_h2
from .readout_functionals import PeakFunctionalResult, evaluate_discrete_peak_functional
from .recombination import (
    Stage2History,
    VisibilityPacket,
    build_visibility_packet,
    local_radiation_temperature_K,
    primitive_local_kappa_prime,
)
from .scalar_acoustic_operator import (
    ClosedS3ScalarAcousticSample,
    ScalarHierarchyRegime,
    _baryon_sound_speed_sq,
    evaluate_closed_s3_scalar_acoustic_derivatives,
    predict_first_order_tight_coupling_contract,
)
from .scalar_hierarchy import ScalarHierarchyState, build_scalar_hierarchy_carrier
from .scalar_metric_state import (
    build_newtonian_scalar_metric_state,
    build_scalar_stress_energy_summary,
    newtonian_constraint_phi,
)
from .scalar_transfer_projector import (
    build_newtonian_scalar_source_history_integrated_by_parts,
    project_closed_s3_scalar_temperature,
)
from .source_initial_conditions import (
    _class_seed_background_fractions,
    build_closed_s3_newtonian_adiabatic_seed,
    build_scalar_source_shell_weight,
)
from .source_block import active_plus_branch_supports_shell
from .stage2_dynamic_network import (
    InheritedFullStage2DynamicHistoryBuilder,
    build_inherited_full_stage2_history,
)
from .thomson_history_contract import (
    ThomsonHistoryContract,
    ThomsonHistorySample,
    build_thomson_history_contract,
    build_typed_split_thomson_history_realization,
)
from .typed_r_operator import build_typed_r_operator_sample


def _nonlinear_grid(z_max: float, samples: int) -> tuple[float, ...]:
    """Return the monotone nonlinear redshift grid used by the scoped driver."""

    if samples < 2:
        raise ValueError("samples must be at least 2")
    z_max = float(z_max)
    if not math.isfinite(z_max) or z_max <= 0.0:
        raise ValueError("z_max must be positive and finite")
    return tuple(z_max * (1.0 - (1.0 - i / (samples - 1)) ** 4) for i in range(samples))


def _positive(value: float, *, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return value


def _finite(value: float, *, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _finite_difference(x: tuple[float, ...], y: tuple[float, ...], index: int) -> float:
    """Return the first derivative on one explicit sample grid."""

    if len(x) != len(y):
        raise ValueError("x and y must have the same length")
    if len(x) < 2:
        raise ValueError("at least two samples are required")
    if index == 0:
        return (y[1] - y[0]) / (x[1] - x[0])
    if index == len(x) - 1:
        return (y[-1] - y[-2]) / (x[-1] - x[-2])
    return (y[index + 1] - y[index - 1]) / (x[index + 1] - x[index - 1])


def _seed_start_is_early_enough(
    n: int,
    *,
    z: float,
    package: PerturbationBranchPackage,
    config: "ScopedTTDriverConfig",
) -> bool:
    """Return whether the shell seed lies in the CLASS-style asymptotic window."""

    model = CurvedBackgroundModel(branch=package.branch)
    curvature_radius = model.curvature_radius_mpc
    k_n = math.sqrt(n * (n + 2.0)) / curvature_radius
    a_prime_over_a = model.hubble_km_s_mpc(z) / (C_KM_S * (1.0 + z))
    tau_c = 1.0 / primitive_local_kappa_prime(
        z,
        1.0,
        omega_b_h2=package.baryon_slots.omega_b_geom_h2,
        helium_mass_fraction=package.branch.YHe,
    )
    return (
        tau_c * a_prime_over_a <= config.seed_start_tau_c_over_tau_h
        and k_n / a_prime_over_a <= config.seed_start_tau_h_over_tau_k
    )


def _required_seed_redshift(
    n: int,
    *,
    package: PerturbationBranchPackage,
    config: "ScopedTTDriverConfig",
) -> float:
    """Return the minimum redshift at which the shell seed is asymptotically safe."""

    lower = max(config.z_exact_max, 10.0)
    if _seed_start_is_early_enough(n, z=lower, package=package, config=config):
        return lower

    upper = max(config.z_init, lower * 2.0)
    while not _seed_start_is_early_enough(n, z=upper, package=package, config=config):
        upper *= 2.0
        if upper > 1.0e9:
            raise ValueError("could not find an early-enough shell seed redshift below z=1e9")

    lo = lower
    hi = upper
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if _seed_start_is_early_enough(n, z=mid, package=package, config=config):
            hi = mid
        else:
            lo = mid
    return hi


@dataclass(frozen=True)
class ScopedTTDriverConfig:
    """Configuration for the scoped TT driver.

    Most fields control numerics or scope. One field is a physics convention:

    - `source_shell_weight_interpretation = "covariance"` means the active
      source law `A_s W_N^(+)` is inserted directly as the closed-`S^3` shell
      covariance `P_X(n)`.
    - `source_shell_weight_interpretation = "delta_q_sq"` means
      `A_s W_N^(+)` is interpreted as `Delta_q^2(n)` and is first converted
      through the exact Paper 28 Jacobian
      `P_X(n) = [2 pi^2 R^3 / (n+1)^3] Delta_q^2(n)`.
    - `constraint_consistent_seed = True` forces the initial shell seed onto
      the closed Newtonian energy-constraint manifold once, then lets the
      subsequent evolution run with the chosen `project_metric_constraint`
      policy. This exists as a diagnostic for separating seed-manifold errors
      from continuous Einstein-side closure errors.
    - `constraint_metric_source_only = True` uses the closed Newtonian
      constraint to build the metric/source drive on every shell substep
      without overwriting the stored `phi` state. This separates a missing
      source-side Einstein closure from a missing state-manifold projection.
    - `source_shell_support = "odd_plus_branch"` restricts the active source
      shell sum to the repaired odd-shell bridge image from Paper 32 hidden-
      identification repair. `"all"` is retained only as an explicit
      off-support diagnostic.

    This convention must stay explicit because the two interpretations give
    very different UV shell weights and therefore very different TT behavior.
    """

    z_exact_max: float = 3000.0
    z_init: float = 20000.0
    exact_history_samples: int = 200
    prehistory_samples: int = 80
    n_max: int = 450
    ell_max: int = 350
    shell_step: int = 1
    shell_parallel_workers: int = 1
    temperature_hierarchy_lmax: int = 6
    polarization_hierarchy_lmax: int = 6
    include_pressureless_matter: bool = True
    use_first_order_tca: bool = True
    observer_tau_target_z: float = 1.0e7
    observer_tau_samples: int = 8192
    line_of_sight_distance_samples: int = 2048
    peak_window_min: int = 120
    peak_window_max: int = 320
    shell_substep_kdt_max: float = 0.35
    shell_substep_drag_dt_max: float = 0.5
    shell_substep_max: int = 256
    project_metric_constraint: bool = True
    constraint_consistent_seed: bool = False
    constraint_metric_source_only: bool = False
    metric_baryon_momentum_slot: str = "eff"
    tight_coupling_trigger_tau_c_over_tau_h: float = 0.015
    tight_coupling_trigger_tau_c_over_tau_k: float = 0.01
    seed_start_tau_c_over_tau_h: float = 0.0015
    seed_start_tau_h_over_tau_k: float = 0.07
    perturbation_package: PerturbationBranchPackage = ACTIVE_PERTURBATION_PACKAGE
    visibility_opacity_factor: float = 1.0
    drag_rate_factor: float = 1.0
    hierarchy_rate_factor: float = 1.0
    source_shell_weight_interpretation: str = "covariance"
    source_shell_support: str = "odd_plus_branch"

    def __post_init__(self) -> None:
        _positive(self.z_exact_max, name="z_exact_max")
        _positive(self.z_init, name="z_init")
        if self.z_init <= self.z_exact_max:
            raise ValueError("z_init must exceed z_exact_max")
        if self.exact_history_samples < 2:
            raise ValueError("exact_history_samples must be at least 2")
        if self.prehistory_samples < 2:
            raise ValueError("prehistory_samples must be at least 2")
        if self.n_max < 4:
            raise ValueError("n_max must be at least 4 on the full-hierarchy shell range")
        if self.ell_max < 2:
            raise ValueError("ell_max must be at least 2")
        if self.shell_step < 1:
            raise ValueError("shell_step must be positive")
        if self.shell_parallel_workers < 1:
            raise ValueError("shell_parallel_workers must be at least 1")
        if self.temperature_hierarchy_lmax < 3:
            raise ValueError("temperature_hierarchy_lmax must be at least 3")
        if self.polarization_hierarchy_lmax < 3:
            raise ValueError("polarization_hierarchy_lmax must be at least 3")
        if self.observer_tau_samples < 2:
            raise ValueError("observer_tau_samples must be at least 2")
        if self.line_of_sight_distance_samples < 2:
            raise ValueError("line_of_sight_distance_samples must be at least 2")
        if self.peak_window_min < 2 or self.peak_window_max < self.peak_window_min:
            raise ValueError("peak window must satisfy 2 <= min <= max")
        _positive(self.shell_substep_kdt_max, name="shell_substep_kdt_max")
        _positive(self.shell_substep_drag_dt_max, name="shell_substep_drag_dt_max")
        if self.shell_substep_max < 1:
            raise ValueError("shell_substep_max must be at least 1")
        if self.metric_baryon_momentum_slot not in {"geom", "eff", "clustering"}:
            raise ValueError("metric_baryon_momentum_slot must be one of: geom, eff, clustering")
        _positive(self.tight_coupling_trigger_tau_c_over_tau_h, name="tight_coupling_trigger_tau_c_over_tau_h")
        _positive(self.tight_coupling_trigger_tau_c_over_tau_k, name="tight_coupling_trigger_tau_c_over_tau_k")
        _positive(self.seed_start_tau_c_over_tau_h, name="seed_start_tau_c_over_tau_h")
        _positive(self.seed_start_tau_h_over_tau_k, name="seed_start_tau_h_over_tau_k")
        _positive(self.visibility_opacity_factor, name="visibility_opacity_factor")
        _positive(self.drag_rate_factor, name="drag_rate_factor")
        _positive(self.hierarchy_rate_factor, name="hierarchy_rate_factor")
        if self.source_shell_weight_interpretation not in {"covariance", "delta_q_sq"}:
            raise ValueError("source_shell_weight_interpretation must be one of: covariance, delta_q_sq")
        if self.source_shell_support not in {"all", "odd_plus_branch"}:
            raise ValueError("source_shell_support must be one of: all, odd_plus_branch")


@dataclass(frozen=True)
class ScopedThermalHistory:
    """Merged exact plus thermal-prehistory Stage-2 history."""

    history: Stage2History
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


@dataclass(frozen=True)
class ConformalClockGrid:
    """Observer conformal clock and local background derivatives on one grid."""

    tau_observer_mpc: float
    z_obs: tuple[float, ...]
    tau_samples_mpc: tuple[float, ...]
    dc_dz_mpc: tuple[float, ...]
    a_prime_over_a_mpc_inv: tuple[float, ...]
    a_primeprime_over_a_mpc_inv2: tuple[float, ...]
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


@dataclass(frozen=True)
class TTValidationSummary:
    """Numerical validation summary for one scoped TT run."""

    ell_peak: int
    peak_value: float
    peak_near_220: bool
    c_220_over_peak: float
    plateau_2_to_30_ratio: float
    high_ell_support_ratio: float
    all_finite: bool
    notes: tuple[str, ...]


@dataclass(frozen=True)
class ScopedTTDriverResult:
    """The current executable scoped TT driver output."""

    config: ScopedTTDriverConfig
    staged_history: ScopedThermalHistory
    conformal_clock: ConformalClockGrid
    thomson_history: ThomsonHistoryContract
    spectrum: ClosedAngularPowerSpectrum
    peak: PeakFunctionalResult
    validation: TTValidationSummary
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


def canonical_first_peak_tt_config(
    *,
    shell_parallel_workers: int = 1,
    ell_max: int = 350,
) -> ScopedTTDriverConfig:
    """Return the current canonical first-peak TT support configuration.

    Status: `conditional / scoped`

    This helper does not claim a theorem-grade full TT closure. It returns the
    strongest current executable branch for the first acoustic peak:

    - repaired metric/source closure on the active package
    - odd-shell bridge support
    - covariance shell weighting
    - finite-history carrier `exact_history_samples = 120`,
      `prehistory_samples = 40`
    - full odd-support shell ladder through `n_max = 501`

    Why this exact configuration is exposed:

    - the executable TT driver is still sensitive to the unresolved
      source-to-seed / high-shell phase frontier
    - this branch is the one that reproducibly places the first broad TT peak
      near `ell ~ 220`
    - higher shell ceilings such as `n_max = 601` remain an explicit open
      boundary rather than something this helper pretends to solve
    """

    return ScopedTTDriverConfig(
        exact_history_samples=120,
        prehistory_samples=40,
        n_max=501,
        ell_max=ell_max,
        shell_step=1,
        shell_parallel_workers=shell_parallel_workers,
        project_metric_constraint=False,
        constraint_metric_source_only=True,
        constraint_consistent_seed=True,
        metric_baryon_momentum_slot="eff",
        source_shell_weight_interpretation="covariance",
        source_shell_support="odd_plus_branch",
    )


def run_canonical_first_peak_tt_driver(
    *,
    shell_parallel_workers: int = 1,
    ell_max: int = 350,
    builder: InheritedFullStage2DynamicHistoryBuilder | None = None,
) -> ScopedTTDriverResult:
    """Run the canonical conditional/scoped first-peak TT branch."""

    return run_scoped_tt_driver(
        canonical_first_peak_tt_config(
            shell_parallel_workers=shell_parallel_workers,
            ell_max=ell_max,
        ),
        builder=builder,
    )


def _cb2_history(
    history: Stage2History,
    *,
    helium_mass_fraction: float,
) -> tuple[float, ...]:
    """Return the carried baryon sound-speed history on one explicit grid."""

    return tuple(
        _baryon_sound_speed_sq(
            z_item,
            x_e_item,
            T_m_item,
            _finite_difference(history.z_obs, history.T_m_loc_K, index),
            helium_mass_fraction=helium_mass_fraction,
        )
        for index, (z_item, x_e_item, T_m_item) in enumerate(zip(history.z_obs, history.x_e, history.T_m_loc_K))
    )


def _linear_interpolate(start: float, end: float, fraction: float) -> float:
    """Return the explicit linear interpolation between two finite scalars."""

    return (1.0 - fraction) * start + fraction * end


def _constraint_anchor_weight(carrier, *, conformal_time_mpc: float) -> float:
    """Return the superhorizon-safe weight for Newtonian constraint anchoring.

    The exact closed energy constraint is the right subhorizon closure, but the
    leading superhorizon seed in the current scoped driver is not built as a
    full constraint-preserving DAE solve. The driver therefore turns on the
    algebraic constraint smoothly across horizon entry rather than by a blind
    all-times overwrite.
    """

    if carrier.mode.n < 24:
        return 0.0
    k_tau = (
        math.sqrt(carrier.mode.primary_spatial_eigenvalue)
        / carrier.curvature_radius_mpc
        * float(conformal_time_mpc)
    )
    if k_tau <= 0.25:
        return 0.0
    if k_tau >= 1.0:
        return 1.0
    x = (k_tau - 0.25) / 0.75
    return x * x * (3.0 - 2.0 * x)


def _tt_shell_weight(
    shell_n: int,
    *,
    radius: float,
    config: ScopedTTDriverConfig,
) -> float:
    """Return the shell weight used in the scoped TT sum.

    Exact structure:

    `C_l = sum_n w(n) |Delta_l(n)|^2`

    with

    `w(n) = ((n+1)^2 / (2 pi^2 R^3)) P_X(n)`.

    What this helper decides is the map from the active source theorem
    `A_s W_N` to `P_X(n)`:

    - `covariance`: `P_X(n) = A_s W_N`
    - `delta_q_sq`: `P_X(n) = covariance_from_delta_q(A_s W_N, n, R)`

    Why it is explicit:

    - Paper 28 fixes the observer-side Jacobian, but it does not silently tell
      the runtime whether a source-side law is already `P_X(n)` or instead a
      dimensionless shell spectrum.
    - The controlled `delta_q_sq` branch exists precisely so public readers can
      see and test that convention choice directly.
    """

    if config.source_shell_support == "odd_plus_branch" and not active_plus_branch_supports_shell(shell_n):
        return 0.0
    source_weight = build_scalar_source_shell_weight(shell_n).covariance_weight
    if config.source_shell_weight_interpretation == "covariance":
        shell_covariance = source_weight
    else:
        shell_covariance = covariance_from_delta_q(source_weight, shell_n, radius=radius)
    return shell_covariance * shell_variance_prefactor(shell_n, radius=radius)


def _source_supported_shell_values(config: ScopedTTDriverConfig) -> tuple[int, ...]:
    """Return the explicit shell ladder used in the scoped TT sum.

    `shell_step` samples the already-supported shell family rather than the raw
    integer ladder, so odd-branch support does not silently disappear just
    because the ladder happens to start at `n=4`.
    """

    all_shells = tuple(range(4, config.n_max + 1))
    if config.source_shell_support == "all":
        supported = all_shells
    else:
        supported = tuple(n for n in all_shells if active_plus_branch_supports_shell(n))
    return supported[:: config.shell_step]


def _state_to_vector(
    state: ScalarHierarchyState,
    delta_ur: float,
    theta_ur: float,
    ur_multipoles: tuple[float, ...],
    delta_m: float,
    theta_m: float,
) -> tuple[float, ...]:
    """Flatten the scalar hierarchy state plus scoped UR/matter carriers."""

    return (
        state.phi,
        state.delta_gamma,
        state.theta_gamma,
        state.delta_b,
        state.theta_b,
        *state.photon_multipoles,
        *state.polarization_multipoles,
        delta_ur,
        theta_ur,
        *ur_multipoles,
        delta_m,
        theta_m,
    )


def _vector_to_state(
    vector: tuple[float, ...],
    *,
    photon_count: int,
    polarization_count: int,
    ur_count: int,
    psi: float,
) -> tuple[ScalarHierarchyState, float, float, tuple[float, ...], float, float]:
    """Rebuild the shell state plus scoped UR/matter carriers."""

    photon_end = 5 + photon_count
    polarization_end = photon_end + polarization_count
    ur_start = polarization_end
    ur_end = ur_start + 2 + ur_count
    state = ScalarHierarchyState(
        phi=vector[0],
        psi=psi,
        delta_gamma=vector[1],
        theta_gamma=vector[2],
        delta_b=vector[3],
        theta_b=vector[4],
        photon_multipoles=tuple(vector[5:photon_end]),
        polarization_multipoles=tuple(vector[photon_end:polarization_end]),
    )
    return (
        state,
        vector[ur_start],
        vector[ur_start + 1],
        tuple(vector[ur_start + 2 : ur_end]),
        vector[ur_end],
        vector[ur_end + 1],
    )


def _build_ur_adiabatic_seed(
    carrier,
    *,
    conformal_time_mpc: float,
    a_prime_over_a_mpc_inv: float,
    scale_factor: float,
    package: PerturbationBranchPackage,
    ur_count: int,
    curvature_amplitude: float = 1.0,
) -> tuple[float, float, tuple[float, ...]]:
    """Return the closed adiabatic ultra-relativistic seed carried by the TT driver."""

    tau = _positive(conformal_time_mpc, name="conformal_time_mpc")
    a_prime_over_a = _positive(a_prime_over_a_mpc_inv, name="a_prime_over_a_mpc_inv")
    scale_factor = _positive(scale_factor, name="scale_factor")
    k_sq = carrier.mode.primary_spatial_eigenvalue / carrier.curvature_radius_mpc**2
    k = math.sqrt(k_sq)
    curvature_k = 1.0 / carrier.curvature_radius_mpc**2
    s2_sq = 1.0 - 3.0 * curvature_k / k_sq
    base_seed = build_closed_s3_newtonian_adiabatic_seed(
        carrier,
        conformal_time_mpc=tau,
        a_prime_over_a_mpc_inv=a_prime_over_a_mpc_inv,
        scale_factor=scale_factor,
        package=package,
        curvature_amplitude=curvature_amplitude,
    )
    fracnu, _, fracb, _, _, om = _class_seed_background_fractions(
        scale_factor=scale_factor,
        package=package,
    )
    ktau_sq = k_sq * tau * tau
    ktau_cubed = k * tau * ktau_sq
    delta_ur_s = -(ktau_sq / 3.0) * (1.0 - om * tau / 5.0) * curvature_amplitude * s2_sq
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
    shear_ur = (
        ktau_sq
        / (45.0 + 12.0 * fracnu)
        * (3.0 * s2_sq - 1.0)
        * (1.0 + (4.0 * fracnu - 5.0) / (4.0 * (2.0 * fracnu + 15.0)) * tau * om)
        * curvature_amplitude
    )
    l3_ur = ktau_cubed * 2.0 / (7.0 * (12.0 * fracnu + 45.0)) * curvature_amplitude
    alpha = base_seed.gauge_shift_alpha
    delta_ur_n = delta_ur_s - 4.0 * a_prime_over_a * alpha
    theta_ur_n = theta_ur_s + k_sq * alpha
    multipoles = [0.0] * ur_count
    if ur_count > 0:
        multipoles[0] = shear_ur
    if ur_count > 1:
        multipoles[1] = l3_ur
    return delta_ur_n, theta_ur_n, tuple(multipoles)


def _ur_hierarchy_derivatives(
    *,
    delta_ur: float,
    theta_ur: float,
    ur_multipoles: tuple[float, ...],
    sample: ClosedS3ScalarAcousticSample,
) -> tuple[float, float, tuple[float, ...]]:
    """Return the collisionless UR hierarchy derivatives on the closed shell."""

    if len(ur_multipoles) < 2:
        raise ValueError("the scoped UR hierarchy requires at least `(shear_ur, l3_ur)`")
    delta_ur_prime = -4.0 / 3.0 * (theta_ur + sample.metric_drive.metric_continuity)
    theta_ur_prime = (
        sample.laplacian_k_sq_mpc_inv2 * (delta_ur / 4.0 - sample.s2_squared * ur_multipoles[0])
        + sample.metric_drive.metric_euler
    )
    ur_prime: list[float] = []
    shear = ur_multipoles[0]
    l3 = ur_multipoles[1]
    ur_prime.append(
        0.5
        * (
            8.0 / 15.0 * (theta_ur + sample.metric_drive.metric_shear)
            - 3.0 / 5.0 * sample.laplacian_k_mpc_inv * sample.s_l(3) / sample.s_l(2) * l3
        )
    )
    ur_lmax = len(ur_multipoles) + 1
    for ell in range(3, ur_lmax + 1):
        current = ur_multipoles[ell - 2]
        if ell == ur_lmax:
            prev = 2.0 * sample.s_l(2) * shear if ell == 3 else ur_multipoles[ell - 3]
            ell_prime = sample.laplacian_k_mpc_inv * (
                sample.s_l(ell) * prev - (ell + 1.0) * sample.cotKgen * current
            )
        else:
            prev = 2.0 * sample.s_l(2) * shear if ell == 3 else ur_multipoles[ell - 3]
            nxt = ur_multipoles[ell - 1]
            ell_prime = (
                sample.laplacian_k_mpc_inv
                / (2.0 * ell + 1.0)
                * (ell * sample.s_l(ell) * prev - (ell + 1.0) * sample.s_l(ell + 1) * nxt)
            )
        ur_prime.append(ell_prime)
    return delta_ur_prime, theta_ur_prime, tuple(ur_prime)


def _interpolated_scalar_acoustic_sample(
    carrier,
    *,
    package: PerturbationBranchPackage,
    fraction: float,
    z_start: float,
    z_end: float,
    tau_start: float,
    tau_end: float,
    apoa_start: float,
    apoa_end: float,
    appoa_start: float,
    appoa_end: float,
    cb2_start: float,
    cb2_end: float,
    dcb2_start: float,
    dcb2_end: float,
    drag_start: float,
    drag_end: float,
    hierarchy_start: float,
    hierarchy_end: float,
    tau_c_start: float,
    tau_c_end: float,
    dtau_c_start: float,
    dtau_c_end: float,
    slip_start: float,
    slip_end: float,
    shear_start: float,
    shear_end: float,
    metric_drive,
) -> ClosedS3ScalarAcousticSample:
    """Return one linearly interpolated local scalar-acoustic sample on one interval."""

    z_obs = _linear_interpolate(z_start, z_end, fraction)
    conformal_time = _linear_interpolate(tau_start, tau_end, fraction)
    a_prime_over_a = _linear_interpolate(apoa_start, apoa_end, fraction)
    a_primeprime_over_a = _linear_interpolate(appoa_start, appoa_end, fraction)
    cb2 = _linear_interpolate(cb2_start, cb2_end, fraction)
    dcb2_dconformal = _linear_interpolate(dcb2_start, dcb2_end, fraction)

    curvature_radius = carrier.curvature_radius_mpc
    curvature_K = 1.0 / (curvature_radius * curvature_radius)
    n = carrier.mode.n
    k_sq = n * (n + 2.0) * curvature_K
    shifted_sq = (n - 1.0) * (n + 3.0) * curvature_K
    q_sq = k_sq + curvature_K
    k = math.sqrt(k_sq)
    root_K = math.sqrt(curvature_K)
    trig = math.tan(root_K * conformal_time)
    if abs(trig) < 1.0e-14:
        raise ValueError("conformal_time_mpc lands on a cotK singularity for the closed scalar shell")

    thomson_sample = ThomsonHistorySample(
        z_obs=z_obs,
        thomson_drag_rate=_linear_interpolate(drag_start, drag_end, fraction),
        thomson_hierarchy_rate=_linear_interpolate(hierarchy_start, hierarchy_end, fraction),
        tau_c=_linear_interpolate(tau_c_start, tau_c_end, fraction),
        dtau_c=_linear_interpolate(dtau_c_start, dtau_c_end, fraction),
        slip=_linear_interpolate(slip_start, slip_end, fraction),
        shear=_linear_interpolate(shear_start, shear_end, fraction),
    )
    typed_R = build_typed_r_operator_sample(
        z_obs,
        thomson_sample,
        omega_b_geom_h2=package.baryon_slots.omega_b_geom_h2,
        t_io_ref_k=package.t_io_ref_k,
    )

    return ClosedS3ScalarAcousticSample(
        carrier=carrier,
        z_obs=z_obs,
        conformal_time_mpc=conformal_time,
        a_prime_over_a_mpc_inv=a_prime_over_a,
        a_primeprime_over_a_mpc_inv2=a_primeprime_over_a,
        laplacian_k_sq_mpc_inv2=k_sq,
        laplacian_k_mpc_inv=k,
        shifted_scalar_sq_mpc_inv2=shifted_sq,
        q_sq_mpc_inv2=q_sq,
        nu=math.sqrt(q_sq / curvature_K),
        cotKgen=root_K / (k * trig),
        s2_squared=shifted_sq / k_sq,
        R_loading=typed_R.R_hierarchy,
        typed_R=typed_R,
        cb2=cb2,
        dcb2_dconformal_mpc_inv=dcb2_dconformal,
        thomson=thomson_sample,
        metric_drive=metric_drive,
        claim_status="conditional / scoped interpolated shell sample",
        provenance_node_ids=(
            "paper23.closed_scalar_operator",
            "paper29.sound_speed_selector",
            "calculator.thomson_history_realization",
            "local.typed_r_operator",
            "local.scoped_tt_driver",
        ),
        scope_boundary=(
            "Linearly interpolated local sample on one explicit scoped TT-driver interval.",
            "Uses theorem-grade local formulas on an interpolated background/history carrier rather than an exact sub-grid Stage-2 solve.",
        ),
    )


def _seed_tca_hidden_hierarchy(
    state: ScalarHierarchyState,
    sample: ClosedS3ScalarAcousticSample,
) -> ScalarHierarchyState:
    """Populate hidden photon/polarization moments from the first-order TCA seed.

    The scoped driver evolves the reduced TCA system on `(delta_gamma, theta_gamma,
    delta_b, theta_b)` only. But when the full hierarchy turns on, the photon
    shear, `F_3`, and the low polarization moments must not still be identically
    zero. CLASS seeds them from the tight-coupling formulas at the transition.

    This helper mirrors that executable logic on the closed-shell carrier:

    - `shear_g = 16/45 tau_c (theta_g + metric_shear)`
    - `F_3 = 6/7 (k / hierarchy_rate) s_3 shear_g`
    - `G_0 = 5/2 shear_g`
    - `G_1 = (k / hierarchy_rate) (5 - 2 s_2) shear_g / 6`
    - `G_2 = 1/2 shear_g`
    - `G_3 = (k / hierarchy_rate) 3 s_3 shear_g / 14`

    Higher moments remain zero on this first-order TCA carrier.
    """

    prediction = predict_first_order_tight_coupling_contract(state, sample)
    shear = prediction.predicted_shear
    hierarchy_rate = sample.thomson.thomson_hierarchy_rate
    k_over_rate = sample.laplacian_k_mpc_inv / hierarchy_rate

    photon = [0.0] * len(state.photon_multipoles)
    if photon:
        photon[0] = shear
    if len(photon) > 1:
        photon[1] = 6.0 / 7.0 * k_over_rate * sample.s_l(3) * shear

    polarization = [0.0] * len(state.polarization_multipoles)
    if polarization:
        polarization[0] = 2.5 * shear
    if len(polarization) > 1:
        polarization[1] = k_over_rate * (5.0 - 2.0 * sample.s_l(2)) * shear / 6.0
    if len(polarization) > 2:
        polarization[2] = 0.5 * shear
    if len(polarization) > 3:
        polarization[3] = k_over_rate * 3.0 * sample.s_l(3) * shear / 14.0

    return ScalarHierarchyState(
        phi=state.phi,
        psi=state.psi,
        delta_gamma=state.delta_gamma,
        theta_gamma=state.theta_gamma,
        delta_b=state.delta_b,
        theta_b=state.theta_b,
        photon_multipoles=tuple(photon),
        polarization_multipoles=tuple(polarization),
    )


def _realize_first_order_tca_sample(
    state: ScalarHierarchyState,
    sample: ClosedS3ScalarAcousticSample,
) -> ClosedS3ScalarAcousticSample:
    """Return the executable TCA sample with realized nontrivial slip/shear.

    The global Thomson-history carrier remains a background/history object, so it
    cannot honestly pre-store shell-dependent first-order TCA slip/shear for all
    shells. The executable TT driver therefore realizes those quantities at the
    shell/substep level, where the current hierarchy state is explicit.
    """

    prediction = predict_first_order_tight_coupling_contract(state, sample)
    realized_thomson = ThomsonHistorySample(
        z_obs=sample.thomson.z_obs,
        thomson_drag_rate=sample.thomson.thomson_drag_rate,
        thomson_hierarchy_rate=sample.thomson.thomson_hierarchy_rate,
        tau_c=sample.thomson.tau_c,
        dtau_c=sample.thomson.dtau_c,
        slip=prediction.predicted_slip,
        shear=prediction.predicted_shear,
    )
    return replace(
        sample,
        thomson=realized_thomson,
        claim_status="conditional / scoped interpolated shell sample with realized first-order TCA slip/shear",
        scope_boundary=(
            "Linearly interpolated local sample on one explicit scoped TT-driver interval.",
            "Realizes first-order shell-dependent TCA slip/shear on the live executable branch rather than consuming the zero placeholder from the background-only Thomson history.",
        ),
    )


def _tight_coupling_active(
    carrier,
    *,
    tau_c: float,
    a_prime_over_a_mpc_inv: float,
    config: ScopedTTDriverConfig,
) -> bool:
    """Return whether the shell stays inside the CLASS-like TCA trigger window.

    The executable scoped driver previously used a shell-blind `kappa' > 1`
    switch. On the closed scalar ladder that is too crude: the physical
    high-`n` shells must leave TCA earlier because the trigger depends on both
    the expansion timescale `tau_h = 1 / (a'/a)` and the shell timescale
    `tau_k = 1 / k_n`.
    """

    tau_c = _positive(tau_c, name="tau_c")
    a_prime_over_a = _positive(a_prime_over_a_mpc_inv, name="a_prime_over_a_mpc_inv")
    tau_h = 1.0 / a_prime_over_a
    tau_k = carrier.curvature_radius_mpc / math.sqrt(carrier.mode.primary_spatial_eigenvalue)
    return (
        tau_c / tau_h < config.tight_coupling_trigger_tau_c_over_tau_h
        and tau_c / tau_k < config.tight_coupling_trigger_tau_c_over_tau_k
    )


def _scoped_shell_rhs(
    vector: tuple[float, ...],
    *,
    carrier,
    photon_count: int,
    polarization_count: int,
    ur_count: int,
    fraction: float,
    z_start: float,
    z_end: float,
    tau_start: float,
    tau_end: float,
    apoa_start: float,
    apoa_end: float,
    appoa_start: float,
    appoa_end: float,
    cb2_start: float,
    cb2_end: float,
    dcb2_start: float,
    dcb2_end: float,
    drag_start: float,
    drag_end: float,
    hierarchy_start: float,
    hierarchy_end: float,
    tau_c_start: float,
    tau_c_end: float,
    dtau_c_start: float,
    dtau_c_end: float,
    slip_start: float,
    slip_end: float,
    shear_start: float,
    shear_end: float,
    include_pressureless_matter: bool,
    use_first_order_tca: bool,
    project_metric_constraint: bool,
    config: ScopedTTDriverConfig,
) -> tuple[tuple[float, ...], object, ScalarHierarchyState]:
    """Return the scoped shell RHS on one interpolated substep carrier."""

    provisional_state, delta_ur, theta_ur, ur_multipoles, delta_m, theta_m = _vector_to_state(
        vector,
        photon_count=photon_count,
        polarization_count=polarization_count,
        ur_count=ur_count,
        psi=0.0,
    )
    z = _linear_interpolate(z_start, z_end, fraction)
    tau = _linear_interpolate(tau_start, tau_end, fraction)
    a_prime_over_a = _linear_interpolate(apoa_start, apoa_end, fraction)
    stress = _stress_summary(
        provisional_state,
        package=config.perturbation_package,
        delta_ur=delta_ur,
        theta_ur=theta_ur,
        ur_multipoles=ur_multipoles,
        delta_m=delta_m,
        theta_m=theta_m,
        z=z,
        include_pressureless_matter=include_pressureless_matter,
        baryon_momentum_slot=config.metric_baryon_momentum_slot,
    )
    use_constraint_metric = project_metric_constraint or config.constraint_metric_source_only
    phi_input = provisional_state.phi
    if use_constraint_metric:
        phi_constraint = newtonian_constraint_phi(
            carrier,
            stress,
            scale_factor=1.0 / (1.0 + z),
            a_prime_over_a_mpc_inv=a_prime_over_a,
        )
        anchor_weight = _constraint_anchor_weight(carrier, conformal_time_mpc=tau)
        if not project_metric_constraint and not config.constraint_metric_source_only:
            anchor_weight = 1.0
        phi_input = (1.0 - anchor_weight) * provisional_state.phi + anchor_weight * phi_constraint
    metric_state = build_newtonian_scalar_metric_state(
        carrier,
        stress,
        scale_factor=1.0 / (1.0 + z),
        a_prime_over_a_mpc_inv=a_prime_over_a,
        phi=phi_input,
    )
    state = ScalarHierarchyState(
        phi=phi_input if project_metric_constraint else provisional_state.phi,
        psi=metric_state.psi,
        delta_gamma=provisional_state.delta_gamma,
        theta_gamma=provisional_state.theta_gamma,
        delta_b=provisional_state.delta_b,
        theta_b=provisional_state.theta_b,
        photon_multipoles=provisional_state.photon_multipoles,
        polarization_multipoles=provisional_state.polarization_multipoles,
    )
    sample = _interpolated_scalar_acoustic_sample(
        carrier,
        package=config.perturbation_package,
        fraction=fraction,
        z_start=z_start,
        z_end=z_end,
        tau_start=tau_start,
        tau_end=tau_end,
        apoa_start=apoa_start,
        apoa_end=apoa_end,
        appoa_start=appoa_start,
        appoa_end=appoa_end,
        cb2_start=cb2_start,
        cb2_end=cb2_end,
        dcb2_start=dcb2_start,
        dcb2_end=dcb2_end,
        drag_start=drag_start,
        drag_end=drag_end,
        hierarchy_start=hierarchy_start,
        hierarchy_end=hierarchy_end,
        tau_c_start=tau_c_start,
        tau_c_end=tau_c_end,
        dtau_c_start=dtau_c_start,
        dtau_c_end=dtau_c_end,
        slip_start=slip_start,
        slip_end=slip_end,
        shear_start=shear_start,
        shear_end=shear_end,
        metric_drive=metric_state.acoustic_drive,
    )
    regime = (
        ScalarHierarchyRegime.TIGHT_COUPLING_CONTRACT
        if _tight_coupling_active(
            carrier,
            tau_c=sample.thomson.tau_c,
            a_prime_over_a_mpc_inv=sample.a_prime_over_a_mpc_inv,
            config=config,
        )
        else ScalarHierarchyRegime.FULL_HIERARCHY
    )

    if regime is ScalarHierarchyRegime.TIGHT_COUPLING_CONTRACT:
        seeded_state = _seed_tca_hidden_hierarchy(state, sample)
        if seeded_state.photon_multipoles != state.photon_multipoles or seeded_state.polarization_multipoles != state.polarization_multipoles:
            stress = _stress_summary(
                seeded_state,
                package=config.perturbation_package,
                delta_ur=delta_ur,
                theta_ur=theta_ur,
                ur_multipoles=ur_multipoles,
                delta_m=delta_m,
                theta_m=theta_m,
                z=z,
                include_pressureless_matter=include_pressureless_matter,
                baryon_momentum_slot=config.metric_baryon_momentum_slot,
            )
            phi_input = seeded_state.phi
            if use_constraint_metric:
                phi_constraint = newtonian_constraint_phi(
                    carrier,
                    stress,
                    scale_factor=1.0 / (1.0 + z),
                    a_prime_over_a_mpc_inv=a_prime_over_a,
                )
                anchor_weight = _constraint_anchor_weight(carrier, conformal_time_mpc=tau)
                if not project_metric_constraint and not config.constraint_metric_source_only:
                    anchor_weight = 1.0
                phi_input = (1.0 - anchor_weight) * seeded_state.phi + anchor_weight * phi_constraint
            metric_state = build_newtonian_scalar_metric_state(
                carrier,
                stress,
                scale_factor=1.0 / (1.0 + z),
                a_prime_over_a_mpc_inv=a_prime_over_a,
                phi=phi_input,
            )
            state = ScalarHierarchyState(
                phi=phi_input if project_metric_constraint else seeded_state.phi,
                psi=metric_state.psi,
                delta_gamma=seeded_state.delta_gamma,
                theta_gamma=seeded_state.theta_gamma,
                delta_b=seeded_state.delta_b,
                theta_b=seeded_state.theta_b,
                photon_multipoles=seeded_state.photon_multipoles,
                polarization_multipoles=seeded_state.polarization_multipoles,
            )
            sample = _interpolated_scalar_acoustic_sample(
                carrier,
                package=config.perturbation_package,
                fraction=fraction,
                z_start=z_start,
                z_end=z_end,
                tau_start=tau_start,
                tau_end=tau_end,
                apoa_start=apoa_start,
                apoa_end=apoa_end,
                appoa_start=appoa_start,
                appoa_end=appoa_end,
                cb2_start=cb2_start,
                cb2_end=cb2_end,
                dcb2_start=dcb2_start,
                dcb2_end=dcb2_end,
                drag_start=drag_start,
                drag_end=drag_end,
                hierarchy_start=hierarchy_start,
                hierarchy_end=hierarchy_end,
                tau_c_start=tau_c_start,
                tau_c_end=tau_c_end,
                dtau_c_start=dtau_c_start,
                dtau_c_end=dtau_c_end,
                slip_start=slip_start,
                slip_end=slip_end,
                shear_start=shear_start,
                shear_end=shear_end,
                metric_drive=metric_state.acoustic_drive,
            )

    if regime is ScalarHierarchyRegime.TIGHT_COUPLING_CONTRACT and use_first_order_tca:
        sample = _realize_first_order_tca_sample(state, sample)

    deriv = evaluate_closed_s3_scalar_acoustic_derivatives(state, sample, regime=regime)
    delta_ur_prime, theta_ur_prime, ur_prime = _ur_hierarchy_derivatives(
        delta_ur=delta_ur,
        theta_ur=theta_ur,
        ur_multipoles=ur_multipoles,
        sample=sample,
    )
    derivatives = (
        0.0 if project_metric_constraint else metric_state.phi_prime,
        deriv.delta_gamma_prime,
        deriv.theta_gamma_prime,
        deriv.delta_b_prime,
        deriv.theta_b_prime,
        *(
            deriv.photon_multipole_prime
            if regime is ScalarHierarchyRegime.FULL_HIERARCHY
            else (0.0,) * photon_count
        ),
        *(
            deriv.polarization_multipole_prime
            if regime is ScalarHierarchyRegime.FULL_HIERARCHY
            else (0.0,) * polarization_count
        ),
        delta_ur_prime,
        theta_ur_prime,
        *ur_prime,
        -(theta_m + sample.metric_drive.metric_continuity),
        -sample.a_prime_over_a_mpc_inv * theta_m + sample.metric_drive.metric_euler,
    )
    return derivatives, metric_state, state


def _adaptive_shell_substeps(
    carrier,
    *,
    dt: float,
    drag_rate: float,
    hierarchy_rate: float,
    config: ScopedTTDriverConfig,
) -> int:
    """Choose the explicit substep count for one shell interval."""

    k_dt = abs(dt) * math.sqrt(carrier.mode.primary_spatial_eigenvalue) / carrier.curvature_radius_mpc
    drag_dt = abs(dt) * max(drag_rate, hierarchy_rate)
    required = max(
        1.0,
        k_dt / config.shell_substep_kdt_max,
        drag_dt / config.shell_substep_drag_dt_max,
    )
    return min(config.shell_substep_max, max(1, math.ceil(required)))


def _rescaled_thomson_history_contract(
    contract: ThomsonHistoryContract,
    *,
    drag_rate_factor: float,
    hierarchy_rate_factor: float,
) -> ThomsonHistoryContract:
    """Return a diagnostic Thomson tuple deformation on one explicit grid.

    This helper keeps the exact typed split realization intact and only applies
    the scoped runtime factors after the realization exists:

    - local drag/contact branch:
      `thomson_drag_rate -> d_drag * thomson_drag_rate`
    - hierarchy/damping branch:
      `thomson_hierarchy_rate -> h_hier * thomson_hierarchy_rate`

    `tau_c` and `dtau_c` remain derived from the drag leg, matching the local
    CLASS fork semantics.
    """

    drag_rate_factor = _positive(drag_rate_factor, name="drag_rate_factor")
    hierarchy_rate_factor = _positive(hierarchy_rate_factor, name="hierarchy_rate_factor")
    if drag_rate_factor == 1.0 and hierarchy_rate_factor == 1.0:
        return contract
    drag_rate = tuple(value * drag_rate_factor for value in contract.thomson_drag_rate)
    hierarchy_rate = tuple(value * hierarchy_rate_factor for value in contract.thomson_hierarchy_rate)
    drag_rate_derivative = tuple(value * drag_rate_factor for value in contract.drag_rate_derivative)
    tau_c = tuple(1.0 / value for value in drag_rate)
    dtau_c = tuple(-derivative * tau * tau for derivative, tau in zip(drag_rate_derivative, tau_c))
    return ThomsonHistoryContract(
        z_obs=contract.z_obs,
        thomson_drag_rate=drag_rate,
        thomson_hierarchy_rate=hierarchy_rate,
        drag_rate_derivative=drag_rate_derivative,
        tau_c=tau_c,
        dtau_c=dtau_c,
        slip=contract.slip,
        shear=contract.shear,
        derivative_coordinate=contract.derivative_coordinate,
        claim_status="conditional / scoped optical-history deformation of the Thomson tuple",
        provenance_node_ids=(
            *contract.provenance_node_ids,
            "local.scoped_tt_driver",
        ),
        scope_boundary=(
            "Applies explicit runtime drag/hierarchy factors after the typed split Thomson realization is built.",
            "This is a diagnostic TT-driver deformation, not a theorem that the exact IO-native Thomson tuple equals these factors on every branch.",
        ),
    )


def _rescaled_visibility_packet(
    visibility: VisibilityPacket,
    *,
    drag_rate: tuple[float, ...],
    opacity_factor: float,
) -> VisibilityPacket:
    """Return the observer-side optical-history packet under the CLASS-style `c` deformation.

    The local CLASS fork implements the visibility factor as

    - `exp(-kappa) -> exp(-c kappa) = exp(-kappa)^c`
    - `g -> c kappa' exp(-c kappa)`

    on the observer-side optical packet, while the primitive local drag/contact
    leg remains separate.
    """

    opacity_factor = _positive(opacity_factor, name="visibility_opacity_factor")
    if opacity_factor == 1.0:
        return visibility
    tau_obs = tuple(opacity_factor * value for value in visibility.tau_obs)
    d_tau_obs_dz = tuple(opacity_factor * value for value in visibility.d_tau_obs_dz)
    g_obs = tuple(
        opacity_factor * rate * math.exp(-tau_value)
        for rate, tau_value in zip(drag_rate, tau_obs)
    )
    return VisibilityPacket(
        z_obs=visibility.z_obs,
        d_tau_obs_dz=d_tau_obs_dz,
        tau_obs=tau_obs,
        g_obs=g_obs,
        lower_boundary_z=visibility.lower_boundary_z,
        absolute_to_observer=visibility.absolute_to_observer,
    )


def build_scoped_stage2_history_with_thermal_prehistory(
    config: ScopedTTDriverConfig,
    *,
    builder: InheritedFullStage2DynamicHistoryBuilder | None = None,
) -> ScopedThermalHistory:
    """Extend the inherited-FULL history with a thermal prehistory segment."""

    shell_safe_z_init = _required_seed_redshift(
        config.n_max,
        package=config.perturbation_package,
        config=config,
    )
    z_init = max(config.z_init, shell_safe_z_init)
    active_builder = (
        InheritedFullStage2DynamicHistoryBuilder(
            branch=config.perturbation_package.branch,
            omega_b_geom_h2=config.perturbation_package.baryon_slots.omega_b_geom_h2,
        )
        if builder is None
        else builder
    )
    exact_z = _nonlinear_grid(config.z_exact_max, config.exact_history_samples)
    exact_history = build_inherited_full_stage2_history(exact_z, builder=active_builder)

    prehistory_z = tuple(
        config.z_exact_max
        + (z_init - config.z_exact_max) * (i / (config.prehistory_samples - 1)) ** 2
        for i in range(config.prehistory_samples)
    )
    x_e_prehistory = (exact_history.x_e[-1],) + (1.0,) * (config.prehistory_samples - 1)
    T_m_prehistory = (exact_history.T_m_loc_K[-1],) + tuple(
        local_radiation_temperature_K(
            z,
            t_io_ref_k=config.perturbation_package.t_io_ref_k,
        )
        for z in prehistory_z[1:]
    )

    merged_history = Stage2History.from_sequences(
        tuple(list(exact_history.z_obs[:-1]) + list(prehistory_z)),
        tuple(list(exact_history.x_e[:-1]) + list(x_e_prehistory)),
        tuple(list(exact_history.T_m_loc_K[:-1]) + list(T_m_prehistory)),
    )
    return ScopedThermalHistory(
        history=merged_history,
        claim_status="conditional / scoped exploratory prehistory extension",
        provenance_node_ids=(
            "premise.2",
            "paper31.stage2_markov_state",
            "local.inherited_full_stage2_dynamic_history_builder",
            "local.scoped_tt_driver",
        ),
        scope_boundary=(
            "Uses the inherited-FULL exact history on `z <= z_exact_max` and a thermal `x_e = 1`, `T_m = T_R` prehistory extension on `z > z_exact_max`.",
            "The prehistory upper boundary is automatically raised when needed so the highest shell starts inside the CLASS-style asymptotic seed window.",
            "This extension is numerically useful for superhorizon seeding but is not itself a universal IO-native Stage-2 theorem.",
        ),
    )


def build_scoped_conformal_clock(
    history: Stage2History,
    *,
    model: CurvedBackgroundModel | None = None,
    config: ScopedTTDriverConfig | None = None,
) -> ConformalClockGrid:
    """Return the observer conformal clock carried by the scoped TT driver."""

    active_config = ScopedTTDriverConfig() if config is None else config
    active_model = (
        CurvedBackgroundModel(branch=active_config.perturbation_package.branch)
        if model is None
        else model
    )
    tau_observer = (C_KM_S / active_model.branch.H0) * active_model.chi_dimless(
        active_config.observer_tau_target_z,
        n=active_config.observer_tau_samples,
    )
    dc_samples = tuple(
        (C_KM_S / active_model.branch.H0)
        * active_model.chi_dimless(z, n=active_config.line_of_sight_distance_samples)
        for z in history.z_obs
    )
    tau_samples = tuple(tau_observer - dc for dc in dc_samples)
    hubble = tuple(active_model.hubble_km_s_mpc(z) for z in history.z_obs)
    dc_dz = tuple(C_KM_S / value for value in hubble)
    apoa = tuple(
        value / (C_KM_S * (1.0 + z))
        for z, value in zip(history.z_obs, hubble)
    )
    appoa = tuple(
        _finite_difference(tau_samples, apoa, index) + apoa[index] ** 2
        for index in range(len(tau_samples))
    )
    return ConformalClockGrid(
        tau_observer_mpc=tau_observer,
        z_obs=history.z_obs,
        tau_samples_mpc=tau_samples,
        dc_dz_mpc=dc_dz,
        a_prime_over_a_mpc_inv=apoa,
        a_primeprime_over_a_mpc_inv2=appoa,
        claim_status="derived / scoped observer conformal clock carrier",
        provenance_node_ids=("paper30.background_surface", "local.scoped_tt_driver"),
        scope_boundary=(
            "Observer conformal clock and local background derivatives on one explicit driver grid.",
            "Derived from the active closed-FRW background and used only as a scoped numeric carrier for the TT driver.",
        ),
    )


def build_visibility_derived_conformal_thomson_history(
    history: Stage2History,
    clock: ConformalClockGrid,
    *,
    package: PerturbationBranchPackage = ACTIVE_PERTURBATION_PACKAGE,
    drag_rate_factor: float = 1.0,
    hierarchy_rate_factor: float = 1.0,
) -> ThomsonHistoryContract:
    """Derive the conformal Thomson tuple through the typed split history path.

    The live scoped TT driver does not flatten everything into one opacity
    scalar. It goes through:

    - primitive local opacity `kappa'_loc`
    - observer-side visibility packet `(d tau_obs / dz, tau_obs, g_obs)`
    - conformal Thomson tuple built from that packet and the observer clock
    """

    realization = build_typed_split_thomson_history_realization(
        history,
        clock.dc_dz_mpc,
        clock.tau_samples_mpc,
        derivative_coordinate="conformal_time",
        omega_b_h2=package.baryon_slots.omega_b_geom_h2,
        helium_mass_fraction=package.branch.YHe,
    )
    return _rescaled_thomson_history_contract(
        realization.contract,
        drag_rate_factor=drag_rate_factor,
        hierarchy_rate_factor=hierarchy_rate_factor,
    )


def _build_conformal_source_visibility(
    history: Stage2History,
    clock: ConformalClockGrid,
    *,
    package: PerturbationBranchPackage = ACTIVE_PERTURBATION_PACKAGE,
    opacity_factor: float = 1.0,
) -> VisibilityPacket:
    """Return the LOS visibility packet with source kernel measured in conformal time.

    The reduced visibility carrier in `recombination.py` stores

    `g(z) = exp(-tau_obs(z)) d tau_obs / dz`.

    The scalar LOS projector integrates over conformal time, so the executable
    TT driver must instead feed

    `g(tau) = exp(-tau_obs) d tau_obs / d tau`

    on the same observer-redshift grid. Reusing the redshift-space kernel
    inside a `d tau` integral is a clock mismatch.
    """

    visibility = build_visibility_packet(
        history,
        omega_b_h2=package.baryon_slots.omega_b_geom_h2,
        helium_mass_fraction=package.branch.YHe,
    )
    drag_rate = tuple(
        abs(d_tau_obs_dz / dc_dz)
        for d_tau_obs_dz, dc_dz in zip(visibility.d_tau_obs_dz, clock.dc_dz_mpc)
    )
    visibility_packet = VisibilityPacket(
        z_obs=visibility.z_obs,
        d_tau_obs_dz=visibility.d_tau_obs_dz,
        tau_obs=visibility.tau_obs,
        g_obs=tuple(math.exp(-tau_value) * rate for tau_value, rate in zip(visibility.tau_obs, drag_rate)),
        lower_boundary_z=visibility.lower_boundary_z,
        absolute_to_observer=visibility.absolute_to_observer,
    )
    return _rescaled_visibility_packet(
        visibility_packet,
        drag_rate=drag_rate,
        opacity_factor=opacity_factor,
    )


def _stress_summary(
    state: ScalarHierarchyState,
    *,
    package: PerturbationBranchPackage = ACTIVE_PERTURBATION_PACKAGE,
    delta_ur: float,
    theta_ur: float,
    ur_multipoles: tuple[float, ...],
    delta_m: float,
    theta_m: float,
    z: float,
    include_pressureless_matter: bool,
    baryon_momentum_slot: str = "eff",
) -> object:
    """Return the typed Einstein-side scalar source on the scoped driver branch.

    This scoped driver does not license one baryon slot for every perturbation
    stress leg. The explicit carrier used here is:

    - density-side baryon inventory `delta_rho_b` on `omega_b,geom`
    - baryon momentum carrier `(rho+p)theta_b` on the explicitly selected slot
      `omega_b,{geom|eff|clustering}`
    - pressureless clustering-side matter carrier on `omega_b,clustering`
    - optional residual pressureless matter completing the active `Omega_m`
      after the explicit geometric and clustering-side carriers are removed

    This is still a scoped numeric composite, not a universal theorem that the
    exact full CMB metric source is an additive sum of independent fluids.
    """

    branch = package.branch
    baryon_slots = package.baryon_slots
    h = branch.h
    omega_gamma0 = omega_gamma_h2(branch.T_cmb) / (h * h)
    omega_ur0 = max(branch.Omega_r - omega_gamma0, 0.0)
    omega_b_geom0 = baryon_slots.omega_b_geom_h2 / (h * h)
    omega_b_eff0 = baryon_slots.omega_b_eff_h2 / (h * h)
    omega_b_clustering0 = baryon_slots.omega_b_clustering_h2 / (h * h)
    omega_pressureless = 0.0
    if include_pressureless_matter:
        # The explicit stress carrier already includes the geometric baryon
        # density leg and the clustering-side pressureless leg. The residual
        # completion must therefore subtract both from the branch-total
        # `Omega_m`; otherwise the Einstein source sees `Omega_m + omega_b,geom`.
        omega_pressureless = max(branch.Omega_m - omega_b_geom0 - omega_b_clustering0, 0.0)
    hubble_factor = (branch.H0 / C_KM_S) ** 2
    rho_g = hubble_factor * omega_gamma0 * (1.0 + z) ** 4
    rho_ur = hubble_factor * omega_ur0 * (1.0 + z) ** 4
    rho_b_geom = hubble_factor * omega_b_geom0 * (1.0 + z) ** 3
    rho_b_eff = hubble_factor * omega_b_eff0 * (1.0 + z) ** 3
    rho_b_clustering = hubble_factor * omega_b_clustering0 * (1.0 + z) ** 3
    rho_m = hubble_factor * omega_pressureless * (1.0 + z) ** 3
    if baryon_momentum_slot == "geom":
        rho_b_momentum = rho_b_geom
    elif baryon_momentum_slot == "eff":
        rho_b_momentum = rho_b_eff
    elif baryon_momentum_slot == "clustering":
        rho_b_momentum = rho_b_clustering
    else:
        raise ValueError("baryon_momentum_slot must be one of: geom, eff, clustering")
    shear = state.photon_multipoles[0] if state.photon_multipoles else 0.0
    shear_ur = ur_multipoles[0] if ur_multipoles else 0.0
    return build_scalar_stress_energy_summary(
        delta_rho=(
            rho_g * state.delta_gamma
            + rho_ur * delta_ur
            + rho_b_geom * state.delta_b
            + rho_b_clustering * delta_m
            + rho_m * delta_m
        ),
        delta_p=(rho_g / 3.0) * state.delta_gamma + (rho_ur / 3.0) * delta_ur,
        rho_plus_p_theta=(
            (4.0 / 3.0) * rho_g * state.theta_gamma
            + (4.0 / 3.0) * rho_ur * theta_ur
            + rho_b_momentum * state.theta_b
            + rho_b_clustering * theta_m
            + rho_m * theta_m
        ),
        rho_plus_p_shear=(8.0 / 3.0) * rho_g * shear + (8.0 / 3.0) * rho_ur * shear_ur,
    )




def _evolve_shell(
    n: int,
    staged_history: ScopedThermalHistory,
    clock: ConformalClockGrid,
    thomson: ThomsonHistoryContract,
    *,
    config: ScopedTTDriverConfig,
) -> tuple[tuple[ScalarHierarchyState, ...], tuple[object, ...]]:
    """Evolve one closed shell on the scoped TT driver."""

    background_model = CurvedBackgroundModel(branch=config.perturbation_package.branch)
    carrier = build_scalar_hierarchy_carrier(n, curvature_radius_mpc=background_model.curvature_radius_mpc)
    temperature_lmax = min(config.temperature_hierarchy_lmax, n)
    polarization_lmax = min(config.polarization_hierarchy_lmax, n)
    ur_lmax = min(config.temperature_hierarchy_lmax, n)
    photon_count = temperature_lmax - 1
    polarization_count = polarization_lmax + 1
    ur_count = ur_lmax - 1
    z_evo = tuple(reversed(staged_history.history.z_obs))
    tau_evo = tuple(reversed(clock.tau_samples_mpc))
    apoa_evo = tuple(reversed(clock.a_prime_over_a_mpc_inv))
    appoa_evo = tuple(reversed(clock.a_primeprime_over_a_mpc_inv2))
    asc_index_for_evo = [len(staged_history.history.z_obs) - 1 - i for i in range(len(staged_history.history.z_obs))]
    cb2_asc = _cb2_history(
        staged_history.history,
        helium_mass_fraction=config.perturbation_package.branch.YHe,
    )
    dcb2_dz_asc = tuple(
        _finite_difference(staged_history.history.z_obs, cb2_asc, index)
        for index in range(len(staged_history.history.z_obs))
    )
    cb2_evo = tuple(reversed(cb2_asc))
    dcb2_dconformal_evo = tuple(
        -(1.0 + z_item) * apoa_item * dcb2_dz_asc[asc_index]
        for z_item, apoa_item, asc_index in zip(z_evo, apoa_evo, asc_index_for_evo)
    )
    drag_evo = tuple(reversed(thomson.thomson_drag_rate))
    hierarchy_evo = tuple(reversed(thomson.thomson_hierarchy_rate))
    tau_c_evo = tuple(reversed(thomson.tau_c))
    dtau_c_evo = tuple(reversed(thomson.dtau_c))
    slip_evo = tuple(reversed(thomson.slip))
    shear_evo = tuple(reversed(thomson.shear))

    if not _seed_start_is_early_enough(
        n,
        z=z_evo[0],
        package=config.perturbation_package,
        config=config,
    ):
        raise ValueError(
            f"shell n={n} starts at z={z_evo[0]:.6g}, outside the asymptotic seed window; "
            "raise z_init or rebuild the scoped thermal prehistory."
        )

    seed = build_closed_s3_newtonian_adiabatic_seed(
        carrier,
        conformal_time_mpc=tau_evo[0],
        a_prime_over_a_mpc_inv=apoa_evo[0],
        scale_factor=1.0 / (1.0 + z_evo[0]),
        package=config.perturbation_package,
        curvature_amplitude=1.0,
    )
    seed_state = seed.hierarchy_state
    state = ScalarHierarchyState(
        phi=seed_state.phi,
        psi=seed_state.psi,
        delta_gamma=seed_state.delta_gamma,
        theta_gamma=seed_state.theta_gamma,
        delta_b=seed_state.delta_b,
        theta_b=seed_state.theta_b,
        photon_multipoles=(0.0,) * photon_count,
        polarization_multipoles=(0.0,) * polarization_count,
    )
    delta_ur, theta_ur, ur_multipoles = _build_ur_adiabatic_seed(
        carrier,
        conformal_time_mpc=tau_evo[0],
        a_prime_over_a_mpc_inv=apoa_evo[0],
        scale_factor=1.0 / (1.0 + z_evo[0]),
        package=config.perturbation_package,
        ur_count=ur_count,
        curvature_amplitude=1.0,
    )
    delta_m = 0.75 * seed_state.delta_gamma
    theta_m = seed_state.theta_gamma
    if config.project_metric_constraint or config.constraint_consistent_seed or config.constraint_metric_source_only:
        seed_stress = _stress_summary(
            state,
            package=config.perturbation_package,
            delta_ur=delta_ur,
            theta_ur=theta_ur,
            ur_multipoles=ur_multipoles,
            delta_m=delta_m,
            theta_m=theta_m,
            z=z_evo[0],
            include_pressureless_matter=config.include_pressureless_matter,
            baryon_momentum_slot=config.metric_baryon_momentum_slot,
        )
        seed_phi_constraint = newtonian_constraint_phi(
            carrier,
            seed_stress,
            scale_factor=1.0 / (1.0 + z_evo[0]),
            a_prime_over_a_mpc_inv=apoa_evo[0],
        )
        if config.constraint_consistent_seed:
            seed_anchor_weight = 1.0
        elif config.project_metric_constraint or config.constraint_metric_source_only:
            seed_anchor_weight = _constraint_anchor_weight(carrier, conformal_time_mpc=tau_evo[0])
        else:
            seed_anchor_weight = 1.0
        seed_metric = build_newtonian_scalar_metric_state(
            carrier,
            seed_stress,
            scale_factor=1.0 / (1.0 + z_evo[0]),
            a_prime_over_a_mpc_inv=apoa_evo[0],
            phi=(1.0 - seed_anchor_weight) * state.phi + seed_anchor_weight * seed_phi_constraint,
        )
        state = ScalarHierarchyState(
            phi=seed_metric.phi if (config.project_metric_constraint or config.constraint_consistent_seed) else state.phi,
            psi=seed_metric.psi,
            delta_gamma=state.delta_gamma,
            theta_gamma=state.theta_gamma,
            delta_b=state.delta_b,
            theta_b=state.theta_b,
            photon_multipoles=state.photon_multipoles,
            polarization_multipoles=state.polarization_multipoles,
        )

    if len(z_evo) > 1:
        seed_vector = _state_to_vector(state, delta_ur, theta_ur, ur_multipoles, delta_m, theta_m)
        _, seed_metric_state, seeded_state = _scoped_shell_rhs(
            seed_vector,
            carrier=carrier,
            photon_count=photon_count,
            polarization_count=polarization_count,
            ur_count=ur_count,
            fraction=0.0,
            z_start=z_evo[0],
            z_end=z_evo[1],
            tau_start=tau_evo[0],
            tau_end=tau_evo[1],
            apoa_start=apoa_evo[0],
            apoa_end=apoa_evo[1],
            appoa_start=appoa_evo[0],
            appoa_end=appoa_evo[1],
            cb2_start=cb2_evo[0],
            cb2_end=cb2_evo[1],
            dcb2_start=dcb2_dconformal_evo[0],
            dcb2_end=dcb2_dconformal_evo[1],
            drag_start=drag_evo[0],
            drag_end=drag_evo[1],
            hierarchy_start=hierarchy_evo[0],
            hierarchy_end=hierarchy_evo[1],
            tau_c_start=tau_c_evo[0],
            tau_c_end=tau_c_evo[1],
            dtau_c_start=dtau_c_evo[0],
            dtau_c_end=dtau_c_evo[1],
            slip_start=slip_evo[0],
            slip_end=slip_evo[1],
            shear_start=shear_evo[0],
            shear_end=shear_evo[1],
            include_pressureless_matter=config.include_pressureless_matter,
            use_first_order_tca=config.use_first_order_tca,
            project_metric_constraint=config.project_metric_constraint,
            config=config,
        )
        state = seeded_state
        _, delta_ur, theta_ur, ur_multipoles, delta_m, theta_m = _vector_to_state(
            seed_vector,
            photon_count=photon_count,
            polarization_count=polarization_count,
            ur_count=ur_count,
            psi=seeded_state.psi,
        )
        if config.project_metric_constraint:
            state = ScalarHierarchyState(
                phi=seed_metric_state.phi,
                psi=seed_metric_state.psi,
                delta_gamma=state.delta_gamma,
                theta_gamma=state.theta_gamma,
                delta_b=state.delta_b,
                theta_b=state.theta_b,
                photon_multipoles=state.photon_multipoles,
                polarization_multipoles=state.polarization_multipoles,
            )

    states_evo = [state]
    metrics_evo: list[object] = []
    for evo_index in range(len(z_evo) - 1):
        z = z_evo[evo_index]
        dt = tau_evo[evo_index + 1] - tau_evo[evo_index]
        substeps = _adaptive_shell_substeps(
            carrier,
            dt=dt,
            drag_rate=max(drag_evo[evo_index], drag_evo[evo_index + 1]),
            hierarchy_rate=max(hierarchy_evo[evo_index], hierarchy_evo[evo_index + 1]),
            config=config,
        )
        vector = _state_to_vector(state, delta_ur, theta_ur, ur_multipoles, delta_m, theta_m)
        final_metric_state = None

        for substep_index in range(substeps):
            fraction_start = substep_index / substeps
            fraction_mid = (substep_index + 0.5) / substeps
            fraction_end = (substep_index + 1.0) / substeps
            sub_dt = dt / substeps
            rhs_kwargs = dict(
                carrier=carrier,
                photon_count=photon_count,
                polarization_count=polarization_count,
                ur_count=ur_count,
                z_start=z_evo[evo_index],
                z_end=z_evo[evo_index + 1],
                tau_start=tau_evo[evo_index],
                tau_end=tau_evo[evo_index + 1],
                apoa_start=apoa_evo[evo_index],
                apoa_end=apoa_evo[evo_index + 1],
                appoa_start=appoa_evo[evo_index],
                appoa_end=appoa_evo[evo_index + 1],
                cb2_start=cb2_evo[evo_index],
                cb2_end=cb2_evo[evo_index + 1],
                dcb2_start=dcb2_dconformal_evo[evo_index],
                dcb2_end=dcb2_dconformal_evo[evo_index + 1],
                drag_start=drag_evo[evo_index],
                drag_end=drag_evo[evo_index + 1],
                hierarchy_start=hierarchy_evo[evo_index],
                hierarchy_end=hierarchy_evo[evo_index + 1],
                tau_c_start=tau_c_evo[evo_index],
                tau_c_end=tau_c_evo[evo_index + 1],
                dtau_c_start=dtau_c_evo[evo_index],
                dtau_c_end=dtau_c_evo[evo_index + 1],
                slip_start=slip_evo[evo_index],
                slip_end=slip_evo[evo_index + 1],
                shear_start=shear_evo[evo_index],
                shear_end=shear_evo[evo_index + 1],
                include_pressureless_matter=config.include_pressureless_matter,
                use_first_order_tca=config.use_first_order_tca,
                project_metric_constraint=config.project_metric_constraint,
                config=config,
            )
            k1, _, _ = _scoped_shell_rhs(vector, fraction=fraction_start, **rhs_kwargs)
            k2, _, _ = _scoped_shell_rhs(
                tuple(value + 0.5 * sub_dt * delta for value, delta in zip(vector, k1)),
                fraction=fraction_mid,
                **rhs_kwargs,
            )
            k3, _, _ = _scoped_shell_rhs(
                tuple(value + 0.5 * sub_dt * delta for value, delta in zip(vector, k2)),
                fraction=fraction_mid,
                **rhs_kwargs,
            )
            k4, final_metric_state, _ = _scoped_shell_rhs(
                tuple(value + sub_dt * delta for value, delta in zip(vector, k3)),
                fraction=fraction_end,
                **rhs_kwargs,
            )
            vector = tuple(
                value + sub_dt / 6.0 * (delta1 + 2.0 * delta2 + 2.0 * delta3 + delta4)
                for value, delta1, delta2, delta3, delta4 in zip(vector, k1, k2, k3, k4)
            )
            if config.project_metric_constraint:
                vector = (final_metric_state.phi,) + vector[1:]
            synced_deriv, synced_metric_state, synced_state = _scoped_shell_rhs(
                vector,
                fraction=fraction_end,
                **rhs_kwargs,
            )
            del synced_deriv
            if (
                _tight_coupling_active(
                    carrier,
                    tau_c=_linear_interpolate(tau_c_evo[evo_index], tau_c_evo[evo_index + 1], fraction_end),
                    a_prime_over_a_mpc_inv=_linear_interpolate(apoa_evo[evo_index], apoa_evo[evo_index + 1], fraction_end),
                    config=config,
                )
                and (
                    any(value != 0.0 for value in synced_state.photon_multipoles)
                    or any(value != 0.0 for value in synced_state.polarization_multipoles)
                )
            ):
                (
                    synced_rebuilt_state,
                    synced_delta_ur,
                    synced_theta_ur,
                    synced_ur_multipoles,
                    synced_delta_m,
                    synced_theta_m,
                ) = _vector_to_state(
                    vector,
                    photon_count=photon_count,
                    polarization_count=polarization_count,
                    ur_count=ur_count,
                    psi=synced_state.psi,
                )
                del synced_rebuilt_state
                vector = _state_to_vector(
                    synced_state,
                    delta_ur=synced_delta_ur,
                    theta_ur=synced_theta_ur,
                    ur_multipoles=synced_ur_multipoles,
                    delta_m=synced_delta_m,
                    theta_m=synced_theta_m,
                )
                final_metric_state = synced_metric_state

        if final_metric_state is None:
            raise RuntimeError("scoped shell evolution failed to produce a terminal metric state")
        state, delta_ur, theta_ur, ur_multipoles, delta_m, theta_m = _vector_to_state(
            vector,
            photon_count=photon_count,
            polarization_count=polarization_count,
            ur_count=ur_count,
            psi=final_metric_state.psi,
        )
        stress_post = _stress_summary(
            state,
            package=config.perturbation_package,
            delta_ur=delta_ur,
            theta_ur=theta_ur,
            ur_multipoles=ur_multipoles,
            delta_m=delta_m,
            theta_m=theta_m,
            z=z_evo[evo_index + 1],
            include_pressureless_matter=config.include_pressureless_matter,
            baryon_momentum_slot=config.metric_baryon_momentum_slot,
        )
        use_constraint_metric = config.project_metric_constraint or config.constraint_metric_source_only
        phi_post = state.phi
        if use_constraint_metric:
            phi_constraint_post = newtonian_constraint_phi(
                carrier,
                stress_post,
                scale_factor=1.0 / (1.0 + z_evo[evo_index + 1]),
                a_prime_over_a_mpc_inv=apoa_evo[evo_index + 1],
            )
            anchor_weight_post = (
                _constraint_anchor_weight(
                    carrier,
                    conformal_time_mpc=tau_evo[evo_index + 1],
                )
                if (config.project_metric_constraint or config.constraint_metric_source_only)
                else 1.0
            )
            phi_post = (1.0 - anchor_weight_post) * state.phi + anchor_weight_post * phi_constraint_post
            if config.project_metric_constraint:
                state = ScalarHierarchyState(
                    phi=phi_post,
                    psi=state.psi,
                    delta_gamma=state.delta_gamma,
                    theta_gamma=state.theta_gamma,
                    delta_b=state.delta_b,
                    theta_b=state.theta_b,
                    photon_multipoles=state.photon_multipoles,
                    polarization_multipoles=state.polarization_multipoles,
                )
                vector = (phi_post,) + vector[1:]
        final_metric_state = build_newtonian_scalar_metric_state(
            carrier,
            stress_post,
            scale_factor=1.0 / (1.0 + z_evo[evo_index + 1]),
            a_prime_over_a_mpc_inv=apoa_evo[evo_index + 1],
            phi=phi_post,
        )
        state = ScalarHierarchyState(
            phi=final_metric_state.phi,
            psi=final_metric_state.psi,
            delta_gamma=state.delta_gamma,
            theta_gamma=state.theta_gamma,
            delta_b=state.delta_b,
            theta_b=state.theta_b,
            photon_multipoles=state.photon_multipoles,
            polarization_multipoles=state.polarization_multipoles,
        )
        metrics_evo.append(final_metric_state)
        values = vector
        if any((not math.isfinite(value) or abs(value) > 1.0e8) for value in values):
            raise RuntimeError(f"shell {n} became numerically unstable at z={z}")
        states_evo.append(state)

    z_terminal = z_evo[-1]
    terminal_stress = _stress_summary(
        state,
        package=config.perturbation_package,
        delta_ur=delta_ur,
        theta_ur=theta_ur,
        ur_multipoles=ur_multipoles,
        delta_m=delta_m,
        theta_m=theta_m,
        z=z_terminal,
        include_pressureless_matter=config.include_pressureless_matter,
        baryon_momentum_slot=config.metric_baryon_momentum_slot,
    )
    terminal_phi = state.phi
    if config.project_metric_constraint or config.constraint_metric_source_only:
        terminal_phi_constraint = newtonian_constraint_phi(
            carrier,
            terminal_stress,
            scale_factor=1.0 / (1.0 + z_terminal),
            a_prime_over_a_mpc_inv=apoa_evo[-1],
        )
        terminal_anchor_weight = (
            _constraint_anchor_weight(
                carrier,
                conformal_time_mpc=tau_evo[-1],
            )
            if (config.project_metric_constraint or config.constraint_metric_source_only)
            else 1.0
        )
        terminal_phi = (1.0 - terminal_anchor_weight) * state.phi + terminal_anchor_weight * terminal_phi_constraint
    metrics_evo.append(
        build_newtonian_scalar_metric_state(
            carrier,
            terminal_stress,
            scale_factor=1.0 / (1.0 + z_terminal),
            a_prime_over_a_mpc_inv=apoa_evo[-1],
            phi=terminal_phi,
        )
    )
    return tuple(reversed(states_evo)), tuple(reversed(metrics_evo))


def validate_scoped_tt_spectrum(
    spectrum: ClosedAngularPowerSpectrum,
    *,
    peak_window_min: int = 120,
    peak_window_max: int = 320,
) -> tuple[PeakFunctionalResult, TTValidationSummary]:
    """Return a compact validation summary for one scoped TT spectrum."""

    peak = evaluate_discrete_peak_functional(
        spectrum,
        ell_min=peak_window_min,
        ell_max=peak_window_max,
    )
    c_map = dict(zip(spectrum.ell_values, spectrum.c_ell))
    c2 = c_map.get(2, 0.0)
    c30 = c_map.get(30, c2)
    c220 = c_map.get(220, 0.0)
    c320 = c_map.get(320, c_map.get(max(spectrum.ell_values), 0.0))
    peak_value = max(peak.peak_value, 1.0e-300)
    summary = TTValidationSummary(
        ell_peak=peak.ell_peak,
        peak_value=peak.peak_value,
        peak_near_220=180 <= peak.ell_peak <= 260,
        c_220_over_peak=c220 / peak_value,
        plateau_2_to_30_ratio=(c2 / c30) if c30 != 0.0 else math.inf,
        high_ell_support_ratio=(c320 / peak_value) if peak_value != 0.0 else 0.0,
        all_finite=all(math.isfinite(value) for value in spectrum.c_ell),
        notes=(
            "This validation summary is numeric only; it does not upgrade the driver to theorem-grade TT closure.",
            "A physically acceptable active-branch run should place the first broad TT peak near ell ~ 220 rather than near the lower edge of the audit window.",
        ),
    )
    return peak, summary


def _scoped_tt_weighted_packet_for_shell(
    n: int,
    staged_history: ScopedThermalHistory,
    clock: ConformalClockGrid,
    thomson: ThomsonHistoryContract,
    source_visibility: VisibilityPacket,
    config: ScopedTTDriverConfig,
):
    """Return the weighted TT transfer packet for one explicit scalar shell.

    Public-release note:

    This helper uses the one common seed/history carrier built for the run.
    That common start surface is intentional at the current scope because the
    cross-shell phase carrier is not yet closed by a theorem-grade shell-local
    alternative.
    """

    background_model = CurvedBackgroundModel(branch=config.perturbation_package.branch)
    states_asc, metrics_asc = _evolve_shell(
        n,
        staged_history,
        clock,
        thomson,
        config=config,
    )
    carrier = build_scalar_hierarchy_carrier(n, curvature_radius_mpc=background_model.curvature_radius_mpc)
    source_history = build_newtonian_scalar_source_history_integrated_by_parts(
        carrier,
        conformal_time_mpc=clock.tau_samples_mpc[1:],
        visibility=source_visibility,
        states=states_asc[1:],
        metric_states=metrics_asc[1:],
    )
    packet = project_closed_s3_scalar_temperature(
        source_history,
        tau_observer_mpc=clock.tau_observer_mpc,
        ell_values=range(2, min(n, config.ell_max) + 1),
    )
    shell_weight = _tt_shell_weight(
        n,
        radius=background_model.curvature_radius_mpc,
        config=config,
    )
    return weight_closed_s3_transfer_packet(packet, shell_weight=shell_weight)


def run_scoped_tt_driver(
    config: ScopedTTDriverConfig | None = None,
    *,
    builder: InheritedFullStage2DynamicHistoryBuilder | None = None,
) -> ScopedTTDriverResult:
    """Run the current executable scoped TT driver on the active branch.

    The exact Stage-2 segment on `z <= z_exact_max` is built once and shared,
    and the thermal prehistory above that sets one common early-time carrier
    for the whole run. That common carrier is part of the live scoped phase
    convention: it should not be silently localized shell by shell unless a
    new theorem closes the cross-shell phase map on such a local carrier.
    """

    active_config = ScopedTTDriverConfig() if config is None else config
    staged_history = build_scoped_stage2_history_with_thermal_prehistory(active_config, builder=builder)
    clock = build_scoped_conformal_clock(staged_history.history, config=active_config)
    thomson = build_visibility_derived_conformal_thomson_history(
        staged_history.history,
        clock,
        package=active_config.perturbation_package,
        drag_rate_factor=active_config.drag_rate_factor,
        hierarchy_rate_factor=active_config.hierarchy_rate_factor,
    )
    visibility = _build_conformal_source_visibility(
        staged_history.history,
        clock,
        package=active_config.perturbation_package,
        opacity_factor=active_config.visibility_opacity_factor,
    )
    source_visibility = VisibilityPacket(
        z_obs=visibility.z_obs[1:],
        d_tau_obs_dz=visibility.d_tau_obs_dz[1:],
        tau_obs=visibility.tau_obs[1:],
        g_obs=visibility.g_obs[1:],
        lower_boundary_z=0.0,
        absolute_to_observer=True,
    )

    shell_values = _source_supported_shell_values(active_config)
    if active_config.shell_parallel_workers == 1:
        weighted_packets = [
            _scoped_tt_weighted_packet_for_shell(
                n,
                staged_history=staged_history,
                clock=clock,
                thomson=thomson,
                source_visibility=source_visibility,
                config=active_config,
            )
            for n in shell_values
        ]
    else:
        with ProcessPoolExecutor(max_workers=active_config.shell_parallel_workers) as executor:
            weighted_packets = list(
                executor.map(
                    _scoped_tt_weighted_packet_for_shell,
                    shell_values,
                    repeat(staged_history),
                    repeat(clock),
                    repeat(thomson),
                    repeat(source_visibility),
                    repeat(active_config),
                )
            )

    spectrum = assemble_closed_s3_angular_power_spectrum(weighted_packets, observable_pair="TT")
    peak, validation = validate_scoped_tt_spectrum(
        spectrum,
        peak_window_min=active_config.peak_window_min,
        peak_window_max=active_config.peak_window_max,
    )
    return ScopedTTDriverResult(
        config=active_config,
        staged_history=staged_history,
        conformal_clock=clock,
        thomson_history=thomson,
        spectrum=spectrum,
        peak=peak,
        validation=validation,
        claim_status="conditional / scoped executable TT driver",
        provenance_node_ids=(
            "premise.2",
            "paper31.stage2_markov_state",
            "local.inherited_full_stage2_dynamic_history_builder",
            "local.closed_scalar_acoustic_generator",
            "local.closed_scalar_transfer_projector",
            "paper28.closed_s3_shell_power",
            "local.scoped_tt_driver",
        ),
        scope_boundary=(
            "Executable active-branch TT driver only.",
            "Uses the inherited-FULL Stage-2 builder plus a thermal prehistory extension and does not claim theorem-grade validated TT closure.",
            "Validation metrics must be read explicitly; a returned spectrum is not itself proof that the physical first peak is correct.",
        ),
    )


__all__ = [
    "canonical_first_peak_tt_config",
    "ConformalClockGrid",
    "ScopedTTDriverConfig",
    "ScopedTTDriverResult",
    "ScopedThermalHistory",
    "TTValidationSummary",
    "build_scoped_conformal_clock",
    "build_scoped_stage2_history_with_thermal_prehistory",
    "build_visibility_derived_conformal_thomson_history",
    "run_canonical_first_peak_tt_driver",
    "run_scoped_tt_driver",
    "validate_scoped_tt_spectrum",
]
