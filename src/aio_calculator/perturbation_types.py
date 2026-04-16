"""Typed perturbation carriers and explicit open seams for Phase 3.

This module packages the theorem-grade perturbation architecture already fixed
by Paper 32:

- `derived / scoped`: the solver lives on a closed-`S^3` typed tuple
- `derived / scoped`: baryon use is typed rather than one-slot
- `derived / scoped`: the remaining perturbation debt is exactly two open
  operators, not an unspecified patch space

The module deliberately makes the open seams first-class interfaces. Any caller
that tries to use them without a later theorem-grade implementation gets an
explicit boundary error.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .recombination import OpenTheoremBoundaryError, Stage2History
from .s3_modes import S3ModeSpectrum


@dataclass(frozen=True)
class OpenPerturbationSeam:
    """A live theorem boundary inside the Phase 3 perturbation stack."""

    seam_id: str
    label: str
    claim_status: str
    statement: str
    required_inputs: tuple[str, ...]
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


@dataclass(frozen=True)
class TypedBaryonAssignment:
    """The theorem-grade baryon-slot split carried into perturbation work."""

    chemistry: str
    primitive_local_opacity: str
    reduced_visibility_readout: str
    clustering_slot: str
    baryon_loading_R: str
    scalar_metric_source: str
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


@dataclass(frozen=True)
class ClosedS3SolverSpecification:
    """The typed closed-`S^3` solver grammar fixed by Paper 32."""

    tuple_label: str
    q_ladder_formula: str
    source_block_formula: str
    stage2_state_formula: str
    thermodynamics_fields: tuple[str, ...]
    perturbation_block: str
    line_of_sight_block: str
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    baryon_assignment: TypedBaryonAssignment
    open_seams: tuple[OpenPerturbationSeam, ...]
    scope_boundary: tuple[str, ...]


@dataclass(frozen=True)
class PerturbationBlockInputs:
    """Typed inputs presented to the still-open perturbation/source operator."""

    mode: S3ModeSpectrum
    history: Stage2History
    baryons: TypedBaryonAssignment
    source_block_formula: str
    thermodynamics_fields: tuple[str, ...]
    claim_status: str
    provenance_node_ids: tuple[str, ...]
    scope_boundary: tuple[str, ...]


class ExactStage2DynamicNetworkOperator(Protocol):
    """Protocol for the still-open exact Stage-2 dynamic-network operator."""

    def solve_history(self, z_obs: tuple[float, ...] | list[float], **kwargs: Any) -> Stage2History:
        """Return the exact Stage-2 history on the requested redshift grid."""


class TypedSourceAcousticOperator(Protocol):
    """Protocol for the still-open final perturbation/source operator."""

    def apply(self, inputs: PerturbationBlockInputs, **kwargs: Any) -> Any:
        """Apply the exact typed source/acoustic operator to one perturbation input packet."""


def active_typed_baryon_assignment() -> TypedBaryonAssignment:
    """Return the live Paper 32 perturbation-era baryon-slot split.

    This object is theorem-grade because it stops exactly where the paper stack
    stops:

    - chemistry: `omega_b,geom`
    - primitive local opacity: `omega_b,geom`
    - reduced visibility/readout: `omega_b,eff`
    - clustering slot remains the named published slot `omega_b,clustering`
    - baryon loading `R`: closed only as a typed local operator, not a single
      hierarchy-wide slot collapse
    - scalar metric source: open
    """

    return TypedBaryonAssignment(
        chemistry="omega_b,geom",
        primitive_local_opacity="omega_b,geom",
        reduced_visibility_readout="omega_b,eff",
        clustering_slot="omega_b,clustering",
        baryon_loading_R=(
            "full hierarchy operator: "
            "R_local(omega_b,geom), "
            "Gamma_bgamma = R_local * thomson_drag_rate, "
            "c_bgamma^2 = 1/[3(1+R_local)], "
            "M_bgamma = 1+R_local, "
            "L_odd/even = R_local/(1+R_local), "
            "D_silk = D_heat + D_visc"
        ),
        scalar_metric_source="open",
        claim_status="derived / scoped",
        provenance_node_ids=(
            "paper32.closed_s3_solver_spec",
            "paper32.typed_baryon_slot_spec",
            "local.typed_r_operator",
            "local.typed_r_site_uniqueness",
        ),
        scope_boundary=(
            "This split preserves the published three-slot architecture while keeping role assignments explicit.",
            "The primitive local `R` leg is closed only through the full site-wise hierarchy operator built from `omega_b,geom` plus the Thomson tuple.",
            "No theorem-grade one-slot collapse of the observed hierarchy onto one `R` branch is licensed.",
            "The named clustering slot exists, but the scalar metric source is not licensed to collapse to `omega_b,clustering`.",
        ),
    )


def exact_stage2_dynamic_network_seam() -> OpenPerturbationSeam:
    """Return the live Stage-2 dynamic-network seam named by Paper 32."""

    return OpenPerturbationSeam(
        seam_id="exact_stage2_dynamic_network_operator",
        label="Exact Stage-2 Dynamic-network Operator",
        claim_status="open",
        statement=(
            "The exact Stage-2 history state is fixed as "
            "`Y_rec = (x_e, T_m, D_-(q;z), L_-(z))`, but the final explicit "
            "dynamic-network renormalization law acting on that state remains open."
        ),
        required_inputs=(
            "Y_rec(z) = (x_e(z), T_m(z), D_-(q;z), L_-(z))",
            "transported local atomic/radiative-transfer law",
            "branch-consistent local background history",
        ),
        provenance_node_ids=("paper31.stage2_markov_state", "paper32.closed_s3_solver_spec"),
        scope_boundary=(
            "The state grammar is fixed; the exact renormalization operator is not.",
            "No finite-dimensional scalar compression is licensed as a replacement.",
        ),
    )


def typed_source_acoustic_operator_seam() -> OpenPerturbationSeam:
    """Return the live perturbation/source seam named by Papers 32 and 37."""

    return OpenPerturbationSeam(
        seam_id="typed_source_acoustic_operator",
        label="Typed Source/Acoustic Operator",
        claim_status="open",
        statement=(
            "The final closed-`S^3` source/acoustic operator remains open. It is "
            "not licensed to collapse to a post-solve source patch, a metric-only "
            "factor, a perturbation-only multiplicative Thomson family, or a silent "
            "one-slot `R` reassignment. The primitive local `R` leg is closed only "
            "through the separate typed local operator."
        ),
        required_inputs=(
            "closed-S^3 mode label and hyperspherical support",
            "typed baryon assignment",
            "exact Stage-2 history state",
            "coupled Thomson-history tuple",
        ),
        provenance_node_ids=(
            "paper32.closed_s3_solver_spec",
            "calculator.thomson_history_realization",
        ),
        scope_boundary=(
            "This seam names the exact remaining perturbation/source debt.",
            "Any future closure must respect the typed carrier and coupled Thomson-history tuple.",
        ),
    )


def closed_s3_solver_specification() -> ClosedS3SolverSpecification:
    """Return the minimal exact solver grammar admitted by the current stack."""

    baryons = active_typed_baryon_assignment()
    return ClosedS3SolverSpecification(
        tuple_label="S_IO",
        q_ladder_formula="q^2 = k^2 + K(1+m)",
        source_block_formula="P_src = B_+ o U_coex o T_field",
        stage2_state_formula="Y_rec = (x_e, T_m, D_-(q;z), L_-(z))",
        thermodynamics_fields=(
            "x_e",
            "dot{kappa}",
            "exp(-kappa)",
            "g",
            "dg",
            "ddg",
            "kappa_b",
        ),
        perturbation_block="E_pert^S3 : (P_src, K_therm) -> y^(md,ic,q)",
        line_of_sight_block="L_S3 with hyperspherical interpolation and closed ell < nu support",
        claim_status="derived / scoped",
        provenance_node_ids=("paper32.closed_s3_solver_spec",),
        baryon_assignment=baryons,
        open_seams=(
            exact_stage2_dynamic_network_seam(),
            typed_source_acoustic_operator_seam(),
        ),
        scope_boundary=(
            "This is a solver specification theorem, not a full perturbation closure.",
            "The remaining perturbation debt is exactly the named open seams, not an arbitrary patch family.",
        ),
    )


def make_perturbation_block_inputs(
    mode: S3ModeSpectrum,
    history: Stage2History,
    *,
    baryons: TypedBaryonAssignment | None = None,
) -> PerturbationBlockInputs:
    """Package one typed input object for the still-open perturbation block."""

    return PerturbationBlockInputs(
        mode=mode,
        history=history,
        baryons=active_typed_baryon_assignment() if baryons is None else baryons,
        source_block_formula="P_src = B_+ o U_coex o T_field",
        thermodynamics_fields=("x_e", "dot{kappa}", "exp(-kappa)", "g", "dg", "ddg", "kappa_b"),
        claim_status="derived / scoped input carrier",
        provenance_node_ids=("paper32.closed_s3_solver_spec",),
        scope_boundary=(
            "Typed perturbation input carrier only.",
            "No exact source/acoustic evaluation is performed here.",
        ),
    )


class OpenTypedSourceAcousticOperator:
    """Explicit placeholder for the still-open perturbation/source operator."""

    seam: OpenPerturbationSeam = typed_source_acoustic_operator_seam()

    def apply(self, inputs: PerturbationBlockInputs, **kwargs: Any) -> Any:
        """Fail honestly until the exact theorem-grade operator exists."""

        raise OpenTheoremBoundaryError(
            "The final typed source/acoustic operator on the closed-S^3 "
            "perturbation hierarchy remains open. Inputs were accepted with "
            f"mode n={inputs.mode.n} on the {inputs.mode.channel.value} channel, "
            "but no theorem-grade operator is available to apply them yet."
        )


class OpenExactStage2DynamicNetworkOperator:
    """Explicit placeholder for the still-open Stage-2 dynamic-network operator."""

    seam: OpenPerturbationSeam = exact_stage2_dynamic_network_seam()

    def solve_history(
        self, z_obs: tuple[float, ...] | list[float], **kwargs: Any
    ) -> Stage2History:
        """Fail honestly until the exact Stage-2 operator is derived."""

        raise OpenTheoremBoundaryError(
            "The universal IO-native Stage-2 dynamic-network operator remains open. "
            "A separate conditional inherited-FULL builder exists for the active IO local "
            "background, but no universal theorem-grade operator is available by default "
            "to produce `Y_rec = (x_e, T_m, D_-(q;z), L_-(z))` from the requested redshift grid."
        )
