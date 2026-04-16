"""Theorem-grade scalar-hierarchy skeleton on closed `S^3`.

This module exposes the part of Phase 3 that is already closed enough to code:

- `derived / scoped`: physical scalar mode support begins at `n >= 2`
- `derived / scoped`: the scalar shell operator is `lambda_n - 3 = (n-1)(n+3)`
- `derived / scoped`: scalar hyperspherical support obeys `ell = 0,1,...,n`
- `derived / scoped`: scalar hierarchy inputs must pass through the typed
  closed-`S^3` carrier and the still-open source/acoustic seam

It does not claim to solve the exact hierarchy. Any attempt to evolve the state
without a later theorem-grade source/acoustic operator fails explicitly.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .perturbation_types import (
    OpenTypedSourceAcousticOperator,
    PerturbationBlockInputs,
    TypedSourceAcousticOperator,
    make_perturbation_block_inputs,
)
from .recombination import OpenTheoremBoundaryError, Stage2History
from .s3_modes import S3Channel, S3ModeSpectrum, scalar_mode
from .thomson_history_contract import ThomsonHistoryContract


def _float_tuple(values: tuple[float, ...] | list[float], *, name: str) -> tuple[float, ...]:
    """Validate a finite tuple of hierarchy moments."""

    coerced = tuple(float(value) for value in values)
    if any(not math.isfinite(value) for value in coerced):
        raise ValueError(f"{name} must contain only finite values")
    return coerced


@dataclass(frozen=True)
class ScalarHierarchyCarrier:
    """The theorem-grade physical scalar shell used by the perturbation block."""

    mode: S3ModeSpectrum
    curvature_radius_mpc: float
    shell_wavenumber_sq_mpc_inv2: float
    ell_min: int
    ell_max: int
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]

    def supports_ell(self, ell: int) -> bool:
        """Return whether this scalar shell supports the given hyperspherical multipole."""

        ell = int(ell)
        return self.ell_min <= ell <= self.ell_max


@dataclass(frozen=True)
class ScalarHierarchyState:
    """A typed scalar hierarchy state on one closed-`S^3` shell.

    The state container is deliberately modest. It is a carrier for data and
    bookkeeping, not a claim that the exact perturbation hierarchy is solved.
    """

    phi: float
    psi: float
    delta_gamma: float
    theta_gamma: float
    delta_b: float
    theta_b: float
    photon_multipoles: tuple[float, ...] = ()
    polarization_multipoles: tuple[float, ...] = ()
    claim_status: str = "derived / scoped carrier state"
    provenance_node_ids: tuple[str, ...] = ("paper32.closed_s3_solver_spec",)
    scope_boundary: tuple[str, ...] = (
        "Typed scalar hierarchy state carrier only.",
        "No exact source/acoustic update is implied by storing the state.",
    )

    def __post_init__(self) -> None:
        scalars = (
            self.phi,
            self.psi,
            self.delta_gamma,
            self.theta_gamma,
            self.delta_b,
            self.theta_b,
        )
        if any(not math.isfinite(value) for value in scalars):
            raise ValueError("scalar hierarchy state values must be finite")
        object.__setattr__(
            self,
            "photon_multipoles",
            _float_tuple(self.photon_multipoles, name="photon_multipoles"),
        )
        object.__setattr__(
            self,
            "polarization_multipoles",
            _float_tuple(self.polarization_multipoles, name="polarization_multipoles"),
        )


@dataclass(frozen=True)
class ScalarHierarchyStepRequest:
    """One theorem-grade request presented to the still-open scalar hierarchy step."""

    carrier: ScalarHierarchyCarrier
    state: ScalarHierarchyState
    perturbation_inputs: PerturbationBlockInputs
    thomson_history: ThomsonHistoryContract
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


def build_scalar_hierarchy_carrier(
    n: int, *, curvature_radius_mpc: float
) -> ScalarHierarchyCarrier:
    """Return the physical scalar shell on the closed `S^3` hierarchy.

    The hierarchy layer is restricted to physical inhomogeneous scalar shells,
    so `n = 0,1` are rejected here even though they remain visible in
    `s3_modes.py` as background/gauge carriers.
    """

    mode = scalar_mode(n)
    if mode.channel is not S3Channel.SCALAR:
        raise ValueError("scalar hierarchy carrier requires a scalar mode")
    if mode.physical_role != "physical":
        raise ValueError("scalar hierarchy carrier requires a physical scalar shell with n >= 2")
    curvature_radius_mpc = float(curvature_radius_mpc)
    if not math.isfinite(curvature_radius_mpc) or curvature_radius_mpc <= 0.0:
        raise ValueError("curvature_radius_mpc must be positive and finite")
    shell_wavenumber_sq = (mode.shifted_scalar_operator or 0.0) / curvature_radius_mpc**2
    return ScalarHierarchyCarrier(
        mode=mode,
        curvature_radius_mpc=curvature_radius_mpc,
        shell_wavenumber_sq_mpc_inv2=shell_wavenumber_sq,
        ell_min=0,
        ell_max=mode.n,
        claim_status="derived / scoped",
        provenance_node_ids=(
            "paper23.closed_scalar_operator",
            "paper32.closed_s3_solver_spec",
        ),
        scope_boundary=(
            "Physical scalar shell carrier only.",
            "The exact source/acoustic evolution operator on this carrier remains open.",
        ),
    )


def make_scalar_hierarchy_step_request(
    carrier: ScalarHierarchyCarrier,
    state: ScalarHierarchyState,
    history: Stage2History,
    thomson_history: ThomsonHistoryContract,
) -> ScalarHierarchyStepRequest:
    """Package a theorem-grade scalar hierarchy request with explicit open seam."""

    return ScalarHierarchyStepRequest(
        carrier=carrier,
        state=state,
        perturbation_inputs=make_perturbation_block_inputs(carrier.mode, history),
        thomson_history=thomson_history,
        claim_status="derived / scoped request carrier",
        provenance_node_ids=("paper32.closed_s3_solver_spec", "calculator.thomson_history_realization"),
        scope_boundary=(
            "This request is a typed input packet for the open scalar hierarchy seam, including the required coupled Thomson-history tuple.",
            "No update is performed until a theorem-grade typed source/acoustic operator is supplied.",
        ),
    )


def evolve_scalar_hierarchy_step(
    request: ScalarHierarchyStepRequest,
    *,
    operator: TypedSourceAcousticOperator | None = None,
    **kwargs: Any,
) -> Any:
    """Apply one scalar hierarchy step if and only if a closed operator exists."""

    active_operator = OpenTypedSourceAcousticOperator() if operator is None else operator
    return active_operator.apply(
        request.perturbation_inputs,
        carrier=request.carrier,
        state=request.state,
        thomson_history=request.thomson_history,
        **kwargs,
    )


def require_scalar_hierarchy_closure(request: ScalarHierarchyStepRequest) -> None:
    """Raise the live theorem boundary for the exact scalar hierarchy."""

    raise OpenTheoremBoundaryError(
        "The scalar closed-S^3 hierarchy carrier is built, but the exact typed "
        "source/acoustic operator remains open. Requesting direct evolution for "
        f"n={request.carrier.mode.n} exceeds the current theorem-grade boundary."
    )
