"""Checks for the typed perturbation carrier and open-seam layer."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator.perturbation_types import (  # noqa: E402
    OpenExactStage2DynamicNetworkOperator,
    OpenTypedSourceAcousticOperator,
    active_typed_baryon_assignment,
    closed_s3_solver_specification,
    make_perturbation_block_inputs,
)
from aio_calculator.recombination import OpenTheoremBoundaryError, Stage2History  # noqa: E402
from aio_calculator.s3_modes import scalar_mode  # noqa: E402


def test_typed_baryon_assignment_closes_r_only_as_a_typed_operator() -> None:
    """Paper 32 typing should keep the no-collapse boundary while surfacing the typed `R` closure."""

    assignment = active_typed_baryon_assignment()
    assert assignment.chemistry == "omega_b,geom"
    assert assignment.primitive_local_opacity == "omega_b,geom"
    assert assignment.reduced_visibility_readout == "omega_b,eff"
    assert assignment.clustering_slot == "omega_b,clustering"
    assert "full hierarchy operator" in assignment.baryon_loading_R
    assert "Gamma_bgamma = R_local * thomson_drag_rate" in assignment.baryon_loading_R
    assert assignment.scalar_metric_source == "open"
    assert assignment.claim_status == "derived / scoped"
    assert assignment.provenance_node_ids == (
        "paper32.closed_s3_solver_spec",
        "paper32.typed_baryon_slot_spec",
        "local.typed_r_operator",
        "local.typed_r_site_uniqueness",
    )


def test_closed_solver_specification_names_exact_two_live_seams() -> None:
    """The Paper 32 solver theorem should surface the remaining seams exactly."""

    spec = closed_s3_solver_specification()
    assert spec.tuple_label == "S_IO"
    assert spec.q_ladder_formula == "q^2 = k^2 + K(1+m)"
    assert spec.stage2_state_formula == "Y_rec = (x_e, T_m, D_-(q;z), L_-(z))"
    assert spec.thermodynamics_fields == (
        "x_e",
        "dot{kappa}",
        "exp(-kappa)",
        "g",
        "dg",
        "ddg",
        "kappa_b",
    )
    assert tuple(seam.seam_id for seam in spec.open_seams) == (
        "exact_stage2_dynamic_network_operator",
        "typed_source_acoustic_operator",
    )


def test_open_typed_source_operator_refuses_to_fake_phase3_closure() -> None:
    """The open perturbation/source seam should fail explicitly when invoked."""

    history = Stage2History.from_sequences(
        [900.0, 1100.0],
        [1.0e-3, 2.0e-3],
        [2500.0, 2900.0],
    )
    inputs = make_perturbation_block_inputs(scalar_mode(5), history)
    with pytest.raises(OpenTheoremBoundaryError):
        OpenTypedSourceAcousticOperator().apply(inputs)


def test_open_stage2_dynamic_network_operator_refuses_to_fake_history_closure() -> None:
    """The Stage-2 perturbation seam should raise until the exact operator exists."""

    with pytest.raises(OpenTheoremBoundaryError):
        OpenExactStage2DynamicNetworkOperator().solve_history([900.0, 1100.0])
