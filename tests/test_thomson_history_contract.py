"""Checks for the coupled Thomson-history tuple contract."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator.recombination import OpenTheoremBoundaryError, Stage2History, build_visibility_packet, primitive_local_kappa_prime  # noqa: E402
from aio_calculator.thomson_history_contract import (  # noqa: E402
    OpenCoupledThomsonHistoryOperator,
    build_typed_split_thomson_history_realization,
    build_thomson_history_contract,
)


def test_thomson_history_contract_builds_tau_c_and_dtau_c_from_drag_rate() -> None:
    """The Calculator tuple formulas should be reproduced exactly."""

    contract = build_thomson_history_contract(
        [900.0, 1100.0],
        [10.0, 20.0],
        [11.0, 21.0],
        [-2.0, -4.0],
        [1.0e-5, 2.0e-5],
        [3.0e-5, 4.0e-5],
    )
    assert contract.claim_status == "derived / scoped"
    assert contract.provenance_node_ids == ("calculator.thomson_history_realization",)
    assert math.isclose(contract.tau_c[0], 0.1, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(contract.tau_c[1], 0.05, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(contract.dtau_c[0], 0.02, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(contract.dtau_c[1], 0.01, rel_tol=0.0, abs_tol=1.0e-15)
    sample = contract.sample(1)
    assert math.isclose(sample.tau_c, 0.05, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(sample.shear, 4.0e-5, rel_tol=0.0, abs_tol=1.0e-15)


def test_thomson_history_contract_rejects_nonpositive_drag_rates() -> None:
    """The tight-coupling time should stay well-defined on every sample."""

    with pytest.raises(ValueError):
        build_thomson_history_contract(
            [900.0],
            [0.0],
            [1.0],
            [0.0],
            [0.0],
            [0.0],
        )


def test_open_thomson_history_operator_refuses_to_fake_the_tuple_law() -> None:
    """The exact tuple-level operator should fail honestly until it is derived."""

    contract = build_thomson_history_contract(
        [900.0],
        [10.0],
        [11.0],
        [-2.0],
        [1.0e-5],
        [3.0e-5],
    )
    with pytest.raises(OpenTheoremBoundaryError):
        OpenCoupledThomsonHistoryOperator().apply(contract)


def test_typed_split_history_realization_exposes_local_opacity_visibility_and_contract() -> None:
    """The live TT path should keep the typed split explicit instead of flattening opacity."""

    history = Stage2History.from_sequences(
        [900.0, 1100.0, 1300.0],
        [5.0e-2, 1.0e-1, 2.0e-1],
        [2600.0, 3000.0, 3300.0],
    )
    dc_dz = (2.0, 4.0, 8.0)
    tau_samples = (1.0, 2.0, 4.0)
    realization = build_typed_split_thomson_history_realization(history, dc_dz, tau_samples)

    visibility = build_visibility_packet(history)
    assert realization.claim_status == "derived / scoped typed split history realization"
    assert realization.provenance_node_ids == (
        "paper31.baryon_assignment",
        "calculator.thomson_history_realization",
        "local.typed_thomson_split_history_realization",
    )
    assert realization.visibility_packet == visibility
    assert realization.primitive_local_kappa_prime == tuple(
        primitive_local_kappa_prime(z, x_e) for z, x_e in zip(history.z_obs, history.x_e)
    )
    expected_drag = tuple(abs(d_tau_dz / dC_dz) for d_tau_dz, dC_dz in zip(visibility.d_tau_obs_dz, dc_dz))
    assert realization.contract.thomson_drag_rate == expected_drag
    assert realization.contract.thomson_hierarchy_rate == expected_drag
    assert realization.contract.derivative_coordinate == "conformal_time"
    assert math.isclose(realization.contract.tau_c[1], 1.0 / expected_drag[1], rel_tol=0.0, abs_tol=1.0e-15)
