"""Checks for theorem-grade readout carriers and explicit peak boundaries."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aio_calculator.los_transfer import ClosedAngularPowerSpectrum  # noqa: E402
from aio_calculator.readout_functionals import (  # noqa: E402
    OpenPeakReadoutIdentificationOperator,
    build_null_family_acoustic_readout_field,
    derive_theta_peak_from_peak_functional,
    evaluate_background_acoustic_estimator,
    evaluate_discrete_peak_functional,
)
from aio_calculator.recombination import OpenTheoremBoundaryError  # noqa: E402


def test_null_family_estimator_uses_only_explicit_reduced_history_and_weights() -> None:
    """The estimator should evaluate only the supplied field, reduction, and weights."""

    field = build_null_family_acoustic_readout_field(
        eta=[1.0, 2.0, 4.0],
        omega_hat=[10.0, 20.0, 30.0],
    )
    estimator = evaluate_background_acoustic_estimator(
        field,
        sound_speed=[2.0, 3.0, 5.0],
        reduced_history=[7.0, 11.0, 13.0],
        quadrature_weights=[0.5, 0.25, 1.0],
    )
    assert estimator.value == 2.0 * 7.0 * 0.5 + 3.0 * 11.0 * 0.25 + 5.0 * 13.0 * 1.0
    assert estimator.provenance_node_ids == (
        "paper29.sound_speed_selector",
        "calculator.null_family_acoustic_readout",
    )


def test_discrete_peak_functional_reads_supplied_window_only() -> None:
    """The peak functional should be read directly from the provided `C_l` samples."""

    spectrum = ClosedAngularPowerSpectrum(
        observable_pair="TT",
        ell_values=(180, 190, 200, 210),
        c_ell=(100.0, 120.0, 180.0, 160.0),
        claim_status="derived / scoped explicit shell assembly",
        provenance_node_ids=("paper28.closed_s3_shell_power", "paper32.closed_s3_solver_spec"),
        scope_boundary=("test",),
    )
    peak = evaluate_discrete_peak_functional(spectrum, ell_min=185, ell_max=205)
    assert peak.observable_pair == "TT"
    assert peak.ell_peak == 200
    assert peak.peak_value == 180.0
    assert peak.provenance_node_ids == ("calculator.peak_functional_separation",)


def test_discrete_peak_functional_rejects_empty_windows() -> None:
    """A peak window with no supplied samples should fail explicitly."""

    spectrum = ClosedAngularPowerSpectrum(
        observable_pair="TT",
        ell_values=(100, 110),
        c_ell=(1.0, 2.0),
        claim_status="derived / scoped explicit shell assembly",
        provenance_node_ids=("paper28.closed_s3_shell_power", "paper32.closed_s3_solver_spec"),
        scope_boundary=("test",),
    )
    with pytest.raises(ValueError):
        evaluate_discrete_peak_functional(spectrum, ell_min=200, ell_max=220)


def test_open_peak_identification_refuses_to_fake_theta_closure() -> None:
    """The final readout map from `A_peak` to `theta_peak` must stay explicit."""

    spectrum = ClosedAngularPowerSpectrum(
        observable_pair="TT",
        ell_values=(180, 190, 200),
        c_ell=(100.0, 150.0, 120.0),
        claim_status="derived / scoped explicit shell assembly",
        provenance_node_ids=("paper28.closed_s3_shell_power", "paper32.closed_s3_solver_spec"),
        scope_boundary=("test",),
    )
    peak = evaluate_discrete_peak_functional(spectrum, ell_min=180, ell_max=210)
    with pytest.raises(OpenTheoremBoundaryError):
        derive_theta_peak_from_peak_functional(peak)
    with pytest.raises(OpenTheoremBoundaryError):
        OpenPeakReadoutIdentificationOperator().derive_theta_peak(peak)
