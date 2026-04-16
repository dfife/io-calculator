"""Theorem-grade source/readout block on the active IO scalar-source sector.

This module implements only the source-side objects that the current paper stack
already closes:

- `derived / scoped`: the coexact DtN shell law `sigma_ell = (ell+1) / r_s`
- `derived / scoped`: the logarithmic generator `Y_ell = log(ell+1)`
- `derived / scoped`: the modular-DtN transfer
  `T_field = exp[-(K_g tensor log(r_s Lambda_DtN^coex)) / (2x)]`
- `derived / scoped`: the quadratic descendant
  `R_cov = T_field^* T_field`
- `derived / scoped`: the repaired plus-branch source window on the affine
  odd-shell bridge image
  `W_N^(+) = ((N+1)/(N_p+1))^(-K_gauge/x)`
- `derived / scoped`: the native source amplitude
  `A_s = 2.0072459972737347e-9`

What this module does not do:

- invent a source-to-phase identification theorem
- pretend the source block closes the perturbation hierarchy
- supply a hidden CLASS-style primordial-spectrum default
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .constants import ACTIVE_BRANCH, ACTIVE_IO_CONSTANTS, IO_SCHWARZSCHILD_RADIUS_M


ACTIVE_SOURCE_PIVOT_SHELL = 711


def _validate_shell_index(shell: int, *, name: str, minimum: int) -> int:
    """Require a finite integral shell label above the stated floor."""

    shell = int(shell)
    if shell < minimum:
        raise ValueError(f"{name} must satisfy {name} >= {minimum}")
    return shell


def _validate_positive_radius(radius_m: float) -> float:
    """Require a positive source radius in meters."""

    radius_m = float(radius_m)
    if not math.isfinite(radius_m) or radius_m <= 0.0:
        raise ValueError("source_radius_m must be positive and finite")
    return radius_m


def active_plus_branch_supports_shell(shell_n: int) -> bool:
    """Return whether the repaired active source theorem supports scalar shell `N`.

    Paper 32 hidden-identification repair puts the active source window on the
    affine odd-shell bridge image:

    - boundary lift: `n = 2 ell`
    - scalar bridge: `N = n - 1` or `N = n + 1`

    so the source-supported scalar shells are the odd shells `N >= 3`.
    """

    shell_n = int(shell_n)
    return shell_n >= 3 and shell_n % 2 == 1


@dataclass(frozen=True)
class CoexactDtNShell:
    """One theorem-grade shell on the coexact DtN source carrier."""

    ell: int
    source_radius_m: float
    sigma_ell_m_inv: float
    logarithmic_generator: float
    field_transfer_factor: float
    covariance_transfer_factor: float
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


@dataclass(frozen=True)
class SourceBlockSpecification:
    """The closed source/readout block carried into Phase 4."""

    source_block_formula: str
    field_transfer_formula: str
    covariance_formula: str
    plus_branch_window_formula: str
    accessible_line_rescaling_formula: str
    scalar_amplitude_formula: str
    active_pivot_shell: int
    accessible_line_rescaling: float
    native_scalar_amplitude: float
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


def coexact_dtn_eigenvalue(ell: int, *, source_radius_m: float = IO_SCHWARZSCHILD_RADIUS_M) -> float:
    """Return the coexact DtN eigenvalue `sigma_ell = (ell+1) / r_s`.

    The coexact `S^2` one-form carrier begins at `ell >= 1`.
    """

    ell = _validate_shell_index(ell, name="ell", minimum=1)
    source_radius_m = _validate_positive_radius(source_radius_m)
    return (ell + 1.0) / source_radius_m


def dtn_logarithmic_generator(ell: int) -> float:
    """Return the dimensionless DtN generator `Y_ell = log(ell+1)`."""

    ell = _validate_shell_index(ell, name="ell", minimum=1)
    return math.log(ell + 1.0)


def modular_dtn_field_transfer_factor(ell: int) -> float:
    """Return the source-shell field factor `(ell+1)^(-K_gauge/(2x))`."""

    y_shell = dtn_logarithmic_generator(ell)
    exponent = -ACTIVE_IO_CONSTANTS.K_gauge * y_shell / (2.0 * ACTIVE_IO_CONSTANTS.x)
    return math.exp(exponent)


def modular_dtn_covariance_transfer_factor(ell: int) -> float:
    """Return the quadratic source-shell factor `(ell+1)^(-K_gauge/x)`."""

    factor = modular_dtn_field_transfer_factor(ell)
    return factor * factor


def accessible_line_rescaling() -> float:
    """Return the one-cell observer readout factor `exp(-K_gauge / 2)`."""

    return math.exp(-0.5 * ACTIVE_IO_CONSTANTS.K_gauge)


def plus_branch_source_window(
    shell_n: int,
    *,
    pivot_shell: int = ACTIVE_SOURCE_PIVOT_SHELL,
) -> float:
    """Return the repaired plus-branch window on the affine odd-shell variable.

    Exact repaired formula:

    `W_N^(+) = ((N+1)/(N_p+1))^(-K_gauge/x)`

    Claim boundary:

    - the theorem-grade support is the odd-shell bridge image `N = 2 ell + 1`
    - this helper evaluates the affine law itself; callers that require strict
      source support should also check `active_plus_branch_supports_shell(N)`
    """

    shell_n = _validate_shell_index(shell_n, name="shell_n", minimum=2)
    pivot_shell = _validate_shell_index(pivot_shell, name="pivot_shell", minimum=2)
    return ((shell_n + 1.0) / (pivot_shell + 1.0)) ** (
        -ACTIVE_IO_CONSTANTS.K_gauge / ACTIVE_IO_CONSTANTS.x
    )


def native_scalar_amplitude() -> float:
    """Return the theorem-grade active-source scalar amplitude `A_s`.

    Formula:

    `A_s = (25/9) [gamma^2 / (1 + gamma^2)] [1 / sqrt(2)] [exp(4 pi sqrt(2)) - 1]^-1`
    """

    gamma = ACTIVE_IO_CONSTANTS.gamma_bi
    numerator = (25.0 / 9.0) * (gamma * gamma / (1.0 + gamma * gamma))
    denominator = math.sqrt(2.0) * (math.exp(4.0 * math.pi * math.sqrt(2.0)) - 1.0)
    return numerator / denominator


def coexact_dtn_shell(ell: int, *, source_radius_m: float = IO_SCHWARZSCHILD_RADIUS_M) -> CoexactDtNShell:
    """Package one theorem-grade coexact DtN shell."""

    return CoexactDtNShell(
        ell=_validate_shell_index(ell, name="ell", minimum=1),
        source_radius_m=_validate_positive_radius(source_radius_m),
        sigma_ell_m_inv=coexact_dtn_eigenvalue(ell, source_radius_m=source_radius_m),
        logarithmic_generator=dtn_logarithmic_generator(ell),
        field_transfer_factor=modular_dtn_field_transfer_factor(ell),
        covariance_transfer_factor=modular_dtn_covariance_transfer_factor(ell),
        claim_status="derived / scoped",
        provenance_node_ids=("paper32.modular_dtn_field_transfer",),
        scope_boundary=(
            "Active linear scalar-source sector only.",
            "Does not determine the downstream acoustic phase/readout operator.",
        ),
    )


def source_block_specification() -> SourceBlockSpecification:
    """Return the theorem-grade source/readout block specification."""

    return SourceBlockSpecification(
        source_block_formula="P_src = B_+ o U_coex o T_field",
        field_transfer_formula=(
            "T_field = exp[-(K_g tensor log(r_s Lambda_DtN^coex)) / (2x)]"
        ),
        covariance_formula=(
            "R_cov = T_field^* T_field = exp[-(K_g tensor log(r_s Lambda_DtN^coex)) / x]"
        ),
        plus_branch_window_formula="W_N^(+) = ((N+1) / (N_p+1))^(-K_gauge / x)",
        accessible_line_rescaling_formula="X_obs = exp(-K_gauge / 2) X_prim = f_Gamma^(1/2) X_prim",
        scalar_amplitude_formula=(
            "A_s = (25/9) [gamma^2 / (1 + gamma^2)] [1 / sqrt(2)] [exp(4 pi sqrt(2)) - 1]^-1"
        ),
        active_pivot_shell=ACTIVE_SOURCE_PIVOT_SHELL,
        accessible_line_rescaling=accessible_line_rescaling(),
        native_scalar_amplitude=native_scalar_amplitude(),
        claim_status="derived / scoped",
        provenance_node_ids=("paper32.modular_dtn_field_transfer",),
        scope_boundary=(
            "Active linear scalar-source block only.",
            "Exact source support lives on the repaired affine odd-shell plus branch.",
            "Does not close the exact Stage-2 dynamic-network operator, the closed-S^3 perturbation hierarchy, or the peak/readout identification theorem.",
        ),
    )


__all__ = [
    "ACTIVE_SOURCE_PIVOT_SHELL",
    "active_plus_branch_supports_shell",
    "CoexactDtNShell",
    "SourceBlockSpecification",
    "accessible_line_rescaling",
    "coexact_dtn_eigenvalue",
    "coexact_dtn_shell",
    "dtn_logarithmic_generator",
    "modular_dtn_covariance_transfer_factor",
    "modular_dtn_field_transfer_factor",
    "native_scalar_amplitude",
    "plus_branch_source_window",
    "source_block_specification",
]
