"""Checks for the theorem-grade source/readout block."""

from __future__ import annotations

import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator.constants import (  # noqa: E402
    ACTIVE_BRANCH,
    ACTIVE_IO_CONSTANTS,
    IO_SCHWARZSCHILD_RADIUS_M,
)
from aio_calculator.source_block import (  # noqa: E402
    ACTIVE_SOURCE_PIVOT_SHELL,
    active_plus_branch_supports_shell,
    accessible_line_rescaling,
    coexact_dtn_shell,
    modular_dtn_covariance_transfer_factor,
    modular_dtn_field_transfer_factor,
    native_scalar_amplitude,
    plus_branch_source_window,
    source_block_specification,
)


def test_coexact_dtn_shell_reproduces_sigma_generator_and_transfer_factors() -> None:
    """The shell carrier should expose the exact Paper 32 DtN formulas."""

    shell = coexact_dtn_shell(4)
    assert math.isclose(shell.sigma_ell_m_inv, 5.0 / IO_SCHWARZSCHILD_RADIUS_M, rel_tol=0.0, abs_tol=1.0e-40)
    assert math.isclose(shell.logarithmic_generator, math.log(5.0), rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(
        shell.field_transfer_factor,
        math.exp(-ACTIVE_IO_CONSTANTS.K_gauge * math.log(5.0) / (2.0 * ACTIVE_IO_CONSTANTS.x)),
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )
    assert math.isclose(
        shell.covariance_transfer_factor,
        shell.field_transfer_factor**2,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )


def test_plus_branch_source_window_is_pivot_normalized() -> None:
    """The plus-branch window should be exactly normalized at the active pivot shell."""

    assert math.isclose(
        plus_branch_source_window(ACTIVE_SOURCE_PIVOT_SHELL),
        1.0,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )
    assert math.isclose(
        plus_branch_source_window(ACTIVE_SOURCE_PIVOT_SHELL + 1),
        ((ACTIVE_SOURCE_PIVOT_SHELL + 2) / (ACTIVE_SOURCE_PIVOT_SHELL + 1))
        ** (-ACTIVE_IO_CONSTANTS.K_gauge / ACTIVE_IO_CONSTANTS.x),
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )
    assert active_plus_branch_supports_shell(ACTIVE_SOURCE_PIVOT_SHELL) is True
    assert active_plus_branch_supports_shell(ACTIVE_SOURCE_PIVOT_SHELL + 1) is False


def test_native_scalar_amplitude_and_accessible_line_rescaling_match_carried_values() -> None:
    """The source block should reproduce the carried amplitude and field rescaling."""

    assert math.isclose(native_scalar_amplitude(), ACTIVE_BRANCH.A_s, rel_tol=0.0, abs_tol=1.0e-24)
    assert math.isclose(
        accessible_line_rescaling(),
        math.sqrt(ACTIVE_IO_CONSTANTS.f_gamma),
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )


def test_source_block_specification_exposes_full_formulas_and_scope() -> None:
    """The public source block object should carry the theorem text directly."""

    spec = source_block_specification()
    assert spec.claim_status == "derived / scoped"
    assert spec.source_block_formula == "P_src = B_+ o U_coex o T_field"
    assert "exp[-(K_g tensor log(r_s Lambda_DtN^coex)) / (2x)]" in spec.field_transfer_formula
    assert "W_N^(+) = ((N+1) / (N_p+1))^(-K_gauge / x)" == spec.plus_branch_window_formula
    assert "X_obs = exp(-K_gauge / 2) X_prim" in spec.accessible_line_rescaling_formula
    assert spec.provenance_node_ids == ("paper32.modular_dtn_field_transfer",)
    assert spec.scope_boundary[0] == "Active linear scalar-source block only."
