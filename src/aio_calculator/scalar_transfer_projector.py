"""Closed-`S^3` scalar source histories and hierarchy-to-transfer projection.

This module closes the hierarchy-to-transfer connector at the scope that is
already fixed once explicit hierarchy histories, metric histories, and
visibility data are supplied:

- `derived / scoped`: the transparent scalar LOS source decomposition on closed
  `S^3` in Newtonian or synchronous gauge
- `derived / scoped`: the exact closed hyperspherical radial chain
  `(Phi_l^nu, dPhi_l^nu / dchi, d2Phi_l^nu / dchi^2)` from the closed
  recurrence on `beta = nu = n+1`
- `verified / numerical`: explicit quadrature of the exact scalar source and
  radial kernels into supplied transfer packets `Delta_l^T(q)` and `Delta_l^E(q)`

What remains outside this module:

- deriving the hierarchy history automatically from the full source/acoustic
  evolution problem
- deriving the exact observer conformal time from a higher-level background
  pipeline
- any hidden flat-space substitution or CLASS-style source patch
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Sequence

from .los_transfer import ClosedS3TransferPacket, TransferObservable
from .recombination import OpenTheoremBoundaryError, VisibilityPacket
from .scalar_hierarchy import ScalarHierarchyCarrier, ScalarHierarchyState
from .scalar_metric_state import NewtonianScalarMetricState, SynchronousScalarMetricState


def _float_tuple(values: Sequence[float], *, name: str) -> tuple[float, ...]:
    """Convert a finite sequence to a validated tuple of floats."""

    coerced = tuple(float(value) for value in values)
    if not coerced:
        raise ValueError(f"{name} must not be empty")
    if any(not math.isfinite(value) for value in coerced):
        raise ValueError(f"{name} must contain only finite values")
    return coerced


def _complex_trapezoid(x: tuple[float, ...], y: tuple[complex, ...]) -> complex:
    """Return the explicit trapezoid integral on one monotone grid."""

    total = 0.0 + 0.0j
    for x0, x1, y0, y1 in zip(x, x[1:], y, y[1:]):
        total += 0.5 * (y0 + y1) * (x1 - x0)
    return total


def _finite_difference(x: tuple[float, ...], y: tuple[float, ...], index: int) -> float:
    """Return the first derivative on one explicit monotone sample grid."""

    if len(x) != len(y):
        raise ValueError("x and y must have the same length")
    if len(x) < 2:
        raise ValueError("at least two samples are required")
    if index == 0:
        return (y[1] - y[0]) / (x[1] - x[0])
    if index == len(x) - 1:
        return (y[-1] - y[-2]) / (x[-1] - x[-2])
    return (y[index + 1] - y[index - 1]) / (x[index + 1] - x[index - 1])


def _require_closed_scalar_history_lengths(
    carrier: ScalarHierarchyCarrier,
    conformal_time_mpc: Sequence[float],
    states: Sequence[ScalarHierarchyState],
    metric_states: Sequence[object],
    visibility: VisibilityPacket,
) -> None:
    """Reject mismatched explicit history carriers."""

    size = len(conformal_time_mpc)
    if size < 2:
        raise ValueError("explicit scalar source histories require at least two samples")
    if len(states) != size or len(metric_states) != size:
        raise ValueError("states and metric_states must match conformal_time_mpc length")
    if len(visibility.z_obs) != size:
        raise ValueError("visibility packet must match the supplied source-history length")
    for state in states:
        if not isinstance(state, ScalarHierarchyState):
            raise TypeError("states must contain ScalarHierarchyState entries")
    for metric_state in metric_states:
        metric_carrier = getattr(metric_state, "carrier", None)
        if metric_carrier != carrier:
            raise ValueError("every metric-state sample must refer to the same scalar carrier")


def _visibility_exp_minus_kappa(visibility: VisibilityPacket) -> tuple[float, ...]:
    """Return the explicit `exp(-kappa)` carrier from the visibility packet."""

    return tuple(math.exp(-tau_value) for tau_value in visibility.tau_obs)


def _closed_scalar_shell_constants(carrier: ScalarHierarchyCarrier) -> tuple[int, float, float, float, float]:
    """Return `(beta, K, k, q, s2)` on the physical closed scalar shell."""

    n = carrier.mode.n
    curvature_radius = carrier.curvature_radius_mpc
    curvature_k = 1.0 / (curvature_radius * curvature_radius)
    laplacian_k = math.sqrt(n * (n + 2.0) * curvature_k)
    q = (n + 1.0) * math.sqrt(curvature_k)
    s2 = math.sqrt((n - 1.0) * (n + 3.0) / (n * (n + 2.0)))
    return n + 1, curvature_k, laplacian_k, q, s2


def _temperature_shear(state: ScalarHierarchyState) -> float:
    """Return the explicit temperature shear carrier `F_2 / 2`."""

    if len(state.photon_multipoles) < 1:
        raise OpenTheoremBoundaryError(
            "The scalar transfer projector requires explicit photon shear `F_2/2` on each history sample."
        )
    return state.photon_multipoles[0]


def _polarization_source_term(state: ScalarHierarchyState, *, s2: float) -> float:
    """Return the explicit scalar polarization source `P`."""

    if len(state.polarization_multipoles) < 3:
        raise OpenTheoremBoundaryError(
            "The scalar transfer projector requires explicit `(G_0, G_2)` polarization history samples."
        )
    shear = _temperature_shear(state)
    g0 = state.polarization_multipoles[0]
    g2 = state.polarization_multipoles[2]
    return (g0 + g2 + 2.0 * s2 * shear) / 8.0


def _sorted_scalar_history_rows(
    visibility: VisibilityPacket,
    conformal_time_mpc: Sequence[float],
    states: Sequence[ScalarHierarchyState],
    metric_states: Sequence[object],
) -> list[tuple[float, float, float, float, ScalarHierarchyState, object]]:
    """Return rows sorted by increasing conformal time."""

    exp_minus_kappa = _visibility_exp_minus_kappa(visibility)
    rows = [
        (
            float(tau),
            float(z),
            float(exp_kappa),
            float(g_obs),
            state,
            metric_state,
        )
        for tau, z, exp_kappa, g_obs, state, metric_state in zip(
            conformal_time_mpc,
            visibility.z_obs,
            exp_minus_kappa,
            visibility.g_obs,
            states,
            metric_states,
        )
    ]
    rows.sort(key=lambda row: row[0])
    if any(b[0] <= a[0] for a, b in zip(rows, rows[1:])):
        raise ValueError("conformal_time_mpc must become strictly increasing after sorting")
    return rows


def _closed_scalar_cf1_from_gegenbauer(ell: int, beta: int, chi: float) -> float:
    """Return `(dPhi_l / dchi) / Phi_l` from the exact Gegenbauer ratio."""

    n = beta - ell - 1
    if n < 0:
        raise ValueError("closed scalar radial ratio requires beta >= ell + 1")
    alpha = ell + 1
    sin_chi = math.sin(chi)
    cot_chi = math.cos(chi) / sin_chi
    x = math.cos(chi)
    if n == 0:
        gegenbauer = 1.0
        derivative = 0.0
    elif n == 1:
        gegenbauer = 2.0 * alpha * x
        derivative = 2.0 * alpha
    elif n == 2:
        gegenbauer = -alpha + 2.0 * alpha * (1.0 + alpha) * x * x
        derivative = 4.0 * x * alpha * (1.0 + alpha)
    elif n == 3:
        gegenbauer = -2.0 * alpha * (1.0 + alpha) * x + (4.0 / 3.0) * alpha * (1.0 + alpha) * (2.0 + alpha) * x**3
        derivative = 2.0 * alpha * (1.0 + alpha) * (2.0 * (2.0 + alpha) * x * x - 1.0)
    else:
        gkm2 = -alpha + 2.0 * alpha * (1.0 + alpha) * x * x
        gkm1 = -2.0 * alpha * (1.0 + alpha) * x + (4.0 / 3.0) * alpha * (1.0 + alpha) * (2.0 + alpha) * x**3
        gegenbauer = gkm1
        for k in range(4, n + 1):
            gegenbauer = (2.0 * (k + alpha - 1.0) * x * gkm1 - (k + 2.0 * alpha - 2.0) * gkm2) / k
            gkm2, gkm1 = gkm1, gegenbauer
        derivative = (-n * x * gegenbauer + (n + 2.0 * alpha - 1.0) * gkm2) / (1.0 - x * x)
    if gegenbauer == 0.0:
        raise ValueError("closed scalar Gegenbauer ratio hit a zero of Phi_l")
    return ell * cot_chi - sin_chi * derivative / gegenbauer


def _closed_scalar_cf1(ell: int, beta: float, chi: float) -> tuple[float, int]:
    """Return the continued-fraction ratio `(dPhi_l / dchi) / Phi_l`."""

    maxiter = max(int(beta - ell - 10), 0)
    tiny = 1.0e-100
    reltol = float.fromhex("0x1.0000000000000p-52")
    beta_sq = beta * beta
    cot_chi = math.cos(chi) / math.sin(chi)
    bj = ell * cot_chi
    fj = bj
    cj = bj if bj != 0.0 else tiny
    dj = 0.0
    sign = 1
    for j in range(1, maxiter + 1):
        sqrt_tmp = math.sqrt(beta_sq - (ell + j + 1.0) * (ell + j + 1.0))
        aj = -math.sqrt(beta_sq - (ell + j) * (ell + j)) / sqrt_tmp
        if j == 1:
            aj *= math.sqrt(beta_sq - (ell + 1.0) * (ell + 1.0))
        bj = (2.0 * (ell + j) + 1.0) / sqrt_tmp * cot_chi
        dj = bj + aj * dj
        if dj == 0.0:
            dj = tiny
        cj = bj + aj / cj
        if cj == 0.0:
            cj = tiny
        dj = 1.0 / dj
        delta_j = cj * dj
        fj *= delta_j
        if dj < 0.0:
            sign *= -1
        if abs(delta_j - 1.0) < reltol:
            return fj, sign
    raise ValueError("closed scalar continued fraction did not converge")


def _closed_scalar_radial_values(beta: int, ell: int, chi: float) -> tuple[float, ...]:
    """Return `Phi_j(chi)` for `j = 0, ..., ell_max` by stable recurrence."""

    if ell < 0:
        raise ValueError("ell must be non-negative")
    if beta < ell + 1:
        raise ValueError("closed scalar support requires beta >= ell + 1")
    sin_chi = math.sin(chi)
    if abs(sin_chi) < 1.0e-14:
        raise ValueError("chi lands on a closed-space radial singularity")
    cot_chi = math.cos(chi) / sin_chi
    phi0 = math.sin(beta * chi) / (beta * sin_chi)
    if ell == 0:
        return (phi0,)

    ell_max = ell
    phi_high = 1.0
    try:
        if beta > 1.5 * ell_max:
            phipr1, _ = _closed_scalar_cf1(ell_max, float(beta), chi)
        else:
            phipr1 = _closed_scalar_cf1_from_gegenbauer(ell_max, beta, chi)
    except ValueError:
        phipr1 = _closed_scalar_cf1_from_gegenbauer(ell_max, beta, chi)

    phi_values = [0.0] * (ell_max + 1)
    phi_values[ell_max] = phi_high
    phi_plus_1_times_sqrt = ell_max * cot_chi * phi_high - phipr1
    phi = phi_high
    for current_ell in range(ell_max, 0, -1):
        sqrt_k = math.sqrt(beta * beta - current_ell * current_ell)
        phi_minus_1 = ((2.0 * current_ell + 1.0) * cot_chi * phi - phi_plus_1_times_sqrt) / sqrt_k
        phi_plus_1_times_sqrt = phi * sqrt_k
        phi = phi_minus_1
        phi_values[current_ell - 1] = phi

    scaling = phi0 / phi_values[0]
    return tuple(value * scaling for value in phi_values)


@dataclass(frozen=True)
class ClosedS3ScalarRadialChain:
    """Exact scalar hyperspherical radial chain on one closed shell."""

    carrier: ScalarHierarchyCarrier
    ell: int
    chi: float
    phi: float
    dphi_dchi: float
    d2phi_dchi2: float
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


@dataclass(frozen=True)
class ClosedS3ScalarSourceHistory:
    """Explicit scalar LOS source history on one closed scalar shell."""

    carrier: ScalarHierarchyCarrier
    gauge: str
    z_obs: tuple[float, ...]
    conformal_time_mpc: tuple[float, ...]
    exp_minus_kappa: tuple[float, ...]
    visibility_source: tuple[float, ...]
    temperature_source_0: tuple[float, ...]
    temperature_source_1: tuple[float, ...]
    temperature_source_2: tuple[float, ...]
    polarization_source: tuple[float, ...]
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]

    def __post_init__(self) -> None:
        size = len(self.conformal_time_mpc)
        vectors = (
            self.z_obs,
            self.exp_minus_kappa,
            self.visibility_source,
            self.temperature_source_0,
            self.temperature_source_1,
            self.temperature_source_2,
            self.polarization_source,
        )
        if any(len(vector) != size for vector in vectors):
            raise ValueError("all scalar source-history vectors must match conformal_time_mpc length")
        if any(b <= a for a, b in zip(self.conformal_time_mpc, self.conformal_time_mpc[1:])):
            raise ValueError("conformal_time_mpc must be strictly increasing")


class ClosedS3ScalarTransferProjector:
    """Exact closed-geometry scalar transfer projector with explicit quadrature."""

    def project_temperature(
        self,
        history: ClosedS3ScalarSourceHistory,
        *,
        tau_observer_mpc: float,
        ell_values: Iterable[int] | None = None,
    ) -> ClosedS3TransferPacket:
        """Project one explicit scalar source history to `Delta_l^T(q)`."""

        return project_closed_s3_scalar_temperature(history, tau_observer_mpc=tau_observer_mpc, ell_values=ell_values)

    def project_e_polarization(
        self,
        history: ClosedS3ScalarSourceHistory,
        *,
        tau_observer_mpc: float,
        ell_values: Iterable[int] | None = None,
    ) -> ClosedS3TransferPacket:
        """Project one explicit scalar source history to `Delta_l^E(q)`."""

        return project_closed_s3_scalar_e_polarization(history, tau_observer_mpc=tau_observer_mpc, ell_values=ell_values)


def evaluate_closed_s3_scalar_radial_chain(
    carrier: ScalarHierarchyCarrier,
    *,
    ell: int,
    chi: float,
) -> ClosedS3ScalarRadialChain:
    """Return the exact closed scalar radial chain on one shell and one `chi`.

    The shell parameter is `beta = nu = n+1`, and the exact radial recurrence
    is

    - `Phi_0 = sin(beta chi) / [beta sin chi]`
    - `Phi_1 = Phi_0 [cot chi - beta cot(beta chi)] / sqrt(beta^2-1)`
    - `Phi_l = [(2l-1) cot chi Phi_{l-1} - sqrt(beta^2-(l-1)^2) Phi_{l-2}] / sqrt(beta^2-l^2)`

    with

    - `dPhi_l / dchi = l cot chi Phi_l - sqrt(beta^2-(l+1)^2) Phi_{l+1}`
    - `d2Phi_l / dchi^2 = -2 cot chi dPhi_l/dchi + [l(l+1) csc^2 chi - beta^2 + 1] Phi_l`
    """

    ell = int(ell)
    if not carrier.supports_ell(ell):
        raise ValueError("ell lies outside the closed scalar shell support")
    chi = float(chi)
    if not math.isfinite(chi) or chi <= 0.0 or chi >= math.pi:
        raise ValueError("chi must satisfy 0 < chi < pi on closed S^3")

    beta = carrier.mode.n + 1
    phi_values = _closed_scalar_radial_values(beta, ell + (0 if ell == carrier.mode.n else 1), chi)
    phi = phi_values[ell]
    cot_chi = math.cos(chi) / math.sin(chi)
    if ell == carrier.mode.n:
        dphi = ell * cot_chi * phi
    else:
        dphi = ell * cot_chi * phi - math.sqrt(beta * beta - (ell + 1.0) * (ell + 1.0)) * phi_values[ell + 1]
    sin_sq = math.sin(chi) ** 2
    d2phi = -2.0 * cot_chi * dphi + (ell * (ell + 1.0) / sin_sq - beta * beta + 1.0) * phi
    return ClosedS3ScalarRadialChain(
        carrier=carrier,
        ell=ell,
        chi=chi,
        phi=phi,
        dphi_dchi=dphi,
        d2phi_dchi2=d2phi,
        claim_status="derived / scoped",
        provenance_node_ids=("paper22.spatial_mode_ladder", "paper23.closed_scalar_operator", "local.closed_scalar_transfer_projector"),
        scope_boundary=(
            "Exact closed scalar radial chain on one physical shell.",
            "Does not by itself perform LOS integration or derive the hierarchy source history.",
        ),
    )


def build_newtonian_scalar_source_history(
    carrier: ScalarHierarchyCarrier,
    *,
    conformal_time_mpc: Sequence[float],
    visibility: VisibilityPacket,
    states: Sequence[ScalarHierarchyState],
    metric_states: Sequence[NewtonianScalarMetricState],
) -> ClosedS3ScalarSourceHistory:
    """Build the transparent Newtonian-gauge scalar LOS source history.

    On each sample:

    - `S_T^(0) = exp(-kappa) phi' + g delta_gamma / 4`
    - `S_T^(1) = exp(-kappa) k_n psi + g theta_b / k_n`
    - `S_T^(2) = g P`
    - `S_E = g P`
    """

    _require_closed_scalar_history_lengths(carrier, conformal_time_mpc, states, metric_states, visibility)
    if not visibility.absolute_to_observer:
        raise OpenTheoremBoundaryError(
            "The scalar transfer projector requires visibility measured to the observer boundary (`z=0`) rather than a relative lower-redshift packet."
        )
    _, _, laplacian_k, _, s2 = _closed_scalar_shell_constants(carrier)
    rows = _sorted_scalar_history_rows(visibility, conformal_time_mpc, states, metric_states)

    tau: list[float] = []
    z_obs: list[float] = []
    exp_minus_kappa: list[float] = []
    g_obs: list[float] = []
    s0: list[float] = []
    s1: list[float] = []
    s2_list: list[float] = []
    se: list[float] = []

    for tau_i, z_i, exp_kappa_i, g_i, state, metric_state in rows:
        if not isinstance(metric_state, NewtonianScalarMetricState):
            raise TypeError("metric_states must contain NewtonianScalarMetricState entries")
        p_source = _polarization_source_term(state, s2=s2)
        tau.append(tau_i)
        z_obs.append(z_i)
        exp_minus_kappa.append(exp_kappa_i)
        g_obs.append(g_i)
        s0.append(exp_kappa_i * metric_state.phi_prime + g_i * state.delta_gamma / 4.0)
        s1.append(exp_kappa_i * laplacian_k * metric_state.psi + g_i * state.theta_b / laplacian_k)
        s2_list.append(g_i * p_source)
        se.append(g_i * p_source)

    return ClosedS3ScalarSourceHistory(
        carrier=carrier,
        gauge="newtonian",
        z_obs=tuple(z_obs),
        conformal_time_mpc=tuple(tau),
        exp_minus_kappa=tuple(exp_minus_kappa),
        visibility_source=tuple(g_obs),
        temperature_source_0=tuple(s0),
        temperature_source_1=tuple(s1),
        temperature_source_2=tuple(s2_list),
        polarization_source=tuple(se),
        claim_status="derived / scoped",
        provenance_node_ids=("paper23.closed_scalar_operator", "local.closed_scalar_transfer_projector"),
        scope_boundary=(
            "Transparent Newtonian-gauge scalar LOS source history on one explicit closed shell.",
            "Requires supplied hierarchy states, supplied Newtonian metric states, and supplied observer-absolute visibility data.",
        ),
    )


def build_newtonian_scalar_source_history_integrated_by_parts(
    carrier: ScalarHierarchyCarrier,
    *,
    conformal_time_mpc: Sequence[float],
    visibility: VisibilityPacket,
    states: Sequence[ScalarHierarchyState],
    metric_states: Sequence[NewtonianScalarMetricState],
) -> ClosedS3ScalarSourceHistory:
    """Build the Newtonian-gauge scalar LOS source history in integrated form.

    On each sample, with all derivatives taken with respect to conformal time:

    - `S_SW = g (delta_gamma / 4 + psi)`
    - `S_Dop = (g' theta_b + g theta_b') / k_n^2`
    - `S_ISW^(0) = g (phi - psi) + 2 exp(-kappa) phi'`
    - `S_T^(0) = S_SW + S_Dop + S_ISW^(0)`
    - `S_T^(1) = exp(-kappa) k_n (psi - phi)`
    - `S_T^(2) = g P`
    - `S_E = g P`

    This is the standard integrated-by-parts Newtonian source representation.
    It is algebraically equivalent to the transparent form on an exact history,
    but is numerically better behaved because the Doppler term is carried in the
    monopole packet rather than directly through the first radial derivative.
    """

    _require_closed_scalar_history_lengths(carrier, conformal_time_mpc, states, metric_states, visibility)
    if not visibility.absolute_to_observer:
        raise OpenTheoremBoundaryError(
            "The scalar transfer projector requires visibility measured to the observer boundary (`z=0`) rather than a relative lower-redshift packet."
        )
    _, _, laplacian_k, _, s2 = _closed_scalar_shell_constants(carrier)
    laplacian_k_sq = laplacian_k * laplacian_k
    rows = _sorted_scalar_history_rows(visibility, conformal_time_mpc, states, metric_states)

    tau_grid = tuple(row[0] for row in rows)
    theta_b_history = tuple(row[4].theta_b for row in rows)
    g_history = tuple(row[3] for row in rows)

    tau: list[float] = []
    z_obs: list[float] = []
    exp_minus_kappa: list[float] = []
    g_obs: list[float] = []
    s0: list[float] = []
    s1: list[float] = []
    s2_list: list[float] = []
    se: list[float] = []

    for index, (tau_i, z_i, exp_kappa_i, g_i, state, metric_state) in enumerate(rows):
        if not isinstance(metric_state, NewtonianScalarMetricState):
            raise TypeError("metric_states must contain NewtonianScalarMetricState entries")
        p_source = _polarization_source_term(state, s2=s2)
        g_prime = _finite_difference(tau_grid, g_history, index)
        theta_b_prime = _finite_difference(tau_grid, theta_b_history, index)
        source_sw = g_i * (state.delta_gamma / 4.0 + metric_state.psi)
        source_dop = (g_prime * state.theta_b + g_i * theta_b_prime) / laplacian_k_sq
        source_isw0 = g_i * (metric_state.phi - metric_state.psi) + 2.0 * exp_kappa_i * metric_state.phi_prime
        tau.append(tau_i)
        z_obs.append(z_i)
        exp_minus_kappa.append(exp_kappa_i)
        g_obs.append(g_i)
        s0.append(source_sw + source_dop + source_isw0)
        s1.append(exp_kappa_i * laplacian_k * (metric_state.psi - metric_state.phi))
        s2_list.append(g_i * p_source)
        se.append(g_i * p_source)

    return ClosedS3ScalarSourceHistory(
        carrier=carrier,
        gauge="newtonian",
        z_obs=tuple(z_obs),
        conformal_time_mpc=tuple(tau),
        exp_minus_kappa=tuple(exp_minus_kappa),
        visibility_source=tuple(g_obs),
        temperature_source_0=tuple(s0),
        temperature_source_1=tuple(s1),
        temperature_source_2=tuple(s2_list),
        polarization_source=tuple(se),
        claim_status="derived / scoped",
        provenance_node_ids=("paper23.closed_scalar_operator", "local.closed_scalar_transfer_projector"),
        scope_boundary=(
            "Integrated-by-parts Newtonian-gauge scalar LOS source history on one explicit closed shell.",
            "Requires supplied hierarchy states, supplied Newtonian metric states, and supplied observer-absolute visibility data on the same conformal-time grid.",
        ),
    )


def build_synchronous_scalar_source_history(
    carrier: ScalarHierarchyCarrier,
    *,
    conformal_time_mpc: Sequence[float],
    visibility: VisibilityPacket,
    states: Sequence[ScalarHierarchyState],
    metric_states: Sequence[SynchronousScalarMetricState],
) -> ClosedS3ScalarSourceHistory:
    """Build the transparent synchronous-gauge scalar LOS source history.

    On each sample:

    - `S_T^(0) = - exp(-kappa) h' / 6 + g delta_gamma / 4`
    - `S_T^(1) = g theta_b / k_n`
    - `S_T^(2) = exp(-kappa) k_n^2 (2/3) s_2 alpha + g P`
    - `S_E = g P`
    """

    _require_closed_scalar_history_lengths(carrier, conformal_time_mpc, states, metric_states, visibility)
    if not visibility.absolute_to_observer:
        raise OpenTheoremBoundaryError(
            "The scalar transfer projector requires visibility measured to the observer boundary (`z=0`) rather than a relative lower-redshift packet."
        )
    _, _, laplacian_k, _, s2 = _closed_scalar_shell_constants(carrier)
    laplacian_k_sq = laplacian_k * laplacian_k
    rows = _sorted_scalar_history_rows(visibility, conformal_time_mpc, states, metric_states)

    tau: list[float] = []
    z_obs: list[float] = []
    exp_minus_kappa: list[float] = []
    g_obs: list[float] = []
    s0: list[float] = []
    s1: list[float] = []
    s2_list: list[float] = []
    se: list[float] = []

    for tau_i, z_i, exp_kappa_i, g_i, state, metric_state in rows:
        if not isinstance(metric_state, SynchronousScalarMetricState):
            raise TypeError("metric_states must contain SynchronousScalarMetricState entries")
        p_source = _polarization_source_term(state, s2=s2)
        tau.append(tau_i)
        z_obs.append(z_i)
        exp_minus_kappa.append(exp_kappa_i)
        g_obs.append(g_i)
        s0.append(-exp_kappa_i * metric_state.h_prime / 6.0 + g_i * state.delta_gamma / 4.0)
        s1.append(g_i * state.theta_b / laplacian_k)
        s2_list.append(exp_kappa_i * laplacian_k_sq * (2.0 / 3.0) * s2 * metric_state.alpha + g_i * p_source)
        se.append(g_i * p_source)

    return ClosedS3ScalarSourceHistory(
        carrier=carrier,
        gauge="synchronous",
        z_obs=tuple(z_obs),
        conformal_time_mpc=tuple(tau),
        exp_minus_kappa=tuple(exp_minus_kappa),
        visibility_source=tuple(g_obs),
        temperature_source_0=tuple(s0),
        temperature_source_1=tuple(s1),
        temperature_source_2=tuple(s2_list),
        polarization_source=tuple(se),
        claim_status="derived / scoped",
        provenance_node_ids=("paper23.closed_scalar_operator", "local.closed_scalar_transfer_projector"),
        scope_boundary=(
            "Transparent synchronous-gauge scalar LOS source history on one explicit closed shell.",
            "Requires supplied hierarchy states, supplied synchronous metric states, and supplied observer-absolute visibility data.",
        ),
    )


def _default_ell_values(history: ClosedS3ScalarSourceHistory) -> tuple[int, ...]:
    """Return the full closed scalar support on the carried shell."""

    return tuple(range(history.carrier.ell_min, history.carrier.ell_max + 1))


def _validate_ell_values(history: ClosedS3ScalarSourceHistory, ell_values: Iterable[int] | None) -> tuple[int, ...]:
    """Return a validated multipole list on the closed support."""

    values = _default_ell_values(history) if ell_values is None else tuple(int(ell) for ell in ell_values)
    if not values:
        raise ValueError("ell_values must not be empty")
    if any(b <= a for a, b in zip(values, values[1:])):
        raise ValueError("ell_values must be strictly increasing")
    for ell in values:
        if not history.carrier.supports_ell(ell):
            raise ValueError("ell_values must stay on the closed scalar shell support")
    return values


def _line_of_sight_chi_grid(history: ClosedS3ScalarSourceHistory, tau_observer_mpc: float) -> tuple[float, ...]:
    """Return the dimensionless closed-space LOS radius `chi = sqrt(K)(tau0-tau)`."""

    tau_observer_mpc = float(tau_observer_mpc)
    if not math.isfinite(tau_observer_mpc):
        raise ValueError("tau_observer_mpc must be finite")
    if tau_observer_mpc <= history.conformal_time_mpc[-1]:
        raise ValueError("tau_observer_mpc must lie strictly above the latest source sample")
    curvature_radius = history.carrier.curvature_radius_mpc
    chi = tuple((tau_observer_mpc - tau) / curvature_radius for tau in history.conformal_time_mpc)
    if any(item <= 0.0 or item >= math.pi for item in chi):
        raise ValueError("closed LOS projection requires 0 < chi < pi on the whole explicit grid")
    return chi


def project_closed_s3_scalar_temperature(
    history: ClosedS3ScalarSourceHistory,
    *,
    tau_observer_mpc: float,
    ell_values: Iterable[int] | None = None,
) -> ClosedS3TransferPacket:
    """Project one explicit scalar source history to a temperature transfer packet."""

    ell_values_t = _validate_ell_values(history, ell_values)
    chi = _line_of_sight_chi_grid(history, tau_observer_mpc)
    beta, curvature_k, laplacian_k, q, s2 = _closed_scalar_shell_constants(history.carrier)
    radial_prefactor_1 = math.sqrt(curvature_k) / laplacian_k
    radial_prefactor_2 = 3.0 * curvature_k / (laplacian_k * laplacian_k)

    delta_l: list[complex] = []
    for ell in ell_values_t:
        integrand: list[complex] = []
        for source_0, source_1, source_2, chi_i in zip(
            history.temperature_source_0,
            history.temperature_source_1,
            history.temperature_source_2,
            chi,
        ):
            radial = evaluate_closed_s3_scalar_radial_chain(history.carrier, ell=ell, chi=chi_i)
            radial_0 = radial.phi
            radial_1 = radial_prefactor_1 * radial.dphi_dchi
            radial_2 = (radial_prefactor_2 * radial.d2phi_dchi2 + radial.phi) / (2.0 * s2)
            integrand.append(source_0 * radial_0 + source_1 * radial_1 + source_2 * radial_2)
        delta_l.append(_complex_trapezoid(history.conformal_time_mpc, tuple(complex(value) for value in integrand)))

    return ClosedS3TransferPacket(
        observable=TransferObservable.TEMPERATURE,
        mode=history.carrier.mode,
        curvature_K=curvature_k,
        q=q,
        ell_values=ell_values_t,
        delta_l=tuple(delta_l),
        claim_status="verified / numerical explicit quadrature of exact closed scalar LOS projector",
        provenance_node_ids=(
            "paper22.spatial_mode_ladder",
            "paper23.closed_scalar_operator",
            "local.closed_scalar_transfer_projector",
        ),
        scope_boundary=(
            "Exact scalar LOS source law plus exact closed radial chain on one explicit shell.",
            "Numeric packet values are produced by explicit trapezoid quadrature on the supplied conformal-time grid.",
            "Does not derive the source history automatically from the full perturbation evolution problem.",
        ),
    )


def project_closed_s3_scalar_e_polarization(
    history: ClosedS3ScalarSourceHistory,
    *,
    tau_observer_mpc: float,
    ell_values: Iterable[int] | None = None,
) -> ClosedS3TransferPacket:
    """Project one explicit scalar source history to an E-polarization transfer packet."""

    ell_values_t = _validate_ell_values(history, ell_values)
    chi = _line_of_sight_chi_grid(history, tau_observer_mpc)
    _, curvature_k, _, q, s2 = _closed_scalar_shell_constants(history.carrier)

    delta_l: list[complex] = []
    for ell in ell_values_t:
        if ell < 2:
            delta_l.append(0.0 + 0.0j)
            continue
        ell_factor = math.sqrt(3.0 / 8.0 * (ell + 2.0) * (ell + 1.0) * ell * (ell - 1.0)) / s2
        integrand: list[complex] = []
        for source_e, chi_i in zip(history.polarization_source, chi):
            radial = evaluate_closed_s3_scalar_radial_chain(history.carrier, ell=ell, chi=chi_i)
            csc_sq = 1.0 / (math.sin(chi_i) * math.sin(chi_i))
            integrand.append(source_e * ell_factor * csc_sq * radial.phi)
        delta_l.append(_complex_trapezoid(history.conformal_time_mpc, tuple(complex(value) for value in integrand)))

    return ClosedS3TransferPacket(
        observable=TransferObservable.E_POLARIZATION,
        mode=history.carrier.mode,
        curvature_K=curvature_k,
        q=q,
        ell_values=ell_values_t,
        delta_l=tuple(delta_l),
        claim_status="verified / numerical explicit quadrature of exact closed scalar LOS projector",
        provenance_node_ids=(
            "paper22.spatial_mode_ladder",
            "paper23.closed_scalar_operator",
            "local.closed_scalar_transfer_projector",
        ),
        scope_boundary=(
            "Exact scalar polarization LOS source law plus exact closed radial chain on one explicit shell.",
            "Numeric packet values are produced by explicit trapezoid quadrature on the supplied conformal-time grid.",
            "Does not derive the source history automatically from the full perturbation evolution problem.",
        ),
    )


__all__ = [
    "ClosedS3ScalarRadialChain",
    "ClosedS3ScalarSourceHistory",
    "ClosedS3ScalarTransferProjector",
    "build_newtonian_scalar_source_history",
    "build_newtonian_scalar_source_history_integrated_by_parts",
    "build_synchronous_scalar_source_history",
    "evaluate_closed_s3_scalar_radial_chain",
    "project_closed_s3_scalar_e_polarization",
    "project_closed_s3_scalar_temperature",
]
