"""Typed local closed-`S^3` scalar acoustic generator.

This module closes the part of `U_pert^{S^3}` that is already fixed by the
current stack once the missing external inputs are supplied explicitly:

- `derived / scoped`: closed scalar transport geometry on the discrete shell
  `n >= 2`, with
  `k_n^2 = n(n+2) / R_curv^2`,
  `q_n^2 = k_n^2 + K = (n+1)^2 / R_curv^2`,
  `s_l = sqrt(1 - K (l^2-1) / k_n^2)`,
  and
  `cot_K^gen(tau) = sqrt(K) / [k_n tan(sqrt(K) tau)]`
- `derived / scoped`: primitive local momentum loading
  `R(z) = 3 rho_b(z) / [4 rho_gamma(z)]` on `omega_b,geom`
- `derived / scoped`: baryon sound speed from the exact sampled Stage-2
  history `(x_e(z), T_m(z))`
- `derived / scoped`: the full photon-baryon hierarchy RHS when the explicit
  hierarchy state is supplied
- `derived / scoped`: the reduced tight-coupling contract RHS when the exact
  Thomson-history tuple supplies `(drag_rate, hierarchy_rate, tau_c, dtau_c,
  slip, shear)`

What remains open here is not the local transport/collision algebra. It is the
builder for the missing external inputs:

- the exact Stage-2 dynamic-network history solver
- the exact Einstein-side metric-drive builder
- the exact hierarchy-to-transfer projector

So this module derives the local generator, not the full end-to-end `C_l`
pipeline.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .constants import ACTIVE_BRANCH, C_SI, HYDROGEN_ATOM_MASS_KG, K_B_SI
from .perturbation_types import PerturbationBlockInputs, TypedSourceAcousticOperator
from .recombination import OpenTheoremBoundaryError, Stage2History
from .scalar_hierarchy import ScalarHierarchyCarrier, ScalarHierarchyState
from .thomson_history_contract import ThomsonHistoryContract, ThomsonHistorySample
from .typed_r_operator import TypedROperatorSample, build_typed_r_operator_sample


def _validate_finite(value: float, *, name: str) -> float:
    """Require one finite float."""

    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _validate_positive(value: float, *, name: str) -> float:
    """Require one strictly positive finite float."""

    value = _validate_finite(value, name=name)
    if value <= 0.0:
        raise ValueError(f"{name} must be strictly positive")
    return value


def _finite_difference(x: tuple[float, ...], y: tuple[float, ...], index: int) -> float:
    """Return the first derivative `dy/dx` on an explicit sample grid."""

    index = int(index)
    if len(x) != len(y):
        raise ValueError("x and y must have the same length")
    if len(x) < 2:
        raise ValueError("at least two samples are required for a derivative")
    if index < 0 or index >= len(x):
        raise IndexError("sample index out of range")
    if len(x) == 2:
        return (y[1] - y[0]) / (x[1] - x[0])
    if index == 0:
        return (y[1] - y[0]) / (x[1] - x[0])
    if index == len(x) - 1:
        return (y[-1] - y[-2]) / (x[-1] - x[-2])
    return (y[index + 1] - y[index - 1]) / (x[index + 1] - x[index - 1])


def _baryon_mu_factor(
    x_e: float,
    *,
    helium_mass_fraction: float = ACTIVE_BRANCH.YHe,
) -> float:
    """Return the CLASS-style baryon mean-mass factor `m_H / mu`."""

    x_e = _validate_finite(x_e, name="x_e")
    return 1.0 + (0.25 - 1.0) * helium_mass_fraction + x_e * (1.0 - helium_mass_fraction)


def _baryon_sound_speed_sq(
    z: float,
    x_e: float,
    T_m_loc_K: float,
    dT_m_dz: float,
    *,
    helium_mass_fraction: float = ACTIVE_BRANCH.YHe,
) -> float:
    """Return the adiabatic baryon sound speed squared from the local history."""

    z = _validate_finite(z, name="z")
    x_e = _validate_finite(x_e, name="x_e")
    T_m_loc_K = _validate_positive(T_m_loc_K, name="T_m_loc_K")
    dT_m_dz = _validate_finite(dT_m_dz, name="dT_m_dz")
    prefactor = K_B_SI / (C_SI * C_SI * HYDROGEN_ATOM_MASS_KG)
    cb2 = prefactor * _baryon_mu_factor(x_e, helium_mass_fraction=helium_mass_fraction) * T_m_loc_K * (
        1.0 + (1.0 + z) * dT_m_dz / (3.0 * T_m_loc_K)
    )
    if not math.isfinite(cb2):
        raise ValueError("derived cb2 must be finite")
    return cb2


class ScalarHierarchyRegime(str, Enum):
    """The theorem-grade scalar hierarchy regimes currently admitted."""

    FULL_HIERARCHY = "full_hierarchy"
    TIGHT_COUPLING_CONTRACT = "tight_coupling_contract"


@dataclass(frozen=True)
class ScalarMetricDrive:
    """Explicit metric source quartet for the local scalar acoustic generator."""

    metric_continuity: float
    metric_euler: float
    metric_shear: float
    metric_shear_prime: float
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("metric_continuity", "metric_euler", "metric_shear", "metric_shear_prime"):
            _validate_finite(getattr(self, name), name=name)


@dataclass(frozen=True)
class ClosedS3ScalarAcousticSample:
    """One explicit local sample for the derived closed-`S^3` scalar generator."""

    carrier: ScalarHierarchyCarrier
    z_obs: float
    conformal_time_mpc: float
    a_prime_over_a_mpc_inv: float
    a_primeprime_over_a_mpc_inv2: float
    laplacian_k_sq_mpc_inv2: float
    laplacian_k_mpc_inv: float
    shifted_scalar_sq_mpc_inv2: float
    q_sq_mpc_inv2: float
    nu: float
    cotKgen: float
    s2_squared: float
    R_loading: float
    typed_R: TypedROperatorSample
    cb2: float
    dcb2_dconformal_mpc_inv: float
    thomson: ThomsonHistorySample
    metric_drive: ScalarMetricDrive
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]

    @property
    def curvature_radius_mpc(self) -> float:
        """Return the curvature radius carried by the scalar shell."""

        return self.carrier.curvature_radius_mpc

    @property
    def curvature_K_mpc_inv2(self) -> float:
        """Return the positive closed-space curvature `K = 1 / R_curv^2`."""

        return 1.0 / (self.curvature_radius_mpc * self.curvature_radius_mpc)

    @property
    def drag_slip_factor(self) -> float:
        """Return `F = tau_c / (1 + R)` on the local photon-baryon subsystem."""

        return self.typed_R.tight_coupling_slip_factor

    def supports_ell(self, ell: int) -> bool:
        """Return whether the scalar shell supports the requested multipole."""

        ell = int(ell)
        return 0 <= ell <= self.carrier.mode.n

    def s_l(self, ell: int) -> float:
        """Return the closed scalar recurrence factor `s_l`."""

        ell = int(ell)
        if ell < 0:
            raise ValueError("ell must be non-negative")
        factor = 1.0 - self.curvature_K_mpc_inv2 * (ell * ell - 1.0) / self.laplacian_k_sq_mpc_inv2
        return math.sqrt(max(factor, 0.0))


@dataclass(frozen=True)
class FirstOrderTightCouplingPrediction:
    """First-order contract prediction derived from the Thomson tuple."""

    predicted_slip: float
    supplied_slip: float
    slip_residual: float
    predicted_shear: float
    supplied_shear: float
    shear_residual: float
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


@dataclass(frozen=True)
class ScalarAcousticDerivatives:
    """RHS of the local closed-`S^3` scalar acoustic subsystem."""

    regime: str
    delta_gamma_prime: float
    theta_gamma_prime: float
    delta_b_prime: float
    theta_b_prime: float
    photon_multipole_prime: tuple[float, ...]
    polarization_multipole_prime: tuple[float, ...]
    used_contract_slip: float | None
    used_contract_shear: float | None
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


def build_scalar_metric_drive(
    *,
    metric_continuity: float,
    metric_euler: float,
    metric_shear: float,
    metric_shear_prime: float = 0.0,
) -> ScalarMetricDrive:
    """Build the explicit metric drive required by the local scalar generator."""

    return ScalarMetricDrive(
        metric_continuity=_validate_finite(metric_continuity, name="metric_continuity"),
        metric_euler=_validate_finite(metric_euler, name="metric_euler"),
        metric_shear=_validate_finite(metric_shear, name="metric_shear"),
        metric_shear_prime=_validate_finite(metric_shear_prime, name="metric_shear_prime"),
        claim_status="derived / scoped explicit metric-drive carrier",
        provenance_node_ids=("paper32.closed_s3_solver_spec",),
        scope_boundary=(
            "Explicit acoustic metric-drive carrier only.",
            "The theorem-grade builder for this quartet from the full Einstein-side perturbation state is still open.",
        ),
    )


def build_newtonian_metric_drive(
    *,
    phi_prime: float,
    psi: float,
    laplacian_k_sq_mpc_inv2: float,
) -> ScalarMetricDrive:
    """Build the acoustic metric quartet from Newtonian-gauge scalar variables.

    The closed local scalar carrier uses the standard gauge mapping

    - `metric_continuity = -3 phi_prime`
    - `metric_euler = k_n^2 psi`
    - `metric_shear = 0`
    - `metric_shear_prime = 0`

    without any extra metric-only closure factor.
    """

    k_sq = _validate_positive(laplacian_k_sq_mpc_inv2, name="laplacian_k_sq_mpc_inv2")
    return build_scalar_metric_drive(
        metric_continuity=-3.0 * _validate_finite(phi_prime, name="phi_prime"),
        metric_euler=k_sq * _validate_finite(psi, name="psi"),
        metric_shear=0.0,
        metric_shear_prime=0.0,
    )


def build_synchronous_metric_drive(
    *,
    h_prime: float,
    alpha: float,
    alpha_prime: float,
    laplacian_k_sq_mpc_inv2: float,
) -> ScalarMetricDrive:
    """Build the acoustic metric quartet from synchronous-gauge scalar variables.

    The closed local scalar carrier uses the standard gauge mapping

    - `metric_continuity = h_prime / 2`
    - `metric_euler = 0`
    - `metric_shear = k_n^2 alpha`
    - `metric_shear_prime = k_n^2 alpha_prime`
    """

    k_sq = _validate_positive(laplacian_k_sq_mpc_inv2, name="laplacian_k_sq_mpc_inv2")
    return build_scalar_metric_drive(
        metric_continuity=0.5 * _validate_finite(h_prime, name="h_prime"),
        metric_euler=0.0,
        metric_shear=k_sq * _validate_finite(alpha, name="alpha"),
        metric_shear_prime=k_sq * _validate_finite(alpha_prime, name="alpha_prime"),
    )


def build_closed_s3_scalar_acoustic_sample(
    carrier: ScalarHierarchyCarrier,
    history: Stage2History,
    thomson_history: ThomsonHistoryContract,
    *,
    index: int,
    conformal_time_mpc: float,
    a_prime_over_a_mpc_inv: float,
    a_primeprime_over_a_mpc_inv2: float,
    metric_drive: ScalarMetricDrive,
) -> ClosedS3ScalarAcousticSample:
    """Build one explicit local sample for the derived scalar acoustic generator."""

    if carrier.mode.physical_role != "physical":
        raise ValueError("the scalar acoustic sample requires a physical scalar shell with n >= 2")
    index = int(index)
    if index < 0 or index >= len(history.z_obs) or index >= len(thomson_history.z_obs):
        raise IndexError("sample index is outside the supplied history grids")
    if "conformal" not in thomson_history.derivative_coordinate.lower():
        raise OpenTheoremBoundaryError(
            "The theorem-grade scalar acoustic generator requires the Thomson-history tuple "
            "to be expressed in conformal-time derivatives. Rebuild the contract with "
            "`derivative_coordinate='conformal_time'`."
        )

    z_obs = history.z_obs[index]
    if not math.isclose(z_obs, thomson_history.z_obs[index], rel_tol=0.0, abs_tol=1.0e-12):
        raise ValueError("Stage-2 history and Thomson-history sample grids must agree at the requested index")

    dT_m_dz = _finite_difference(history.z_obs, history.T_m_loc_K, index)
    cb2_history = tuple(
        _baryon_sound_speed_sq(
            z_item,
            x_e_item,
            T_m_item,
            _finite_difference(history.z_obs, history.T_m_loc_K, i),
        )
        for i, (z_item, x_e_item, T_m_item) in enumerate(zip(history.z_obs, history.x_e, history.T_m_loc_K))
    )
    cb2 = cb2_history[index]
    dcb2_dz = _finite_difference(history.z_obs, cb2_history, index)
    a_prime_over_a = _validate_finite(a_prime_over_a_mpc_inv, name="a_prime_over_a_mpc_inv")
    dcb2_dconformal = -(1.0 + z_obs) * a_prime_over_a * dcb2_dz

    curvature_radius = carrier.curvature_radius_mpc
    curvature_K = 1.0 / (curvature_radius * curvature_radius)
    n = carrier.mode.n
    k_sq = n * (n + 2.0) * curvature_K
    shifted_sq = (n - 1.0) * (n + 3.0) * curvature_K
    q_sq = k_sq + curvature_K
    k = math.sqrt(k_sq)
    tau = _validate_positive(conformal_time_mpc, name="conformal_time_mpc")
    root_K = math.sqrt(curvature_K)
    trig = math.tan(root_K * tau)
    if abs(trig) < 1.0e-14:
        raise ValueError("conformal_time_mpc lands on a cotK singularity for the closed scalar shell")

    thomson_sample = thomson_history.sample(index)
    typed_R = build_typed_r_operator_sample(z_obs, thomson_sample)

    return ClosedS3ScalarAcousticSample(
        carrier=carrier,
        z_obs=z_obs,
        conformal_time_mpc=tau,
        a_prime_over_a_mpc_inv=a_prime_over_a,
        a_primeprime_over_a_mpc_inv2=_validate_finite(
            a_primeprime_over_a_mpc_inv2, name="a_primeprime_over_a_mpc_inv2"
        ),
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
        claim_status="derived / scoped local scalar acoustic sample",
        provenance_node_ids=(
            "paper23.closed_scalar_operator",
            "paper29.sound_speed_selector",
            "calculator.thomson_history_realization",
            "local.typed_r_operator",
            "local.typed_r_site_uniqueness",
            "local.closed_scalar_acoustic_generator",
        ),
        scope_boundary=(
            "Local photon-baryon scalar subsystem only.",
            "Requires an explicit conformal-time sample, explicit metric drive, and a supplied exact Thomson-history tuple.",
            "Does not by itself build the full Einstein-side metric drive or the exact Stage-2 history solver.",
        ),
    )


def _temperature_lmax(state: ScalarHierarchyState) -> int:
    """Return the temperature hierarchy truncation `l_max` carried by the state."""

    return len(state.photon_multipoles) + 1


def _polarization_lmax(state: ScalarHierarchyState) -> int:
    """Return the polarization hierarchy truncation `l_max` carried by the state."""

    return len(state.polarization_multipoles) - 1


def _temperature_multipole(state: ScalarHierarchyState, ell: int) -> float:
    """Return the explicit temperature hierarchy sample at `ell >= 3`."""

    ell = int(ell)
    if ell < 3:
        raise ValueError("temperature multipole access is defined here only for ell >= 3")
    return state.photon_multipoles[ell - 2]


def _polarization_multipole(state: ScalarHierarchyState, ell: int) -> float:
    """Return the explicit polarization hierarchy sample `G_ell`."""

    ell = int(ell)
    if ell < 0:
        raise ValueError("polarization ell must be non-negative")
    return state.polarization_multipoles[ell]


def predict_first_order_tight_coupling_contract(
    state: ScalarHierarchyState,
    sample: ClosedS3ScalarAcousticSample,
) -> FirstOrderTightCouplingPrediction:
    """Predict the first-order TCA slip/shear from the explicit Thomson tuple."""

    F = sample.drag_slip_factor
    theta_gap = state.theta_b - state.theta_gamma
    slip = (
        (sample.thomson.dtau_c / sample.thomson.tau_c - 2.0 * sample.a_prime_over_a_mpc_inv / (1.0 + sample.R_loading))
        * theta_gap
        + F
        * (
            -sample.a_primeprime_over_a_mpc_inv2 * state.theta_b
            + sample.laplacian_k_sq_mpc_inv2
            * (
                -sample.a_prime_over_a_mpc_inv * state.delta_gamma / 2.0
                + sample.dcb2_dconformal_mpc_inv * state.delta_b
                + sample.cb2 * (-state.theta_b - sample.metric_drive.metric_continuity)
                + (state.theta_gamma + sample.metric_drive.metric_continuity) / 3.0
            )
            - sample.a_prime_over_a_mpc_inv * sample.metric_drive.metric_euler
        )
    )
    shear = 16.0 / 45.0 * sample.thomson.tau_c * (state.theta_gamma + sample.metric_drive.metric_shear)
    return FirstOrderTightCouplingPrediction(
        predicted_slip=slip,
        supplied_slip=sample.thomson.slip,
        slip_residual=sample.thomson.slip - slip,
        predicted_shear=shear,
        supplied_shear=sample.thomson.shear,
        shear_residual=sample.thomson.shear - shear,
        claim_status="derived / scoped first-order TCA tuple audit",
        provenance_node_ids=("calculator.thomson_history_realization", "local.closed_scalar_acoustic_generator"),
        scope_boundary=(
            "First-order local TCA audit only.",
            "Does not claim that every supplied contract already satisfies this reduction unless the caller checks the residuals.",
        ),
    )


def evaluate_closed_s3_scalar_acoustic_derivatives(
    state: ScalarHierarchyState,
    sample: ClosedS3ScalarAcousticSample,
    *,
    regime: ScalarHierarchyRegime = ScalarHierarchyRegime.FULL_HIERARCHY,
) -> ScalarAcousticDerivatives:
    """Evaluate the derived local closed-`S^3` scalar acoustic generator."""

    delta_gamma_prime = -4.0 / 3.0 * (state.theta_gamma + sample.metric_drive.metric_continuity)
    delta_b_prime = -(state.theta_b + sample.metric_drive.metric_continuity)

    if regime is ScalarHierarchyRegime.TIGHT_COUPLING_CONTRACT:
        shear = sample.thomson.shear
        inertia_factor = sample.typed_R.baryon_inertia_factor
        odd_even_factor = sample.typed_R.odd_even_dynamic_loading_factor
        inverse_loading = sample.typed_R.inverse_baryon_loading_factor
        theta_b_prime = (
            (-sample.a_prime_over_a_mpc_inv * state.theta_b)
            + sample.laplacian_k_sq_mpc_inv2 * sample.cb2 * state.delta_b
        ) / inertia_factor + sample.metric_drive.metric_euler + odd_even_factor * (
            sample.laplacian_k_sq_mpc_inv2 * (state.delta_gamma / 4.0 - sample.s2_squared * shear)
            + sample.thomson.slip
        )
        theta_gamma_prime = (
            -(theta_b_prime + sample.a_prime_over_a_mpc_inv * state.theta_b - sample.laplacian_k_sq_mpc_inv2 * sample.cb2 * state.delta_b)
            * inverse_loading
            + sample.laplacian_k_sq_mpc_inv2 * (state.delta_gamma / 4.0 - sample.s2_squared * shear)
            + inertia_factor * inverse_loading * sample.metric_drive.metric_euler
        )
        return ScalarAcousticDerivatives(
            regime=regime.value,
            delta_gamma_prime=delta_gamma_prime,
            theta_gamma_prime=theta_gamma_prime,
            delta_b_prime=delta_b_prime,
            theta_b_prime=theta_b_prime,
            photon_multipole_prime=(),
            polarization_multipole_prime=(),
            used_contract_slip=sample.thomson.slip,
            used_contract_shear=sample.thomson.shear,
            claim_status="derived / scoped",
            provenance_node_ids=(
                "paper23.closed_scalar_operator",
                "paper29.sound_speed_selector",
                "calculator.thomson_history_realization",
                "local.closed_scalar_acoustic_generator",
            ),
            scope_boundary=(
                "Reduced tight-coupling-contract RHS only.",
                "Consumes supplied `slip` and `shear` from the exact Thomson-history tuple instead of rebuilding them from a chosen approximation scheme.",
            ),
        )

    if len(state.photon_multipoles) < 2:
        raise OpenTheoremBoundaryError(
            "The full closed-S^3 hierarchy RHS needs at least `(shear_g, F_3)` in `photon_multipoles`."
        )
    if len(state.polarization_multipoles) < 4:
        raise OpenTheoremBoundaryError(
            "The full closed-S^3 hierarchy RHS needs at least `(G_0, G_1, G_2, G_3)` in `polarization_multipoles`."
        )

    temperature_lmax = _temperature_lmax(state)
    polarization_lmax = _polarization_lmax(state)
    if temperature_lmax > sample.carrier.mode.n or polarization_lmax > sample.carrier.mode.n:
        raise ValueError("hierarchy truncation exceeds the closed scalar support ell <= n")

    shear = state.photon_multipoles[0]
    P0 = (
        _polarization_multipole(state, 0)
        + _polarization_multipole(state, 2)
        + 2.0 * sample.s_l(2) * shear
    ) / 8.0

    theta_b_prime = (
        -sample.a_prime_over_a_mpc_inv * state.theta_b
        + sample.metric_drive.metric_euler
        + sample.laplacian_k_sq_mpc_inv2 * sample.cb2 * state.delta_b
        + sample.typed_R.baryon_momentum_exchange_rate * (state.theta_gamma - state.theta_b)
    )
    theta_gamma_prime = (
        sample.laplacian_k_sq_mpc_inv2 * (state.delta_gamma / 4.0 - sample.s2_squared * shear)
        + sample.metric_drive.metric_euler
        + sample.thomson.thomson_drag_rate * (state.theta_b - state.theta_gamma)
    )

    photon_prime: list[float] = []
    polarization_prime: list[float] = []

    l3 = _temperature_multipole(state, 3)
    s2 = sample.s_l(2)
    s3 = sample.s_l(3)
    shear_prime = 0.5 * (
        8.0 / 15.0 * (state.theta_gamma + sample.metric_drive.metric_shear)
        - 3.0 / 5.0 * sample.laplacian_k_mpc_inv * s3 / s2 * l3
        - sample.thomson.thomson_hierarchy_rate * (2.0 * shear - 4.0 / (5.0 * s2) * P0)
    )
    photon_prime.append(shear_prime)

    for ell in range(3, temperature_lmax + 1):
        current = _temperature_multipole(state, ell)
        if ell == temperature_lmax:
            prev = 2.0 * sample.s_l(2) * shear if ell == 3 else _temperature_multipole(state, ell - 1)
            ell_prime = (
                sample.laplacian_k_mpc_inv
                * (sample.s_l(ell) * prev - (ell + 1.0) * sample.cotKgen * current)
                - sample.thomson.thomson_hierarchy_rate * current
            )
        else:
            prev = 2.0 * sample.s_l(2) * shear if ell == 3 else _temperature_multipole(state, ell - 1)
            nxt = _temperature_multipole(state, ell + 1)
            ell_prime = (
                sample.laplacian_k_mpc_inv
                / (2.0 * ell + 1.0)
                * (ell * sample.s_l(ell) * prev - (ell + 1.0) * sample.s_l(ell + 1) * nxt)
                - sample.thomson.thomson_hierarchy_rate * current
            )
        photon_prime.append(ell_prime)

    pol0 = _polarization_multipole(state, 0)
    pol1 = _polarization_multipole(state, 1)
    pol2 = _polarization_multipole(state, 2)
    polarization_prime.append(
        -sample.laplacian_k_mpc_inv * pol1
        - sample.thomson.thomson_hierarchy_rate * (pol0 - 4.0 * P0)
    )
    polarization_prime.append(
        sample.laplacian_k_mpc_inv / 3.0 * (pol0 - 2.0 * sample.s_l(2) * pol2)
        - sample.thomson.thomson_hierarchy_rate * pol1
    )
    polarization_prime.append(
        sample.laplacian_k_mpc_inv / 5.0 * (2.0 * sample.s_l(2) * pol1 - 3.0 * sample.s_l(3) * _polarization_multipole(state, 3))
        - sample.thomson.thomson_hierarchy_rate * (pol2 - 4.0 / 5.0 * P0)
    )
    for ell in range(3, polarization_lmax + 1):
        current = _polarization_multipole(state, ell)
        if ell == polarization_lmax:
            ell_prime = (
                sample.laplacian_k_mpc_inv
                * (
                    sample.s_l(ell) * _polarization_multipole(state, ell - 1)
                    - (ell + 1.0) * sample.cotKgen * current
                )
                - sample.thomson.thomson_hierarchy_rate * current
            )
        else:
            ell_prime = (
                sample.laplacian_k_mpc_inv
                / (2.0 * ell + 1.0)
                * (
                    ell * sample.s_l(ell) * _polarization_multipole(state, ell - 1)
                    - (ell + 1.0) * sample.s_l(ell + 1) * _polarization_multipole(state, ell + 1)
                )
                - sample.thomson.thomson_hierarchy_rate * current
            )
        if ell > 2:
            polarization_prime.append(ell_prime)

    return ScalarAcousticDerivatives(
        regime=regime.value,
        delta_gamma_prime=delta_gamma_prime,
        theta_gamma_prime=theta_gamma_prime,
        delta_b_prime=delta_b_prime,
        theta_b_prime=theta_b_prime,
        photon_multipole_prime=tuple(photon_prime),
        polarization_multipole_prime=tuple(polarization_prime),
        used_contract_slip=None,
        used_contract_shear=None,
        claim_status="derived / scoped",
        provenance_node_ids=(
            "paper23.closed_scalar_operator",
            "paper29.sound_speed_selector",
            "calculator.thomson_history_realization",
            "local.closed_scalar_acoustic_generator",
        ),
        scope_boundary=(
            "Local full-hierarchy photon-baryon RHS only.",
            "Requires an explicit hierarchy truncation, explicit metric drive, and a supplied exact Thomson-history tuple.",
            "Does not build the Einstein-side metric source or the exact hierarchy-to-transfer projector.",
        ),
    )


class ClosedS3ScalarAcousticOperator:
    """Concrete local scalar generator admitted by the current theorem stack."""

    def apply(self, inputs: PerturbationBlockInputs, **kwargs: Any) -> ScalarAcousticDerivatives:
        """Apply the derived local generator on an explicit scalar acoustic sample."""

        sample = kwargs.get("sample")
        state = kwargs.get("state")
        carrier = kwargs.get("carrier")
        regime = kwargs.get("regime", ScalarHierarchyRegime.FULL_HIERARCHY)
        if sample is None:
            raise OpenTheoremBoundaryError(
                "The local closed-S^3 scalar acoustic generator is derived only on an explicit sample "
                "`(carrier, Stage-2 history, Thomson tuple, conformal time, a'/a, a''/a, metric drive)`. "
                "The calculator does not yet derive that sample builder automatically from the full Einstein/Stage-2 state."
            )
        if not isinstance(sample, ClosedS3ScalarAcousticSample):
            raise TypeError("sample must be a ClosedS3ScalarAcousticSample")
        if not isinstance(state, ScalarHierarchyState):
            raise TypeError("state must be a ScalarHierarchyState")
        if carrier is not None and sample.carrier != carrier:
            raise ValueError("explicit carrier and sample carrier must agree")
        if inputs.mode.n != sample.carrier.mode.n:
            raise ValueError("perturbation inputs and scalar acoustic sample must refer to the same shell")
        if isinstance(regime, str):
            regime = ScalarHierarchyRegime(regime)
        return evaluate_closed_s3_scalar_acoustic_derivatives(state, sample, regime=regime)


__all__ = [
    "ClosedS3ScalarAcousticOperator",
    "ClosedS3ScalarAcousticSample",
    "FirstOrderTightCouplingPrediction",
    "ScalarAcousticDerivatives",
    "ScalarHierarchyRegime",
    "ScalarMetricDrive",
    "build_closed_s3_scalar_acoustic_sample",
    "build_newtonian_metric_drive",
    "build_scalar_metric_drive",
    "build_synchronous_metric_drive",
    "evaluate_closed_s3_scalar_acoustic_derivatives",
    "predict_first_order_tight_coupling_contract",
]
