"""Provenance graph and explained-output surfaces for the calculator.

The calculator should publish numbers together with the authority chain that
licenses them. This module keeps that layer explicit instead of making every
intermediate arithmetic operation provenance-aware.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .constants import (
    ACTIVE_BRANCH,
    ACTIVE_IO_CONSTANTS,
    AUTHORITY_PATHS,
    MASTER_CLOCK_BARE_BRANCH,
    T_IO_REF_K,
)
from .model import CurvedBackgroundModel, late_eta_io
from .recombination import (
    free_electron_density_m3,
    hydrogen_number_density_m3,
    local_background_state,
    local_baryon_loading_R,
    local_scattering_to_expansion_ratio,
    local_sound_speed_m_s,
    optical_depth_gradient_per_redshift,
    primitive_local_kappa_prime,
    saha_equilibrium_xe,
)
from .theorem_theta_star import compute_active_branch_theta_star


LAB_PREMISES_PATH = AUTHORITY_PATHS["lab_premises"]
ACTIVE_BRANCH_THETA_STAR_ELL_PEAK = 220.47514473507064
OBSERVED_FIRST_TT_PEAK_ELL_REFERENCE = 220.0
PLANCK_FLAT_REFERENCE_THETA_MC_100 = 1.04090
PLANCK_CLOSED_REFERENCE_THETA_MC_100 = 1.04116
PLANCK_CLOSED_REFERENCE_OMEGA_K = -0.044
ACTIVE_BBN_DEUTERIUM_RATIO = 2.509e-5
ACTIVE_BBN_LI7_RATIO = 1.7500878203658553e-10
THEOREM_REFERENCE_NOTE = (
    "Supporting references only. The theorem text carried on this node is the "
    "calculator's self-contained public dictionary entry."
)
TT_FIRST_PEAK_APPROVED_STATUS = (
    "Conditional/scoped/verified TT first-peak support on the repaired "
    "active-branch canonical carrier (n_max = 501), with inherited-FULL "
    "Stage-2 history and equal-rate typed Thomson specialization."
)
TT_FIRST_PEAK_CANONICAL_EXACT_HISTORY_SAMPLES = 120
TT_FIRST_PEAK_CANONICAL_PREHISTORY_SAMPLES = 40
TT_FIRST_PEAK_CANONICAL_N_MAX = 501
TT_FIRST_PEAK_CANONICAL_SHELL_STEP = 1
TT_FIRST_PEAK_CANONICAL_ELL_PEAK = 224.0
TT_FIRST_PEAK_CANONICAL_C220_OVER_PEAK = 0.9938104102565932
TT_FIRST_PEAK_CANONICAL_C2_OVER_C30 = 1148.794609154744
TT_FIRST_PEAK_NEIGHBOR_N_MAX = 453
TT_FIRST_PEAK_NEIGHBOR_ELL_PEAK = 222.0
TT_FIRST_PEAK_NEIGHBOR_C220_OVER_PEAK = 0.976859196443279
TT_FIRST_PEAK_OPEN_FRONTIER = (
    "The surviving `n_max >= 601` shell-ceiling drift remains open: on tested "
    "history carriers the peak drifts upward to `ell_peak = 260` to `277`."
)


@dataclass(frozen=True)
class TheoremNode:
    """One premise, theorem, audit, or scoped authority in the calculator graph."""

    node_id: str
    kind: str
    label: str
    claim_status: str
    statement: str
    scope: str
    authority_paths: tuple[str, ...]
    depends_on: tuple[str, ...] = ()
    premises: tuple[str, ...] = ()
    proof_outline: tuple[str, ...] = ()
    scope_boundary: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    reference_note: str = THEOREM_REFERENCE_NOTE

    def as_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "kind": self.kind,
            "label": self.label,
            "claim_status": self.claim_status,
            "statement": self.statement,
            "scope": self.scope,
            "authority_paths": list(self.authority_paths),
            "depends_on": list(self.depends_on),
            "premises": list(self.premises),
            "proof_outline": list(self.proof_outline),
            "scope_boundary": list(self.scope_boundary),
            "notes": list(self.notes),
            "reference_note": self.reference_note,
        }


@dataclass(frozen=True)
class ObservableComparison:
    """Direct-observable comparison attached to an explained output."""

    label: str
    claim_status: str
    predicted_value: float
    observed_reference: float
    delta: float
    units: str
    note: str
    source_note: str
    source_links: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "claim_status": self.claim_status,
            "predicted_value": self.predicted_value,
            "observed_reference": self.observed_reference,
            "delta": self.delta,
            "units": self.units,
            "note": self.note,
            "source_note": self.source_note,
            "source_links": list(self.source_links),
        }


@dataclass(frozen=True)
class ExplainedValue:
    """Published value plus its scope, conditions, and provenance chain."""

    output_id: str
    label: str
    primary_key: str
    primary_value: float | str
    units: str | None
    claim_status: str
    provenance_status: str
    payload: dict[str, Any]
    scope_boundary: tuple[str, ...]
    conditional_on: tuple[str, ...]
    provenance_root_id: str
    chain_ids: tuple[str, ...]
    premise_ids: tuple[str, ...]
    supporting_node_ids: tuple[str, ...] = ()
    zero_fitted_parameters: bool = False
    non_claims: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    geometry_explanation: str | None = None
    comparison_context: dict[str, Any] = field(default_factory=dict)
    direct_observable_comparisons: tuple[ObservableComparison, ...] = ()

    def as_dict(
        self,
        *,
        nodes: dict[str, TheoremNode] | None = None,
        include_provenance: bool = True,
    ) -> dict[str, Any]:
        payload = dict(self.payload)
        payload.update(
            {
                "output_id": self.output_id,
                "label": self.label,
                "primary_key": self.primary_key,
                "primary_value": self.primary_value,
                "units": self.units,
                "claim_status": self.claim_status,
                "provenance_status": self.provenance_status,
                "zero_fitted_parameters": self.zero_fitted_parameters,
                "conditional_on_premises": list(self.conditional_on),
                "scope_boundary": list(self.scope_boundary),
                "non_claims": list(self.non_claims),
                "notes": list(self.notes),
            }
        )
        if self.geometry_explanation is not None:
            payload["geometry_explanation"] = self.geometry_explanation
        if self.comparison_context:
            payload["comparison_context"] = dict(self.comparison_context)
        if self.direct_observable_comparisons:
            comparisons = [row.as_dict() for row in self.direct_observable_comparisons]
            payload["direct_observable_comparisons"] = comparisons
            if len(comparisons) == 1:
                payload["direct_observable_comparison"] = comparisons[0]
        if include_provenance:
            graph = theorem_graph() if nodes is None else nodes
            payload["provenance"] = {
                "root_node": self.provenance_root_id,
                "premise_ids": list(self.premise_ids),
                "chain_ids": list(self.chain_ids),
                "supporting_node_ids": list(self.supporting_node_ids),
                "nodes": {node_id: graph[node_id].as_dict() for node_id in graph},
            }
        return payload


def theorem_graph() -> dict[str, TheoremNode]:
    """Return the current calculator theorem dictionary."""

    ag = str(LAB_PREMISES_PATH)
    theta_star = compute_active_branch_theta_star()
    rd_mpc = ACTIVE_BRANCH.rd_mpc
    eta_late = late_eta_io()
    bare_clock_age = CurvedBackgroundModel(branch=MASTER_CLOCK_BARE_BRANCH).age_today_gyr(
        n=4096
    )
    return {
        "premise.1": TheoremNode(
            node_id="premise.1",
            kind="premise",
            label="Premise 1",
            claim_status="conditional premise",
            statement=(
                "We live inside a black hole, and the CMB is the event horizon, "
                "with Hawking radiation falling inward and being observed from "
                "the interior."
            ),
            scope="Global working assumption for IO model-building in this lab.",
            authority_paths=(ag,),
            proof_outline=(
                "This node is declared as a working premise of the calculator rather than proved internally.",
                "Any downstream node that lists `premise.1` is explicitly conditional on this premise.",
            ),
            scope_boundary=(
                "Applies only as a lab working assumption for IO model-building.",
                "Not presented here as an empirically established theorem.",
            ),
        ),
        "premise.2": TheoremNode(
            node_id="premise.2",
            kind="premise",
            label="Premise 2",
            claim_status="conditional premise",
            statement=(
                "The physics inside our black hole are the same as the physics "
                "outside our black hole."
            ),
            scope="Global working assumption for IO model-building in this lab.",
            authority_paths=(ag,),
            proof_outline=(
                "This node is declared as a working premise of the calculator rather than proved internally.",
                "Any downstream node that lists `premise.2` is explicitly conditional on this premise.",
            ),
            scope_boundary=(
                "Applies only as a lab working assumption for IO model-building.",
                "Not presented here as an empirically established theorem.",
            ),
        ),
        "paper12.baryon_dictionary_fraction": TheoremNode(
            node_id="paper12.baryon_dictionary_fraction",
            kind="theorem",
            label="Paper 12 Baryon Dictionary Fraction Theorem",
            claim_status="derived / scoped",
            statement=(
                "The Baryon Dictionary Principle fixes the framework baryon "
                "inventory fraction to "
                f"`f_b = 2 gamma_BI / x = {ACTIVE_IO_CONSTANTS.f_b:.15f}` "
                "on the standard minimal-coupling matter class."
            ),
            scope="Framework baryon inventory fraction before observable-class slot transport.",
            authority_paths=(str(AUTHORITY_PATHS["paper12_baryon_dictionary"]),),
            depends_on=("premise.1", "premise.2"),
            premises=(
                "`premise.1` and `premise.2` fix the IO horizon setting in which the baryon dictionary is posed.",
                "The baryon fraction is an inventory-class selection statement, not a late-time one-number density theorem for every observable.",
            ),
            proof_outline=(
                "Identify baryons as the dust subset coupled to the boundary gauge sector rather than as an arbitrary fitted matter fraction.",
                "Use the surviving line-scale exponent to select the `alpha = 1` branch of the geometric inventory map.",
                "Read off the exact inventory fraction `f_b = 2 gamma_BI / x` without introducing a fitted baryon parameter.",
            ),
            scope_boundary=(
                "Inventory fraction only.",
                "Does not by itself determine every observable-class baryon slot or the full perturbation-era hierarchy loading.",
            ),
        ),
        "paper17.gttp_thermal_readout": TheoremNode(
            node_id="paper17.gttp_thermal_readout",
            kind="theorem",
            label="Paper 17 GTTP Thermal Readout Theorem",
            claim_status="derived / scoped",
            statement=(
                "The observer thermal readout obeys "
                "`T_obs = T_IO x^K_gauge` with "
                f"`K_gauge = ln(1 + gamma_BI^2) = {ACTIVE_IO_CONSTANTS.K_gauge:.15f}`. "
                "On the carried active thermal slot "
                f"`T_IO = {T_IO_REF_K:.4f} K`, this gives "
                f"`T_CMB = {ACTIVE_BRANCH.T_cmb:.4f} K`."
            ),
            scope="Observer-side thermal transfer law on the IO active branch.",
            authority_paths=(str(AUTHORITY_PATHS["paper17_gttp"]),),
            depends_on=("premise.1", "premise.2"),
            premises=(
                "`premise.1` identifies the observed CMB with the interior horizon readout problem.",
                "`premise.2` licenses the local thermal transfer class used to promote GTTP to theorem grade.",
            ),
            proof_outline=(
                "Use KMS rigidity to fix exact Planck-form preservation under uniform frequency rescaling.",
                "Combine multiplicative horizon gauge data with additive transfer generators to force a logarithmic homomorphism.",
                "Fix the coefficient on the Schwarzschild `S^2` horizon and evaluate the resulting thermal map on the carried IO temperature slot.",
            ),
            scope_boundary=(
                "Thermal readout law only.",
                "Does not by itself determine every late-time background or perturbation observable on the active branch.",
            ),
        ),
        "paper21.branch_assignment": TheoremNode(
            node_id="paper21.branch_assignment",
            kind="theorem",
            label="Paper 21 TIO Branch Assignment",
            claim_status="derived / scoped",
            statement=(
                "The active calculator branch is the carried Paper 10 legacy "
                "projected branch used by the public runtime surface."
            ),
            scope="Calculator branch selection and carried active package.",
            authority_paths=(str(AUTHORITY_PATHS["paper21_tio_branch_assignment"]),),
            depends_on=("premise.1", "premise.2"),
            premises=(
                "`premise.1` and `premise.2` fix the IO setting in which a carried active branch is meaningful.",
                "The calculator publishes one carried active package rather than dynamically averaging over multiple branch candidates.",
            ),
            proof_outline=(
                "Read the carried runtime package selected by the Paper 21 branch-assignment result.",
                "Identify that public runtime package with the legacy Paper 10 projected branch used by the live calculator constants and derived outputs.",
                "Once this identification is fixed, all downstream calculator outputs inherit one branch label instead of refitting branch choice per observable.",
            ),
            scope_boundary=(
                "Applies only to the calculator's carried active package.",
                "Does not assert uniqueness of the branch outside the published runtime surface.",
            ),
        ),
        "paper22.spatial_mode_ladder": TheoremNode(
            node_id="paper22.spatial_mode_ladder",
            kind="theorem",
            label="Paper 22 Spatial Mode Ladder",
            claim_status="derived / scoped",
            statement=(
                "The closed `S^3` spatial carrier decomposes into scalar, vector, "
                "and TT tensor ladders with "
                "`lambda_n^(S) = n(n+2) / a^2`, "
                "`lambda_n^(V) = (n+1)^2 / a^2`, "
                "`lambda_n^(TT,rough) = (n(n+2)-2) / a^2`, "
                "multiplicities `(n+1)^2`, `2n(n+2)`, `2(n-1)(n+3)`, and "
                "diagonal-spin floors `J_min = 0,1,2` respectively."
            ),
            scope="Spatial harmonic carrier on closed `S^3`.",
            authority_paths=(str(AUTHORITY_PATHS["paper22_spatial_hodge_complex"]),),
            depends_on=("premise.1", "premise.2"),
            premises=(
                "`premise.1` and `premise.2` place the perturbation problem on the accepted IO closed-space setting.",
                "Paper 22 constructs the scalar/vector Hodge carriers and the TT extension on round `S^3`.",
            ),
            proof_outline=(
                "Decompose the round-`S^3` spatial Hilbert space into scalar, coexact-vector, and TT tensor branches.",
                "Read off the exact eigenvalues, multiplicities, and diagonal-spin supports for each branch.",
                "Use those branch laws as the theorem-grade spatial carrier for later perturbation work.",
            ),
            scope_boundary=(
                "Spatial carrier only.",
                "Does not by itself determine the dynamical perturbation/source equations.",
            ),
        ),
        "paper23.closed_scalar_operator": TheoremNode(
            node_id="paper23.closed_scalar_operator",
            kind="theorem",
            label="Paper 23 Closed Scalar Operator Theorem",
            claim_status="derived / scoped",
            statement=(
                "On the closed scalar hierarchy, the first curvature correction is "
                "`lambda_n - 3 = (n-1)(n+3)`, scalar hyperspherical support obeys "
                "`ell = 0,1,...,n`, and the physical inhomogeneous scalar spectrum "
                "begins at `n >= 2` with `n = 1` pure gauge."
            ),
            scope="Closed scalar shell operator and physical mode support.",
            authority_paths=(str(AUTHORITY_PATHS["paper23_scalar_perturbations"]),),
            depends_on=("paper22.spatial_mode_ladder",),
            premises=(
                "`paper22.spatial_mode_ladder` fixes the scalar harmonic carrier on `S^3`.",
                "The closed scalar perturbation problem lives on that discrete shell basis rather than a flat continuous `k` basis.",
            ),
            proof_outline=(
                "Start from the scalar `S^3` harmonic ladder with `lambda_n = n(n+2)`.",
                "Insert the closed-space scalar curvature correction to obtain `lambda_n - 3 = (n-1)(n+3)`.",
                "Classify `n = 0` as background, `n = 1` as gauge, and `n >= 2` as physical scalar support.",
            ),
            scope_boundary=(
                "Closed scalar shell operator and support only.",
                "Does not by itself close the full metric-plus-fluid source/acoustic hierarchy.",
            ),
        ),
        "paper23.bridge_uniqueness": TheoremNode(
            node_id="paper23.bridge_uniqueness",
            kind="theorem",
            label="Paper 23 Bridge Uniqueness Theorem",
            claim_status="derived / scoped",
            statement=(
                "The accepted one-slot background-contraction bridge sends a boundary "
                "vector shell `n` only to adjacent scalar shells `N = n - 1` or "
                "`N = n + 1`, so the bridge image is multiplicity-one and "
                "adjacent-shell by construction."
            ),
            scope="Adjacent-shell bridge grammar on the accepted Paper 23 one-slot scalar sector.",
            authority_paths=(str(AUTHORITY_PATHS["paper23_bridge_uniqueness"]),),
            depends_on=("premise.1", "premise.2"),
            premises=(
                "`premise.1` and `premise.2` fix the IO horizon setting in which the bridge is posed.",
                "Paper 23 works on the one-slot background-contraction bridge rather than a generic multi-shell source operator.",
            ),
            proof_outline=(
                "Start from the accepted Paper 23 background-contraction bridge operator on the boundary vector carrier.",
                "Project that bridge onto scalar shells and read off the exact selection rule.",
                "Kill non-adjacent shell targets, leaving only the multiplicity-one adjacent-shell image `N = n - 1` or `N = n + 1`.",
            ),
            scope_boundary=(
                "Accepted one-slot bridge grammar only.",
                "Does not by itself fix the downstream source coefficients or the full perturbation/readout solver.",
            ),
        ),
        "paper28.closed_s3_shell_power": TheoremNode(
            node_id="paper28.closed_s3_shell_power",
            kind="theorem",
            label="Paper 28 Closed S^3 Shell-power Definition",
            claim_status="derived / scoped",
            statement=(
                "The exact observer-side closed-`S^3` shell covariance obeys "
                "`Var_n(X) = ((n+1)^2 / (2 pi^2 R^3)) P_X(n)`, with dimensionless "
                "shell conventions "
                "`Delta_q^2(n) = ((n+1)^3 / (2 pi^2 R^3)) P_X(n)`, "
                "`Delta_scalar^2(n) = (n(n+1)(n+2) / (2 pi^2 R^3)) P_X(n)`, and "
                "`Delta_MS^2(n) = (((n-1)(n+1)(n+3)) / (2 pi^2 R^3)) P_X(n)`."
            ),
            scope="Observer-side shell covariance and power-spectrum conventions on closed `S^3`.",
            authority_paths=(str(AUTHORITY_PATHS["paper28_closed_s3_power_definition"]),),
            depends_on=("paper22.spatial_mode_ladder", "paper23.closed_scalar_operator"),
            premises=(
                "`paper22.spatial_mode_ladder` fixes the exact scalar-shell degeneracy `(n+1)^2` on closed `S^3`.",
                "`paper23.closed_scalar_operator` fixes the physical scalar shell variable `k_MS(n) = sqrt((n-1)(n+3)) / R`.",
            ),
            proof_outline=(
                "Expand the observer-side scalar field in orthonormal closed-`S^3` hyperspherical harmonics.",
                "Write the equal-point variance shell by shell using the scalar degeneracy `(n+1)^2` and the volume `2 pi^2 R^3`.",
                "From that invariant shell variance, read off the exact `q`, scalar-Laplacian, and Mukhanov-Sasaki `Delta^2` conventions without importing the flat `k^3` law as primitive.",
            ),
            scope_boundary=(
                "Observer-side closed-shell power definitions only.",
                "Does not by itself derive the physical IO source-side shell covariance law or the missing bridge typing.",
            ),
        ),
        "paper28.boundary_fixed_point_scalar_tilt": TheoremNode(
            node_id="paper28.boundary_fixed_point_scalar_tilt",
            kind="theorem",
            label="Paper 28 Boundary Fixed-point Scalar Tilt Law",
            claim_status="conditional / scoped",
            statement=(
                "Conditional on the Boundary Fixed-point Principle, the active "
                "scalar tilt closes as "
                f"`n_s = 1 - K_gauge / x = {ACTIVE_BRANCH.n_s:.4f}`."
            ),
            scope="Active scalar-tilt closure on the published Paper 28 scalar sector.",
            authority_paths=(str(AUTHORITY_PATHS["paper28_scalar_tilt"]),),
            depends_on=("premise.1", "premise.2"),
            premises=(
                "`premise.1` and `premise.2` fix the IO boundary/source setting for the scalar sector.",
                "The Boundary Fixed-point Principle is the surviving scalar-sector premise replacing the older boundary-covariance route.",
            ),
            proof_outline=(
                "Use the Paper 28 boundary audit to kill the ordinary local shell-blind tilt mechanisms.",
                "Retain the fixed-point route as the surviving scalar-sector coefficient principle.",
                "Evaluate the resulting tilt law `n_s = 1 - K_gauge / x` on the active IO constants.",
            ),
            scope_boundary=(
                "Conditional scalar-tilt closure only.",
                "The current stack does not license this law as an unconditional theorem independent of the Boundary Fixed-point Principle.",
            ),
        ),
        "paper30.background_surface": TheoremNode(
            node_id="paper30.background_surface",
            kind="theorem",
            label="Paper 30 Legacy Recompute Surface",
            claim_status="derived / scoped",
            statement=(
                "The active branch supports the late-time closed-FRW background "
                "surface with "
                "`H(z) = H_0 sqrt[Omega_r (1+z)^4 + Omega_m (1+z)^3 + Omega_k (1+z)^2 + Omega_Lambda]`, "
                "`D_M(z) = R_c sin(chi(z))`, "
                "`chi(z) = ∫_0^z dz' H_0 / H(z')`, and "
                "`t(z) = ∫_z^∞ dz' / ((1+z') H(z'))`."
            ),
            scope="Observer-side background geometry and BAO-side runtime surface.",
            authority_paths=(str(AUTHORITY_PATHS["paper30_legacy_recompute"]),),
            depends_on=("paper21.branch_assignment",),
            premises=(
                "`paper21.branch_assignment` fixes the active branch package.",
                "Closed-FRW background evolution on that branch is already part of the accepted runtime surface.",
            ),
            proof_outline=(
                "Evaluate the active-branch closed-FRW integrals for expansion, transverse distance, radial distance, volume distance, lookback time, and age.",
                "Export those quantities directly in the calculator without delegating geometry to a flat-space backend.",
                "Use the carried branch value consistently across the public background and BAO surfaces.",
            ),
            scope_boundary=(
                "Observer-side closed-FRW background geometry on the fixed active branch only.",
                "Does not by itself determine a full perturbation transfer solver.",
            ),
        ),
        "paper30.active_branch_parameter_package": TheoremNode(
            node_id="paper30.active_branch_parameter_package",
            kind="theorem",
            label="Paper 30 Active-branch Parameter Package",
            claim_status="derived / scoped",
            statement=(
                "The carried public runtime branch fixes "
                f"`H0 = {ACTIVE_BRANCH.H0:.12f} km/s/Mpc`, "
                f"`Omega_m = {ACTIVE_BRANCH.Omega_m:.12f}`, "
                f"`Omega_k = {ACTIVE_BRANCH.Omega_k:.12f}`, "
                f"`Omega_Lambda = {ACTIVE_BRANCH.Omega_lambda:.12f}`, "
                f"`T_CMB = {ACTIVE_BRANCH.T_cmb:.4f} K`, and "
                f"`Y_p = {ACTIVE_BRANCH.YHe:.4f}`."
            ),
            scope="Fixed active runtime parameter package carried by the public calculator.",
            authority_paths=(str(AUTHORITY_PATHS["paper30_published"]),),
            depends_on=("paper21.branch_assignment",),
            premises=(
                "`paper21.branch_assignment` fixes the carried active branch rather than refitting a branch per observable.",
                "The public calculator exposes one reviewed runtime package as its active numerical surface.",
            ),
            proof_outline=(
                "Read the active branch constants from the reviewed Paper 30 runtime package.",
                "Carry those values unchanged into the calculator constants layer.",
                "Expose them as public theorem-grade or scoped-active package values rather than hiding them behind an opaque backend.",
            ),
            scope_boundary=(
                "Fixed active runtime package only.",
                "Does not claim that the active package is the unique surviving branch outside the reviewed public calculator surface.",
            ),
        ),
        "paper30.bare_master_clock": TheoremNode(
            node_id="paper30.bare_master_clock",
            kind="theorem",
            label="Paper 30 Bare Master-clock Theorem",
            claim_status="derived / scoped plus verified / carried numeric evaluation",
            statement=(
                "The all-epoch local IO master clock is the bare FRW proper-time "
                "integral "
                "`t_bare(z) = integral_z^infinity dz' / [(1+z') H_bare(z')]` with "
                "`E(z)^2 = Omega_r (1+z)^4 + Omega_m (1+z)^3 + Omega_k (1+z)^2 + Omega_Lambda`, "
                "equivalently "
                "`t_bare(a) = H0_bare^-1 integral_0^a da' / sqrt(Omega_r + Omega_m a' + Omega_k a'^2 + Omega_Lambda a'^4)`, "
                f"yielding `t_bare(z=0) = {bare_clock_age:.12f} Gyr` "
                "on the carried bare branch with exact radiation."
            ),
            scope="Bare local-clock theorem on the Paper 30 master-clock branch.",
            authority_paths=(
                str(AUTHORITY_PATHS["paper30_master_clock_correction"]),
                str(AUTHORITY_PATHS["paper30_published"]),
            ),
            depends_on=("premise.1", "premise.2", "paper17.gttp_thermal_readout"),
            premises=(
                "`premise.1` and `premise.2` fix the IO local-clock setting and allow the standard local radiation-density input.",
                "`paper17.gttp_thermal_readout` fixes the carried observer CMB temperature entering the exact radiation density.",
                "The Paper 30 master-clock correction replaces the old dust cycloid as the all-epoch local clock.",
            ),
            proof_outline=(
                "Derive the exact bare radiation density from the carried thermal readout and standard-neutrino slot.",
                "Insert that radiation term into the bare FRW proper-time integral instead of dropping to the dust cycloid approximation.",
                "Evaluate the corrected integral on the carried bare branch and expose the resulting present-day local age.",
            ),
            scope_boundary=(
                "Bare local-clock branch only.",
                "Not the projected observer-side age already exposed by the active closed-FRW background snapshot.",
            ),
        ),
        "paper30.deuterium_scorecard": TheoremNode(
            node_id="paper30.deuterium_scorecard",
            kind="theorem",
            label="Paper 30 Active Deuterium Scorecard",
            claim_status="derived / scoped plus verified / surviving precision scorecard",
            statement=(
                "The active repaired BBN scorecard carries the fixed deuterium "
                f"prediction `D/H = {ACTIVE_BBN_DEUTERIUM_RATIO:.12e}`. "
                "The Paper 30 absorber compilation verifies that this fixed IO "
                "prediction survives the current precision sample cleanly."
            ),
            scope="Active repaired BBN deuterium scorecard carried by the calculator.",
            authority_paths=(
                str(AUTHORITY_PATHS["paper30_deuterium_scorecard"]),
                str(AUTHORITY_PATHS["paper30_published"]),
            ),
            depends_on=("premise.1", "premise.2", "paper12.baryon_dictionary_fraction"),
            premises=(
                "`premise.1` and `premise.2` fix the IO BBN setting.",
                "`paper12.baryon_dictionary_fraction` repairs the old deuterium crisis by fixing the surviving baryon fraction route.",
            ),
            proof_outline=(
                "Carry the repaired IO deuterium prediction on the active BBN scorecard rather than the superseded low-baryon route.",
                "Compare that fixed prediction against the current absorber compilation without re-fitting the value.",
                "Retain the scorecard as a public carried output because the surviving route remains numerically clean against the precision sample.",
            ),
            scope_boundary=(
                "Active repaired deuterium scorecard only.",
                "Does not claim a live calculator nuclear-network re-integration on demand.",
            ),
        ),
        "paper30.primordial_helium_scorecard": TheoremNode(
            node_id="paper30.primordial_helium_scorecard",
            kind="theorem",
            label="Paper 30 Active Primordial Helium Scorecard",
            claim_status="derived / scoped plus verified / observational scorecard",
            statement=(
                "The active repaired BBN scorecard and runtime package carry "
                f"`Y_p = {ACTIVE_BRANCH.YHe:.4f}` on the public calculator surface."
            ),
            scope="Active primordial helium scorecard carried by the calculator.",
            authority_paths=(
                str(AUTHORITY_PATHS["paper30_helium_scorecard"]),
                str(AUTHORITY_PATHS["paper30_published"]),
            ),
            depends_on=("paper21.branch_assignment", "paper30.active_branch_parameter_package"),
            premises=(
                "`paper21.branch_assignment` fixes the active runtime branch.",
                "`paper30.active_branch_parameter_package` carries the reviewed active helium mass fraction on the public calculator surface.",
            ),
            proof_outline=(
                "Read the active helium mass fraction from the reviewed runtime package.",
                "Carry that value unchanged into the live calculator constants and public bundle.",
                "Cross-check the fixed value against the current primordial-helium data compilation without promoting the comparison itself to a new fit.",
            ),
            scope_boundary=(
                "Active carried helium scorecard only.",
                "Does not claim a live calculator BBN network solve for `Y_p`.",
            ),
        ),
        "paper29.sound_speed_selector": TheoremNode(
            node_id="paper29.sound_speed_selector",
            kind="theorem",
            label="Paper 29 Sound-speed Baryon-slot Selector",
            claim_status="derived / scoped",
            statement=(
                "The local sound-speed loading term uses "
                "`R(z) = 3 rho_b(z) / [4 rho_gamma(z)]` with the unique "
                "theorem-grade baryon slot `omega_b,geom` on the rebuilt "
                "reduced-stack scope."
            ),
            scope="Local photon-baryon inertia coefficient for the active branch.",
            authority_paths=(str(AUTHORITY_PATHS["paper29_sound_speed_selector"]),),
            depends_on=("premise.1", "premise.2", "paper21.branch_assignment"),
            premises=(
                "`premise.1` and `premise.2` fix the IO setting for the local pre-recombination plasma.",
                "`paper21.branch_assignment` fixes the carried active branch used by the live calculator.",
            ),
            proof_outline=(
                "Identify `R(z)` as the local photon-baryon inertia coefficient rather than an observer-side readout scalar.",
                "Use the rebuilt Paper 29 slot audit to rule out the late clustering branch for this local fluid coefficient.",
                "Conclude that the unique theorem-grade slot for `R(z)` is `omega_b,geom` on the live calculator branch.",
            ),
            scope_boundary=(
                "Applies to the local sound-speed loading term `R(z)` on the active branch.",
                "Does not by itself close the full drag-epoch or BAO standard-ruler theorem.",
            ),
        ),
        "paper31.geometric_pre_drag_ruler": TheoremNode(
            node_id="paper31.geometric_pre_drag_ruler",
            kind="theorem",
            label="Paper 31 Geometric Pre-drag Ruler",
            claim_status="derived / scoped",
            statement=(
                "The active branch carries the published pre-drag ruler "
                "`r_d = ∫ c_s(z) / H(z) dz` with "
                "`c_s(z) = c / sqrt(3[1 + R(z)])`, yielding "
                f"`r_d = {rd_mpc:.12f} Mpc` on the calculator surface."
            ),
            scope="Active-branch BAO ruler slot.",
            authority_paths=(str(AUTHORITY_PATHS["paper31_legacy_recompute"]),),
            depends_on=("paper21.branch_assignment", "paper29.sound_speed_selector"),
            premises=(
                "`paper21.branch_assignment` fixes the active branch on which the ruler is read.",
                "`paper29.sound_speed_selector` fixes `R(z)` to the theorem-grade slot `omega_b,geom`.",
                "The published BAO surface uses one carried ruler slot rather than a per-query fit parameter.",
            ),
            proof_outline=(
                "Evaluate the active-branch sound-horizon / pre-drag integral using the carried closed background and the theorem-grade sound-speed slot.",
                "Expose that carried value as the calculator's published `r_d` slot.",
                "Use the same carried slot in `D_M/r_d`, `D_H/r_d`, and `D_V/r_d` outputs.",
            ),
            scope_boundary=(
                "Active-branch ruler slot only.",
                "Does not claim a universal branch-independent drag-ruler theorem.",
            ),
        ),
        "paper31.baryon_assignment": TheoremNode(
            node_id="paper31.baryon_assignment",
            kind="theorem",
            label="Paper 31 Baryon Assignment",
            claim_status="derived / scoped",
            statement=(
                "The active branch exposes typed baryon slots and assigns "
                "`omega_b,geom` as the local chemistry density entering "
                "`n_H(z)`, `n_e(z) = x_e n_H(z)`, and "
                "`kappa'_loc = a_loc n_e sigma_T` in the live recombination primitives."
            ),
            scope="Typed baryon-slot split on the active branch.",
            authority_paths=(str(AUTHORITY_PATHS["paper31_baryon_assignment"]),),
            depends_on=("paper21.branch_assignment",),
            premises=(
                "`paper21.branch_assignment` fixes the active branch package.",
                "The calculator distinguishes typed baryon slots for geometry, chemistry, and downstream operator use.",
            ),
            proof_outline=(
                "Separate the baryon inventory into typed calculator slots rather than one undifferentiated parameter.",
                "Assign `omega_b,geom` as the chemistry density used by the live recombination primitives on the active branch.",
                "Propagate that slot choice into the local background-state and opacity chains.",
            ),
            scope_boundary=(
                "Typed baryon assignment on the fixed active branch only.",
                "Does not assert a theorem-grade completion of every possible chemistry closure.",
            ),
        ),
        "paper31.local_background_state_map": TheoremNode(
            node_id="paper31.local_background_state_map",
            kind="theorem",
            label="Paper 31 Local Background State Map",
            claim_status="derived / scoped",
            statement=(
                "The calculator's local recombination state map "
                "(`H_loc`, `T_R,loc`, `n_H,geom`, `u`, `a_loc`) is a theorem-grade "
                "map on the active branch, with "
                "`H_loc = (c / r_s) sqrt[(1-u)/u^3]`, "
                "`T_R,loc = x^(-K_gauge) T_obs,0 (1+z)`, "
                "`a_loc = u R_U`, and `n_H,geom = rho_b,geom / m_H`."
            ),
            scope="Local recombination background-state primitives.",
            authority_paths=(str(AUTHORITY_PATHS["paper31_local_background_state_map"]),),
            depends_on=("paper21.branch_assignment", "paper31.baryon_assignment"),
            premises=(
                "`paper21.branch_assignment` fixes the active branch package.",
                "`paper31.baryon_assignment` fixes the local chemistry slot as `omega_b,geom`.",
            ),
            proof_outline=(
                "Start from the active-branch closed background and the typed chemistry slot.",
                "Construct the local recombination state map `H_loc`, `T_R,loc`, `n_H,geom`, `u`, and `a_loc` at a supplied redshift.",
                "Export those primitives as calculator-visible local-state quantities.",
            ),
            scope_boundary=(
                "Local recombination background-state primitives on the fixed active branch.",
                "Does not by itself close the exact dynamic-network recombination problem.",
            ),
        ),
        "paper31.recombination_clock_transport": TheoremNode(
            node_id="paper31.recombination_clock_transport",
            kind="theorem",
            label="Paper 31 Recombination Clock Transport",
            claim_status="derived / scoped",
            statement=(
                "The live primitive opacity chain derives "
                "`kappa'_loc = a_loc n_e sigma_T`, "
                "`d tau_obs / dz = kappa'_loc c / ((1+z) H_loc)`, and "
                "`Gamma_T / H_loc = n_e sigma_T c / H_loc` once the local "
                "background state and `omega_b,geom` chemistry slot are fixed."
            ),
            scope="Primitive local opacity and LOS clock transport.",
            authority_paths=(str(AUTHORITY_PATHS["paper31_clock_transport"]),),
            depends_on=("paper31.local_background_state_map",),
            premises=(
                "`paper31.local_background_state_map` provides the local branch background state.",
                "Chemistry-dependent outputs are derived only when `x_e` is supplied by the local Saha seed or another separately justified source.",
            ),
            proof_outline=(
                "Use the local background state and chemistry slot to build `kappa'_loc`, `d tau_obs / dz`, `Gamma_T/H_loc`, `R_local,geom`, and `c_s,local`.",
                "Treat the local Saha seed as the default derived ionization input in the published calculator.",
                "When a user overrides `x_e`, keep the local background state derived but mark chemistry-dependent rows as conditional.",
            ),
            scope_boundary=(
                "Primitive local opacity and LOS clock transport on the active branch.",
                "Not a theorem-grade exact dynamic-network recombination closure.",
            ),
        ),
        "local.saha_seed": TheoremNode(
            node_id="local.saha_seed",
            kind="theorem",
            label="Local Saha Seed Theorem",
            claim_status="derived / scoped under Premise 2 standard hydrogen microphysics",
            statement=(
                "The default ionization seed is fixed by the local Saha law "
                "`x_e^2/(1-x_e) = ((m_e k_B T_R,loc)/(2 pi hbar^2))^(3/2) "
                "exp(-chi_H/(k_B T_R,loc)) / n_H,geom`."
            ),
            scope="Default local ionization seed used by the published recombination primitives.",
            authority_paths=(),
            depends_on=("premise.2", "paper31.local_background_state_map", "paper31.baryon_assignment"),
            premises=(
                "`premise.2` licenses standard hydrogen microphysics inside the horizon.",
                "`paper31.local_background_state_map` fixes `T_R,loc` and `n_H,geom` on the active branch.",
                "`paper31.baryon_assignment` fixes the chemistry slot as `omega_b,geom`.",
            ),
            proof_outline=(
                "Use the active-branch local radiation temperature and hydrogen number density as the thermodynamic inputs.",
                "Apply the standard hydrogen Saha equilibrium equation to those local variables.",
                "Solve the algebraic relation for the default local seed `x_e` used by the published primitive surface.",
            ),
            scope_boundary=(
                "Default local equilibrium seed only.",
                "Does not claim an exact dynamic-network recombination history or visibility peak closure.",
            ),
            notes=(
                "No published paper reference is used here; the theorem text is carried self-contained in the calculator dictionary.",
            ),
        ),
        "paper32.closed_s3_solver_spec": TheoremNode(
            node_id="paper32.closed_s3_solver_spec",
            kind="theorem",
            label="Paper 32 S^3 Solver Specification",
            claim_status="derived / scoped",
            statement=(
                "The IO perturbation/transfer geometry is organized on closed "
                "S^3 spatial sections rather than on a flat `K=0` transfer basis."
            ),
            scope="Closed-space transfer geometry specification for the IO stack.",
            authority_paths=(str(AUTHORITY_PATHS["paper32_s3_solver_spec"]),),
            depends_on=("premise.1", "premise.2"),
            premises=(
                "`premise.1` and `premise.2` place the IO transfer problem on the interior black-hole branch with outside-equivalent microphysics.",
                "Spatial sections in the accepted IO perturbation stack are closed rather than flat.",
            ),
            proof_outline=(
                "Specify the perturbation and transfer geometry on closed `S^3` sections rather than a flat `K=0` basis.",
                "Use that specification to interpret acoustic and peak-location quantities in a closed-geometry transfer setting.",
                "Treat flat-space extractions as comparison conventions rather than native calculator geometry.",
            ),
            scope_boundary=(
                "Geometry specification for the IO transfer stack.",
                "Not a theorem-grade completion of the full TT/TE/EE solver by itself.",
            ),
        ),
        "paper32.modular_dtn_field_transfer": TheoremNode(
            node_id="paper32.modular_dtn_field_transfer",
            kind="theorem",
            label="Paper 32 Modular-DtN Field Transfer",
            claim_status="derived / scoped",
            statement=(
                "On the active scalar-source sector, the unique positive one-slot "
                "field transfer is "
                "`T_field = exp[-(K_g tensor log(r_s Lambda_DtN^coex)) / (2x)]`, "
                "with quadratic descendant "
                "`R_cov = T_field^* T_field`, full source block "
                "`P_src = B_+ o U_coex o T_field`, repaired plus-branch window "
                "`W_N^(+) = ((N+1) / (N_p+1))^(-K_gauge / x)` on the affine "
                "odd-shell bridge image, and native amplitude "
                "`A_s = (25/9) [gamma^2 / (1 + gamma^2)] [1 / sqrt(2)] [exp(4 pi sqrt(2)) - 1]^-1`."
            ),
            scope="Active scalar-source block and one-slot post-bridge field sector.",
            authority_paths=(
                str(AUTHORITY_PATHS["paper32_modular_dtn_field_transfer"]),
                str(AUTHORITY_PATHS["paper32_hidden_identification_repair"]),
            ),
            depends_on=("premise.1", "premise.2", "paper32.hidden_identification_repair"),
            premises=(
                "`premise.1` and `premise.2` place the source/readout problem on the accepted IO interior-horizon branch.",
                "The active source block is the one-slot modular-DtN field sector rather than the full perturbation hierarchy.",
            ),
            proof_outline=(
                "Use the coexact DtN spectrum to define the shell generator `Y = log(r_s Lambda_DtN^coex)`.",
                "Combine the reduced gauge modular weight with the accessible-line divisor `1/x` to obtain the unique positive source transfer `T_field`.",
                "Apply the plus bridge and pivot normalization to recover the source window and the native scalar amplitude on the active sector.",
            ),
            scope_boundary=(
                "Active scalar-source block only.",
                "The exact source window is the repaired affine odd-shell law from the hidden-identification repair, not the older `N / N_p` shorthand.",
                "Does not by itself close the exact Stage-2 history operator, the closed-S^3 perturbation hierarchy, or the peak/readout identification theorem.",
            ),
        ),
        "paper32.hidden_identification_repair": TheoremNode(
            node_id="paper32.hidden_identification_repair",
            kind="theorem",
            label="Paper 32 Hidden-identification Repair",
            claim_status="derived / scoped",
            statement=(
                "The active source exponent lives on the boundary DtN shell "
                "variable `s_ell = ell + 1`, and under the accepted even-shell "
                "boundary lift plus the Paper 23 bridge rule `N = n +- 1` it "
                "pushes forward to the affine odd-shell laws "
                "`W_N^(+) = ((N+1)/(N_p+1))^(-beta)` and "
                "`W_N^(-) = ((N+3)/(N_p+3))^(-beta)`. "
                "The line-class descent is `1/x`, not the legacy area factor "
                "`1/x^2`."
            ),
            scope="Repaired shell relabeling and line-class descent for the Paper 32 source theorem.",
            authority_paths=(str(AUTHORITY_PATHS["paper32_hidden_identification_repair"]),),
            depends_on=("premise.1", "premise.2", "paper23.bridge_uniqueness"),
            premises=(
                "`premise.1` and `premise.2` keep the source/readout problem on the accepted IO branch.",
                "`paper23.bridge_uniqueness` fixes the multiplicity-one adjacent-shell bridge grammar `N = n - 1` or `N = n + 1`.",
            ),
            proof_outline=(
                "Separate the boundary DtN shell variable `s_ell = ell + 1` from the scalar-shell bridge label `N`.",
                "Push the DtN exponent through the accepted even-shell boundary lift `n = 2 ell` and the adjacent-shell bridge rule to obtain the affine odd-shell windows.",
                "Use the one-slot line-class identification to keep the accessibility divisor at `1/x` rather than importing the old area factor.",
            ),
            scope_boundary=(
                "Repairs the Paper 32 source/readout theorem on the active one-slot source sector only.",
                "Does not by itself determine the branch coefficients `B_(N,±)` or the full perturbation/readout solver.",
            ),
        ),
        "paper32.typed_baryon_slot_spec": TheoremNode(
            node_id="paper32.typed_baryon_slot_spec",
            kind="theorem",
            label="Typed Baryon-slot Specification",
            claim_status="derived / scoped",
            statement=(
                "The native solver preserves the typed baryon split: "
                "recombination chemistry `omega_b,geom`, primitive local opacity "
                "`omega_b,geom`, reduced visibility/readout `omega_b,eff`, while "
                "the perturbation block forbids any silent one-slot collapse on "
                "`R`. On the current calculator scope, the surviving closure is a "
                "typed local `R` operator built from primitive `R_local,geom` plus "
                "the coupled Thomson tuple, while the scalar metric-source slot "
                "still remains open. No silent one-slot collapse on `R` is "
                "licensed anywhere in the perturbation pipeline."
            ),
            scope="Perturbation-era baryon typing on the closed `S^3` solver grammar.",
            authority_paths=(str(AUTHORITY_PATHS["paper32_s3_solver_spec"]),),
            depends_on=("paper32.closed_s3_solver_spec",),
            premises=(
                "`paper32.closed_s3_solver_spec` fixes the typed closed-`S^3` solver grammar.",
                "The perturbation block is not licensed to collapse to a one-slot baryon assignment.",
            ),
            proof_outline=(
                "Read the active typed baryon placements from Corollary 32.S3.1.",
                "Assign theorem-grade slots only where the stack actually closes them.",
                "Forbid any one-slot hierarchy-wide `R` reassignment while allowing only the later typed local `R` operator closure on its proper carrier.",
                "Leave the scalar metric-source slot explicitly open instead of backfilling it from local helpers.",
                "Reject any silent one-slot reassignment of the full perturbation `R` slot to a local helper quantity.",
            ),
            scope_boundary=(
                "Typed solver grammar only.",
                "Does not derive a single theorem-grade baryon slot for the full observed hierarchy.",
                "In particular, the full-hierarchy `R` slot is not licensed to collapse silently to one local scalar anywhere in the composed pipeline.",
            ),
        ),
        "paper31.stage2_markov_state": TheoremNode(
            node_id="paper31.stage2_markov_state",
            kind="theorem",
            label="Paper 31 Stage-2 Markov State",
            claim_status="derived / scoped",
            statement=(
                "The exact Stage-2 hydrogen radiative-transfer branch admits a "
                "lossless Markov closure on "
                "`Y_rec = (x_e, T_m, D_-(q;z), L_-(z))`, and no fixed finite-dimensional "
                "scalar moment vector replaces that field exactly."
            ),
            scope="Exact Stage-2 history-state carrier.",
            authority_paths=(str(AUTHORITY_PATHS["paper31_stage2_markov_state"]),),
            depends_on=("premise.2",),
            premises=(
                "`premise.2` licenses the accepted exterior local atomic/radiative-transfer class inside the horizon.",
                "Stage 2 belongs to the local bulk radiative-transfer sector rather than an observer-side readout patch.",
            ),
            proof_outline=(
                "Audit the exact FULL Stage-2 update chain and identify the outgoing characteristic distortion field plus line-handoff sector.",
                "Show that the extended state `(x_e, T_m, D_-(q;z), L_-(z))` is a lossless Markov closure of the exact branch.",
                "Kill any fixed finite-dimensional scalar compression as an exact replacement.",
            ),
            scope_boundary=(
                "Exact Stage-2 state carrier only.",
                "Does not by itself supply the final explicit dynamic-network renormalization operator.",
            ),
        ),
        "local.inherited_full_stage2_dynamic_history_builder": TheoremNode(
            node_id="local.inherited_full_stage2_dynamic_history_builder",
            kind="theorem",
            label="Inherited FULL Stage-2 Dynamic-history Builder Theorem",
            claim_status="conditional / scoped",
            statement=(
                "On the active IO local background with "
                "`T_R,loc(z) = T_IO,0 (1+z)` and "
                "`H_loc(z) = (c / R_S) sqrt((1-u)/u^3)` for `u = 1 / [x (1+z)]`, "
                "the standalone inherited-FULL builder runs exact FULL HyRec history outside the forbidden pointwise wrapper and exports "
                "`Y_rec(z) = (x_e(z), T_m(z), D_-(q;z), L_-(z))` with "
                "`D_-(q;z) = interp_Dfnu(lna_0, dlna, Dfminus_hist(q;.), N_z, -ln(1+z))` and "
                "`L_-(z) = interp_Dfnu(lna_0, dlna, Dfminus_Ly_hist(.), N_z, -ln(1+z))`."
            ),
            scope="Conditional exact inherited-FULL Stage-2 history builder on the active IO local background.",
            authority_paths=(),
            depends_on=("premise.2", "paper31.local_background_state_map", "paper31.stage2_markov_state"),
            premises=(
                "`premise.2` licenses the inherited FULL atomic and radiative-transfer physics class on the local bulk branch.",
                "`paper31.local_background_state_map` fixes the active local thermal and Hubble histories entering the standalone driver.",
                "`paper31.stage2_markov_state` fixes the exact exported state grammar `Y_rec = (x_e, T_m, D_-(q;z), L_-(z))`.",
            ),
            proof_outline=(
                "Promote the existing standalone FULL-history route from the Paper 31 benchmark layer into the calculator instead of calling FULL HyRec through a pointwise `(z, x_e, T_m)` wrapper.",
                "Run FULL HyRec on the active IO local background arrays with the explicit history-grid fix used by the benchmark route.",
                "Export `x_e`, `T_m`, `Dfminus_hist`, and `Dfminus_Ly_hist` on the requested observer-redshift grid without silently collapsing the characteristic field to one preferred scalar.",
            ),
            scope_boundary=(
                "Conditional exact inherited-FULL history builder only.",
                "Uses inherited FULL atomic and radiative-transfer physics under Premise 2 rather than a new universal IO-native renormalization theorem.",
                "Does not pick a preferred one-dimensional compression of `D_-(q;z)` unless the caller chooses one explicitly.",
            ),
            notes=(
                "The theorem text is self-contained here; there is no published paper reference for this post-Paper-32 local completion step.",
            ),
        ),
        "calculator.thomson_history_realization": TheoremNode(
            node_id="calculator.thomson_history_realization",
            kind="theorem",
            label="Thomson-history Realization Theorem",
            claim_status="derived / scoped",
            statement=(
                "Any exact IO-native closure on the surviving acoustic branch must "
                "be realized on the coupled tuple "
                "`(thomson_drag_rate, thomson_hierarchy_rate, tau_c, dtau_c, slip, shear)` "
                "with `tau_c = 1 / thomson_drag_rate` and "
                "`dtau_c = - d(thomson_drag_rate) * tau_c^2`."
            ),
            scope="Coupled Thomson-history carrier for the perturbation hierarchy.",
            authority_paths=(str(AUTHORITY_PATHS["calculator_thomson_history_realization"]),),
            depends_on=("paper32.closed_s3_solver_spec", "paper31.stage2_markov_state"),
            premises=(
                "`paper32.closed_s3_solver_spec` fixes the perturbation block as part of the typed closed-`S^3` solver grammar.",
                "`paper31.stage2_markov_state` fixes the exact history-state carrier feeding the perturbation seam.",
                "The tight-coupling system depends on distinct drag and hierarchy rates together with `tau_c`, `dtau_c`, slip, and shear.",
            ),
            proof_outline=(
                "Localize the surviving acoustic perturbation seam to the broad Thomson-history leg rather than a narrow visibility patch.",
                "Read the carrier formulas for `thomson_drag_rate`, `thomson_hierarchy_rate`, `tau_c`, and `dtau_c` from the accepted local hierarchy code path.",
                "Promote the coupled tuple to the exact admissible carrier and kill one-site downstream rescalings as fake closures.",
            ),
            scope_boundary=(
                "Tuple carrier only.",
                "Does not yet derive the exact IO-native operator acting on that tuple.",
            ),
        ),
        "local.typed_r_operator": TheoremNode(
            node_id="local.typed_r_operator",
            kind="theorem",
            label="Full Typed R Hierarchy Operator Theorem",
            claim_status="derived / scoped as maps",
            statement=(
                "On the accepted equal-rate scoped branch "
                "`thomson_hierarchy_rate = thomson_drag_rate`, the primitive acoustic loading object stays "
                "`R_local,geom(z) = 3 rho_b,geom(z) / [4 rho_gamma(z)]`, and the "
                "full oscillator-site hierarchy maps are "
                "`Gamma_gammab = thomson_drag_rate`, "
                "`Gamma_bgamma = R_local,geom thomson_drag_rate = R_local,geom / tau_c`, "
                "`c_bgamma^2 = 1 / [3 (1 + R_local,geom)]`, "
                "`M_bgamma = 1 + R_local,geom`, "
                "`L_odd/even = R_local,geom / (1 + R_local,geom)`, "
                "`F_tca = tau_c / (1 + R_local,geom)` with "
                "`tau_c = 1 / thomson_drag_rate`, and the split Silk operator "
                "`D_heat = R_local,geom^2 / [6 (1+R_local,geom)^2 thomson_drag_rate]`, "
                "`D_visc = 16 / [90 (1+R_local,geom) thomson_hierarchy_rate]`, "
                "`D_silk = D_heat + D_visc`. Dynamic odd/even modulation is generated "
                "inside the oscillator by `c_bgamma^2` and `L_odd/even`; the "
                "observed peak-height ratio is the downstream transfer/readout "
                "functional of that evolved hierarchy and not a separate baryon-slot assignment."
            ),
            scope="Equal-rate scoped branch of the full typed `R` hierarchy operator on the closed scalar photon-baryon oscillator.",
            authority_paths=(str(AUTHORITY_PATHS["calculator_typed_r_operator"]),),
            depends_on=(
                "paper29.sound_speed_selector",
                "paper32.typed_baryon_slot_spec",
                "calculator.thomson_history_realization",
            ),
            premises=(
                "`paper29.sound_speed_selector` fixes the primitive local enthalpy ratio `R_local` on `omega_b,geom`.",
                "`paper32.typed_baryon_slot_spec` forbids any one-slot full-hierarchy reassignment of `R` and therefore forces a typed operator closure instead.",
                "`calculator.thomson_history_realization` fixes the exact drag/hierarchy tuple consumed by the local hierarchy.",
            ),
            proof_outline=(
                "Keep the primitive enthalpy ratio itself on the inventory branch `omega_b,geom` instead of back-propagating observer-side `omega_b,eff` into the local plasma leg.",
                "Read the full hierarchy site map from the closed scalar oscillator: momentum exchange depends on `(thomson_drag_rate, R_local)`, pressure restoration on `1/[3(1+R_local)]`, inertia on `1+R_local`, and dynamic odd/even loading on `R_local/(1+R_local)`.",
                "Split the standard Silk integrand into the heat-conduction term carried by baryon-photon slip and the viscosity term carried by the photon hierarchy, then bind those two pieces to `thomson_drag_rate` and `thomson_hierarchy_rate` respectively.",
                "Conclude that the hierarchy requires a site-wise typed operator rather than a slot swap, and that the final observed odd/even peak pattern is downstream transfer/readout of this evolved oscillator rather than a new primitive `R` slot.",
            ),
            scope_boundary=(
                "Closes the full site-wise hierarchy operator carried by the primitive local `R` leg and the Thomson tuple on the accepted equal-rate scoped branch `thomson_hierarchy_rate = thomson_drag_rate`.",
                "Does not claim a one-slot closure of the full observed peak/readout hierarchy.",
                "Observer-side `omega_b,eff` remains downstream readout packaging and is not back-propagated into the primitive local `R` leg.",
                "Does not yet claim a theorem-grade nontrivial drag-vs-hierarchy deformation.",
            ),
            notes=(
                "The theorem text is self-contained here; the linked report is supplementary supporting material only.",
            ),
        ),
        "local.typed_r_site_uniqueness": TheoremNode(
            node_id="local.typed_r_site_uniqueness",
            kind="theorem",
            label="Typed R Site-uniqueness Theorem",
            claim_status="derived / scoped",
            statement=(
                "On the accepted equal-rate scoped branch `thomson_hierarchy_rate = thomson_drag_rate`, the site-wise hierarchy placements carried by `local.typed_r_operator` are the unique admissible typed operators on the current IO stack: "
                "pressure/restoring force must use `c_bgamma^2 = 1 / [3 (1 + R_local,geom)]`, "
                "inertia and dynamic odd/even loading must use `M_bgamma = 1 + R_local,geom` and `L_odd/even = R_local,geom / (1 + R_local,geom)`, "
                "momentum exchange must use the pair `Gamma_gammab = thomson_drag_rate`, `Gamma_bgamma = R_local,geom thomson_drag_rate`, "
                "and Silk damping must split uniquely as "
                "`D_heat = R_local,geom^2 / [6 (1+R_local,geom)^2 thomson_drag_rate]` and "
                "`D_visc = 16 / [90 (1+R_local,geom) thomson_hierarchy_rate]`. "
                "No alternate site placement is compatible with the primitive local `R` theorem, the no-single-slot theorem, the Thomson-history tuple theorem, and the lower-triangular non-backpropagation boundary."
            ),
            scope="Uniqueness-by-elimination for the four actual `R` insertion sites in the closed scalar hierarchy on the equal-rate scoped branch.",
            authority_paths=(str(AUTHORITY_PATHS["calculator_typed_r_site_uniqueness"]),),
            depends_on=(
                "paper29.sound_speed_selector",
                "paper31.baryon_assignment",
                "paper32.typed_baryon_slot_spec",
                "calculator.thomson_history_realization",
                "local.typed_r_operator",
            ),
            premises=(
                "`paper29.sound_speed_selector` fixes the primitive local enthalpy ratio on `omega_b,geom` for the local acoustic leg.",
                "`paper31.baryon_assignment` proves photon-baryon coupling is composite in `(kappa', R)` and that diffusion is not a one-slot baryon observable.",
                "`paper32.typed_baryon_slot_spec` and its lower-triangular boundary forbid observer/readout back-propagation and any hierarchy-wide one-slot collapse of `R`.",
                "`calculator.thomson_history_realization` fixes the exact drag/hierarchy tuple consumed by the local hierarchy.",
                "`local.typed_r_operator` provides the candidate site map to test for uniqueness.",
            ),
            proof_outline=(
                "Kill every alternative that moves pressure or inertia off the primitive local enthalpy object; doing so would require a drag-vs-sound branch separation or observer-side back-propagation that the current stack explicitly forbids.",
                "Use the local hierarchy convention `tau_c = 1 / thomson_drag_rate` to fix the momentum-exchange pair uniquely as photon-side `1/tau_c` and baryon-side `R_local / tau_c`; the inverse-`R` alternative is a convention mismatch on this carrier rather than a second admissible site.",
                "Identify the diffusion heat term with the slip/TCA sector and the viscosity term with the photon hierarchy sector; any swapped or collapsed rate placement breaks the explicit local generator even though the equal-rate limit hides that distinction numerically.",
                "Conclude by elimination that the carried site map is the unique admissible typed hierarchy operator at the four actual insertion sites.",
            ),
            scope_boundary=(
                "Uniqueness theorem for the local closed scalar hierarchy sites on the accepted equal-rate scoped branch only.",
                "Does not claim that the final observed peak-height pattern is itself a primitive one-slot baryon observable.",
                "Does not validate the late-time TT driver handoff numerically.",
            ),
            notes=(
                "The theorem text is self-contained here; the linked report is supplementary supporting material only.",
            ),
        ),
        "local.typed_thomson_split_history_realization": TheoremNode(
            node_id="local.typed_thomson_split_history_realization",
            kind="theorem",
            label="Typed Split Thomson-history Realization Theorem",
            claim_status="derived / scoped as maps",
            statement=(
                "The live conformal Thomson tuple is built through the typed split history path "
                "`kappa'_loc(z) = a n_e(z) sigma_T` on the local chemistry/electron-inventory branch, "
                "then the observer-side optical packet "
                "`d tau_obs / dz`, `tau_obs`, `g_obs = exp(-tau_obs) d tau_obs / dz`, "
                "and finally the accepted equal-rate scoped conformal tuple "
                "`thomson_drag_rate = |(d tau_obs / dz) / (dC / dz)|`, "
                "`thomson_hierarchy_rate = thomson_drag_rate`, "
                "`tau_c = 1 / thomson_drag_rate`, "
                "`dtau_c = - d(thomson_drag_rate) tau_c^2`. "
                "So the implementation realizes the tuple from typed local opacity plus typed visibility/readout history, not from one undifferentiated opacity scalar."
            ),
            scope="Implementation-level typed path from Stage-2 chemistry history to the accepted equal-rate scoped conformal Thomson tuple.",
            authority_paths=(str(AUTHORITY_PATHS["calculator_typed_thomson_split_history_audit"]),),
            depends_on=(
                "paper31.baryon_assignment",
                "calculator.thomson_history_realization",
            ),
            premises=(
                "`paper31.baryon_assignment` fixes primitive local opacity on the inventory branch and reduced visibility/readout as a distinct downstream layer.",
                "`calculator.thomson_history_realization` fixes the exact tuple grammar consumed by the hierarchy.",
            ),
            proof_outline=(
                "Read the local chemistry/electron history `x_e(z)` and form `kappa'_loc = a n_e sigma_T` explicitly on the local branch.",
                "Build the observer-side visibility packet `(d tau_obs / dz, tau_obs, g_obs)` from that local history without collapsing the two layers.",
                "Transport the observer-side packet onto the conformal clock and then package the Thomson tuple from the transported packet rather than from a raw opacity scalar.",
            ),
            scope_boundary=(
                "Implementation theorem for the scoped equal-rate tuple path used by the current TT driver.",
                "Does not yet derive a nontrivial drag-vs-hierarchy deformation of the Thomson tuple.",
            ),
            notes=(
                "The theorem text is self-contained here; the linked report is supplementary supporting material only.",
            ),
        ),
        "local.closed_scalar_metric_state_builder": TheoremNode(
            node_id="local.closed_scalar_metric_state_builder",
            kind="theorem",
            label="Closed Scalar Metric-state Builder Theorem",
            claim_status="derived / scoped as maps",
            statement=(
                "Once the Einstein-normalized scalar stress summary "
                "`(delta_rho, delta_p, rho_plus_p_theta, rho_plus_p_shear)` is supplied on one closed scalar shell, "
                "the Newtonian metric state is fixed by "
                "`psi = phi - 4.5 (a^2 / k_n^2) rho_plus_p_shear` and "
                "`phi' = -(a'/a) psi + 1.5 (a^2 / k_n^2) rho_plus_p_theta`, "
                "while the synchronous metric state is fixed by "
                "`h' = [k_n^2 s_2^2 eta + 1.5 a^2 delta_rho] / (0.5 a'/a)`, "
                "`eta' = [1.5 a^2 rho_plus_p_theta + 0.5 K h'] / (k_n^2 s_2^2)`, "
                "`alpha = (h' + 6 eta') / (2 k_n^2)`, and "
                "`alpha' = -2 (a'/a) alpha + eta - 4.5 (a^2 / k_n^2) rho_plus_p_shear`."
            ),
            scope="Einstein-side scalar metric-state reconstruction on one explicit closed shell.",
            authority_paths=(),
            depends_on=("paper23.closed_scalar_operator",),
            premises=(
                "`paper23.closed_scalar_operator` fixes the closed scalar shell geometry and the `s_2^2 = 1 - 3K/k_n^2` factor.",
                "The total scalar stress summary is supplied explicitly rather than guessed from a hidden matter model.",
            ),
            proof_outline=(
                "Write the scalar Einstein equations on one physical closed shell in Newtonian and synchronous gauge.",
                "Solve algebraically for the metric variables and their first derivatives from the explicit stress summary.",
                "Feed those metric variables into the acoustic quartet without introducing any extra closure factor.",
            ),
            scope_boundary=(
                "Metric-state builder from an explicit total scalar stress summary only.",
                "Does not derive the stress summary from a full multi-species perturbation hierarchy by itself.",
            ),
            notes=(
                "The theorem text is self-contained here; there is no published paper reference for this post-Paper-32 local completion step.",
            ),
        ),
        "local.closed_scalar_adiabatic_seed_bridge": TheoremNode(
            node_id="local.closed_scalar_adiabatic_seed_bridge",
            kind="theorem",
            label="Closed Scalar Adiabatic-seed Bridge Theorem",
            claim_status="derived / scoped",
            statement=(
                "On the active scalar-source branch, the source shell weight is "
                "`C_N^src = A_s W_N^(+) = A_s ((N+1) / (N_p+1))^(-K_gauge / x)` "
                "on the repaired affine odd-shell plus branch, and the leading radiation-era closed-`S^3` adiabatic seed obeys "
                "`delta_gamma^(S) = -(k_n tau)^2 s_2^2 R_n / 3`, "
                "`theta_gamma^(S) = -k_n (k_n tau)^3 s_2^2 R_n / 36`, "
                "`delta_b^(S) = 3 delta_gamma^(S) / 4`, "
                "`theta_b^(S) = theta_gamma^(S)`, "
                "`eta^(S) = R_n [1 - (k_n tau)^2 / 36]`, "
                "followed by the explicit synchronous-to-Newtonian shift "
                "`delta_gamma^(N) = delta_gamma^(S) - 4 (a'/a) alpha`, "
                "`theta_gamma^(N) = theta_gamma^(S) + k_n^2 alpha`, "
                "`delta_b^(N) = delta_b^(S) - 3 (a'/a) alpha`, and "
                "`theta_b^(N) = theta_b^(S) + k_n^2 alpha`."
            ),
            scope="Active scalar-source shell weight plus leading closed-shell photon-baryon adiabatic seed.",
            authority_paths=(),
            depends_on=("paper32.modular_dtn_field_transfer", "paper32.hidden_identification_repair", "paper23.closed_scalar_operator"),
            premises=(
                "`paper32.modular_dtn_field_transfer` fixes the active scalar-source shell weight `A_s W_N^(+)` on the repaired affine odd-shell plus branch.",
                "`paper23.closed_scalar_operator` fixes the physical scalar-shell support and the closed-shell geometric factor `s_2^2`.",
            ),
            proof_outline=(
                "Take the active scalar-source shell covariance `A_s W_N^(+)` from the source block without adding a new primordial fit.",
                "Write the leading radiation-era closed-shell photon-baryon adiabatic seed in synchronous gauge.",
                "Transform that seed explicitly to Newtonian gauge on the same shell and package the resulting hierarchy state.",
            ),
            scope_boundary=(
                "Leading photon-baryon adiabatic seed on the active scalar-source branch only.",
                "Does not derive low-shell puncture occupations, anomalous phase correlations, or full multi-species isocurvature families.",
            ),
            notes=(
                "The theorem text is self-contained here; there is no published paper reference for this post-Paper-32 local completion step.",
            ),
        ),
        "local.closed_scalar_transfer_projector": TheoremNode(
            node_id="local.closed_scalar_transfer_projector",
            kind="theorem",
            label="Closed Scalar Transfer Projector Theorem",
            claim_status="derived / scoped as maps",
            statement=(
                "Given an explicit closed-shell scalar source history, the transparent LOS source law is "
                "`S_T^(0) = exp(-kappa) phi' + g delta_gamma / 4`, "
                "`S_T^(1) = exp(-kappa) k_n psi + g theta_b / k_n` in Newtonian gauge, "
                "`S_T^(0) = -exp(-kappa) h' / 6 + g delta_gamma / 4`, "
                "`S_T^(1) = g theta_b / k_n`, "
                "`S_T^(2) = exp(-kappa) k_n^2 (2/3) s_2 alpha + g P` in synchronous gauge, "
                "with `S_T^(2) = g P` and `S_E = g P` on the scalar polarization source, "
                "and the exact closed radial chain is "
                "`Phi_0 = sin(beta chi) / [beta sin chi]`, "
                "`Phi_l = [(2l-1) cot chi Phi_{l-1} - sqrt(beta^2-(l-1)^2) Phi_{l-2}] / sqrt(beta^2-l^2)`, "
                "`dPhi_l/dchi = l cot chi Phi_l - sqrt(beta^2-(l+1)^2) Phi_{l+1}`, "
                "`d2Phi_l/dchi^2 = -2 cot chi dPhi_l/dchi + [l(l+1) csc^2 chi - beta^2 + 1] Phi_l`, "
                "so that `Delta_l^T(q)` and `Delta_l^E(q)` are fixed by explicit LOS integration on `chi = sqrt(K) (tau_0 - tau)`."
            ),
            scope="Closed scalar hierarchy-to-transfer projector on one explicit source history and one observer conformal time.",
            authority_paths=(),
            depends_on=(
                "paper22.spatial_mode_ladder",
                "paper23.closed_scalar_operator",
                "local.closed_scalar_metric_state_builder",
            ),
            premises=(
                "`paper22.spatial_mode_ladder` fixes the closed spatial carrier and the scalar radial support on `S^3`.",
                "`paper23.closed_scalar_operator` fixes the discrete scalar shell parameter `beta = n+1` and the physical shell support `n >= 2`.",
                "`local.closed_scalar_metric_state_builder` supplies the explicit scalar metric histories entering the transparent LOS source law.",
            ),
            proof_outline=(
                "Build the transparent scalar LOS sources directly from the hierarchy state, metric state, and observer-absolute visibility packet without rewriting them as hidden CLASS source patches.",
                "Evaluate the exact closed scalar radial chain from the stable recurrence on `beta = n+1` and the radial derivative identities.",
                "Integrate the explicit source and radial kernels on the supplied conformal-time grid to obtain `Delta_l^T(q)` and `Delta_l^E(q)` on the closed support.",
            ),
            scope_boundary=(
                "Exact source law and exact closed radial chain on one explicit scalar history.",
                "Numeric packet values still depend on explicit quadrature on the supplied conformal-time grid.",
                "Does not derive the hierarchy history automatically from the full perturbation evolution problem.",
            ),
            notes=(
                "The theorem text is self-contained here; there is no published paper reference for this post-Paper-32 local completion step.",
            ),
        ),
        "local.closed_scalar_acoustic_generator": TheoremNode(
            node_id="local.closed_scalar_acoustic_generator",
            kind="theorem",
            label="Closed Scalar Acoustic Generator Theorem",
            claim_status="derived / scoped as maps",
            statement=(
                "On one explicit physical closed-`S^3` scalar shell `n >= 2`, the "
                "local photon-baryon acoustic generator is fixed by "
                "`k_n^2 = n(n+2) / R_curv^2`, "
                "`q_n^2 = k_n^2 + K = (n+1)^2 / R_curv^2`, "
                "`s_l = sqrt(1 - K (l^2-1) / k_n^2)`, "
                "`cot_K^gen(tau) = sqrt(K) / [k_n tan(sqrt(K) tau)]`, "
                "local baryon loading `R = 3 rho_b / (4 rho_gamma)` on `omega_b,geom`, "
                "and the explicit scalar RHS "
                "`delta_gamma' = -(4/3)(theta_gamma + metric_continuity)`, "
                "`delta_b' = -(theta_b + metric_continuity)`, "
                "`theta_b' = -a'/a theta_b + metric_euler + k_n^2 c_b^2 delta_b + R * drag_rate * (theta_gamma-theta_b)`, "
                "`theta_gamma' = k_n^2 (delta_gamma/4 - s_2^2 F_2) + metric_euler + drag_rate * (theta_b-theta_gamma)`, "
                "with gauge-to-quartet maps "
                "`(metric_continuity, metric_euler, metric_shear, metric_shear_prime) = (-3 phi', k_n^2 psi, 0, 0)` in Newtonian gauge and "
                "`(h'/2, 0, k_n^2 alpha, k_n^2 alpha')` in synchronous gauge, "
                "with higher multipoles and the reduced TCA contract driven by the coupled tuple "
                "`(thomson_drag_rate, thomson_hierarchy_rate, tau_c, dtau_c, slip, shear)`. "
                "The local primitive loading `R(z)` used here is not a silent one-slot collapse of the full hierarchy-wide perturbation `R` slot."
            ),
            scope="Local affine scalar acoustic generator on an explicit sampled closed-`S^3` shell.",
            authority_paths=(str(AUTHORITY_PATHS["calculator_closed_scalar_acoustic_generator"]),),
            depends_on=(
                "paper23.closed_scalar_operator",
                "paper29.sound_speed_selector",
                "paper32.typed_baryon_slot_spec",
                "calculator.thomson_history_realization",
                "local.typed_r_site_uniqueness",
            ),
            premises=(
                "`paper23.closed_scalar_operator` fixes the discrete scalar shell support and the shifted scalar operator on `S^3`.",
                "`paper29.sound_speed_selector` fixes the theorem-grade local inertia loading `R(z)` on `omega_b,geom` for the primitive acoustic leg.",
                "`paper32.typed_baryon_slot_spec` forbids collapsing the hierarchy to one baryon slot and keeps the metric-source leg explicit.",
                "`calculator.thomson_history_realization` fixes the exact coupled Thomson tuple that an admissible local closure must consume.",
                "`local.typed_r_site_uniqueness` proves that the carried site-wise `R` hierarchy operator is the unique admissible placement at the actual oscillator sites.",
            ),
            proof_outline=(
                "Insert the closed-`S^3` scalar shell identities into the non-flat scalar hierarchy so the geometric recurrence factors are explicit on each discrete `n` shell.",
                "Use the theorem-grade local history sample `(x_e, T_m)` to recover `c_b^2` and its derivative, and use the theorem-grade primitive loading `R(z)` together with its typed Thomson-tuple composites for the local momentum-loading leg.",
                "Feed the coupled Thomson tuple into the baryon drag, photon hierarchy damping, and tight-coupling contract equations to obtain the full local scalar photon-baryon RHS at explicit sample level.",
                "Conclude that the local generator itself is fixed once the external metric-drive and Stage-2/Thomson sample builders are supplied explicitly.",
            ),
            scope_boundary=(
                "Local explicit-sample scalar generator only.",
                "Does not derive the exact Stage-2 dynamic-network history builder or the total multi-species stress summary by itself.",
                "Does not by itself integrate the full scalar history from initial conditions to transfer packets without those explicit upstream builders.",
                "No theorem-grade hierarchy-wide one-slot collapse on `R` is claimed anywhere in this map.",
            ),
            notes=(
                "The theorem text is self-contained here; the linked report is supplementary supporting material only.",
            ),
        ),
        "local.scoped_closed_scalar_pipeline": TheoremNode(
            node_id="local.scoped_closed_scalar_pipeline",
            kind="theorem",
            label="Scoped Closed-scalar Pipeline Theorem",
            claim_status="conditional / scoped",
            statement=(
                "On the active scalar-source branch, the composed closed-`S^3` scalar map from "
                "`(P_src, C_N^src, ic_n, Y_rec, Thomson tuple, stress summary)` "
                "to `y^(n)(tau)`, then to `Delta_l^X(q)`, and then to shell-summed `C_l`, "
                "is carried end-to-end once the exact Stage-2 history enters through the conditional inherited-FULL builder. "
                "The carrier laws, metric formulas, projector formulas, and LOS formulas remain `derived / scoped as maps`, "
                "while the full composition is only `conditional / scoped` because it inherits the Stage-2 builder status. "
                "No silent one-slot collapse on the hierarchy-wide perturbation `R` slot appears anywhere in this composition."
            ),
            scope="Composed active-branch closed-scalar pipeline from source shell to transfer packets and shell-summed spectra.",
            authority_paths=(),
            depends_on=(
                "paper32.modular_dtn_field_transfer",
                "local.closed_scalar_adiabatic_seed_bridge",
                "local.inherited_full_stage2_dynamic_history_builder",
                "calculator.thomson_history_realization",
                "local.closed_scalar_metric_state_builder",
                "local.closed_scalar_acoustic_generator",
                "local.closed_scalar_transfer_projector",
                "paper28.closed_s3_shell_power",
                "paper32.closed_s3_solver_spec",
            ),
            premises=(
                "`paper32.modular_dtn_field_transfer` fixes the active scalar source block.",
                "`local.closed_scalar_adiabatic_seed_bridge` fixes the active closed-shell source-to-initial-condition bridge.",
                "`local.inherited_full_stage2_dynamic_history_builder` supplies the exact sampled Stage-2 history carrier at conditional inherited-FULL scope.",
                "`calculator.thomson_history_realization` fixes the exact coupled Thomson tuple that the local hierarchy map must consume.",
                "`local.closed_scalar_metric_state_builder`, `local.closed_scalar_acoustic_generator`, and `local.closed_scalar_transfer_projector` provide the explicit map-level formulas from shell data to transfer packets.",
                "`paper28.closed_s3_shell_power` and `paper32.closed_s3_solver_spec` supply the shell weighting and closed-space LOS assembly grammar.",
            ),
            proof_outline=(
                "Compose the active scalar source block, closed-shell seed bridge, sampled Stage-2 history, Thomson tuple, metric-state builder, local acoustic generator, and scalar transfer projector without inserting any hidden flat-space or CLASS default.",
                "Carry the resulting transfer packets into the explicit shell-weighted `C_l` assembly on the closed support.",
                "Track the claim status through the composition: map-level formulas remain `derived / scoped as maps`, while the full end-to-end pipeline inherits `conditional / scoped` status from the Stage-2 history builder.",
            ),
            scope_boundary=(
                "Full composed active-branch scalar pipeline only.",
                "Conditional on the inherited-FULL Stage-2 history builder rather than a universal IO-native Stage-2 renormalization theorem.",
                "No theorem-grade hierarchy-wide one-slot collapse on `R` is licensed anywhere in this composition.",
                "Not a universal automatic TT/TE/EE solver closure for arbitrary branches or sectors.",
            ),
            notes=(
                "The theorem text is self-contained here; there is no published paper reference for this post-Paper-32 composed-pipeline step.",
            ),
        ),
        "local.scoped_tt_driver": TheoremNode(
            node_id="local.scoped_tt_driver",
            kind="theorem",
            label="Scoped TT Driver Composition Theorem",
            claim_status="conditional / scoped",
            statement=(
                "On the active scalar-source branch, the executable TT carrier is the explicit composition "
                "`Y_rec^scoped -> Thomson^conf -> metric/state history -> Delta_l^T(q) -> C_l^TT`, "
                "with the Stage-2 segment supplied by the inherited-FULL builder on `z <= z_exact_max`, "
                "a thermal `x_e = 1`, `T_m = T_R` prehistory extension on `z > z_exact_max`, "
                "the repaired odd-shell source support, the explicit shell weight "
                "`w(n) = ((n+1)^2 / (2 pi^2 R^3)) P_X(n)`, and one common early-time carrier for the whole run. "
                "The resulting `C_l^TT` array is a conditional/scoped executable spectrum rather than a theorem-grade validated full CMB closure."
            ),
            scope="Executable active-branch TT driver on the current repaired branch.",
            authority_paths=(),
            depends_on=(
                "local.inherited_full_stage2_dynamic_history_builder",
                "local.typed_thomson_split_history_realization",
                "local.closed_scalar_acoustic_generator",
                "local.closed_scalar_transfer_projector",
                "paper28.closed_s3_shell_power",
                "local.scoped_closed_scalar_pipeline",
            ),
            premises=(
                "`local.inherited_full_stage2_dynamic_history_builder` supplies the conditional Stage-2 history segment used by the executable branch.",
                "`local.typed_thomson_split_history_realization` fixes the equal-rate typed Thomson-history path consumed by the local hierarchy carrier.",
                "`local.closed_scalar_acoustic_generator`, `local.closed_scalar_transfer_projector`, and `paper28.closed_s3_shell_power` provide the map-level hierarchy, projector, and shell-sum laws.",
                "`local.scoped_closed_scalar_pipeline` fixes the composed closed-scalar grammar and its status discipline.",
            ),
            proof_outline=(
                "Build the scoped history carrier from the inherited-FULL exact segment plus the explicit thermal prehistory extension.",
                "Transport that history onto the conformal Thomson tuple, evolve the repaired closed-scalar hierarchy shell by shell, project the source histories to `Delta_l^T(q)`, and assemble the shell-summed `C_l^TT` array.",
                "Keep the runtime status honest: executable and reproducible, but only conditional/scoped because the history carrier inherits the inherited-FULL Stage-2 status and the high-shell source/phase frontier remains open.",
            ),
            scope_boundary=(
                "Executable TT carrier only.",
                "Does not by itself prove that the returned spectrum is physically correct for arbitrary shell ceilings or arbitrary history-carrier choices.",
                "Retains one common early-time carrier for the whole run; any shell-local alternative would require a new theorem-grade phase map.",
            ),
            notes=(
                "The theorem text is self-contained here; there is no published paper reference for this post-Paper-32 executable TT composition step.",
            ),
        ),
        "local.scoped_tt_first_peak_support": TheoremNode(
            node_id="local.scoped_tt_first_peak_support",
            kind="theorem",
            label="Scoped TT First-peak Support Theorem",
            claim_status=TT_FIRST_PEAK_APPROVED_STATUS,
            statement=(
                f"{TT_FIRST_PEAK_APPROVED_STATUS} On that canonical carrier "
                f"`(exact_history_samples, prehistory_samples, n_max, shell_step) = "
                f"({TT_FIRST_PEAK_CANONICAL_EXACT_HISTORY_SAMPLES}, "
                f"{TT_FIRST_PEAK_CANONICAL_PREHISTORY_SAMPLES}, "
                f"{TT_FIRST_PEAK_CANONICAL_N_MAX}, "
                f"{TT_FIRST_PEAK_CANONICAL_SHELL_STEP})` with "
                "`constraint_metric_source_only = True`, `constraint_consistent_seed = True`, "
                "`metric_baryon_momentum_slot = omega_b,eff`, repaired odd-shell "
                "source support, and covariance shell weights, the executable "
                "TT spectrum lands in the physical first-peak family with "
                f"`ell_peak = {TT_FIRST_PEAK_CANONICAL_ELL_PEAK:.0f}`, "
                f"`C_220 / C_peak = {TT_FIRST_PEAK_CANONICAL_C220_OVER_PEAK}`, "
                f"and `C_2 / C_30 = {TT_FIRST_PEAK_CANONICAL_C2_OVER_C30}`. "
                f"The neighboring ceiling `n_max = {TT_FIRST_PEAK_NEIGHBOR_N_MAX}` "
                f"stays on the same family with `ell_peak = {TT_FIRST_PEAK_NEIGHBOR_ELL_PEAK:.0f}` "
                f"and `C_220 / C_peak = {TT_FIRST_PEAK_NEIGHBOR_C220_OVER_PEAK}`. "
                f"{TT_FIRST_PEAK_OPEN_FRONTIER}"
            ),
            scope=(
                "Canonical repaired active-branch TT first-peak carrier only, "
                "with the surviving high-shell ceiling drift left explicit."
            ),
            authority_paths=(str(AUTHORITY_PATHS["calculator_tt_first_peak_support"]),),
            depends_on=(
                "local.scoped_tt_driver",
                "calculator.peak_functional_separation",
            ),
            premises=(
                "`local.scoped_tt_driver` provides the executable repaired TT carrier on which the first-peak audit is performed.",
                "`calculator.peak_functional_separation` keeps the reported peak functional explicit rather than collapsing it to the background angle by fiat.",
            ),
            proof_outline=(
                "Run the canonical repaired TT carrier on the full odd-support ladder through `n_max = 501` and record the resulting discrete TT peak functional.",
                "Cross-check the neighboring ceiling `n_max = 453` to show the same first-peak family survives below the canonical ceiling.",
                "Check `n_max = 601` on the same repaired branch and record the surviving upward drift as the exact remaining open boundary rather than hiding it.",
            ),
            scope_boundary=(
                "Canonical repaired first-peak carrier only.",
                "This is not a theorem-grade full high-`ell` TT closure.",
                TT_FIRST_PEAK_OPEN_FRONTIER,
            ),
            notes=(
                "The theorem text is self-contained here; the linked report is supplementary supporting material only.",
            ),
        ),
        "calculator.null_family_acoustic_readout": TheoremNode(
            node_id="calculator.null_family_acoustic_readout",
            kind="theorem",
            label="Null-family Acoustic Readout Theorem",
            claim_status="derived / scoped",
            statement=(
                "The explicit null-family readout field "
                "`omega_hat(eta) = (ev_eta tensor C_n) P_src(Phi)` can be built "
                "from the theorem-grade source block, and the resulting "
                "background acoustic estimator class "
                "`E_rs = integral_0^{eta_rec} c_s(eta) R_hist^ac(omega_hat(eta)) d eta` "
                "is itself one-slot on the current scoped sector."
            ),
            scope="Explicit null-family acoustic readout field and estimator class.",
            authority_paths=(str(AUTHORITY_PATHS["calculator_null_family_readout"]),),
            depends_on=("paper32.modular_dtn_field_transfer", "paper29.sound_speed_selector"),
            premises=(
                "`paper32.modular_dtn_field_transfer` closes the one-slot source/readout block `P_src`.",
                "`paper29.sound_speed_selector` fixes the theorem-grade local sound-speed slot entering the acoustic estimator kernel.",
                "Gauge-neutral direction collection and history evaluation preserve one-slot degree on the current scoped sector.",
            ),
            proof_outline=(
                "Evaluate the one-slot source block at fixed history label and readout direction to obtain `omega_hat(eta)`.",
                "Apply the already-closed homogeneous acoustic history-reduction operator to that explicit field.",
                "Integrate against the theorem-grade sound-speed kernel to obtain the background acoustic estimator class without creating a second gauge slot.",
            ),
            scope_boundary=(
                "Explicit readout field and estimator class only.",
                "Does not yet derive the exact acoustic endpoint/phase scalar or the final peak-position angle.",
            ),
        ),
        "calculator.peak_functional_separation": TheoremNode(
            node_id="calculator.peak_functional_separation",
            kind="theorem",
            label="Peak-functional Separation Theorem",
            claim_status="derived / scoped",
            statement=(
                "The background ratio "
                "`100theta_s = 100 r_s(z_rec) / D_M(z_rec)` is not, by itself, "
                "the exact physical peak-position readout `theta_peak`; theorem-grade "
                "numeric closure requires either the exact `A_peak` / closed-`S^3` "
                "perturbation readout or a separate theorem identifying that peak "
                "functional with the background ratio on the relevant scope."
            ),
            scope="Boundary between background acoustic ratios and physical peak-position readout.",
            authority_paths=(str(AUTHORITY_PATHS["calculator_peak_functional_separation"]),),
            depends_on=("paper32.closed_s3_solver_spec",),
            premises=(
                "`paper32.closed_s3_solver_spec` fixes the full linear IO transfer as a typed map with a perturbation/readout side beyond the source block.",
                "Peak-position observables live downstream of the primitive sky field and the quadratic power spectrum rather than at the raw background ratio alone.",
            ),
            proof_outline=(
                "Place `theta_peak` on the measurement chain `primitive field -> harmonic coefficients -> C_l -> A_peak`.",
                "Use the typed-transfer theorem to separate the background ratio from the unresolved perturbation/readout block.",
                "Conclude that no theorem may identify the numeric peak-position angle with `100theta_s` alone without an additional peak/readout identification theorem.",
            ),
            scope_boundary=(
                "Boundary theorem only.",
                "Does not itself derive the final `A_peak -> theta_peak` identification law.",
            ),
        ),
        "paper35.late_baryon_counting_law": TheoremNode(
            node_id="paper35.late_baryon_counting_law",
            kind="theorem",
            label="Late-time Baryon-counting Law",
            claim_status="derived / scoped under Premise 2 standard low-temperature baryonic matter",
            statement=(
                "On the late-time baryonic dust sector, "
                "`n_b = rho_b / m_bar * [1 + O(k_B T / (m_p c^2))]`, so the "
                "surviving normalization ambiguity is the standard mean-baryon-mass "
                "convention rather than an open IO-side bridge."
            ),
            scope="Late-time baryon-number conversion on the active branch.",
            authority_paths=(),
            depends_on=("premise.2", "paper21.branch_assignment"),
            premises=(
                "`premise.2` licenses standard low-temperature baryonic matter inside the horizon.",
                "`paper21.branch_assignment` fixes the active branch and its carried `omega_b,geom` slot.",
            ),
            proof_outline=(
                "Treat the late-time matter sector as nonrelativistic baryonic dust on the active branch.",
                "Convert rest-mass density to baryon number density with the standard mean mass per baryon.",
                "Keep the remaining normalization ambiguity explicit as a standard mass convention rather than an unresolved framework theorem gap.",
            ),
            scope_boundary=(
                "Late-time baryonic dust sector only.",
                "Does not provide a primordial/source-era baryogenesis theorem.",
            ),
            notes=(
                "No published paper reference is used here; the theorem text is carried self-contained in the calculator dictionary.",
            ),
        ),
        "paper35.eta_io_late_closure": TheoremNode(
            node_id="paper35.eta_io_late_closure",
            kind="theorem",
            label="Late-time eta_IO Closure Theorem",
            claim_status="derived / scoped",
            statement=(
                "The preferred late-time baryon-to-photon ratio "
                f"`eta_IO = n_b / n_gamma = {eta_late:.12e}` is closed on the "
                "active branch, equivalently "
                "`eta_IO,late = C_eta(T_obs, m_bar) * omega_b,geom`."
            ),
            scope="Late-time baryon-to-photon ratio convention used by the calculator.",
            authority_paths=(),
            depends_on=("paper21.branch_assignment", "paper35.late_baryon_counting_law"),
            premises=(
                "`paper21.branch_assignment` fixes the active branch package.",
                "`paper35.late_baryon_counting_law` converts the carried mass density to baryon number density on the late-time dust sector.",
                "The calculator needs one carried late-time `eta_IO` convention rather than multiple unresolved conventions.",
            ),
            proof_outline=(
                "Start from the active-branch physical-density slot `omega_b,geom` together with the late-time baryon-counting law.",
                "Convert the active-branch baryon density and observed CMB temperature into the baryon-to-photon prefactor `C_eta(T_obs, m_bar)`.",
                "Fix the preferred exported `eta_IO,late` convention to that closed branch value.",
                "Expose the convention directly through the calculator and bundle.",
            ),
            scope_boundary=(
                "Preferred late-time `eta_IO` convention on the active branch.",
                "Does not claim that every alternative mass convention is closed to theorem grade.",
            ),
            notes=(
                "No published paper reference is used here; the theorem text is carried self-contained in the calculator dictionary.",
            ),
        ),
        "paper24.conditional_lithium_scorecard": TheoremNode(
            node_id="paper24.conditional_lithium_scorecard",
            kind="theorem",
            label="Paper 24 Conditional Lithium Scorecard",
            claim_status="conditional / scoped",
            statement=(
                "Conditional on the Paper 22 BBN premise package and one "
                "empirical cluster-deformation input, the channel-resolved "
                "mass-7 route lands "
                f"`Li-7/H = {ACTIVE_BBN_LI7_RATIO:.15e}` with zero fitted "
                "parameters while preserving the repaired deuterium and helium "
                "scorecard."
            ),
            scope="Conditional active BBN lithium repair scorecard.",
            authority_paths=(str(AUTHORITY_PATHS["paper24_lithium_paper"]),),
            depends_on=("premise.1", "premise.2", "paper12.baryon_dictionary_fraction"),
            premises=(
                "`premise.1` and `premise.2` fix the IO BBN setting.",
                "`paper12.baryon_dictionary_fraction` provides the repaired baryon-fraction route inherited by the active BBN scorecard.",
                "The surviving lithium closure is conditional on the Paper 22 BBN premise package and one empirical cluster-deformation input.",
            ),
            proof_outline=(
                "Use the Paper 24 channel-resolved mass-7 route rather than uniform TT dressing or destruction-side fixes.",
                "Condition that route on the surviving Paper 22 premise package plus the empirical cluster-deformation input.",
                "Evaluate the resulting active lithium scorecard while keeping the non-mass-7 outputs on the repaired BBN scorecard.",
            ),
            scope_boundary=(
                "Conditional lithium-repair scorecard only.",
                "Does not license an unconditional theorem-grade lithium closure independent of the Paper 22 premise package and cluster deformation input.",
            ),
        ),
        "calculator.phase_equivalent_selector": TheoremNode(
            node_id="calculator.phase_equivalent_selector",
            kind="theorem",
            label="Phase-equivalent Selector Theorem",
            claim_status="derived / scoped",
            statement=(
                "The strict-bare selector backbone solves "
                "`theta_bare(z_sel) = r_s(z_sel) / D_M(z_sel)` on the certified "
                "monotone interval and carries observer-side angle by "
                "`theta_obs = J_theta theta_bare` with fixed `J_theta`."
            ),
            scope="Strict-bare phase-ruler selector backbone.",
            authority_paths=(str(AUTHORITY_PATHS["calculator_phase_selector"]),),
            depends_on=("premise.1", "premise.2", "paper21.branch_assignment"),
            premises=(
                "`premise.1` and `premise.2` fix the IO setting.",
                "`paper21.branch_assignment` fixes the active branch package on which the selector is evaluated.",
                "The strict-bare selector interval is certified monotone on its published domain.",
            ),
            proof_outline=(
                "Use the certified monotone interval to make the strict-bare selector exactly invertible on the published branch domain.",
                "Map the selected bare phase-ruler leaf to observer-side `theta` with the fixed Jacobian `J_theta`.",
                "Reduce theorem-grade numeric `theta_*` to identifying the physical selector leaf carried by the active branch.",
            ),
            scope_boundary=(
                "Strict-bare selector backbone on the certified interval.",
                "Does not by itself identify which leaf is physical on the active branch.",
            ),
        ),
        "calculator.packet_coefficient_fixing": TheoremNode(
            node_id="calculator.packet_coefficient_fixing",
            kind="theorem",
            label="Packet Coefficient Fixing Theorem",
            claim_status="derived / scoped plus verified / support-promoted",
            statement=(
                "The outgoing-update and Ly-line coefficients are fixed on the "
                "surviving packet law by "
                "`xr[1] = 3 x1s Dfplus_Ly[0]` and "
                "`xr[0] = x1s exp(E32 / TR) Dfplus_Ly[1]`, yielding the "
                "support-reduced packet carrier close to the final active endpoint."
            ),
            scope="Packet-law closure on the surviving active endpoint family.",
            authority_paths=(
                str(AUTHORITY_PATHS["calculator_packet_coefficient_fixing"]),
                str(AUTHORITY_PATHS["calculator_packet1500_support_promotion"]),
            ),
            depends_on=("calculator.phase_equivalent_selector",),
            premises=(
                "`calculator.phase_equivalent_selector` reduces `theta_*` closure to fixing the active packet and leaf carrier.",
                "The surviving outgoing-update packet law is constrained by the accepted Calculator boundary transport identities.",
            ),
            proof_outline=(
                "Use the outgoing-update and Ly-line boundary transport identities to fix the live packet-law coefficients rather than fitting them.",
                "Construct the support-reduced packet carrier on the surviving active endpoint family with those fixed coefficients.",
                "Show that the reduced carrier lands very close to the final active endpoint while keeping the coefficients theorem-governed.",
            ),
            scope_boundary=(
                "Packet-law closure on the surviving active endpoint family.",
                "Does not yet prove that the surviving packet alone carries the physical selector leaf.",
            ),
        ),
        "calculator.highz_tail_slaving": TheoremNode(
            node_id="calculator.highz_tail_slaving",
            kind="theorem",
            label="High-z Tail Slaving Theorem",
            claim_status="derived / scoped plus verified / support sharpening",
            statement=(
                "Support above `z ~ 1500` is demoted to a slaved residual tail "
                "rather than an independent selector-bearing sector, with the "
                "reduced packet differing from the full endpoint family only by "
                "`Delta_theta = +5.386582264233e-06` and "
                "`Delta_ell = -4.390006880612e-04`."
            ),
            scope="Endpoint-family support decomposition.",
            authority_paths=(str(AUTHORITY_PATHS["calculator_highz_tail_slaving"]),),
            depends_on=("calculator.packet_coefficient_fixing",),
            premises=(
                "`calculator.packet_coefficient_fixing` isolates the live packet carrier near the active endpoint.",
                "Any support above `z ~ 1500` still has to be checked for an independent selector-bearing branch.",
            ),
            proof_outline=(
                "Audit the continuation of the active endpoint family above the reduced packet support.",
                "Show that the remaining high-`z` contribution is slaved to the packet carrier rather than introducing a second independent selector sector.",
                "Demote the high-`z` continuation to a residual tail in the active-branch support decomposition.",
            ),
            scope_boundary=(
                "Support decomposition on the active endpoint family.",
                "Does not by itself identify the physical selector leaf.",
            ),
        ),
        "calculator.peak_window_tail_profile_audit": TheoremNode(
            node_id="calculator.peak_window_tail_profile_audit",
            kind="audit",
            label="Peak-window Tail Profile Audit",
            claim_status="verified / scoped",
            statement=(
                "After the best pure-amplitude rescale is removed, the residual "
                "first-peak parent-profile mismatch obeys "
                "`RMS_rel[ell in [190,250]] = 2.950052007950388e-06`, so the "
                "remaining tail is not a second active selector-bearing branch."
            ),
            scope="First-peak TT parent-profile audit on the active endpoint family.",
            authority_paths=(str(AUTHORITY_PATHS["calculator_peak_window_tail_profile_audit"]),),
            depends_on=("calculator.highz_tail_slaving",),
            premises=(
                "`calculator.highz_tail_slaving` demotes the high-`z` continuation to a residual tail candidate.",
                "The physical relevance of that tail still has to be checked against the first-peak parent profile.",
            ),
            proof_outline=(
                "Compare the first-peak parent profile with and without the residual tail after removing the best pure-amplitude rescale.",
                "Measure the remaining mismatch on the peak window and show that it is tiny.",
                "Use that audit to rule out the residual tail as a second active selector-bearing branch.",
            ),
            scope_boundary=(
                "First-peak TT parent-profile audit on the active endpoint family.",
                "Verified only on the relevant first-peak window, not as a full-spectrum theorem.",
            ),
        ),
        "calculator.selector_support_promotion": TheoremNode(
            node_id="calculator.selector_support_promotion",
            kind="theorem",
            label="Selector-support Promotion Theorem",
            claim_status="derived / scoped plus verified / carried selector closure",
            statement=(
                "The support-certified cumulative packet `z_cross < 1500` carries "
                "the physical selector leaf on the active branch, fixing "
                f"`z_sel = {theta_star.selector_leaf_z:.12f}`."
            ),
            scope="Carried active-branch physical selector leaf.",
            authority_paths=(str(AUTHORITY_PATHS["calculator_selector_support_promotion"]),),
            depends_on=(
                "calculator.packet_coefficient_fixing",
                "calculator.highz_tail_slaving",
                "calculator.peak_window_tail_profile_audit",
            ),
            premises=(
                "`calculator.packet_coefficient_fixing` provides the support-reduced active carrier.",
                "`calculator.highz_tail_slaving` and `calculator.peak_window_tail_profile_audit` remove the residual tail as an independent selector branch.",
            ),
            proof_outline=(
                "Promote the cumulative packet `z_cross < 1500` from a reduced support object to the carried physical selector carrier on the active branch.",
                "Collapse the old endpoint-family selector interval to the leaf transported by that certified support packet.",
                "Feed the carried leaf back into the Calculator selector backbone as the physical active-branch leaf.",
            ),
            scope_boundary=(
                "Carried active-branch physical selector leaf only.",
                "Does not establish a universal selector-promotion theorem off branch.",
            ),
        ),
        "calculator.active_branch_theta_star": TheoremNode(
            node_id="calculator.active_branch_theta_star",
            kind="theorem",
            label="Active-branch Theta-star Theorem",
            claim_status="derived / scoped",
            statement=(
                "Evaluating the exact strict-bare selector backbone at the carried "
                "active selector leaf gives "
                f"`theta_bare = {theta_star.theta_bare_deg:.12f} deg`, "
                f"`theta_obs = {theta_star.theta_obs_deg:.12f} deg`, and "
                f"`100theta_* = {theta_star.theta_star_100:.12f}` on the fixed "
                "active branch package."
            ),
            scope="Fixed active Paper 10 legacy projected branch only.",
            authority_paths=(str(AUTHORITY_PATHS["calculator_active_theta_star"]),),
            depends_on=("calculator.selector_support_promotion", "calculator.phase_equivalent_selector"),
            premises=(
                "`calculator.selector_support_promotion` fixes the carried physical selector leaf on the active branch.",
                "`calculator.phase_equivalent_selector` gives the exact observer-side map from that leaf to `theta_*`.",
            ),
            proof_outline=(
                "Evaluate the exact strict-bare selector backbone at the carried active selector leaf.",
                "Obtain `theta_bare`, transport to `theta_obs` with the fixed Jacobian `J_theta`, and report `100theta_*` for the active branch.",
                "Check the same carried solution against the direct first TT peak observable so the derived number remains tied to the measured peak position.",
            ),
            scope_boundary=(
                "Fixed active Paper 10 legacy projected branch only.",
                "Theorem-grade numeric closure on the carried selector leaf only.",
                "Not a universal off-branch transfer theorem or a full TT/TE/EE solver closure.",
            ),
        ),
    }


def explained_output_specs() -> dict[str, dict[str, Any]]:
    """Return the currently published explained-output families."""

    return {
        "theta_star_theorem": {
            "label": "Theorem-grade active-branch theta_*",
            "claim_status": "derived / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {},
            "note": (
                "First fully explained calculator output; includes the complete "
                "accepted theorem chain and the direct-observable peak comparison."
            ),
        },
        "branch_rd_mpc": {
            "label": "Active-branch r_d",
            "claim_status": "derived / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {},
            "note": (
                "Full theorem chain installed for the active-branch pre-drag "
                "ruler, including the sound-speed baryon-slot selector."
            ),
        },
        "branch_h0": {
            "label": "Active-branch H0",
            "claim_status": "derived / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {},
            "note": (
                "Carried active-branch Hubble constant exposed as its own "
                "explained output card."
            ),
        },
        "branch_omega_m": {
            "label": "Active-branch Omega_m",
            "claim_status": "derived / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {},
            "note": (
                "Active-branch matter density surfaced directly from the "
                "reviewed runtime package."
            ),
        },
        "branch_omega_k": {
            "label": "Active-branch Omega_k",
            "claim_status": "derived / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {},
            "note": (
                "Closed-space curvature density from the carried active branch."
            ),
        },
        "branch_omega_lambda": {
            "label": "Active-branch Omega_Lambda",
            "claim_status": "derived / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {},
            "note": (
                "Active-branch dark-energy density surfaced as a standalone "
                "explained output."
            ),
        },
        "active_t_cmb": {
            "label": "Active-branch T_CMB",
            "claim_status": "derived / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {},
            "note": (
                "Observer-side CMB temperature carried by the GTTP thermal "
                "readout law on the active branch."
            ),
        },
        "bare_master_clock_age": {
            "label": "Bare master-clock age",
            "claim_status": "derived / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {},
            "note": (
                "Bare local age integral surfaced separately from the projected "
                "observer-side age already shown in background snapshots."
            ),
        },
        "scalar_tilt_ns": {
            "label": "Active scalar tilt n_s",
            "claim_status": "conditional / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {},
            "note": (
                "This card preserves the live Boundary Fixed-point Principle "
                "status instead of upgrading tilt by presentation."
            ),
        },
        "native_scalar_amplitude_as": {
            "label": "Active scalar amplitude A_s",
            "claim_status": "derived / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {},
            "note": (
                "Native scalar amplitude carried by the modular-DtN source "
                "block is surfaced as its own explained output."
            ),
        },
        "bbn_deuterium_ratio": {
            "label": "Active BBN deuterium scorecard",
            "claim_status": "derived / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {},
            "note": (
                "Fixed active deuterium prediction surfaced as a standalone "
                "BBN output card."
            ),
        },
        "bbn_helium_fraction": {
            "label": "Active BBN helium scorecard",
            "claim_status": "derived / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {},
            "note": (
                "Primordial helium mass fraction carried by the active branch "
                "package is surfaced as its own BBN card."
            ),
        },
        "bbn_lithium_ratio": {
            "label": "Conditional BBN lithium scorecard",
            "claim_status": "conditional / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {},
            "note": (
                "Lithium remains explicitly conditional on the Paper 22 premise "
                "package plus cluster-deformation input."
            ),
        },
        "baryon_fraction_fb": {
            "label": "Baryon dictionary fraction",
            "claim_status": "derived / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {},
            "note": (
                "Framework baryon inventory fraction surfaced separately from "
                "observable-specific baryon slots."
            ),
        },
        "eta_io_late": {
            "label": "Late-time eta_IO",
            "claim_status": "derived / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {},
            "note": (
                "Full theorem chain installed for the preferred late-time "
                "`eta_IO` convention on the active branch."
            ),
        },
        "background_snapshot": {
            "label": "Closed-FRW background snapshot",
            "claim_status": "derived / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {
                "z": {"type": "float", "default": 0.57, "meaning": "observer-side redshift"}
            },
            "note": (
                "Full theorem chain installed for parameterized background "
                "snapshots, including the carried active-branch `r_d` slot."
            ),
        },
        "recombination_point": {
            "label": "Local recombination primitives at one z",
            "claim_status": "derived / scoped",
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {
                "z": {"type": "float", "default": 1100.0, "meaning": "observer-side redshift"},
                "x_e_override": {
                    "type": "float | null",
                    "default": None,
                    "meaning": "optional user-supplied ionization fraction; makes the output conditional",
                },
            },
            "note": (
                "Full theorem chain installed for the default theorem-grade "
                "local-state primitives, with the override path kept explicitly conditional."
            ),
        },
        "tt_first_peak_support": {
            "label": "Canonical TT first-peak support",
            "claim_status": TT_FIRST_PEAK_APPROVED_STATUS,
            "provenance_status": "full",
            "zero_fitted_parameters": True,
            "conditional_on_premises": ["premise.1", "premise.2"],
            "parameters": {},
            "note": (
                "First published IO-native CMB TT spectrum card on the "
                "repaired active-branch canonical carrier, with the surviving "
                "`n_max >= 601` drift surfaced explicitly."
            ),
        },
    }


def explain_active_branch_theta_star() -> ExplainedValue:
    """Return the first fully explained published calculator output."""

    theta = compute_active_branch_theta_star()
    direct_peak = ObservableComparison(
        label="First TT peak position",
        claim_status="verified / scoped direct-observable comparison",
        predicted_value=ACTIVE_BRANCH_THETA_STAR_ELL_PEAK,
        observed_reference=OBSERVED_FIRST_TT_PEAK_ELL_REFERENCE,
        delta=ACTIVE_BRANCH_THETA_STAR_ELL_PEAK - OBSERVED_FIRST_TT_PEAK_ELL_REFERENCE,
        units="ell",
        note=(
            "The active-branch carrier peak lies at `ell_peak = 220.475...`, "
            "aligned with the observed first TT peak near `ell ≈ 220`. The "
            "direct observable agrees even though the extracted `100theta_*` "
            "depends on the geometry used in the transfer map."
        ),
        source_note=(
            "Calculator packet1500/selector-support chain for the IO carrier, "
            "compared against the observed first TT peak near `ell ≈ 220`."
        ),
    )
    return ExplainedValue(
        output_id="theta_star_theorem",
        label="Theorem-grade active-branch theta_*",
        primary_key="theta_star_100",
        primary_value=theta.theta_star_100,
        units="100theta_*",
        claim_status=(
            "derived / scoped, zero fitted parameters, conditional on Premises 1 and 2"
        ),
        provenance_status="full",
        payload={
            **theta.as_dict(),
            "ell_peak": ACTIVE_BRANCH_THETA_STAR_ELL_PEAK,
            "observed_first_peak_ell_reference": OBSERVED_FIRST_TT_PEAK_ELL_REFERENCE,
            "first_peak_delta": (
                ACTIVE_BRANCH_THETA_STAR_ELL_PEAK - OBSERVED_FIRST_TT_PEAK_ELL_REFERENCE
            ),
        },
        scope_boundary=(
            "Fixed active Paper 10 legacy projected branch only.",
            "Theorem-grade numeric closure on the carried selector leaf only.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="calculator.active_branch_theta_star",
        chain_ids=(
            "premise.1",
            "premise.2",
            "paper21.branch_assignment",
            "calculator.phase_equivalent_selector",
            "calculator.packet_coefficient_fixing",
            "calculator.highz_tail_slaving",
            "calculator.peak_window_tail_profile_audit",
            "calculator.selector_support_promotion",
            "calculator.active_branch_theta_star",
        ),
        premise_ids=("premise.1", "premise.2"),
        supporting_node_ids=("paper32.closed_s3_solver_spec",),
        zero_fitted_parameters=True,
        non_claims=(
            "Not a universal off-branch transfer theorem.",
            "Not a universal reduction theorem for arbitrary TT parent-profile deformations.",
            "Not a theorem-grade full TT/TE/EE solver closure.",
        ),
        notes=(
            "This number is published as a theorem-grade calculator output.",
            "The direct observable is the first TT peak location; `100theta_*` is a geometry-dependent extraction.",
        ),
        geometry_explanation=(
            "This number differs from Planck's reported value because Planck "
            "assumes flat space in its standard `K=0` extraction convention, "
            "while the IO framework derives a closed `K=+1` geometry and "
            "evaluates the active-branch selector leaf there. The direct "
            "observable is the peak position. On that direct observable, the "
            "active-branch carrier agrees with the measured first TT peak near "
            "`ell ≈ 220`."
        ),
        comparison_context={
            "planck_flat_reference_theta_mc_100": PLANCK_FLAT_REFERENCE_THETA_MC_100,
            "planck_closed_reference_theta_mc_100": PLANCK_CLOSED_REFERENCE_THETA_MC_100,
            "planck_closed_reference_omegak": PLANCK_CLOSED_REFERENCE_OMEGA_K,
            "statement": (
                "Planck's own non-flat refits keep `100theta_MC` near `1.0411`, "
                "so the IO calculator presents its `100theta_*` as a competing "
                "closed-geometry derivation rather than as a tension in the "
                "direct first-peak observable."
            ),
        },
        direct_observable_comparisons=(direct_peak,),
    )


def explain_tt_first_peak_support() -> ExplainedValue:
    """Return the published canonical TT first-peak support snapshot."""

    direct_peak = ObservableComparison(
        label="First TT peak position",
        claim_status=TT_FIRST_PEAK_APPROVED_STATUS,
        predicted_value=TT_FIRST_PEAK_CANONICAL_ELL_PEAK,
        observed_reference=OBSERVED_FIRST_TT_PEAK_ELL_REFERENCE,
        delta=TT_FIRST_PEAK_CANONICAL_ELL_PEAK - OBSERVED_FIRST_TT_PEAK_ELL_REFERENCE,
        units="ell",
        note=(
            "On the repaired canonical carrier the first broad TT peak lands at "
            "`ell_peak = 224`, with `C_220 / C_peak = 0.9938104102565932`."
        ),
        source_note=(
            "Scoped TT first-peak support audit on the repaired active-branch "
            "canonical carrier."
        ),
    )
    return ExplainedValue(
        output_id="tt_first_peak_support",
        label="Canonical TT first-peak support",
        primary_key="ell_peak",
        primary_value=TT_FIRST_PEAK_CANONICAL_ELL_PEAK,
        units="ell",
        claim_status=TT_FIRST_PEAK_APPROVED_STATUS,
        provenance_status="full",
        payload={
            "ell_peak": TT_FIRST_PEAK_CANONICAL_ELL_PEAK,
            "observed_first_peak_ell_reference": OBSERVED_FIRST_TT_PEAK_ELL_REFERENCE,
            "first_peak_delta": (
                TT_FIRST_PEAK_CANONICAL_ELL_PEAK - OBSERVED_FIRST_TT_PEAK_ELL_REFERENCE
            ),
            "c_220_over_peak": TT_FIRST_PEAK_CANONICAL_C220_OVER_PEAK,
            "c_2_over_c_30": TT_FIRST_PEAK_CANONICAL_C2_OVER_C30,
            "exact_history_samples": TT_FIRST_PEAK_CANONICAL_EXACT_HISTORY_SAMPLES,
            "prehistory_samples": TT_FIRST_PEAK_CANONICAL_PREHISTORY_SAMPLES,
            "n_max": TT_FIRST_PEAK_CANONICAL_N_MAX,
            "shell_step": TT_FIRST_PEAK_CANONICAL_SHELL_STEP,
            "metric_baryon_momentum_slot": "omega_b,eff",
            "source_shell_support": "odd_plus_branch",
            "source_shell_weight_interpretation": "covariance",
            "neighbor_n_max": TT_FIRST_PEAK_NEIGHBOR_N_MAX,
            "neighbor_ell_peak": TT_FIRST_PEAK_NEIGHBOR_ELL_PEAK,
            "neighbor_c_220_over_peak": TT_FIRST_PEAK_NEIGHBOR_C220_OVER_PEAK,
        },
        scope_boundary=(
            "Canonical repaired first-peak carrier only.",
            "Not a theorem-grade full high-`ell` TT closure.",
            TT_FIRST_PEAK_OPEN_FRONTIER,
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="local.scoped_tt_first_peak_support",
        chain_ids=(
            "premise.1",
            "premise.2",
            "local.inherited_full_stage2_dynamic_history_builder",
            "local.typed_thomson_split_history_realization",
            "local.typed_r_operator",
            "local.closed_scalar_acoustic_generator",
            "local.closed_scalar_transfer_projector",
            "local.scoped_tt_driver",
            "local.scoped_tt_first_peak_support",
        ),
        premise_ids=("premise.1", "premise.2"),
        supporting_node_ids=("calculator.peak_functional_separation",),
        zero_fitted_parameters=True,
        non_claims=(
            "Not a theorem-grade full high-`ell` TT closure.",
            "Not a theorem-grade full `C_l` spectrum closure.",
            "Not a theorem-grade Planck extractor.",
        ),
        notes=(
            "This card publishes the verified canonical repaired-carrier TT result without hiding the surviving high-shell ceiling drift.",
            "The CLI `tt-spectrum` command computes the same repaired carrier directly; this card is the public explained snapshot.",
        ),
        direct_observable_comparisons=(direct_peak,),
    )


def explain_branch_rd_mpc() -> ExplainedValue:
    """Return the full explained value for the active-branch `r_d`."""

    return ExplainedValue(
        output_id="branch_rd_mpc",
        label="Active-branch pre-drag ruler",
        primary_key="r_d_mpc",
        primary_value=ACTIVE_BRANCH.rd_mpc,
        units="Mpc",
        claim_status="derived / scoped active-branch published ruler",
        provenance_status="full",
        payload={
            "branch_label": ACTIVE_BRANCH.label,
            "r_d_mpc": ACTIVE_BRANCH.rd_mpc,
        },
        scope_boundary=(
            "Fixed active branch package only.",
            "Published pre-drag ruler slot carried by the live BAO/background surface.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="paper31.geometric_pre_drag_ruler",
        chain_ids=(
            "premise.1",
            "premise.2",
            "paper21.branch_assignment",
            "paper29.sound_speed_selector",
            "paper31.geometric_pre_drag_ruler",
        ),
        premise_ids=("premise.1", "premise.2"),
        zero_fitted_parameters=True,
        notes=(
            "This is the theorem-grade pre-drag ruler used by the live BAO ratios.",
            "The sound-speed baryon slot is fixed before the ruler is carried into the calculator surface.",
        ),
    )


def explain_branch_h0() -> ExplainedValue:
    """Return the full explained value for the active-branch `H0`."""

    return ExplainedValue(
        output_id="branch_h0",
        label="Active-branch H0",
        primary_key="H0",
        primary_value=ACTIVE_BRANCH.H0,
        units="km/s/Mpc",
        claim_status="derived / scoped active-branch carried Hubble constant",
        provenance_status="full",
        payload={
            "branch_label": ACTIVE_BRANCH.label,
            "H0_km_s_mpc": ACTIVE_BRANCH.H0,
        },
        scope_boundary=(
            "Fixed active runtime package only.",
            "Public calculator carry value rather than a per-query fitted parameter.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="paper30.active_branch_parameter_package",
        chain_ids=(
            "premise.1",
            "premise.2",
            "paper21.branch_assignment",
            "paper30.active_branch_parameter_package",
        ),
        premise_ids=("premise.1", "premise.2"),
        zero_fitted_parameters=True,
        notes=(
            "This card surfaces the active-branch Hubble constant directly from the reviewed runtime package.",
        ),
    )


def explain_branch_omega_m() -> ExplainedValue:
    """Return the full explained value for the active-branch `Omega_m`."""

    return ExplainedValue(
        output_id="branch_omega_m",
        label="Active-branch Omega_m",
        primary_key="Omega_m",
        primary_value=ACTIVE_BRANCH.Omega_m,
        units=None,
        claim_status="derived / scoped active-branch carried matter density",
        provenance_status="full",
        payload={
            "branch_label": ACTIVE_BRANCH.label,
            "Omega_m": ACTIVE_BRANCH.Omega_m,
        },
        scope_boundary=(
            "Fixed active runtime package only.",
            "Public calculator carry value rather than a per-query fitted parameter.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="paper30.active_branch_parameter_package",
        chain_ids=(
            "premise.1",
            "premise.2",
            "paper21.branch_assignment",
            "paper30.active_branch_parameter_package",
        ),
        premise_ids=("premise.1", "premise.2"),
        zero_fitted_parameters=True,
        notes=(
            "This card surfaces the active-branch matter density directly from the reviewed runtime package.",
        ),
    )


def explain_branch_omega_k() -> ExplainedValue:
    """Return the full explained value for the active-branch `Omega_k`."""

    return ExplainedValue(
        output_id="branch_omega_k",
        label="Active-branch Omega_k",
        primary_key="Omega_k",
        primary_value=ACTIVE_BRANCH.Omega_k,
        units=None,
        claim_status="derived / scoped active-branch carried curvature density",
        provenance_status="full",
        payload={
            "branch_label": ACTIVE_BRANCH.label,
            "Omega_k": ACTIVE_BRANCH.Omega_k,
        },
        scope_boundary=(
            "Fixed active runtime package only.",
            "Closed-space curvature density on the public calculator branch.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="paper30.active_branch_parameter_package",
        chain_ids=(
            "premise.1",
            "premise.2",
            "paper21.branch_assignment",
            "paper30.active_branch_parameter_package",
        ),
        premise_ids=("premise.1", "premise.2"),
        zero_fitted_parameters=True,
        notes=(
            "This is the carried closed-space curvature density of the active branch.",
        ),
    )


def explain_branch_omega_lambda() -> ExplainedValue:
    """Return the full explained value for the active-branch `Omega_Lambda`."""

    return ExplainedValue(
        output_id="branch_omega_lambda",
        label="Active-branch Omega_Lambda",
        primary_key="Omega_Lambda",
        primary_value=ACTIVE_BRANCH.Omega_lambda,
        units=None,
        claim_status="derived / scoped active-branch carried dark-energy density",
        provenance_status="full",
        payload={
            "branch_label": ACTIVE_BRANCH.label,
            "Omega_Lambda": ACTIVE_BRANCH.Omega_lambda,
        },
        scope_boundary=(
            "Fixed active runtime package only.",
            "Public calculator carry value rather than a per-query fitted parameter.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="paper30.active_branch_parameter_package",
        chain_ids=(
            "premise.1",
            "premise.2",
            "paper21.branch_assignment",
            "paper30.active_branch_parameter_package",
        ),
        premise_ids=("premise.1", "premise.2"),
        zero_fitted_parameters=True,
        notes=(
            "This card surfaces the carried dark-energy density of the active runtime package.",
        ),
    )


def explain_active_t_cmb() -> ExplainedValue:
    """Return the full explained value for the active observer-side `T_CMB`."""

    return ExplainedValue(
        output_id="active_t_cmb",
        label="Active-branch T_CMB",
        primary_key="T_CMB",
        primary_value=ACTIVE_BRANCH.T_cmb,
        units="K",
        claim_status="derived / scoped observer-side thermal readout",
        provenance_status="full",
        payload={
            "branch_label": ACTIVE_BRANCH.label,
            "T_CMB_K": ACTIVE_BRANCH.T_cmb,
            "T_IO_K": T_IO_REF_K,
            "x": ACTIVE_IO_CONSTANTS.x,
            "K_gauge": ACTIVE_IO_CONSTANTS.K_gauge,
        },
        scope_boundary=(
            "Observer-side thermal readout on the fixed active branch.",
            "The local bulk thermal slot `T_IO` remains a distinct internal quantity.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="paper30.active_branch_parameter_package",
        chain_ids=(
            "premise.1",
            "premise.2",
            "paper17.gttp_thermal_readout",
            "paper21.branch_assignment",
            "paper30.active_branch_parameter_package",
        ),
        premise_ids=("premise.1", "premise.2"),
        zero_fitted_parameters=True,
        notes=(
            "This is the observer-side CMB temperature on the active branch.",
            "The theorem chain keeps the thermal readout law explicit instead of treating `T_CMB` as a bare constant.",
        ),
    )


def explain_bare_master_clock_age() -> ExplainedValue:
    """Return the full explained value for the bare master-clock age."""

    bare_model = CurvedBackgroundModel(branch=MASTER_CLOCK_BARE_BRANCH)
    age = bare_model.age_today_gyr(n=4096)
    return ExplainedValue(
        output_id="bare_master_clock_age",
        label="Bare master-clock age",
        primary_key="Age_bare",
        primary_value=age,
        units="Gyr",
        claim_status="derived / scoped bare master-clock evaluation",
        provenance_status="full",
        payload={
            "branch_label": MASTER_CLOCK_BARE_BRANCH.label,
            "age_bare_gyr": age,
            "H0_bare_km_s_mpc": MASTER_CLOCK_BARE_BRANCH.H0,
            "Omega_m_bare": MASTER_CLOCK_BARE_BRANCH.Omega_m,
            "Omega_k_bare": MASTER_CLOCK_BARE_BRANCH.Omega_k,
            "Omega_Lambda_bare": MASTER_CLOCK_BARE_BRANCH.Omega_lambda,
            "Omega_r_bare": MASTER_CLOCK_BARE_BRANCH.Omega_r,
            "T_CMB_K": MASTER_CLOCK_BARE_BRANCH.T_cmb,
        },
        scope_boundary=(
            "Bare local-clock branch only.",
            "Not the projected observer-side age already shown on the active background snapshot card.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="paper30.bare_master_clock",
        chain_ids=(
            "premise.1",
            "premise.2",
            "paper17.gttp_thermal_readout",
            "paper30.bare_master_clock",
        ),
        premise_ids=("premise.1", "premise.2"),
        zero_fitted_parameters=True,
        non_claims=(
            "Not the projected photon/readout age of the active branch.",
        ),
        notes=(
            "The bare master clock uses the corrected radiation-inclusive FRW proper-time integral, not the old dust cycloid.",
        ),
    )


def explain_scalar_tilt_ns() -> ExplainedValue:
    """Return the full explained value for the active scalar tilt `n_s`."""

    return ExplainedValue(
        output_id="scalar_tilt_ns",
        label="Active scalar tilt n_s",
        primary_key="n_s",
        primary_value=ACTIVE_BRANCH.n_s,
        units=None,
        claim_status="conditional / scoped active scalar tilt",
        provenance_status="full",
        payload={
            "n_s": ACTIVE_BRANCH.n_s,
            "K_gauge": ACTIVE_IO_CONSTANTS.K_gauge,
            "x": ACTIVE_IO_CONSTANTS.x,
        },
        scope_boundary=(
            "Conditional scalar-tilt closure only.",
            "The current stack does not license this value as an unconditional theorem independent of the Boundary Fixed-point Principle.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="paper28.boundary_fixed_point_scalar_tilt",
        chain_ids=(
            "premise.1",
            "premise.2",
            "paper28.boundary_fixed_point_scalar_tilt",
        ),
        premise_ids=("premise.1", "premise.2"),
        zero_fitted_parameters=True,
        non_claims=(
            "Not an unconditional scalar-tilt theorem independent of the Boundary Fixed-point Principle.",
        ),
        notes=(
            "This card keeps the active scalar tilt at its strongest honest archive status.",
        ),
    )


def explain_native_scalar_amplitude_as() -> ExplainedValue:
    """Return the full explained value for the active source amplitude `A_s`."""

    return ExplainedValue(
        output_id="native_scalar_amplitude_as",
        label="Active scalar amplitude A_s",
        primary_key="A_s",
        primary_value=ACTIVE_BRANCH.A_s,
        units=None,
        claim_status="derived / scoped native scalar amplitude",
        provenance_status="full",
        payload={
            "A_s": ACTIVE_BRANCH.A_s,
            "gamma_BI": ACTIVE_IO_CONSTANTS.gamma_bi,
            "x": ACTIVE_IO_CONSTANTS.x,
            "K_gauge": ACTIVE_IO_CONSTANTS.K_gauge,
        },
        scope_boundary=(
            "Active scalar-source block only.",
            "Does not by itself close the full primordial-sector family or the downstream perturbation/readout solver.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="paper32.modular_dtn_field_transfer",
        chain_ids=(
            "premise.1",
            "premise.2",
            "paper32.modular_dtn_field_transfer",
        ),
        premise_ids=("premise.1", "premise.2"),
        zero_fitted_parameters=True,
        notes=(
            "This amplitude is carried directly from the theorem-grade modular-DtN source block.",
        ),
    )


def explain_bbn_deuterium_ratio() -> ExplainedValue:
    """Return the full explained value for the active deuterium scorecard."""

    return ExplainedValue(
        output_id="bbn_deuterium_ratio",
        label="Active BBN deuterium scorecard",
        primary_key="D/H",
        primary_value=ACTIVE_BBN_DEUTERIUM_RATIO,
        units=None,
        claim_status="derived / scoped active deuterium scorecard",
        provenance_status="full",
        payload={
            "D_H_ratio": ACTIVE_BBN_DEUTERIUM_RATIO,
        },
        scope_boundary=(
            "Active repaired deuterium scorecard only.",
            "Does not claim a live calculator BBN network integration on demand.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="paper30.deuterium_scorecard",
        chain_ids=(
            "premise.1",
            "premise.2",
            "paper12.baryon_dictionary_fraction",
            "paper30.deuterium_scorecard",
        ),
        premise_ids=("premise.1", "premise.2"),
        zero_fitted_parameters=True,
        notes=(
            "This is the fixed active deuterium prediction carried by the repaired BBN scorecard.",
        ),
    )


def explain_bbn_helium_fraction() -> ExplainedValue:
    """Return the full explained value for the active helium scorecard."""

    return ExplainedValue(
        output_id="bbn_helium_fraction",
        label="Active BBN helium scorecard",
        primary_key="Y_p",
        primary_value=ACTIVE_BRANCH.YHe,
        units=None,
        claim_status="derived / scoped active primordial helium scorecard",
        provenance_status="full",
        payload={
            "branch_label": ACTIVE_BRANCH.label,
            "Y_p": ACTIVE_BRANCH.YHe,
        },
        scope_boundary=(
            "Active carried helium scorecard only.",
            "Does not claim a live calculator BBN network solve for `Y_p`.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="paper30.primordial_helium_scorecard",
        chain_ids=(
            "premise.1",
            "premise.2",
            "paper21.branch_assignment",
            "paper30.active_branch_parameter_package",
            "paper30.primordial_helium_scorecard",
        ),
        premise_ids=("premise.1", "premise.2"),
        zero_fitted_parameters=True,
        notes=(
            "This is the active primordial helium mass fraction carried by the runtime package.",
        ),
    )


def explain_bbn_lithium_ratio() -> ExplainedValue:
    """Return the full explained value for the conditional lithium scorecard."""

    return ExplainedValue(
        output_id="bbn_lithium_ratio",
        label="Conditional BBN lithium scorecard",
        primary_key="Li-7/H",
        primary_value=ACTIVE_BBN_LI7_RATIO,
        units=None,
        claim_status="conditional / scoped channel-resolved lithium scorecard",
        provenance_status="full",
        payload={
            "Li7_H_ratio": ACTIVE_BBN_LI7_RATIO,
        },
        scope_boundary=(
            "Conditional lithium-repair scorecard only.",
            "The current stack does not license this value as an unconditional theorem independent of the Paper 22 premise package and cluster-deformation input.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="paper24.conditional_lithium_scorecard",
        chain_ids=(
            "premise.1",
            "premise.2",
            "paper12.baryon_dictionary_fraction",
            "paper24.conditional_lithium_scorecard",
        ),
        premise_ids=("premise.1", "premise.2"),
        zero_fitted_parameters=True,
        non_claims=(
            "Not an unconditional lithium theorem.",
        ),
        notes=(
            "This card keeps the lithium scorecard explicitly conditional on the surviving Paper 22 premise package and cluster-deformation input.",
        ),
    )


def explain_baryon_fraction_fb() -> ExplainedValue:
    """Return the full explained value for the baryon inventory fraction `f_b`."""

    return ExplainedValue(
        output_id="baryon_fraction_fb",
        label="Baryon dictionary fraction",
        primary_key="f_b",
        primary_value=ACTIVE_IO_CONSTANTS.f_b,
        units=None,
        claim_status="derived / scoped baryon inventory fraction",
        provenance_status="full",
        payload={
            "f_b": ACTIVE_IO_CONSTANTS.f_b,
            "gamma_BI": ACTIVE_IO_CONSTANTS.gamma_bi,
            "x": ACTIVE_IO_CONSTANTS.x,
        },
        scope_boundary=(
            "Framework inventory fraction only.",
            "Observable-specific baryon slots still require their own typed placement theorems.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="paper12.baryon_dictionary_fraction",
        chain_ids=(
            "premise.1",
            "premise.2",
            "paper12.baryon_dictionary_fraction",
        ),
        premise_ids=("premise.1", "premise.2"),
        zero_fitted_parameters=True,
        notes=(
            "This is the raw framework baryon inventory fraction, not a universal late-time density parameter for every observable class.",
        ),
    )


def explain_eta_io_late() -> ExplainedValue:
    """Return the full explained value for `eta_IO,late`."""

    value = late_eta_io()
    return ExplainedValue(
        output_id="eta_io_late",
        label="Late-time eta_IO",
        primary_key="eta_IO_late",
        primary_value=value,
        units=None,
        claim_status="derived / scoped preferred Paper 35 late-time convention",
        provenance_status="full",
        payload={
            "branch_label": ACTIVE_BRANCH.label,
            "eta_IO_late": value,
        },
        scope_boundary=(
            "Preferred late-time `eta_IO` convention on the active branch.",
            "Late-time baryonic dust sector only; not a primordial freeze-out theorem.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="paper35.eta_io_late_closure",
        chain_ids=(
            "premise.1",
            "premise.2",
            "paper21.branch_assignment",
            "paper35.late_baryon_counting_law",
            "paper35.eta_io_late_closure",
        ),
        premise_ids=("premise.1", "premise.2"),
        zero_fitted_parameters=True,
        notes=(
            "This is the preferred late-time calculator convention for `eta_IO`.",
            "The chain closes on the active branch without introducing fitted cosmological parameters.",
        ),
    )


def explain_background_snapshot(z: float) -> ExplainedValue:
    """Return a full explained background snapshot at one redshift."""

    model = CurvedBackgroundModel()
    snapshot = model.snapshot(z)
    snapshot["eta_IO_late"] = late_eta_io()
    return ExplainedValue(
        output_id="background_snapshot",
        label="Closed-FRW background snapshot",
        primary_key="DM_mpc",
        primary_value=snapshot["DM_mpc"],
        units="Mpc",
        claim_status="derived / scoped active-branch background snapshot",
        provenance_status="full",
        payload={"z": z, **snapshot},
        scope_boundary=(
            "Closed-FRW observer-side background geometry on the fixed active branch.",
            "BAO ratios inherit the carried active-branch `r_d` slot.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="paper30.background_surface",
        chain_ids=(
            "premise.1",
            "premise.2",
            "paper21.branch_assignment",
            "paper30.background_surface",
            "paper29.sound_speed_selector",
            "paper31.geometric_pre_drag_ruler",
        ),
        premise_ids=("premise.1", "premise.2"),
        zero_fitted_parameters=True,
        notes=(
            "This snapshot is evaluated on the theorem-grade active closed-FRW branch.",
            "The BAO ratios in the payload inherit the carried pre-drag ruler `r_d`.",
        ),
    )


def explain_recombination_point(
    z: float,
    x_e_override: float | None = None,
) -> ExplainedValue:
    """Return a full explained recombination-point payload."""

    state = local_background_state(z)
    x_e = saha_equilibrium_xe(z) if x_e_override is None else x_e_override
    claim_status = (
        "derived / scoped local recombination primitives on omega_b,geom"
        if x_e_override is None
        else "conditional on supplied ionization fraction over a derived local background state map"
    )
    chain_ids = (
        (
            "premise.1",
            "premise.2",
            "paper21.branch_assignment",
            "paper31.baryon_assignment",
            "paper29.sound_speed_selector",
            "paper31.local_background_state_map",
            "local.saha_seed",
            "paper31.recombination_clock_transport",
        )
        if x_e_override is None
        else (
            "premise.1",
            "premise.2",
            "paper21.branch_assignment",
            "paper31.baryon_assignment",
            "paper29.sound_speed_selector",
            "paper31.local_background_state_map",
            "paper31.recombination_clock_transport",
        )
    )
    notes = (
        "Uses the local Saha seed when no override is supplied.",
        "Setting `x_e_override` changes the chemistry-dependent rows from derived to conditional.",
    )
    return ExplainedValue(
        output_id="recombination_point",
        label="Local recombination primitives at one redshift",
        primary_key="kappa_prime_loc",
        primary_value=primitive_local_kappa_prime(z, x_e),
        units=None,
        claim_status=claim_status,
        provenance_status="full",
        payload={
            "z": z,
            "x_e": x_e,
            "u": state.u,
            "a_loc_m": state.a_loc_m,
            "H_loc_s_inv": state.H_loc_s_inv,
            "T_r_loc_K": state.T_r_loc_K,
            "n_H_geom_m3": hydrogen_number_density_m3(z),
            "n_e_m3": free_electron_density_m3(z, x_e),
            "kappa_prime_loc": primitive_local_kappa_prime(z, x_e),
            "d_tau_obs_dz": optical_depth_gradient_per_redshift(z, x_e),
            "Gamma_T_over_H_loc": local_scattering_to_expansion_ratio(z, x_e),
            "R_local_geom": local_baryon_loading_R(z),
            "c_s_local_m_s": local_sound_speed_m_s(z),
        },
        scope_boundary=(
            "Derived local background-state map on the active branch.",
            "Chemistry-dependent quantities are derived only when `x_e` comes from the local Saha seed.",
            "Local `R` and `c_s` rows inherit the theorem-grade `omega_b,geom` sound-speed slot.",
        ),
        conditional_on=("premise.1", "premise.2"),
        provenance_root_id="paper31.recombination_clock_transport",
        chain_ids=chain_ids,
        premise_ids=("premise.1", "premise.2"),
        zero_fitted_parameters=x_e_override is None,
        notes=notes,
    )


def published_explained_outputs() -> dict[str, dict[str, Any]]:
    """Return the default explained-output bundle shipped to the web surface."""

    nodes = theorem_graph()
    return {
        "theta_star_theorem": explain_active_branch_theta_star().as_dict(nodes=nodes),
        "tt_first_peak_support": explain_tt_first_peak_support().as_dict(nodes=nodes),
        "branch_rd_mpc": explain_branch_rd_mpc().as_dict(nodes=nodes),
        "branch_h0": explain_branch_h0().as_dict(nodes=nodes),
        "branch_omega_m": explain_branch_omega_m().as_dict(nodes=nodes),
        "branch_omega_k": explain_branch_omega_k().as_dict(nodes=nodes),
        "branch_omega_lambda": explain_branch_omega_lambda().as_dict(nodes=nodes),
        "active_t_cmb": explain_active_t_cmb().as_dict(nodes=nodes),
        "bare_master_clock_age": explain_bare_master_clock_age().as_dict(nodes=nodes),
        "scalar_tilt_ns": explain_scalar_tilt_ns().as_dict(nodes=nodes),
        "native_scalar_amplitude_as": explain_native_scalar_amplitude_as().as_dict(
            nodes=nodes
        ),
        "bbn_deuterium_ratio": explain_bbn_deuterium_ratio().as_dict(nodes=nodes),
        "bbn_helium_fraction": explain_bbn_helium_fraction().as_dict(nodes=nodes),
        "bbn_lithium_ratio": explain_bbn_lithium_ratio().as_dict(nodes=nodes),
        "baryon_fraction_fb": explain_baryon_fraction_fb().as_dict(nodes=nodes),
        "eta_io_late": explain_eta_io_late().as_dict(nodes=nodes),
        "background_snapshot_z_0_57": explain_background_snapshot(0.57).as_dict(nodes=nodes),
        "recombination_point_z_1100": explain_recombination_point(1100.0).as_dict(nodes=nodes),
    }


__all__ = [
    "ACTIVE_BRANCH_THETA_STAR_ELL_PEAK",
    "ExplainedValue",
    "ObservableComparison",
    "TheoremNode",
    "TT_FIRST_PEAK_APPROVED_STATUS",
    "explain_active_branch_theta_star",
    "explain_active_t_cmb",
    "explain_background_snapshot",
    "explain_bare_master_clock_age",
    "explain_baryon_fraction_fb",
    "explain_bbn_deuterium_ratio",
    "explain_bbn_helium_fraction",
    "explain_bbn_lithium_ratio",
    "explain_branch_h0",
    "explain_branch_omega_k",
    "explain_branch_omega_lambda",
    "explain_branch_omega_m",
    "explain_branch_rd_mpc",
    "explain_eta_io_late",
    "explain_native_scalar_amplitude_as",
    "explain_recombination_point",
    "explain_scalar_tilt_ns",
    "explain_tt_first_peak_support",
    "explained_output_specs",
    "published_explained_outputs",
    "theorem_graph",
]
