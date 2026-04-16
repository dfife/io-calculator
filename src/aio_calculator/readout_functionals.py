"""Readout functionals on supplied closed-geometry spectra and source fields.

This module implements only the readout objects already admitted by the current
stack:

- `derived / scoped`: the null-family acoustic readout field
  `omega_hat(eta) = (ev_eta tensor C_n) P_src(Phi)` can be carried explicitly
- `derived / scoped`: the background acoustic estimator class
  `E_rs = integral c_s(eta) R_hist^ac(omega_hat(eta)) d eta`
  can be evaluated as an explicit weighted sum once the reduced history and
  weights are supplied
- `derived / scoped`: a peak functional may be read directly from a supplied
  discrete `C_l` window

What remains open is the identification

`A_peak -> theta_peak`.

This module keeps that seam explicit and raising.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Protocol

from .los_transfer import ClosedAngularPowerSpectrum
from .recombination import OpenTheoremBoundaryError


def _float_tuple(values: tuple[float, ...] | list[float], *, name: str) -> tuple[float, ...]:
    """Validate a finite non-empty real tuple."""

    coerced = tuple(float(value) for value in values)
    if not coerced:
        raise ValueError(f"{name} must not be empty")
    if any(not math.isfinite(value) for value in coerced):
        raise ValueError(f"{name} must contain only finite values")
    return coerced


@dataclass(frozen=True)
class NullFamilyAcousticReadoutField:
    """An explicit sampled carrier for `omega_hat(eta)` on the null family."""

    eta: tuple[float, ...]
    omega_hat: tuple[float, ...]
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]

    def __post_init__(self) -> None:
        if len(self.eta) != len(self.omega_hat):
            raise ValueError("eta and omega_hat must have the same length")
        if any(b <= a for a, b in zip(self.eta, self.eta[1:])):
            raise ValueError("eta must be strictly increasing")


@dataclass(frozen=True)
class BackgroundAcousticEstimator:
    """A supplied-weight evaluation of the null-family acoustic estimator class."""

    value: float
    eta: tuple[float, ...]
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


@dataclass(frozen=True)
class PeakFunctionalResult:
    """A peak functional read directly from a supplied discrete `C_l` window."""

    observable_pair: str
    ell_min: int
    ell_max: int
    ell_peak: int
    peak_value: float
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


class PeakReadoutIdentificationOperator(Protocol):
    """Protocol for the still-open `A_peak -> theta_peak` identification theorem."""

    def derive_theta_peak(self, peak: PeakFunctionalResult, **kwargs: Any) -> Any:
        """Turn a peak functional into a numeric acoustic-angle readout."""


def build_null_family_acoustic_readout_field(
    eta: tuple[float, ...] | list[float],
    omega_hat: tuple[float, ...] | list[float],
) -> NullFamilyAcousticReadoutField:
    """Package a sampled null-family readout field `omega_hat(eta)`."""

    return NullFamilyAcousticReadoutField(
        eta=_float_tuple(eta, name="eta"),
        omega_hat=_float_tuple(omega_hat, name="omega_hat"),
        claim_status="derived / scoped",
        provenance_node_ids=("calculator.null_family_acoustic_readout",),
        scope_boundary=(
            "Explicit null-family readout field only.",
            "Does not by itself determine the exact acoustic endpoint or the physical peak-position angle.",
        ),
    )


def evaluate_background_acoustic_estimator(
    field: NullFamilyAcousticReadoutField,
    *,
    sound_speed: tuple[float, ...] | list[float],
    reduced_history: tuple[float, ...] | list[float],
    quadrature_weights: tuple[float, ...] | list[float],
) -> BackgroundAcousticEstimator:
    """Evaluate the estimator class from explicit reduced-history data and weights.

    This function performs only the explicit weighted sum corresponding to a
    caller-supplied discretization of

    `E_rs = integral c_s(eta) R_hist^ac(omega_hat(eta)) d eta`.

    It does not invent the reduction operator or the quadrature rule.
    """

    sound_speed_t = _float_tuple(sound_speed, name="sound_speed")
    reduced_history_t = _float_tuple(reduced_history, name="reduced_history")
    quadrature_weights_t = _float_tuple(quadrature_weights, name="quadrature_weights")
    size = len(field.eta)
    if len(sound_speed_t) != size or len(reduced_history_t) != size or len(quadrature_weights_t) != size:
        raise ValueError("sound_speed, reduced_history, and quadrature_weights must match the field length")
    value = sum(
        cs * reduced * weight
        for cs, reduced, weight in zip(sound_speed_t, reduced_history_t, quadrature_weights_t)
    )
    return BackgroundAcousticEstimator(
        value=value,
        eta=field.eta,
        claim_status="derived / scoped explicit weighted evaluation",
        provenance_node_ids=("paper29.sound_speed_selector", "calculator.null_family_acoustic_readout"),
        scope_boundary=(
            "Explicit weighted evaluation of the theorem-grade estimator class only.",
            "Does not derive the exact endpoint/phase scalar or identify the resulting estimator numerically with theta_peak.",
        ),
    )


def evaluate_discrete_peak_functional(
    spectrum: ClosedAngularPowerSpectrum,
    *,
    ell_min: int,
    ell_max: int,
) -> PeakFunctionalResult:
    """Read a discrete peak functional from a supplied `C_l` window."""

    ell_min = int(ell_min)
    ell_max = int(ell_max)
    if ell_min < 0 or ell_max < ell_min:
        raise ValueError("peak window must satisfy 0 <= ell_min <= ell_max")
    candidates = [
        (ell, value)
        for ell, value in zip(spectrum.ell_values, spectrum.c_ell)
        if ell_min <= ell <= ell_max
    ]
    if not candidates:
        raise ValueError("peak window contains no supplied C_l samples")
    ell_peak, peak_value = max(candidates, key=lambda item: item[1])
    return PeakFunctionalResult(
        observable_pair=spectrum.observable_pair,
        ell_min=ell_min,
        ell_max=ell_max,
        ell_peak=ell_peak,
        peak_value=peak_value,
        claim_status="derived / scoped discrete peak readout",
        provenance_node_ids=("calculator.peak_functional_separation",),
        scope_boundary=(
            "Discrete peak functional on supplied C_l samples only.",
            "No theorem-grade identification from this peak functional to numeric theta_peak is supplied here.",
        ),
    )


class OpenPeakReadoutIdentificationOperator:
    """Explicit placeholder for the still-open peak-to-angle identification."""

    def derive_theta_peak(self, peak: PeakFunctionalResult, **kwargs: Any) -> Any:
        """Fail honestly until the exact peak/readout identification theorem exists."""

        raise OpenTheoremBoundaryError(
            "The peak functional may be read from supplied C_l data, but the exact "
            "identification `A_peak -> theta_peak` remains open. "
            f"The supplied peak was ell_peak={peak.ell_peak} on {peak.observable_pair}, "
            "which is not enough by itself to derive a theorem-grade numeric acoustic angle."
        )


def derive_theta_peak_from_peak_functional(
    peak: PeakFunctionalResult,
    *,
    operator: PeakReadoutIdentificationOperator | None = None,
    **kwargs: Any,
) -> Any:
    """Apply the exact peak/readout identification if and only if it exists."""

    active_operator = OpenPeakReadoutIdentificationOperator() if operator is None else operator
    return active_operator.derive_theta_peak(peak, **kwargs)


__all__ = [
    "BackgroundAcousticEstimator",
    "NullFamilyAcousticReadoutField",
    "OpenPeakReadoutIdentificationOperator",
    "PeakFunctionalResult",
    "PeakReadoutIdentificationOperator",
    "build_null_family_acoustic_readout_field",
    "derive_theta_peak_from_peak_functional",
    "evaluate_background_acoustic_estimator",
    "evaluate_discrete_peak_functional",
]
