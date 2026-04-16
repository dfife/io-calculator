"""Theorem-grade closed-`S^3` mode infrastructure for Phase 3.

This module implements only the discrete spatial carrier that is already closed
by the paper stack:

- `derived / scoped`: the scalar / vector / tensor harmonic ladders on `S^3`
- `derived / scoped`: the closed-universe `q` relation
  `q^2 = k^2 + K(1+m)`
- `derived / scoped`: the closed transfer support rule `ell < nu = q / sqrt(K)`

What this module does not do:

- solve the perturbation hierarchy
- choose a source normalization
- invent a full `R` slot for the hierarchy
- pretend that the exact perturbation operator is already closed
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum


class S3Channel(str, Enum):
    """The three spatial perturbation channels on the closed `S^3` carrier."""

    SCALAR = "scalar"
    VECTOR = "vector"
    TENSOR = "tensor"


@dataclass(frozen=True)
class S3ModeSpectrum:
    """One discrete `S^3` harmonic mode with theorem-grade metadata.

    The object is intentionally descriptive rather than dynamic. It packages the
    carrier formulas already fixed by Papers 22, 23, and 32, together with the
    scope boundary that this is only the spatial/harmonic grammar.
    """

    channel: S3Channel
    n: int
    radius: float
    bundle_spin: int
    j_min: int
    j_max: int
    multiplicity: int
    primary_spatial_operator: str
    primary_spatial_eigenvalue: float
    shifted_scalar_operator: float | None
    rough_laplacian_eigenvalue: float | None
    lichnerowicz_eigenvalue: float | None
    physical_role: str
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]

    @property
    def diagonal_spin_range(self) -> tuple[int, int]:
        """Return the allowed diagonal-spin interval `(J_min, J_max)`."""

        return (self.j_min, self.j_max)


def _validate_radius(radius: float) -> float:
    """Require a positive `S^3` radius."""

    radius = float(radius)
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("radius must be a positive finite number")
    return radius


def _validate_scalar_n(n: int) -> int:
    """Allow all scalar shell labels, including background/gauge carriers."""

    n = int(n)
    if n < 0:
        raise ValueError("scalar n must satisfy n >= 0")
    return n


def _validate_vector_n(n: int) -> int:
    """Vector/coexact 1-form modes begin at `n >= 1`."""

    n = int(n)
    if n < 1:
        raise ValueError("vector n must satisfy n >= 1")
    return n


def _validate_tensor_n(n: int) -> int:
    """TT tensor modes begin at `n >= 2`."""

    n = int(n)
    if n < 2:
        raise ValueError("tensor n must satisfy n >= 2")
    return n


def scalar_mode(n: int, *, radius: float = 1.0) -> S3ModeSpectrum:
    """Return the theorem-grade scalar harmonic carrier on `S^3`.

    Paper 22 fixes the spatial scalar branch with
    `lambda_n = n(n+2)/a^2`, multiplicity `(n+1)^2`, and diagonal-spin support
    `J = 0..n`. Paper 23 sharpens the scalar perturbation operator to
    `lambda_n - 3 = (n-1)(n+3)` and classifies:

    - `n = 0`: homogeneous background renormalization
    - `n = 1`: pure-gauge scalar dipole / conformal-Killing sector
    - `n >= 2`: physical inhomogeneous scalar modes
    """

    n = _validate_scalar_n(n)
    radius = _validate_radius(radius)
    hodge = n * (n + 2) / radius**2
    if n == 0:
        role = "background"
    elif n == 1:
        role = "gauge"
    else:
        role = "physical"
    return S3ModeSpectrum(
        channel=S3Channel.SCALAR,
        n=n,
        radius=radius,
        bundle_spin=0,
        j_min=0,
        j_max=n,
        multiplicity=(n + 1) ** 2,
        primary_spatial_operator="scalar_hodge_laplacian",
        primary_spatial_eigenvalue=hodge,
        shifted_scalar_operator=(n - 1) * (n + 3) / radius**2,
        rough_laplacian_eigenvalue=None,
        lichnerowicz_eigenvalue=None,
        physical_role=role,
        claim_status="derived / scoped",
        provenance_node_ids=(
            "paper22.spatial_mode_ladder",
            "paper23.closed_scalar_operator",
        ),
        scope_boundary=(
            "Spatial scalar carrier only; not the full scalar metric-plus-fluid hierarchy.",
            "The shifted scalar operator is the closed-shell replacement `lambda_n - 3`, not a complete source/acoustic closure.",
        ),
    )


def vector_mode(n: int, *, radius: float = 1.0) -> S3ModeSpectrum:
    """Return the coexact-vector harmonic carrier on `S^3`.

    Paper 22 fixes the vector branch with eigenvalue `(n+1)^2/a^2`,
    multiplicity `2 n (n+2)`, and diagonal-spin support `J = 1..n`.
    """

    n = _validate_vector_n(n)
    radius = _validate_radius(radius)
    return S3ModeSpectrum(
        channel=S3Channel.VECTOR,
        n=n,
        radius=radius,
        bundle_spin=1,
        j_min=1,
        j_max=n,
        multiplicity=2 * n * (n + 2),
        primary_spatial_operator="coexact_vector_hodge_laplacian",
        primary_spatial_eigenvalue=(n + 1) ** 2 / radius**2,
        shifted_scalar_operator=None,
        rough_laplacian_eigenvalue=None,
        lichnerowicz_eigenvalue=None,
        physical_role="physical",
        claim_status="derived / scoped",
        provenance_node_ids=("paper22.spatial_mode_ladder",),
        scope_boundary=(
            "Spatial coexact-vector carrier only.",
            "No vector dynamical source law is supplied here.",
        ),
    )


def tensor_mode(n: int, *, radius: float = 1.0) -> S3ModeSpectrum:
    """Return the TT tensor harmonic carrier on `S^3`.

    Paper 22 fixes the TT branch with multiplicity `2(n-1)(n+3)`,
    rough-Laplacian eigenvalue `(n(n+2)-2)/a^2`, Lichnerowicz eigenvalue
    `(n(n+2)+4)/a^2`, and diagonal-spin support `J = 2..n`.
    """

    n = _validate_tensor_n(n)
    radius = _validate_radius(radius)
    return S3ModeSpectrum(
        channel=S3Channel.TENSOR,
        n=n,
        radius=radius,
        bundle_spin=2,
        j_min=2,
        j_max=n,
        multiplicity=2 * (n - 1) * (n + 3),
        primary_spatial_operator="tt_rough_laplacian",
        primary_spatial_eigenvalue=(n * (n + 2) - 2) / radius**2,
        shifted_scalar_operator=None,
        rough_laplacian_eigenvalue=(n * (n + 2) - 2) / radius**2,
        lichnerowicz_eigenvalue=(n * (n + 2) + 4) / radius**2,
        physical_role="physical",
        claim_status="derived / scoped",
        provenance_node_ids=("paper22.spatial_mode_ladder",),
        scope_boundary=(
            "Spatial TT carrier only.",
            "No tensor transfer/source normalization theorem is supplied here.",
        ),
    )


def closed_q_squared(k: float, curvature_K: float, channel: S3Channel) -> float:
    """Return the closed-universe shell relation `q^2 = k^2 + K(1+m)`.

    Here `K > 0` is the positive curvature parameter of the closed transfer
    layer, and `m = 0,1,2` for scalar/vector/tensor modes respectively.
    """

    k = float(k)
    curvature_K = float(curvature_K)
    if not math.isfinite(k):
        raise ValueError("k must be finite")
    if not math.isfinite(curvature_K) or curvature_K <= 0.0:
        raise ValueError("curvature_K must be positive and finite")
    m = {
        S3Channel.SCALAR: 0,
        S3Channel.VECTOR: 1,
        S3Channel.TENSOR: 2,
    }[channel]
    return k * k + curvature_K * (1 + m)


def closed_k_squared_from_q(q: float, curvature_K: float, channel: S3Channel) -> float:
    """Invert the closed-shell relation back to `k^2`.

    The function rejects shell labels below the geometric curvature floor.
    """

    q = float(q)
    curvature_K = float(curvature_K)
    if not math.isfinite(q) or q < 0.0:
        raise ValueError("q must be finite and non-negative")
    if not math.isfinite(curvature_K) or curvature_K <= 0.0:
        raise ValueError("curvature_K must be positive and finite")
    m = {
        S3Channel.SCALAR: 0,
        S3Channel.VECTOR: 1,
        S3Channel.TENSOR: 2,
    }[channel]
    k_squared = q * q - curvature_K * (1 + m)
    if k_squared < -1.0e-15:
        raise ValueError("q is below the closed-space curvature floor for this channel")
    return max(0.0, k_squared)


def hyperspherical_nu(q: float, curvature_K: float) -> float:
    """Return the closed transfer support label `nu = q / sqrt(K)`."""

    q = float(q)
    curvature_K = float(curvature_K)
    if not math.isfinite(q) or q < 0.0:
        raise ValueError("q must be finite and non-negative")
    if not math.isfinite(curvature_K) or curvature_K <= 0.0:
        raise ValueError("curvature_K must be positive and finite")
    return q / math.sqrt(curvature_K)


def closed_supports_ell(ell: int, q: float, curvature_K: float) -> bool:
    """Return whether the closed transfer basis allows this multipole.

    Paper 32 audits the standard closed transfer support rule `ell < nu`.
    """

    ell = int(ell)
    if ell < 0:
        raise ValueError("ell must be non-negative")
    return float(ell) < hyperspherical_nu(q, curvature_K)
