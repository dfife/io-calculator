"""Coupled Thomson-history tuple contract for the Phase 3 perturbation block.

Calculator fixes the surviving Thomson carrier more sharply than "change
`dkappa` somewhere." The exact closure, if it exists, must act on the coupled
tuple

`(thomson_drag_rate, thomson_hierarchy_rate, tau_c, dtau_c, slip, shear)`.

This module implements that contract and nothing stronger. It does not invent
the final IO-native operator on the tuple; it keeps that seam explicit.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Protocol

from .recombination import (
    OpenTheoremBoundaryError,
    Stage2History,
    VisibilityPacket,
    build_visibility_packet,
    primitive_local_kappa_prime,
)


def _float_tuple(values: tuple[float, ...] | list[float], *, name: str) -> tuple[float, ...]:
    """Validate a finite tuple of Thomson-history values."""

    coerced = tuple(float(value) for value in values)
    if not coerced:
        raise ValueError(f"{name} must not be empty")
    if any(not math.isfinite(value) for value in coerced):
        raise ValueError(f"{name} must contain only finite values")
    return coerced


@dataclass(frozen=True)
class ThomsonHistorySample:
    """One sample of the Calculator coupled Thomson-history tuple."""

    z_obs: float
    thomson_drag_rate: float
    thomson_hierarchy_rate: float
    tau_c: float
    dtau_c: float
    slip: float
    shear: float


@dataclass(frozen=True)
class TypedThomsonSplitHistoryRealization:
    """Typed realization of the Thomson tuple from local opacity plus visibility."""

    z_obs: tuple[float, ...]
    primitive_local_kappa_prime: tuple[float, ...]
    visibility_packet: VisibilityPacket
    contract: "ThomsonHistoryContract"
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


@dataclass(frozen=True)
class ThomsonHistoryContract:
    """A typed sampled carrier for the coupled Thomson-history tuple."""

    z_obs: tuple[float, ...]
    thomson_drag_rate: tuple[float, ...]
    thomson_hierarchy_rate: tuple[float, ...]
    drag_rate_derivative: tuple[float, ...]
    tau_c: tuple[float, ...]
    dtau_c: tuple[float, ...]
    slip: tuple[float, ...]
    shear: tuple[float, ...]
    derivative_coordinate: str
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]

    def __post_init__(self) -> None:
        size = len(self.z_obs)
        if size < 1:
            raise ValueError("z_obs must not be empty")
        vectors = (
            self.thomson_drag_rate,
            self.thomson_hierarchy_rate,
            self.drag_rate_derivative,
            self.tau_c,
            self.dtau_c,
            self.slip,
            self.shear,
        )
        if any(len(values) != size for values in vectors):
            raise ValueError("all Thomson-history vectors must match z_obs length")
        if any(z < 0.0 for z in self.z_obs):
            raise ValueError("z_obs values must be non-negative")
        if any(b <= a for a, b in zip(self.z_obs, self.z_obs[1:])):
            raise ValueError("z_obs must be strictly increasing")
        if any(rate <= 0.0 for rate in self.thomson_drag_rate):
            raise ValueError("thomson_drag_rate must stay strictly positive")
        if any(rate <= 0.0 for rate in self.thomson_hierarchy_rate):
            raise ValueError("thomson_hierarchy_rate must stay strictly positive")

    def sample(self, index: int) -> ThomsonHistorySample:
        """Return one sampled tuple entry."""

        return ThomsonHistorySample(
            z_obs=self.z_obs[index],
            thomson_drag_rate=self.thomson_drag_rate[index],
            thomson_hierarchy_rate=self.thomson_hierarchy_rate[index],
            tau_c=self.tau_c[index],
            dtau_c=self.dtau_c[index],
            slip=self.slip[index],
            shear=self.shear[index],
        )


class CoupledThomsonHistoryOperator(Protocol):
    """Protocol for a future exact operator acting on the Thomson-history tuple."""

    def apply(self, contract: ThomsonHistoryContract, **kwargs: Any) -> Any:
        """Apply the exact IO-native operator on the coupled Thomson-history tuple."""


def _finite_difference(x: tuple[float, ...], y: tuple[float, ...], index: int) -> float:
    """Return the first derivative `dy/dx` on one explicit sample grid."""

    index = int(index)
    if len(x) != len(y):
        raise ValueError("x and y must have the same length")
    if len(x) < 2:
        raise ValueError("at least two samples are required for a derivative")
    if index < 0 or index >= len(x):
        raise IndexError("sample index out of range")
    if len(x) == 2 or index == 0:
        return (y[1] - y[0]) / (x[1] - x[0])
    if index == len(x) - 1:
        return (y[-1] - y[-2]) / (x[-1] - x[-2])
    return (y[index + 1] - y[index - 1]) / (x[index + 1] - x[index - 1])


def build_thomson_history_contract(
    z_obs: tuple[float, ...] | list[float],
    thomson_drag_rate: tuple[float, ...] | list[float],
    thomson_hierarchy_rate: tuple[float, ...] | list[float],
    drag_rate_derivative: tuple[float, ...] | list[float],
    slip: tuple[float, ...] | list[float],
    shear: tuple[float, ...] | list[float],
    *,
    derivative_coordinate: str = "local_time",
) -> ThomsonHistoryContract:
    """Build the sampled Calculator Thomson tuple from supplied rates.

    The theorem-grade part here is the carrier relation itself:

    - `tau_c = 1 / thomson_drag_rate`
    - `dtau_c = - d(thomson_drag_rate) * tau_c^2`

    The function does not infer the drag or hierarchy rates; callers must supply
    them from whatever later theorem-grade operator eventually closes that seam.
    """

    z_obs_t = _float_tuple(z_obs, name="z_obs")
    drag_t = _float_tuple(thomson_drag_rate, name="thomson_drag_rate")
    hierarchy_t = _float_tuple(thomson_hierarchy_rate, name="thomson_hierarchy_rate")
    derivative_t = _float_tuple(drag_rate_derivative, name="drag_rate_derivative")
    slip_t = _float_tuple(slip, name="slip")
    shear_t = _float_tuple(shear, name="shear")
    if any(rate <= 0.0 for rate in drag_t):
        raise ValueError("thomson_drag_rate must stay strictly positive")
    if any(rate <= 0.0 for rate in hierarchy_t):
        raise ValueError("thomson_hierarchy_rate must stay strictly positive")
    tau_c = tuple(1.0 / rate for rate in drag_t)
    dtau_c = tuple(-derivative * tau * tau for derivative, tau in zip(derivative_t, tau_c))
    return ThomsonHistoryContract(
        z_obs=z_obs_t,
        thomson_drag_rate=drag_t,
        thomson_hierarchy_rate=hierarchy_t,
        drag_rate_derivative=derivative_t,
        tau_c=tau_c,
        dtau_c=dtau_c,
        slip=slip_t,
        shear=shear_t,
        derivative_coordinate=str(derivative_coordinate),
        claim_status="derived / scoped",
        provenance_node_ids=("calculator.thomson_history_realization",),
        scope_boundary=(
            "This is the coupled Thomson-history carrier only.",
            "The exact IO-native operator acting on this tuple remains open.",
        ),
    )


def build_typed_split_thomson_history_realization(
    history: Stage2History,
    dc_dz_mpc: tuple[float, ...] | list[float],
    tau_samples_mpc: tuple[float, ...] | list[float],
    *,
    derivative_coordinate: str = "conformal_time",
    omega_b_h2: float | None = None,
    helium_mass_fraction: float | None = None,
) -> TypedThomsonSplitHistoryRealization:
    """Build the typed split history realization used by the live TT driver.

    Code path:

    1. local chemistry / opacity:
       `kappa'_loc(z) = a n_e(z) sigma_T`
    2. observer-side optical packet:
       `d tau_obs / dz`, `tau_obs`, `g_obs`
    3. conformal Thomson tuple:
       `thomson_drag_rate = |(d tau_obs / dz) / (dC / dz)|`
       and then
       `(thomson_drag_rate, thomson_hierarchy_rate, tau_c, dtau_c, slip, shear)`

    This keeps the geometric local-opacity layer and the observer-side
    visibility/readout layer explicit instead of flattening them into one raw
    opacity scalar.
    """

    dc_dz_t = _float_tuple(dc_dz_mpc, name="dc_dz_mpc")
    tau_samples_t = _float_tuple(tau_samples_mpc, name="tau_samples_mpc")
    if len(dc_dz_t) != len(history.z_obs):
        raise ValueError("dc_dz_mpc must match the Stage2History grid")
    if len(tau_samples_t) != len(history.z_obs):
        raise ValueError("tau_samples_mpc must match the Stage2History grid")
    if any(value <= 0.0 for value in dc_dz_t):
        raise ValueError("dc_dz_mpc must stay strictly positive")

    local_kwargs = {}
    if omega_b_h2 is not None:
        local_kwargs["omega_b_h2"] = omega_b_h2
    if helium_mass_fraction is not None:
        local_kwargs["helium_mass_fraction"] = helium_mass_fraction

    local_kappa_prime = tuple(
        primitive_local_kappa_prime(z, x_e, **local_kwargs)
        for z, x_e in zip(history.z_obs, history.x_e)
    )
    visibility = build_visibility_packet(
        history,
        **local_kwargs,
    )
    drag_rate = tuple(
        abs(d_tau_obs_dz / dc_dz)
        for d_tau_obs_dz, dc_dz in zip(visibility.d_tau_obs_dz, dc_dz_t)
    )
    drag_rate_derivative = tuple(
        _finite_difference(tau_samples_t, drag_rate, index)
        for index in range(len(drag_rate))
    )
    contract = build_thomson_history_contract(
        history.z_obs,
        drag_rate,
        drag_rate,
        drag_rate_derivative,
        [0.0] * len(history.z_obs),
        [0.0] * len(history.z_obs),
        derivative_coordinate=derivative_coordinate,
    )
    return TypedThomsonSplitHistoryRealization(
        z_obs=history.z_obs,
        primitive_local_kappa_prime=local_kappa_prime,
        visibility_packet=visibility,
        contract=contract,
        claim_status="derived / scoped typed split history realization",
        provenance_node_ids=(
            "paper31.baryon_assignment",
            "calculator.thomson_history_realization",
            "local.typed_thomson_split_history_realization",
        ),
        scope_boundary=(
            "This closes the typed implementation path from local Stage-2 chemistry to the conformal Thomson tuple on one explicit grid.",
            "The live driver still uses the scoped equal-rate branch `thomson_drag_rate = thomson_hierarchy_rate` on this realization path.",
        ),
    )


class OpenCoupledThomsonHistoryOperator:
    """Explicit placeholder for the still-open Calculator Thomson operator."""

    def apply(self, contract: ThomsonHistoryContract, **kwargs: Any) -> Any:
        """Fail honestly until the exact tuple-level operator is derived."""

        raise OpenTheoremBoundaryError(
            "The coupled Thomson-history tuple is explicit, but the exact IO-native "
            "operator acting on `(thomson_drag_rate, thomson_hierarchy_rate, tau_c, "
            "dtau_c, slip, shear)` remains open."
        )


__all__ = [
    "CoupledThomsonHistoryOperator",
    "OpenCoupledThomsonHistoryOperator",
    "ThomsonHistoryContract",
    "ThomsonHistorySample",
    "TypedThomsonSplitHistoryRealization",
    "build_thomson_history_contract",
    "build_typed_split_thomson_history_realization",
]
