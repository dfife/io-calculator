"""Closed-`S^3` line-of-sight carriers and explicit angular-spectrum assembly.

This module implements the part of the LOS stack that is already theorem-grade:

- `derived / scoped`: the closed LOS grammar uses hyperspherical support
  `ell < nu = q / sqrt(K)`
- `derived / scoped`: transfer packets `Delta_l^X(q)` live on that closed
  support rather than a flat `K=0` basis
- `derived / scoped`: `C_l` is assembled as a degree-2 shell sum from explicit
  transfer packets and explicit shell weights

What remains open here is the exact projector

`y^(md,ic,q)(tau) -> Delta_l^X(q)`.

This module keeps that seam explicit and raising. It does not invent a flat
line-of-sight default.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol

from .recombination import OpenTheoremBoundaryError
from .s3_modes import S3ModeSpectrum, closed_supports_ell


def _float_tuple(values: tuple[float, ...] | list[float], *, name: str) -> tuple[float, ...]:
    """Validate a finite non-empty real tuple."""

    coerced = tuple(float(value) for value in values)
    if not coerced:
        raise ValueError(f"{name} must not be empty")
    if any(not math.isfinite(value) for value in coerced):
        raise ValueError(f"{name} must contain only finite values")
    return coerced


def _complex_tuple(values: tuple[complex, ...] | list[complex], *, name: str) -> tuple[complex, ...]:
    """Validate a finite non-empty complex tuple."""

    coerced = tuple(complex(value) for value in values)
    if not coerced:
        raise ValueError(f"{name} must not be empty")
    if any(not math.isfinite(value.real) or not math.isfinite(value.imag) for value in coerced):
        raise ValueError(f"{name} must contain only finite values")
    return coerced


def _ell_tuple(values: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    """Validate a finite non-empty strictly increasing ell tuple."""

    coerced = tuple(int(value) for value in values)
    if not coerced:
        raise ValueError("ell_values must not be empty")
    if coerced[0] < 0:
        raise ValueError("ell_values must be non-negative")
    if any(b <= a for a, b in zip(coerced, coerced[1:])):
        raise ValueError("ell_values must be strictly increasing")
    return coerced


class TransferObservable(str, Enum):
    """Observable labels on the closed LOS transfer surface."""

    TEMPERATURE = "T"
    E_POLARIZATION = "E"
    B_POLARIZATION = "B"


def _observable(value: TransferObservable | str) -> TransferObservable:
    """Normalize user input to a transfer-observable enum member."""

    if isinstance(value, TransferObservable):
        return value
    return TransferObservable(str(value))


@dataclass(frozen=True)
class ClosedS3LineOfSightHistory:
    """A typed LOS-history packet awaiting the still-open exact projector."""

    observable: TransferObservable
    mode: S3ModeSpectrum
    curvature_K: float
    q: float
    tau: tuple[float, ...]
    source_samples: tuple[complex, ...]
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]

    def __post_init__(self) -> None:
        if not math.isfinite(self.curvature_K) or self.curvature_K <= 0.0:
            raise ValueError("curvature_K must be positive and finite")
        if not math.isfinite(self.q) or self.q < 0.0:
            raise ValueError("q must be finite and non-negative")
        if len(self.tau) != len(self.source_samples):
            raise ValueError("tau and source_samples must have the same length")
        if any(b <= a for a, b in zip(self.tau, self.tau[1:])):
            raise ValueError("tau must be strictly increasing")


@dataclass(frozen=True)
class ClosedS3TransferPacket:
    """A supplied closed-geometry transfer packet `Delta_l^X(q)`."""

    observable: TransferObservable
    mode: S3ModeSpectrum
    curvature_K: float
    q: float
    ell_values: tuple[int, ...]
    delta_l: tuple[complex, ...]
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]

    def __post_init__(self) -> None:
        if not math.isfinite(self.curvature_K) or self.curvature_K <= 0.0:
            raise ValueError("curvature_K must be positive and finite")
        if not math.isfinite(self.q) or self.q < 0.0:
            raise ValueError("q must be finite and non-negative")
        if len(self.ell_values) != len(self.delta_l):
            raise ValueError("ell_values and delta_l must have the same length")
        for ell in self.ell_values:
            if not closed_supports_ell(ell, self.q, self.curvature_K):
                raise ValueError("transfer packet contains ell outside the closed support ell < nu")

    def delta_at(self, ell: int) -> complex:
        """Return `Delta_l` at the requested multipole, defaulting to zero."""

        ell = int(ell)
        for packet_ell, value in zip(self.ell_values, self.delta_l):
            if packet_ell == ell:
                return value
        return 0.0 + 0.0j


@dataclass(frozen=True)
class WeightedClosedS3TransferPacket:
    """A transfer packet paired with an explicit shell covariance weight."""

    packet: ClosedS3TransferPacket
    shell_weight: float
    weight_label: str
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]

    def __post_init__(self) -> None:
        if not math.isfinite(self.shell_weight) or self.shell_weight < 0.0:
            raise ValueError("shell_weight must be finite and non-negative")


@dataclass(frozen=True)
class ClosedAngularPowerSpectrum:
    """A supplied-shell angular power spectrum assembled on closed `S^3`."""

    observable_pair: str
    ell_values: tuple[int, ...]
    c_ell: tuple[float, ...]
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


class ClosedS3LineOfSightProjector(Protocol):
    """Protocol for the still-open exact closed-geometry LOS projector."""

    def project(self, history: ClosedS3LineOfSightHistory, **kwargs: Any) -> ClosedS3TransferPacket:
        """Project one supplied hierarchy history to a closed transfer packet."""


def build_closed_s3_los_history(
    observable: TransferObservable | str,
    mode: S3ModeSpectrum,
    *,
    curvature_K: float,
    q: float,
    tau: tuple[float, ...] | list[float],
    source_samples: tuple[complex, ...] | list[complex],
) -> ClosedS3LineOfSightHistory:
    """Package one LOS-history carrier for the still-open projector seam."""

    return ClosedS3LineOfSightHistory(
        observable=_observable(observable),
        mode=mode,
        curvature_K=float(curvature_K),
        q=float(q),
        tau=_float_tuple(tau, name="tau"),
        source_samples=_complex_tuple(source_samples, name="source_samples"),
        claim_status="derived / scoped LOS source carrier",
        provenance_node_ids=("paper32.closed_s3_solver_spec",),
        scope_boundary=(
            "Supplied LOS-history carrier only.",
            "The exact hyperspherical projector to Delta_l^X(q) remains open.",
        ),
    )


def build_closed_s3_transfer_packet(
    observable: TransferObservable | str,
    mode: S3ModeSpectrum,
    *,
    curvature_K: float,
    q: float,
    ell_values: tuple[int, ...] | list[int],
    delta_l: tuple[complex, ...] | list[complex],
) -> ClosedS3TransferPacket:
    """Package one supplied `Delta_l^X(q)` packet on the closed support."""

    return ClosedS3TransferPacket(
        observable=_observable(observable),
        mode=mode,
        curvature_K=float(curvature_K),
        q=float(q),
        ell_values=_ell_tuple(ell_values),
        delta_l=_complex_tuple(delta_l, name="delta_l"),
        claim_status="derived / scoped explicit transfer carrier",
        provenance_node_ids=("paper32.closed_s3_solver_spec",),
        scope_boundary=(
            "Supplied closed-geometry transfer packet only.",
            "No exact hierarchy-to-transfer projection theorem is supplied here.",
        ),
    )


def weight_closed_s3_transfer_packet(
    packet: ClosedS3TransferPacket,
    *,
    shell_weight: float,
    weight_label: str = "explicit_shell_covariance",
) -> WeightedClosedS3TransferPacket:
    """Attach an explicit shell weight to a transfer packet."""

    return WeightedClosedS3TransferPacket(
        packet=packet,
        shell_weight=float(shell_weight),
        weight_label=str(weight_label),
        claim_status="derived / scoped explicit shell-weight carrier",
        provenance_node_ids=("paper28.closed_s3_shell_power", "paper32.closed_s3_solver_spec"),
        scope_boundary=(
            "Explicit shell weighting only.",
            "The physical IO source-side shell covariance law must still be supplied rather than guessed here.",
        ),
    )


class OpenClosedS3LineOfSightOperator:
    """Explicit placeholder for the still-open LOS projector."""

    def project(self, history: ClosedS3LineOfSightHistory, **kwargs: Any) -> ClosedS3TransferPacket:
        """Fail honestly until the exact hyperspherical LOS projector exists."""

        raise OpenTheoremBoundaryError(
            "The closed-S^3 line-of-sight grammar is fixed, but the exact projector "
            "from `y^(md,ic,q)(tau)` to `Delta_l^X(q)` remains open. "
            f"Inputs were accepted for observable {history.observable.value} on q={history.q}, "
            "but no theorem-grade projector is available yet."
        )


def project_closed_s3_line_of_sight(
    history: ClosedS3LineOfSightHistory,
    *,
    operator: ClosedS3LineOfSightProjector | None = None,
    **kwargs: Any,
) -> ClosedS3TransferPacket:
    """Apply the exact LOS projector if and only if a theorem-grade one exists."""

    active_operator = OpenClosedS3LineOfSightOperator() if operator is None else operator
    return active_operator.project(history, **kwargs)


def _match_packet_pair(
    left: WeightedClosedS3TransferPacket,
    right: WeightedClosedS3TransferPacket,
) -> None:
    """Require shell-by-shell compatibility for a cross-spectrum pair."""

    if left.packet.mode.channel is not right.packet.mode.channel or left.packet.mode.n != right.packet.mode.n:
        raise ValueError("cross-spectrum packets must share the same closed shell")
    if not math.isclose(left.packet.q, right.packet.q, rel_tol=0.0, abs_tol=1.0e-15):
        raise ValueError("cross-spectrum packets must share the same q shell")
    if not math.isclose(left.packet.curvature_K, right.packet.curvature_K, rel_tol=0.0, abs_tol=1.0e-15):
        raise ValueError("cross-spectrum packets must share the same curvature_K")
    if not math.isclose(left.shell_weight, right.shell_weight, rel_tol=0.0, abs_tol=1.0e-15):
        raise ValueError("cross-spectrum packets must share the same shell weight")


def assemble_closed_s3_angular_power_spectrum(
    left_packets: tuple[WeightedClosedS3TransferPacket, ...] | list[WeightedClosedS3TransferPacket],
    *,
    right_packets: tuple[WeightedClosedS3TransferPacket, ...] | list[WeightedClosedS3TransferPacket] | None = None,
    observable_pair: str | None = None,
) -> ClosedAngularPowerSpectrum:
    """Assemble `C_l` from supplied transfer packets and explicit shell weights."""

    left_t = tuple(left_packets)
    if not left_t:
        raise ValueError("left_packets must not be empty")
    right_t = left_t if right_packets is None else tuple(right_packets)
    if len(left_t) != len(right_t):
        raise ValueError("left_packets and right_packets must have the same length")
    for left, right in zip(left_t, right_t):
        _match_packet_pair(left, right)

    ell_union = sorted({ell for packet in left_t for ell in packet.packet.ell_values} | {ell for packet in right_t for ell in packet.packet.ell_values})
    c_ell = []
    for ell in ell_union:
        total = 0.0 + 0.0j
        for left, right in zip(left_t, right_t):
            total += left.shell_weight * left.packet.delta_at(ell) * right.packet.delta_at(ell).conjugate()
        if abs(total.imag) > 1.0e-12:
            raise ValueError("assembled C_l must be real on the supplied packet family")
        c_ell.append(total.real)

    pair_label = observable_pair
    if pair_label is None:
        pair_label = f"{left_t[0].packet.observable.value}{right_t[0].packet.observable.value}"
    return ClosedAngularPowerSpectrum(
        observable_pair=pair_label,
        ell_values=tuple(ell_union),
        c_ell=tuple(c_ell),
        claim_status="derived / scoped explicit shell assembly",
        provenance_node_ids=("paper28.closed_s3_shell_power", "paper32.closed_s3_solver_spec"),
        scope_boundary=(
            "Angular-spectrum assembly from supplied closed transfer packets and supplied shell weights only.",
            "Does not derive the exact hierarchy-to-transfer projector or the physical IO source-side shell covariance law.",
        ),
    )


__all__ = [
    "ClosedAngularPowerSpectrum",
    "ClosedS3LineOfSightHistory",
    "ClosedS3LineOfSightProjector",
    "ClosedS3TransferPacket",
    "OpenClosedS3LineOfSightOperator",
    "TransferObservable",
    "WeightedClosedS3TransferPacket",
    "assemble_closed_s3_angular_power_spectrum",
    "build_closed_s3_los_history",
    "build_closed_s3_transfer_packet",
    "project_closed_s3_line_of_sight",
    "weight_closed_s3_transfer_packet",
]
